FROM nvcr.io/nvidia/l4t-jetpack:r35.3.1

# System deps (kept minimal)
RUN apt-get update && apt-get install -y \
    git build-essential python3 python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Build llama.cpp with CUDA/cuBLAS for Jetson
WORKDIR /workspace
RUN git clone https://github.com/ggerganov/llama.cpp.git
WORKDIR /workspace/llama.cpp
RUN make LLAMA_CUBLAS=1 -j"$(nproc)"

# Keep working directory clean and predictable
WORKDIR /workspace
