#!/usr/bin/env bash
# ============================================================
# 仓库 → Hermes 单向部署脚本（2026-08-06 加固版）
#
# 用法：
#   bash scripts/sync_to_hermes.sh             # 常规同步
#   bash scripts/sync_to_hermes.sh --prune     # 同步 + 清理陈旧文件（引擎目录与注入目标）
#   HERMES_HOME=D:/tools/hermes bash scripts/sync_to_hermes.sh   # 指定 Hermes 根（默认 /d/tools/hermes）
#
# 特性：
#   1. 自动收集 skills/andiii-* 引擎清单（新增引擎无需改脚本）
#   2. mtime 活文档守卫：Hermes 副本比仓库新 = 疑似未推回活文档 → 拦截并置失败
#   3. 覆盖前自动备份到 .local/backup/<ts>/（gitignored）
#   4. 拷贝失败即失败（退出码非零），不再静默吞错
#   5. --prune：删除目标目录中仓库已不存在的陈旧文件（仅视觉引擎目录 + 顶层注入目标）
#   6. 同步完成后逐文件 cmp 复核
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-/d/tools/hermes}"

if [ ! -d "$HERMES_HOME/skills" ]; then
  echo "🔴 HERMES_HOME 无效: $HERMES_HOME（可用 HERMES_HOME=xxx 覆盖）" >&2
  exit 1
fi

PRUNE=0
[ "${1:-}" = "--prune" ] && PRUNE=1

BACKUP_DIR="$REPO_ROOT/.local/backup/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "🗂  备份目录: $BACKUP_DIR"

FAILED=0
COPIED=0
SKIPPED_SAME=0

# --- mtime 活文档守卫（2026-08-06 事故后保留，绝不可移除）---
# 仓库→Hermes 单向同步只允许"仓库更新"覆盖；Hermes 副本比仓库新 = 活文档未推回 → 拦截
guarded_cp() {
  local src="$1" dst="$2"
  if [ ! -f "$src" ]; then
    echo "⚠️  跳过（仓库无此文件）: $src" >&2
    return 0
  fi
  mkdir -p "$(dirname "$dst")"
  if [ -f "$dst" ] && cmp -s "$src" "$dst"; then
    SKIPPED_SAME=$((SKIPPED_SAME + 1))
    return 0
  fi
  if [ -f "$dst" ] && [ "$dst" -nt "$src" ]; then
    echo "🔴 拦截（Hermes 副本比仓库新，疑似未推回活文档）: $dst" >&2
    echo "   处理：先 diff 确认 → 反向推回仓库 → 再跑本脚本" >&2
    FAILED=1
    return 1
  fi
  if [ -f "$dst" ]; then
    cp -p "$dst" "$BACKUP_DIR/" 2>/dev/null || true
  fi
  if ! cp "$src" "$dst"; then
    echo "🔴 拷贝失败: $src → $dst" >&2
    FAILED=1
    return 1
  fi
  COPIED=$((COPIED + 1))
  return 0
}

# --- 自动收集引擎清单（新增引擎无需改脚本）---
VISUAL_ENGINES=()
WRITING_SKILLS=()
for d in "$REPO_ROOT"/skills/andiii-*; do
  [ -d "$d" ] || continue
  b="$(basename "$d")"
  case "$b" in
    andiii-writing-style) WRITING_SKILLS+=("$b") ;;
    *) VISUAL_ENGINES+=("$b") ;;
  esac
done

# 顶层参考 → 注入目标映射（顶层 references/ 是唯一权威源，skill 内不放同名副本）
declare -A REF_MAP=(
  ["design-reasoning.md"]="$HERMES_HOME/skills/creative/ai-image-style-engine/references/design-reasoning.md"
  ["image-style-routing.md"]="$HERMES_HOME/skills/productivity/wechat-content-automation/references/image-style-routing.md"
  ["theme-routing.md"]="$HERMES_HOME/skills/productivity/wechat-content-automation/references/theme-routing.md"
  ["de-ai-craft.md"]="$HERMES_HOME/skills/writing/andiii-writing-style/references/de-ai-craft.md"
)

echo "== 视觉引擎: ${VISUAL_ENGINES[*]:-（无）} | 写作层: ${WRITING_SKILLS[*]:-（无）} =="

