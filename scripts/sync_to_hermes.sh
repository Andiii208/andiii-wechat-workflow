#!/usr/bin/env bash
# 同步 andiii-* 风格引擎到 Hermes skills 目录（单向：仓库 → Hermes）
# 用法：改完仓库里的引擎后运行 `bash scripts/sync_to_hermes.sh`
# 背景：仓库是主副本，Hermes skills 目录是运行副本；手动 cp 易漏（2026-08-03 两次差点漏同步）
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_SKILLS="/d/tools/hermes/skills/creative"

# 🔴 mtime 守卫（2026-08-06 事故后加）：仓库→Hermes 单向同步只允许"仓库更新"覆盖。
#   若 Hermes 副本比仓库新（Hermes 是活文档、内容未推回仓库），跳过并告警——否则会静默丢教训。
#   用法同 cp：guarded_cp <src> <dst>
guarded_cp() {
  local src="$1" dst="$2"
  if [ ! -f "$src" ]; then
    echo "⚠️  跳过（仓库无此文件）: $src"
    return 0
  fi
  # 内容一致 → 无事发生
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    return 0
  fi
  # 内容不一致且 Hermes 副本比仓库新 → 疑似未推回的活文档，拦截
  if [ -f "$dst" ] && [ "$dst" -nt "$src" ]; then
    echo "🔴 跳过（Hermes 副本比仓库新，疑似未推回的活文档）: $dst"
    echo "   处理：先 diff 确认 Hermes 独有内容 → 反向同步进仓库 → 再跑本脚本"
    return 1
  fi
  cp "$src" "$dst"
  return 0
}

ENGINES=(andiii-image-style andiii-zine-style andiii-heytear-style andiii-sketchy-style andiii-minimal-style)

for ENG in "${ENGINES[@]}"; do
  SRC="$REPO_ROOT/skills/$ENG"
  DST="$HERMES_SKILLS/$ENG"

  if [ ! -d "$SRC" ]; then
    echo "⚠️  跳过（仓库无此引擎）: $ENG"
    continue
  fi
  mkdir -p "$DST" "$DST/scripts" "$DST/references"

  guarded_cp "$SRC/SKILL.md" "$DST/SKILL.md" || true
  [ -d "$SRC/scripts" ] && cp "$SRC/scripts/"*.py "$DST/scripts/" 2>/dev/null || true
  [ -d "$SRC/references" ] && cp "$SRC/references/"*.md "$DST/references/" 2>/dev/null || true

  echo "✅ $ENG → Hermes"
done

# 写作层参考（de-ai-craft 手册，仓库为主副本 → Hermes andiii-writing-style）
DEAIC_SRC="$REPO_ROOT/references/de-ai-craft.md"
DEAIC_DST="/d/tools/hermes/skills/writing/andiii-writing-style/references/de-ai-craft.md"
if [ -f "$DEAIC_SRC" ]; then
  guarded_cp "$DEAIC_SRC" "$DEAIC_DST"
  echo "✅ de-ai-craft.md → Hermes (andiii-writing-style)"
fi

# 顶层参考（design-reasoning / image-style-routing / theme-routing / de-ai-craft，仓库为主副本 → Hermes 对应 skill）
# ⚠️ 2026-08-06 教训（两次）: image-style-routing.md 和 de-ai-craft.md 曾同时存在于 skills/*/references/（旧副本），
#    同步时后拷的旧副本覆盖了顶层新副本 → Hermes 丢新行。顶层 references/ 是唯一权威源，skills/*/references/ 不得放同名副本。
#    已删除 skills/andiii-writing-style/references/de-ai-craft.md 与 skills/wechat-content-automation/references/theme-routing.md。
declare -A REF_MAP=(
  ["design-reasoning.md"]="/d/tools/hermes/skills/creative/ai-image-style-engine/references/design-reasoning.md"
  ["image-style-routing.md"]="/d/tools/hermes/skills/productivity/wechat-content-automation/references/image-style-routing.md"
  ["theme-routing.md"]="/d/tools/hermes/skills/productivity/wechat-content-automation/references/theme-routing.md"
)
for REF in "${!REF_MAP[@]}"; do
  if [ -f "$REPO_ROOT/references/$REF" ]; then
    guarded_cp "$REPO_ROOT/references/$REF" "${REF_MAP[$REF]}"
    echo "✅ $REF → Hermes"
  fi
done

# 写作层 skill 本体（仓库为主副本 → Hermes skills 目录，2026-08-04 起纳入）
mkdir -p "/d/tools/hermes/skills/writing/andiii-writing-style/references" \
         "/d/tools/hermes/skills/productivity/wechat-content-automation/references"
guarded_cp "$REPO_ROOT/skills/andiii-writing-style/SKILL.md" "/d/tools/hermes/skills/writing/andiii-writing-style/SKILL.md"
[ -d "$REPO_ROOT/skills/andiii-writing-style/references" ] && cp "$REPO_ROOT/skills/andiii-writing-style/references/"*.md "/d/tools/hermes/skills/writing/andiii-writing-style/references/" 2>/dev/null || true
guarded_cp "$REPO_ROOT/skills/wechat-content-automation/SKILL.md" "/d/tools/hermes/skills/productivity/wechat-content-automation/SKILL.md"
[ -d "$REPO_ROOT/skills/wechat-content-automation/references" ] && cp "$REPO_ROOT/skills/wechat-content-automation/references/"*.md "/d/tools/hermes/skills/productivity/wechat-content-automation/references/" 2>/dev/null || true
echo "✅ 写作层 skill → Hermes (andiii-writing-style + wechat-content-automation)"

echo "完成。引擎清单: ${ENGINES[*]}"
