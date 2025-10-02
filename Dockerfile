# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Create non-root user first
RUN groupadd --system --gid 999 nonroot \
 && useradd  --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Put the venv ahead of PATH for runtime
ENV PATH="/app/.venv/bin:$PATH"

# Switch early so the venv is created with correct ownership
USER nonroot

# Install deps using only the lock + pyproject; cache under the user's home
RUN --mount=type=cache,target=/home/nonroot/.cache/uv \
    --mount=type=bind,source=uv.lock,target=/app/uv.lock,ro \
    --mount=type=bind,source=pyproject.toml,target=/app/pyproject.toml,ro \
    uv sync --locked --no-install-project --no-dev

# Now add the project sources owned by nonroot, then install the project
COPY --chown=999:999 . /app
RUN --mount=type=cache,target=/home/nonroot/.cache/uv \
    uv sync --locked --no-dev

CMD ["uv", "run", "main.py"]
