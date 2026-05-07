FROM python:3.11-slim AS builder

WORKDIR /build

# Install build deps
RUN pip install --no-cache-dir build

COPY . .

# Build wheel
RUN python -m build --wheel

# ---------------------------------------------------------------------------
# Runtime image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy wheel from builder
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy patterns (loaded at runtime by auto-kit CLI)
COPY patterns/ /app/patterns/

# Non-root user
RUN useradd -m automationkit
USER automationkit

ENTRYPOINT ["auto-kit"]
CMD ["--help"]
