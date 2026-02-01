#!/bin/bash

IMAGE_NAME="vim4rabbit-dev"

# Build the Docker image
docker build -t "$IMAGE_NAME" .

# Run the container interactively with port mapping and local directory mounted
#docker run -it --rm -p 8000:8000 -v "$(pwd)":/app "$IMAGE_NAME"
docker run -it --rm -v "$(pwd)/..":/app/vim4rabbit "$IMAGE_NAME"

exit 0