# ---- 1. 视觉引擎 → Hermes creative/ ----
for ENG in "${VISUAL_ENGINES[@]}"; do
  SRC="$REPO_ROOT/skills/$ENG"
  DST="$HERMES_HOME/skills/creative/$ENG"
  mkdir -p "$DST/scripts" "$DST/references"

  guarded_cp "$SRC/SKILL.md" "$DST/SKILL.md" || true
  if [ -d "$SRC/scripts" ]; then
    for f in "$SRC/scripts/"*.py; do
      [ -f "$f" ] && guarded_cp "$f" "$DST/scripts/$(basename "$f")" || true
    done
  fi
  if [ -d "$SRC/references" ]; then
    for f in "$SRC/references/"*.md; do
      [ -f "$f" ] && guarded_cp "$f" "$DST/references/$(basename "$f")" || true
    done
  fi

  # ---- stale 清理（仅 --prune；引擎目录是纯仓库资产，Hermes 侧不应有独有文件）----
  if [ "$PRUNE" = 1 ]; then
    newest_repo="$(ls -t "$SRC"/SKILL.md "$SRC"/scripts/*.py "$SRC"/references/*.md 2>/dev/null | head -1 || true)"
    while IFS= read -r stale; do
      rel="${stale#"$DST"/}"
      [ -f "$SRC/$rel" ] && continue
      # prune 守卫：stale 文件比仓库最新文件还新 = 疑似刚写过的活文档 → 拦截，不删
      if [ -n "$newest_repo" ] && [ "$stale" -nt "$newest_repo" ]; then
        echo "🔴 拦截（陈旧但比仓库最新文件还新，疑似活文档）: $rel" >&2
        FAILED=1
        continue
      fi
      cp -p "$stale" "$BACKUP_DIR/" 2>/dev/null || true
      rm -f "$stale"
      echo "🗑  清理陈旧文件: $rel（已备份）"
    done < <(find "$DST" -type f \( -name "*.md" -o -name "*.py" \) 2>/dev/null)
  fi
  echo "✅ $ENG → Hermes"
done

# ---- 2. 顶层参考注入 ----
for REF in "${!REF_MAP[@]}"; do
  if [ -f "$REPO_ROOT/references/$REF" ]; then
    guarded_cp "$REPO_ROOT/references/$REF" "${REF_MAP[$REF]}" || true
  else
    echo "⚠️  仓库无顶层参考: references/$REF" >&2
    FAILED=1
  fi
done
echo "✅ 顶层参考注入完成"

# ---- 3. 写作层 skill 整目录同步 ----
for SK in "${WRITING_SKILLS[@]}"; do
  case "$SK" in
    andiii-writing-style) DST="$HERMES_HOME/skills/writing/$SK" ;;
    *) DST="$HERMES_HOME/skills/writing/$SK" ;;
  esac
  mkdir -p "$DST/references"
  guarded_cp "$REPO_ROOT/skills/$SK/SKILL.md" "$DST/SKILL.md" || true
  if [ -d "$REPO_ROOT/skills/$SK/references" ]; then
    for f in "$REPO_ROOT/skills/$SK/references/"*.md; do
      [ -f "$f" ] && guarded_cp "$f" "$DST/references/$(basename "$f")" || true
    done
  fi
  echo "✅ $SK → Hermes"
done

# wechat-content-automation（productivity/ 分类）
WCA_SRC="$REPO_ROOT/skills/wechat-content-automation"
WCA_DST="$HERMES_HOME/skills/productivity/wechat-content-automation"
mkdir -p "$WCA_DST/references"
guarded_cp "$WCA_SRC/SKILL.md" "$WCA_DST/SKILL.md" || true
if [ -d "$WCA_SRC/references" ]; then
  for f in "$WCA_SRC/references/"*.md; do
    [ -f "$f" ] && guarded_cp "$f" "$WCA_DST/references/$(basename "$f")" || true
  done
fi
echo "✅ wechat-content-automation → Hermes"

# ---- 4. 最终复核：仓库 vs Hermes 逐文件 cmp（仅覆盖仓库声明的文件）----
echo "== 复核中… =="
MISMATCH=0
verify() {
  local src="$1" dst="$2"
  if [ -f "$src" ] && [ -f "$dst" ] && ! cmp -s "$src" "$dst"; then
    echo "🔴 复核不一致: $dst" >&2
    MISMATCH=$((MISMATCH + 1))
  fi
}
for ENG in "${VISUAL_ENGINES[@]}"; do
  SRC="$REPO_ROOT/skills/$ENG"; DST="$HERMES_HOME/skills/creative/$ENG"
  verify "$SRC/SKILL.md" "$DST/SKILL.md"
  [ -d "$SRC/scripts" ] && for f in "$SRC/scripts/"*.py; do [ -f "$f" ] && verify "$f" "$DST/scripts/$(basename "$f")"; done
  [ -d "$SRC/references" ] && for f in "$SRC/references/"*.md; do [ -f "$f" ] && verify "$f" "$DST/references/$(basename "$f")"; done
done
for REF in "${!REF_MAP[@]}"; do
  [ -f "$REPO_ROOT/references/$REF" ] && verify "$REPO_ROOT/references/$REF" "${REF_MAP[$REF]}"
done
verify "$REPO_ROOT/skills/andiii-writing-style/SKILL.md" "$HERMES_HOME/skills/writing/andiii-writing-style/SKILL.md"
verify "$WCA_SRC/SKILL.md" "$WCA_DST/SKILL.md"

# ---- 5. 汇总 ----
echo ""
echo "===== 同步汇总 ====="
echo "复制/更新: $COPIED  | 已一致跳过: $SKIPPED_SAME | 拦截或失败: $FAILED | 复核不一致: $MISMATCH"
if [ "$PRUNE" = 1 ]; then echo "陈旧文件清理: 已启用"; else echo "陈旧文件清理: 未启用（加 --prune 启用）"; fi

if [ "$FAILED" -gt 0 ] || [ "$MISMATCH" -gt 0 ]; then
  echo "🔴 同步未完全成功，请按上方提示处理（常见：Hermes 活文档未推回仓库）" >&2
  exit 1
fi
echo "✅ 同步完成，仓库与 Hermes 一致"
