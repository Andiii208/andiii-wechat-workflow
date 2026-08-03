#!/usr/bin/env python3
"""andiii-image-style 图片裁剪脚本 — 中心/底部锚点裁剪 + JPEG 压缩。

用法:
    python crop_image.py <input> <output> [--ratio 16:9] [--anchor center|bottom] [--quality 85]

设计背景（2026-08-03）:
    Wan2.7 只出 16:9/1:1/9:16，公众号首图需裁成 2.35:1 ≈ 900×383。
    引擎模板规定主体簇位于画面下方 → 中心裁剪会切掉下方主体（实测确认）。
    → 封面用 --anchor bottom（保留底部主体），内文图用默认 center。
"""
import argparse
from PIL import Image


def crop(img: Image.Image, ratio_w: float, ratio_h: float, anchor: str) -> Image.Image:
    w, h = img.size
    target = ratio_w / ratio_h
    cur = w / h
    if cur > target:  # 太宽 → 裁左右（中心即可，标题横向居中）
        nw = int(h * target)
        x = (w - nw) // 2
        return img.crop((x, 0, x + nw, h))
    # 太高 → 裁上下
    nh = int(w / target)
    if anchor == "bottom":
        y = h - nh          # 保留底部（主体常在下方）
    else:
        y = (h - nh) // 2   # 中心裁剪
    return img.crop((0, y, w, y + nh))


def main():
    ap = argparse.ArgumentParser(description="按目标比例裁剪图片并压成 JPEG")
    ap.add_argument("input", help="输入图片路径")
    ap.add_argument("output", help="输出 jpg 路径")
    ap.add_argument("--ratio", default="16:9", help="目标比例，如 16:9 / 2.35:1 / 1:1（默认 16:9）")
    ap.add_argument("--anchor", default="center", choices=["center", "bottom"],
                    help="上下裁剪锚点：center=中心（默认），bottom=保留底部（封面用）")
    ap.add_argument("--quality", type=int, default=85, help="JPEG 质量（默认 85）")
    args = ap.parse_args()

    rw, rh = (float(x) for x in args.ratio.split(":"))
    img = Image.open(args.input).convert("RGB")
    img = crop(img, rw, rh, args.anchor)
    img.save(args.output, "JPEG", quality=args.quality)
    print(f"{args.output}: {img.size}")


if __name__ == "__main__":
    main()
