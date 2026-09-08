# Mind Archive backend.
#
# Python 3.12 rather than whatever happens to be installed on the host — the
# machine this project started on had Python 3.7 and 3.8, both end-of-life.
# See docs/project-memory/DECISIONS.md D-006.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy the dependency manifest first so that editing source code does not
# invalidate the cached dependency layer.
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e ".[dev]"

COPY tests ./tests

# Run as a non-root user. The archive directory is mounted at runtime and must
# be writable by this user.
RUN useradd --create-home --uid 1000 archive \
    && mkdir -p /data \
    && chown -R archive:archive /app /data
USER archive

EXPOSE 8000

# Bind to all interfaces inside the container; Compose decides what is actually
# published to the host.
CMD ["uvicorn", "mind_archive.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
