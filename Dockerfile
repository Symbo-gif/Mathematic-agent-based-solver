# Dockerfile for SYMBO Agentic Reasoners
# ========================================
#
# Build:
#   docker build -t math-agent-solver .
#
# Run interactive mode:
#   docker run -it math-agent-solver
#
# Solve a single problem:
#   docker run math-agent-solver solve "2 + 2"
#
# Batch process a file (mount volume):
#   docker run -v $(pwd)/problems:/data math-agent-solver solve-file /data/problems.txt

FROM python:3.11-slim

# Set labels
LABEL org.opencontainers.image.title="SYMBO Agentic Reasoners"
LABEL org.opencontainers.image.description="Mathematical Agent-Based Solver"
LABEL org.opencontainers.image.version="0.6.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip cache purge

# Copy the source code
COPY src/ ./src/
COPY config.yaml ./

# Create a non-root user
RUN useradd --create-home --shell /bin/bash solver
USER solver

# Set default config
ENV MATH_SOLVER_LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "from symbo_agentic_reasoners.api import solve_expression; result = solve_expression('1+1'); exit(0 if result.status == 'ok' else 1)"

# Default command - run interactive mode
ENTRYPOINT ["math-agent-solver"]
CMD []
