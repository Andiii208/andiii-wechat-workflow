#!/usr/bin/env bash
# 同步 andiii-image-style 引擎到 Hermes skills 目录（单向：仓库 → Hermes）
# 用法：改完仓库里的引擎后运行 `bash scripts/sync_to_hermes.sh`
# 背景：仓库是主副本，Hermes skills 目录是运行副本；手动 cp 易漏（2026-08-03 两次差点漏同步）
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/skills/andiii-image-style"
DST="/d/tools/hermes/skills/creative/andiii-image-style"

if [ ! -d "$SRC" ]; then
  echo "❌ 源目录不存在: $SRC" >&2
  exit 1
fi
if [ ! -d "$DST" ]; then
  echo "❌ Hermes 目标目录不存在: $DST" >&2
  exit 1
fi

cp "$SRC/SKILL.md" "$DST/SKILL.md"
cp "$SRC/scripts/check_engine_prompt.py" "$DST/scripts/"
cp "$SRC/scripts/crop_image.py" "$DST/scripts/"
cp "$SRC/references/watercolor-prompt-library.md" "$DST/references/"
cp "$SRC/references/NOTES.md" "$DST/references/"

echo "✅ 已同步 Hermes:"
echo "   - SKILL.md"
echo "   - scripts/check_engine_prompt.py"
echo "   - scripts/crop_image.py"
echo "   - references/watercolor-prompt-library.md"
echo "   - references/NOTES.md"
