#!/usr/bin/env bash
# ============================================================
# Hermes → 仓库 反向推回脚本（活文档回仓库）
#
# 用途：Hermes runtime 的 skill 是"活文档"，教训直接写进去后经常忘记推回仓库。
#       sync_to_hermes.sh 的 mtime 守卫会因此拦截下次同步。本脚本把反向过程
#       变成显式操作：先扫描出"runtime 比仓库新/仓库没有"的候选，确认后推回。
#
# 用法：
#   bash scripts/push_back_to_repo.sh             # 扫描模式（只读），列出候选 + diff 统计
#   bash scripts/push_back_to_repo.sh --apply     # 推回模式：备份后复制 runtime → 仓库
#
# 安全设计：
#   - 默认只扫描不写；--apply 才落盘
#   - 覆盖前备份到 .local/backup/pushback/<ts>/（保留相对路径结构）
#   - 推回后提示跑 validate_repo.py + sync_to_hermes.sh 复核
#
# ⚠️ 与 scripts/sync_to_hermes.sh 的映射必须保持一致（改一处改两处）
# ============================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-/d/tools/hermes}"

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

if [ ! -d "$HERMES_HOME/skills" ]; then
  echo "🔴 HERMES_HOME 无效: $HERMES_HOME" >&2
  exit 1
fi

CANDIDATES=()

# ---- 收集反向映射对 (runtime 路径, 仓库相对路径) ----
# 整目录对（写作层 / 主链路 / 排版引擎 / 聚合引擎母版）
DIR_PAIRS=(
  "skills/writing/andiii-writing-style:skills/andiii-writing-style"
  "skills/productivity/wechat-content-automation:skills/wechat-content-automation"
  "skills/productivity/gzh-design-skill:skills/gzh-design-skill"
  "skills/creative/ai-image-style-engine:skills/ai-image-style-engine"
)
# 顶层参考注入的反向（单文件对）
FILE_PAIRS=(
  "skills/productivity/wechat-content-automation/references/image-style-routing.md:references/image-style-routing.md"
  "skills/productivity/wechat-content-automation/references/theme-routing.md:references/theme-routing.md"
  "skills/writing/andiii-writing-style/references/de-ai-craft.md:references/de-ai-craft.md"
  "skills/creative/ai-image-style-engine/references/design-reasoning.md:references/design-reasoning.md"
  "skills/creative/ai-image-style-engine/references/learnings/design-image-studio-anti-slop.md:references/learnings/design-image-studio-anti-slop.md"
)
# 顶层注入目标在 runtime 的副本路径（整目录扫描时跳过，避免误报"仓库缺失"）
INJECTED=(
  "skills/writing/andiii-writing-style/references/de-ai-craft.md"
  "skills/productivity/wechat-content-automation/references/image-style-routing.md"
  "skills/productivity/wechat-content-automation/references/theme-routing.md"
  "skills/creative/ai-image-style-engine/references/design-reasoning.md"
  "skills/creative/ai-image-style-engine/references/learnings/design-image-studio-anti-slop.md"
)

# 视觉引擎自动发现（与 sync_to_hermes.sh 一致）
for d in "$HERMES_HOME"/skills/creative/andiii-*; do
  [ -d "$d" ] || continue
  DIR_PAIRS+=("skills/creative/$(basename "$d"):skills/$(basename "$d")")
done

scan_candidate() {
  # $1 = runtime 文件, $2 = 仓库文件, $3 = 显示名
  local rf="$1" rp="$2" rel="$3" i
  for i in "${INJECTED[@]}"; do
    if [ "$rel" = "$i" ]; then return 0; fi
  done
  if [ ! -f "$rp" ]; then
    echo "🆕 仓库缺失: $rel"
    if [ "$APPLY" = 1 ]; then CANDIDATES+=("$rf|$rp"); fi
    return 0
  fi
  if ! cmp -s "$rf" "$rp" && [ "$rf" -nt "$rp" ]; then
    local lines
    lines=$(diff "$rp" "$rf" 2>/dev/null | grep -c '^[<>]' || true)
    echo "🔵 活文档(runtime 新, ±${lines}行): $rel"
    if [ "$APPLY" = 1 ]; then CANDIDATES+=("$rf|$rp"); fi
  fi
}

# 整目录对：遍历 SKILL.md / references/*.md / scripts/*.py / assets/*.md
for pair in "${DIR_PAIRS[@]}"; do
  rtdir="$HERMES_HOME/${pair%%:*}"
  repodir="$REPO_ROOT/${pair#*:}"
  [ -d "$rtdir" ] || continue
  while IFS= read -r rf; do
    sub="${rf#"$rtdir"/}"                    # 目录内相对路径（SKILL.md / references/x.md）
    rel="${rf#"$HERMES_HOME"/}"              # runtime 侧相对路径（skills/creative/…）
    scan_candidate "$rf" "$repodir/$sub" "$rel"
  done < <(find "$rtdir" -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.html" \) -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/.github/*" 2>/dev/null)
done

# 单文件对
for pair in "${FILE_PAIRS[@]}"; do
  rtdir="$HERMES_HOME/${pair%%:*}"
  rel="${pair#*:}"
  [ -f "$rtdir" ] || continue
  scan_candidate "$rtdir" "$REPO_ROOT/$rel" "$rel"
done

if [ "$APPLY" = 0 ]; then
  echo ""
  echo "===== 扫描完成（只读，未写任何文件）====="
  echo "确认后执行: bash scripts/push_back_to_repo.sh --apply"
  exit 0
fi

N=${#CANDIDATES[@]}
if [ "$N" -eq 0 ]; then
  echo ""
  echo "✅ 无候选推回：runtime 与仓库一致"
  exit 0
fi

BACKUP_DIR="$REPO_ROOT/.local/backup/pushback/$(date +%Y%m%d-%H%M%S)"
PUSHED=0
for c in "${CANDIDATES[@]}"; do
  rf="${c%%|*}"; rp="${c#*|}"
  rel="${rp#"$REPO_ROOT"/}"
  mkdir -p "$BACKUP_DIR/$(dirname "$rel")" "$(dirname "$rp")"
  cp -p "$rp" "$BACKUP_DIR/$rel" 2>/dev/null || true
  cp "$rf" "$rp"
  echo "📤 推回: $rel"
  PUSHED=$((PUSHED + 1))
done

echo ""
echo "===== 推回完成: $PUSHED 个文件 ====="
echo "备份: $BACKUP_DIR"
echo "下一步："
echo "  1. cd $REPO_ROOT && git diff --stat   # 人工确认变更"
echo "  2. python scripts/validate_repo.py    # 校验通过后 commit + push"
echo "  3. bash scripts/sync_to_hermes.sh     # 复核一致性"
