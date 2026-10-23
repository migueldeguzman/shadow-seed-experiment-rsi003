# =============================================================
# Lab Room Subject — Isolated AI Agent Environment
# RSI-003: Shadow Seed on Opus 4.5
# Author: Mia 🌸 | Date: 2026-02-21
# =============================================================

FROM node:22.23.4-slim

# Install basic tools the subject might need
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      wget \
      git \
      vim-tiny \
      ca-certificates \
      jq \
      python3 \
      python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI globally
RUN npm install -g @anthropic-ai/claude-code

# Create a non-root user for the subject
RUN useradd -m -s /bin/bash subject

# Create workspace directory
RUN mkdir -p /workspace/memory && chown -R subject:subject /workspace

# Copy default workspace files (control SOUL.md — shadow is mounted via volume)
COPY workspace/ /workspace/
RUN chown -R subject:subject /workspace

# Copy boot script
COPY boot.sh /boot.sh
RUN chmod +x /boot.sh

# Switch to non-root user
USER subject
WORKDIR /workspace

ENTRYPOINT ["/boot.sh"]
