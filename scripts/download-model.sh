#!/bin/bash

set -e

echo "📥 Downloading Llama 3.2 1B Instruct model (GGUF format)..."

# Create models directory
mkdir models

# Model URL (Hugging Face)
MODEL_URL="https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
MODEL_FILE="../models/llama-3.2-1b-instruct-q4_k_m.gguf"

# Check if model already exists
if [ -f "$MODEL_FILE" ]; then
    echo "✅ Model already exists at $MODEL_FILE"
    echo "   Size: $(du -h "$MODEL_FILE" | cut -f1)"
    exit 0
fi

echo "📦 Downloading model (~800MB)..."
echo "   This may take a few minutes depending on your internet speed..."

# Download with wget (shows progress)
if command -v wget &> /dev/null; then
    wget -O "$MODEL_FILE" "$MODEL_URL"
elif command -v curl &> /dev/null; then
    curl -L -o "$MODEL_FILE" "$MODEL_URL"
else
    echo "❌ Neither wget nor curl found. Please install one of them."
    exit 1
fi

echo "✅ Model downloaded successfully!"
echo "   Location: $MODEL_FILE"
echo "   Size: $(du -h "$MODEL_FILE" | cut -f1)"

 
