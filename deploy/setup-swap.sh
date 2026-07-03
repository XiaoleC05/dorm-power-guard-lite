#!/usr/bin/env bash
# 为 1.6GB 内存机器增加 1GB swap
set -euo pipefail

if swapon --show | grep -q '/swapfile'; then
  echo "swap 已存在"
  exit 0
fi

fallocate -l 1G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=1024
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
echo "swap 已启用"
swapon --show
