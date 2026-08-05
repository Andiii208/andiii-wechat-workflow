# NOTICE

## 本仓库自身

- 版权：© 2026 Andiii208
- 主许可证：MIT（见根目录 `LICENSE`）
- 仓库中**本仓库原创的内容**（工作流设计、风格引擎规则、路由表、脚本、文档）遵循 MIT。

## 许可证边界声明

本仓库是「工作流规则 + 脚本」仓库，不复制任何上游项目的完整代码进本仓库：

- **运行依赖**（gzh-design、baoyu-*、antibes-holiday 等）通过 Hermes skills 系统**外部加载**，本仓库仅路由引用，不包含其代码。
- 若未来复制或修改了 AGPL 组件的代码，对应文件必须按 AGPL-3.0 要求处理，并在本文件登记。
- 文风蒸馏样本仅保留**风格特征分析和短引用**，不保存完整文章副本。

## 上游与第三方内容清单

| 上游项目 | 来源 | 用途 | 许可证 | 本仓库使用方式 |
|---|---|---|---|---|
| gzh-design-skill | github.com/isjiamu/gzh-design-skill | 微信公众号排版引擎（theme-routing 路由） | AGPL-3.0 | 外部运行依赖，仅路由引用 |
| baoyu-skills | github.com/JimLiu/baoyu-skills | baoyu-post-to-wechat / baoyu-cover-image / baoyu-article-illustrator / baoyu-image-gen | MIT | 外部运行依赖，仅路由引用 |
| muted-zine-poster-v01 | github.com/moonlin1213/muted-zine-poster-v01 | Zine 拼贴引擎风格参考 | MIT | 风格参考与适配 |
| gc-minimal-zine-poster | github.com/LiamGvchi/gc-minimal-zine-poster | 石墨极简 zine 风格参考 | MIT | 风格参考 |
| antibes-holiday | haorantang97/antibes-holiday | 黑白针管笔引擎（路由引用） | MIT | 外部 skill，路由引用，不走本仓库质检门 |
| human-writing | KKKKhazix/human-writing | check_prose.py 文字质检门（de-ai-craft 联动） | MIT | 吸取质检思路，外部运行依赖 |
| wechatDownload | github.com/qiye45/wechatDownload | 公众号文章批量采集 MCP | 待核实 | 外部工具集成，MCP 引用 |
| design-image-studio anti-slop 手册 | 第三方 skill 内容摘录 | references/learnings/ 存档 | 待核实 | 仅摘录要点，来源未在原文标注 |

## 文风蒸馏参考对象

`andiii-writing-style` 的风格特征分析基于以下公众号的公开文章：槽边往事、MorningRocks、我要WhatYouNeed、杂乱无章、L先生说、新世相。

- 仅保留风格特征、结构模式与短引用；
- 不保存、不复制任何完整文章；
- 具体公众号名称在仓库内映射为内部风格特征标签使用。

## 注意

- 本仓库为公开仓库，**严禁提交**任何真实凭据（AppSecret、API Key、Token）、个人私密素材或运行产物。
- 本机路径、IP 白名单等个人机器细节一律使用 `REDACTED` 占位符。
