#!/usr/bin/env bash
# GitHub Actions 自托管 Runner 入口（固定路径，便于 sudoers 授权）
set -euo pipefail

TARBALL="${1:?用法: ci-deploy.sh /path/to/dormguard-release.tar.gz}"
WORK="${2:-/tmp/dormguard-release}"

if [ ! -f "$TARBALL" ]; then
  echo "错误：找不到发布包 $TARBALL" >&2
  exit 1
fi

rm -rf "$WORK"
mkdir -p "$WORK"
tar xzf "$TARBALL" -C "$WORK"

if [ ! -f "$WORK/deploy/apply-release.sh" ]; then
  echo "错误：发布包内缺少 deploy/apply-release.sh" >&2
  exit 1
fi

exec /usr/bin/bash "$WORK/deploy/apply-release.sh" "$WORK"
