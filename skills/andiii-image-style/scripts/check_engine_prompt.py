#!/usr/bin/env python3
"""andiii-image-style 质检门 v1 — prompt 层检查（无 vision 依赖）。

用法:
    echo "prompt内容" | python check_engine_prompt.py
    python check_engine_prompt.py prompt.txt

退出码: 0 = PASS, 1 = FAIL/WARN
"""
import sys

PAPER_WORDS = [
    "cold-pressed paper", "paper texture", "paper fiber", "aged paper",
    "washi", "水彩纸", "旧纸", "纸纹", "纸纤维",
]
TEXTURE_WORDS = [
    "brush stroke", "wet-on-wet", "granulating", "bloom", "bleeding",
    "splatter", "wash", "晕染", "笔触", "渗开", "水痕", "洗淡",
]
HARD_BLOCK = [
    "flat vector", "minimalist line art", "charcoal", "gold foil",
    "gallery poster", "vivid gradient", "glassmorphism", "neon glow",
    "3d render", "anime style", "swiss grid", "matte poster",
    "clean white background", "cta", "logo",
    "全出血", "玻璃拟态", "霓虹灯", "日系动漫",
]
SOFT_WARN = [
    "gradient", "drop shadow", "bokeh", "photo-realistic",
    "stock photo", "high saturation",
]


def check(text: str):
    t = text.lower()
    issues = []
    if not any(w in t for w in PAPER_WORDS):
        issues.append("FAIL: 缺纸感词 (cold-pressed paper / 纸纹 / 旧纸 …)")
    tex_hits = [w for w in TEXTURE_WORDS if w in t]
    if len(tex_hits) < 2:
        issues.append(f"FAIL: 纹理词 < 2 个 (当前 {len(tex_hits)}: {tex_hits})")
    if not any(w in t for w in ["16:9", "1:1", "21:9", "square", "portrait", "landscape", "竖版", "横版", "方形"]):
        issues.append("FAIL: 缺画布比例声明")
    for w in HARD_BLOCK:
        if w in t:
            issues.append(f"FAIL: 硬规避命中 [{w}]")
    for w in SOFT_WARN:
        if w in t:
            issues.append(f"WARN: 软规避命中 [{w}]")
    has_fail = any(i.startswith("FAIL") for i in issues)
    return ("FAIL" if has_fail else "PASS", issues)


def main():
    # Windows 下 stdin 管道可能是 GBK 解码，强制 UTF-8 防中文 prompt 误判（2026-08-03）
    try:
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    status, issues = check(text)
    print(status)
    for i in issues:
        print(" ", i)
    sys.exit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
