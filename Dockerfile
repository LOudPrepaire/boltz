FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

RUN apt-get update && \
    apt-get install -y locales && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
    apt-get install -y wget git build-essential nano unzip curl g++ libfftw3-3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.utf8

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /miniconda && \
    rm miniconda.sh

ENV PATH="/miniconda/bin:${PATH}"

# Initialize Conda and set up environment
RUN echo 'export PATH="/miniconda/bin:${PATH}"' >> ~/.bashrc && \
    /miniconda/bin/conda init bash && \
    /miniconda/bin/conda config --set auto_activate_base false

# Create a Conda environment with Python 3.10
RUN /miniconda/bin/conda create -n myenv python=3.10 -y && \
    /miniconda/bin/conda run -n myenv conda install -c bioconda abnumber -y && \
    /miniconda/bin/conda run -n myenv conda install -c conda-forge pdbfixer pyyaml -y && \
    /miniconda/bin/conda run -n myenv conda install -c pytorch -c nvidia pytorch torchvision torchaudio pytorch-cuda=11.8 -y

# Install pip dependencies in the Conda environment
RUN /miniconda/bin/conda run -n myenv pip install --no-cache-dir bolt boto3

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /workspace
COPY . /workspace/

# Set permissions for entrypoint
RUN chmod +x /workspace/entrypoint.sh

# Activate Conda environment in entrypoint
CMD ["/miniconda/bin/conda", "run", "-n", "myenv", "bash", "/workspace/entrypoint.sh"]