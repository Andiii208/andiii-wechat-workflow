#!/usr/bin/env bash
# 同步 andiii-* 风格引擎到 Hermes skills 目录（单向：仓库 → Hermes）
# 用法：改完仓库里的引擎后运行 `bash scripts/sync_to_hermes.sh`
# 背景：仓库是主副本，Hermes skills 目录是运行副本；手动 cp 易漏（2026-08-03 两次差点漏同步）
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_SKILLS="/d/tools/hermes/skills/creative"

ENGINES=(andiii-image-style andiii-zine-style andiii-heytear-style andiii-sketchy-style andiii-minimal-style)

for ENG in "${ENGINES[@]}"; do
  SRC="$REPO_ROOT/skills/$ENG"
  DST="$HERMES_SKILLS/$ENG"

  if [ ! -d "$SRC" ]; then
    echo "⚠️  跳过（仓库无此引擎）: $ENG"
    continue
  fi
  mkdir -p "$DST" "$DST/scripts" "$DST/references"

  cp "$SRC/SKILL.md" "$DST/SKILL.md" 2>/dev/null || true
  [ -d "$SRC/scripts" ] && cp "$SRC/scripts/"*.py "$DST/scripts/" 2>/dev/null || true
  [ -d "$SRC/references" ] && cp "$SRC/references/"*.md "$DST/references/" 2>/dev/null || true

  echo "✅ $ENG → Hermes"
done

echo "完成。引擎清单: ${ENGINES[*]}"
