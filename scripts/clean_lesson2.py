# -*- coding: utf-8 -*-
"""清理被 bash 污染的反引号内容, 重写干净的 lesson2 行"""
import re

REPO_TOP = r'D:\tools\andiii-wechat-workflow\references\theme-routing.md'
REPO_SKILL = r'D:\tools\andiii-wechat-workflow\skills\wechat-content-automation\references\theme-routing.md'
HERMES = r'D:\tools\hermes\skills\productivity\wechat-content-automation\references\theme-routing.md'

lesson2 = '- 🔴🔴 **注入正则的 `>` 陷阱（2026-08-04 二次翻车，同晚实战）**：`re.sub(r\'<(p|h3|section) style="([^"]*)"\', inject, html)` 只匹配到 style 引号**不含 `>`**，inject 返回值**不要再补 `>`**（原文的 `>` 还在），否则每个注入点变成 `">><`，页面渲染出 118 个孤立 `>` 字符，整篇排版错乱。修后必须自检：`assert html.count(\'">><\') == 0`，并浏览器打开实际渲染（console 查 `document.body.innerText` 无孤立 `>`、`getComputedStyle(p).fontFamily` 为宋体栈）再推送'

for p in [REPO_TOP, REPO_SKILL, HERMES]:
    h = open(p, encoding='utf-8').read()
    # 找到被污染的行: 以 "- 🔴🔴 **注入正则" 开头, 到换行结束
    m = re.search(r'- 🔴🔴 \*\*注入正则[^\n]*', h)
    if m:
        h = h.replace(m.group(0), lesson2)
        open(p, 'w', encoding='utf-8').write(h)
        print('fixed:', p.split('\\')[-3] + '/' + p.split('\\')[-1])
    else:
        print('NOT FOUND in:', p)

# 最终验证
for p in [REPO_TOP, REPO_SKILL, HERMES]:
    h = open(p, encoding='utf-8').read()
    i = h.find('注入正则')
    print('---', p.split('\\')[-1], '片段:', repr(h[i:i+100]) if i >= 0 else 'MISSING')
