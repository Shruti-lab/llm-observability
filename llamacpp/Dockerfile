# Custom llama.cpp Dockerfile for Kubernetes
# This bakes the model into the image for self-contained deployment

FROM ubuntu:22.04 AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone and build llama.cpp
WORKDIR /app
RUN git clone https://github.com/ggerganov/llama.cpp.git
WORKDIR /app/llama.cpp
RUN cmake -B build -DLLAMA_CURL=ON && \
    cmake --build build --config Release -j$(nproc)

# Download model (baked into image)
RUN wget -O /app/model.gguf \
    https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf

# Final stage - smaller image
FROM ubuntu:22.04

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built binary and model from builder
COPY --from=builder /app/llama.cpp/build/bin/llama-server /usr/local/bin/llama-server
COPY --from=builder /app/model.gguf /models/model.gguf

# Create non-root user
RUN useradd -m -u 1000 llama && \
    chown -R llama:llama /models

USER llama
WORKDIR /home/llama

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run server
CMD ["llama-server", \
     "--model", "/models/model.gguf", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--ctx-size", "2048", \
     "--n-predict", "128", \
     "--threads", "4"]