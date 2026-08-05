#!/usr/bin/env python3
"""andiii-image-style 质检门 v1.1 — prompt 层检查（无 vision 依赖）。

用法:
    echo "prompt内容" | python check_engine_prompt.py
    python check_engine_prompt.py prompt.txt
    python check_engine_prompt.py --format json prompt.txt

退出码: 0 = PASS, 1 = FAIL, 2 = WARN（软规避命中）, 3 = 脚本/参数错误

2026-08-06 修订:
    - 退出码三态化：WARN 不再伪装成 PASS（原实现 WARN-only 返回 0）
    - --format json 机器可读输出（含 exit_code，供 CI/包装器消费）
    - 负向表达识别升级：规避词后 8 字符内出现目标词即豁免
      （"不要使用高饱和" / "do not use neon glow" 不再误报）
    - 软规避（SOFT_WARN）同样应用负向豁免

已知限制（2026-08-06 记录）:
    - 纸感/纹理/规避词表为全引擎共用，未做 per-engine profile
      （石墨极简/黑白针管笔等非纸张风格需要独立词表时再引入 policies/）
    - 负向豁免是全文级：同一词在"豁免句 + 正向句"中同时出现时整体豁免
"""
import json
import re
import sys

PAPER_WORDS = [
    "cold-pressed paper", "paper texture", "paper fiber", "aged paper",
    "washi", "水彩纸", "旧纸", "纸纹", "纸纤维",
    # 喜茶系 / 潦草系（2026-08-03 加）
    "宣纸", "牛皮纸", "sketch paper", "白纸",
]
TEXTURE_WORDS = [
    "brush stroke", "wet-on-wet", "granulating", "bloom", "bleeding",
    "splatter", "wash", "晕染", "笔触", "渗开", "水痕", "洗淡",
    # zine 系（andiii-zine-style，2026-08-03 加）
    "risograph", "xerox", "halftone", "scan noise", "ink bleed",
    "grain", "mottling", "letterpress", "拼贴", "影印",
    # 喜茶系（新中式，2026-08-03 加）
    "水墨", "茶渍", "印章", "书法", "宣纸纹理",
    # 潦草系（sketchy 手账，2026-08-03 加）
    "sketchy", "scribble", "doodle", "胶带", "涂改", "马克笔", "铅笔",
    # 极简系（andiii-minimal-style，2026-08-03 加）
    "hairline", "grid", "cross-hatch", "subtle shadow", "monochrome", "几何",
]
HARD_BLOCK = [
    "flat vector", "minimalist line art", "charcoal", "gold foil",
    "gallery poster", "vivid gradient", "glassmorphism", "neon glow",
    "3d render", "anime style", "swiss grid", "matte poster",
    "clean white background", "cta", "logo",
    "全出血", "玻璃拟态", "霓虹灯", "日系动漫",
    "炭黑金", "高饱和", "渐变紫", "动漫脸", "卡通",
]
SOFT_WARN = [
    "gradient", "drop shadow", "bokeh", "photo-realistic",
    "stock photo", "high saturation",
]

# 规避表述豁免："避免X / 不要X / do not use X / avoid X / without X" 不算命中。
# 2026-08-06 升级：目标词前 12 字符内出现规避前缀即豁免（不再要求连续前缀）
_AVOID_RE = re.compile(r"(?:避免|不要|no\s+|not\s+|avoid\s+|without\s+)")


def _is_avoided(t: str, w: str) -> bool:
    idx = t.find(w.lower())
    if idx < 0:
        return False
    start = max(0, idx - 12)
    return _AVOID_RE.search(t[start:idx]) is not None


def check(text: str):
    t = text.lower()
    issues = []
    if not any(w in t for w in PAPER_WORDS):
        issues.append("FAIL: 缺纸感词 (cold-pressed paper / 纸纹 / 旧纸 …)")
    tex_hits = [w for w in TEXTURE_WORDS if w in t and not _is_avoided(t, w)]
    if len(tex_hits) < 2:
        issues.append(f"FAIL: 纹理词 < 2 个 (当前 {len(tex_hits)}: {tex_hits})")
    if not any(w in t for w in ["16:9", "1:1", "21:9", "square", "portrait", "landscape", "竖版", "横版", "方形"]):
        issues.append("FAIL: 缺画布比例声明")
    for w in HARD_BLOCK:
        if w in t and not _is_avoided(t, w):
            issues.append(f"FAIL: 硬规避命中 [{w}]")
    for w in SOFT_WARN:
        if w in t and not _is_avoided(t, w):
            issues.append(f"WARN: 软规避命中 [{w}]")
    has_fail = any(i.startswith("FAIL") for i in issues)
    has_warn = any(i.startswith("WARN") for i in issues)
    if has_fail:
        return ("FAIL", issues)
    if has_warn:
        return ("WARN", issues)
    return ("PASS", issues)


def main():
    args = sys.argv[1:]
    fmt = "text"
    if "--format" in args:
        i = args.index("--format")
        fmt = args[i + 1] if i + 1 < len(args) else "text"
        del args[i:i + 2]
    if fmt not in ("text", "json"):
        print(f"🔴 未知 --format: {fmt}（支持 text/json）", file=sys.stderr)
        sys.exit(3)

    # Windows 下 stdin 管道可能是 GBK 解码，强制 UTF-8 防中文 prompt 误判（2026-08-03）
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if args and args[0] != "-":
        try:
            with open(args[0], encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"🔴 读取失败: {e}", file=sys.stderr)
            sys.exit(3)
    else:
        text = sys.stdin.read()

    status, issues = check(text)
    code = {"PASS": 0, "FAIL": 1, "WARN": 2}[status]

    if fmt == "json":
        print(json.dumps(
            {"status": status, "exit_code": code, "issues": issues},
            ensure_ascii=False,
        ))
    else:
        print(status)
        for i in issues:
            print(" ", i)
    sys.exit(code)


if __name__ == "__main__":
    main()
