#!/usr/bin/env python3
"""andiii-image-style 图片裁剪脚本 — 锚点裁剪 + LANCZOS 缩放 + JPEG 压缩（2026-08-06 加固版）。

用法:
    python crop_image.py <input> <output> [--ratio 16:9] [--anchor center|bottom|top] [--width 900] [--quality 85]

设计背景（2026-08-03）:
    Wan2.7 只出 16:9/1:1/9:16，公众号首图需裁成 2.35:1 ≈ 900×383。
    引擎模板规定主体簇位于画面下方 → 中心裁剪会切掉下方主体（实测确认）。
    → 封面用 --anchor bottom（保留底部主体），内文图用默认 center。

2026-08-06 加固（对齐文档承诺）:
    - 裁剪后 LANCZOS resize 到 --width（默认 900，只缩不放）
    - EXIF orientation 修正（手机图方向正确）
    - 参数合法性校验（ratio / quality / anchor）
    - 输出扩展名强制 .jpg（避免 .png 文件名装 JPEG 内容）
    - 临时文件 + 原子替换（中断不产生半成品）
    - 输出后重新打开验证真实格式与尺寸
"""
import argparse
import os
import re
import sys
import tempfile

from PIL import Image, ImageOps


def parse_ratio(text: str) -> tuple[float, float]:
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)", text.strip())
    if not m:
        raise ValueError(f"非法比例: {text!r}（应为 W:H，如 16:9 / 2.35:1 / 1:1）")
    rw, rh = float(m.group(1)), float(m.group(2))
    if rw <= 0 or rh <= 0:
        raise ValueError(f"比例必须为正数: {text!r}")
    return rw, rh


def crop(img: Image.Image, rw: float, rh: float, anchor: str) -> Image.Image:
    w, h = img.size
    target = rw / rh
    cur = w / h
    if cur > target:  # 太宽 → 裁左右（中心即可，标题横向居中）
        nw = max(1, int(h * target))
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    # 太高 → 裁上下
    nh = max(1, int(w / target))
    if anchor == "bottom":
        y = h - nh          # 保留底部（主体常在下方）
    elif anchor == "top":
        y = 0               # 保留顶部
    else:
        y = (h - nh) // 2   # 中心裁剪
    return img.crop((0, y, w, y + nh))


def main():
    ap = argparse.ArgumentParser(description="按目标比例裁剪图片、缩放到目标宽度并压成 JPEG")
    ap.add_argument("input", help="输入图片路径")
    ap.add_argument("output", help="输出 jpg 路径")
    ap.add_argument("--ratio", default="16:9", help="目标比例，如 16:9 / 2.35:1 / 1:1（默认 16:9）")
    ap.add_argument("--anchor", default="center", choices=["center", "bottom", "top"],
                    help="上下裁剪锚点：center=中心（默认），bottom=保留底部（封面用），top=保留顶部")
    ap.add_argument("--width", type=int, default=900,
                    help="输出宽度 px（LANCZOS 缩放，默认 900；设 0 不缩放）")
    ap.add_argument("--quality", type=int, default=85, help="JPEG 质量 1-100（默认 85）")
    args = ap.parse_args()

    # ---- 参数校验 ----
    try:
        rw, rh = parse_ratio(args.ratio)
    except ValueError as e:
        print(f"🔴 {e}", file=sys.stderr)
        sys.exit(2)
    if not 1 <= args.quality <= 100:
        print(f"🔴 quality 必须在 1-100 之间: {args.quality}", file=sys.stderr)
        sys.exit(2)
    if args.width < 0:
        print(f"🔴 width 不能为负: {args.width}", file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(args.input):
        print(f"🔴 输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(2)

    # 输出扩展名强制 .jpg（.png 文件名装 JPEG 内容会触发 wechat-api Format mismatch）
    out_path = args.output
    if not out_path.lower().endswith((".jpg", ".jpeg")):
        out_path = os.path.splitext(out_path)[0] + ".jpg"
        print(f"ℹ️  输出扩展名强制 .jpg: {out_path}")

    out_dir = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(out_dir, exist_ok=True)

    # ---- 处理链：EXIF 修正 → RGB → 裁剪 → 缩放 → JPEG ----
    try:
        with Image.open(args.input) as img:
            img = ImageOps.exif_transpose(img)          # 手机图方向修正
            img = img.convert("RGB")
            img = crop(img, rw, rh, args.anchor)
            if args.width and img.width > args.width:    # 只缩不放
                img = img.resize(
                    (args.width, max(1, round(args.width * rh / rw))),
                    Image.Resampling.LANCZOS,
                )
    except Exception as e:
        print(f"🔴 图片处理失败: {e}", file=sys.stderr)
        sys.exit(2)

    # ---- 原子写：临时文件 → os.replace ----
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".jpg", dir=out_dir)
    try:
        with os.fdopen(tmp_fd, "wb") as f:
            img.save(f, "JPEG", quality=args.quality)
        os.replace(tmp_path, out_path)
    except Exception as e:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        print(f"🔴 写入失败: {e}", file=sys.stderr)
        sys.exit(2)

    # ---- 输出验证：重新打开确认真实格式与尺寸 ----
    try:
        with Image.open(out_path) as v:
            fmt, size = v.format, v.size
            assert fmt == "JPEG", f"输出格式异常: {fmt}"
    except Exception as e:
        print(f"🔴 输出验证失败: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"{out_path}: {size[0]}x{size[1]} ({fmt}, q{args.quality})")


if __name__ == "__main__":
    main()
