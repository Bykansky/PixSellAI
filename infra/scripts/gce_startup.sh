#!/bin/bash
apt-get update
apt-get install -y docker.io
systemctl enable docker
# In production: install NVIDIA drivers and nvidia-docker2 for GPU support
