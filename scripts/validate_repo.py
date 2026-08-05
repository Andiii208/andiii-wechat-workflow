#!/usr/bin/env python3
"""轻量仓库校验（CI 用）— 2026-08-06 加入。

检查项:
  1. 所有 .md 的相对链接目标存在（broken-link）
  2. SKILL.md 引用的 references/*.md 在本地或顶层 references/ 至少一处存在
     （覆盖"顶层唯一权威源"策略：skill 本地无副本时顶层必须有）
  3. secret pattern 快扫（WECHAT_APP_SECRET / APP_ID / sk- key，REDACTED 占位符豁免）
  4. frontmatter 版本号格式校验

用法:
    python scripts/validate_repo.py
退出码: 0 = 通过, 1 = 有问题
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
errors = []


def is_skipped(p: Path) -> bool:
    return ".git" in p.parts or ".local" in p.parts or p.suffix not in (".md", ".py", ".sh", ".yaml", ".yml", ".json", ".toml", ".txt")


# ---- 1. markdown 相对链接 ----
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_links():
    for md in ROOT.rglob("*.md"):
        if is_skipped(md):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        # 跳过 ``` 围栏代码块（内部路径多为示例/占位符，非真引用）
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for m in LINK_RE.finditer(text):
            target = m.group(1).strip()
            if not target or target.startswith(("http://", "https://", "//", "#", "mailto:", "data:")):
                continue
            if not re.search(r"[A-Za-z0-9\u4e00-\u9fff]", target):
                continue  # 纯符号目标（如 `![](...)` 语法占位符）
            if re.match(r"^[A-Za-z]:[\\/]", target):  # Windows 绝对路径 D:/...
                continue
            if re.match(r"^/[a-z]/", target):  # MSYS 路径 /d/...
                continue
            clean = target.split("#")[0].strip()
            if not clean:
                continue
            p = (md.parent / clean).resolve()
            if not p.exists():
                errors.append(f"[link] {md.relative_to(ROOT)}: `{target}` 不存在")


# ---- 2. SKILL references 引用（本地或顶层任一存在即可）----
REF_RE = re.compile(r"references/([A-Za-z0-9_.\-]+\.md)")


def check_refs():
    for sk in (ROOT / "skills").glob("*/SKILL.md"):
        try:
            text = sk.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in REF_RE.finditer(text):
            fname = m.group(1)
            local = sk.parent / "references" / fname
            top = ROOT / "references" / fname
            if not local.exists() and not top.exists():
                errors.append(
                    f"[ref] {sk.relative_to(ROOT)}: references/{fname} 不存在"
                    "（skill 本地与顶层 references/ 均无）"
                )


# ---- 3. secret pattern 快扫（REDACTED / example 占位符豁免）----
SECRET_PATTERNS = [
    (re.compile(r"WECHAT_APP_SECRET\s*[:=]\s*(?!WECHAT_APP_SECRET_REDACTED|your_app_secret|REDACTED)[A-Za-z0-9]{16,}"), "WECHAT_APP_SECRET 疑似真实值"),
    (re.compile(r"WECHAT_APP_ID\s*[:=]\s*(?!WECHAT_APP_ID_REDACTED|your_app_id|REDACTED)[A-Za-z0-9]{15,}"), "WECHAT_APP_ID 疑似真实值"),
    (re.compile(r"(?<![\w])sk-[A-Za-z0-9]{20,}"), "疑似 API key (sk-)"),
    (re.compile(r"access_token[\"'=:\s]+[A-Za-z0-9_\-]{40,}"), "疑似 access_token"),
]


def check_secrets():
    for f in ROOT.rglob("*"):
        if is_skipped(f) or not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for pat, desc in SECRET_PATTERNS:
            for m in pat.finditer(text):
                errors.append(f"[secret] {f.relative_to(ROOT)}: {desc}: {m.group(0)[:16]}…")


# ---- 4. frontmatter version 格式 ----
FRONT_RE = re.compile(r"^---\n(.*?)\n---", re.S | re.M)
VERSION_RE = re.compile(r"^\s*version\s*:\s*(\d+\.\d+\.\d+)\s*$", re.M)


def check_versions():
    for sk in (ROOT / "skills").glob("*/SKILL.md"):
        text = sk.read_text(encoding="utf-8", errors="replace")
        fm = FRONT_RE.search(text)
        if not fm:
            errors.append(f"[frontmatter] {sk.relative_to(ROOT)}: 无 frontmatter")
            continue
        ver = VERSION_RE.search(fm.group(1))
        if not ver:
            errors.append(f"[frontmatter] {sk.relative_to(ROOT)}: version 缺失或格式错误（需 x.y.z）")
        elif "image-style" in sk.name:
            # 引擎 frontmatter 版本须与 NOTES 版本历史最新一致（防漂移）
            notes = sk.parent / "references" / "NOTES.md"
            if notes.exists():
                ntext = notes.read_text(encoding="utf-8", errors="replace")
                vers = re.findall(r"^- v(\d+\.\d+\.\d+)[:：]", ntext, re.M)
                if vers and vers[-1] != ver.group(1):
                    errors.append(
                        f"[version] {sk.relative_to(ROOT)}: frontmatter {ver.group(1)} "
                        f"≠ NOTES 最新版本 {vers[-1]}（防漂移，对齐 NOTES）"
                    )


def main():
    check_links()
    check_refs()
    check_secrets()
    check_versions()
    if errors:
        print(f"🔴 校验失败: {len(errors)} 个问题")
        for e in errors:
            print("  ", e)
        sys.exit(1)
    print("✅ 校验通过：链接 / references / secrets / frontmatter 全部正常")


if __name__ == "__main__":
    main()
