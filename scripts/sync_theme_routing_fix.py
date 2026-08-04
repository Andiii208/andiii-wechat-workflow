# -*- coding: utf-8 -*-
"""同步 theme-routing.md 三副本 + 补 '>' 陷阱教训 (用 D:/ 路径, 避免 MSYS 问题)"""
import shutil

REPO_TOP = r'D:\tools\andiii-wechat-workflow\references\theme-routing.md'
REPO_SKILL = r'D:\tools\andiii-wechat-workflow\skills\wechat-content-automation\references\theme-routing.md'
HERMES = r'D:\tools\hermes\skills\productivity\wechat-content-automation\references\theme-routing.md'

# 1. 检查仓库顶层现状 (bash 转义是否污染)
h = open(REPO_TOP, encoding='utf-8').read()
print('顶层含"段落级显式注入":', '段落级显式注入' in h)
print('顶层含"注入正则":', '注入正则' in h)
i = h.find('注入正则')
if i >= 0:
    print('污染检查片段:', repr(h[i:i+120]))

# 2. 若污染或缺失, 干净地重写字体约定节
marker_old = '## 字体约定（2026-08-03 定稿）'
marker_new = '## 字体约定（2026-08-03 定稿，2026-08-04 修订）'

lesson1 = '- 🔴 **必须段落级显式注入（2026-08-04 实战翻车教训）**：只靠最外层容器 `font-family` 继承 **不可靠**——微信编辑器手动编辑后可能剥掉容器样式，微信阅读器（尤其 iOS）对容器级字体继承不稳，实际发布后正文显示成默认黑体（用户当场发现"没遵循宋体要求"）。**排版装配时必须给每个 `<p>/<h3>/<section>` 显式注入 font-family 宋体栈**（正则：style 里没有 font-family 就 `style.rstrip(\';\') + \';font-family: \' + 宋体栈`），标题/引言/金句块的 `\'Noto Serif SC\', Georgia...` 也统一替换为宋体栈。校验脚本不查字体，需自查 `html.count(\'Songti\')` 覆盖率'

lesson2 = '- 🔴🔴 **注入正则的 `>` 陷阱（2026-08-04 二次翻车，同晚实战）**：`re.sub(r\'<(p|h3|section) style="([^"]*)"\', inject, html)` 只匹配到 style 引号**不含 `>`**，inject 返回值**不要再补 `>`**（原文的 `>` 还在），否则每个注入点变成 `">><`，页面渲染出 118 个孤立 `>` 字符，整篇排版错乱。修后必须自检：`assert html.count(\'">><\') == 0`，并浏览器打开实际渲染（console 查 `document.body.innerText` 无孤立 `>`、`getComputedStyle(p).fontFamily` 为宋体栈）再推送'

def ensure_lessons(text):
    if '段落级显式注入' not in text:
        # 旧版 -> 插入两条
        old_block = '## 字体约定（2026-08-03 定稿）\n\n- **正文/全局字体：宋体衬线栈**'
        assert old_block in text, 'old block not found'
        text = text.replace(old_block,
            '## 字体约定（2026-08-03 定稿，2026-08-04 修订）\n\n- **正文/全局字体：宋体衬线栈**', 1)
        # 在「- **正文/全局字体」行后插入 lesson1, 在「已写入」行后插入 lesson2
        text = text.replace('- **正文/全局字体：宋体衬线栈**',
                            '- **正文/全局字体：宋体衬线栈**\n' + lesson1, 1)
    if '注入正则' not in text:
        anchor = '- 已写入 **全部 6 套主题**'
        assert anchor in text, 'anchor not found for lesson2'
        text = text.replace(anchor, anchor + '\n' + lesson2, 1)
    return text

# 处理顶层
h = ensure_lessons(h)
open(REPO_TOP, 'w', encoding='utf-8').write(h)
print('顶层 OK, 段落级注入:', h.count('段落级显式注入'), '| 注入正则教训:', h.count('注入正则'))

# 复制到其余两份
shutil.copy(REPO_TOP, REPO_SKILL)
print('skills 副本 OK')
shutil.copy(REPO_TOP, HERMES)
print('Hermes 副本 OK')
