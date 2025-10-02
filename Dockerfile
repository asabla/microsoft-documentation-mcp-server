FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

USER nonroot
WORKDIR /home/nonroot/app

ENV UV_COMPILE_BYTECODE=1
ENV UV_CACHE_DIR=/home/nonroot/.cache/uv

RUN --mount=type=cache,target=/home/nonroot/.cache/uv,uid=999,gid=999 \
    --mount=type=bind,source=uv.lock,target=/home/nonroot/app/uv.lock,ro \
    --mount=type=bind,source=pyproject.toml,target=/home/nonroot/app/pyproject.toml,ro \
    uv sync --locked --no-install-project --no-dev

COPY --chown=999:999 . /home/nonroot/app
RUN --mount=type=cache,target=/home/nonroot/.cache/uv,uid=999,gid=999 \
    uv sync --locked --no-dev

CMD ["uv", "run", "main.py"]
