# 配图风格路由表（wechat-content-automation 配图层）

> 2026-08-03 建。原则：**文风路由 → 配图风格 → 引擎**——写作层定了文风，配图跟着文风走，不默认全用水彩（v1.2 教训：单风格默认是错的）。

> ⚠️ **总原则（用户 2026-08-03 明确）：风格是参考，不是限制**——路由只给推荐方向，不强制；编译 prompt 时允许跨风格借用/混搭/偏离，以激发创意为准。质检门（质感/雷区底线）仍生效，风格本身是软的。

## 路由表

| 写作风格 / 话题关键词 | 配图风格 | 引擎 | 状态 |
|---|---|---|---|
| MorningRocks 风（诗意/黄昏/夜晚/宇宙/海） | 手绘水彩 | `andiii-image-style` | ✅ 已建已测 |
| WhatYouNeed 风（情感命名/小习惯/心理翻译） | 手绘水彩 | `andiii-image-style` | ✅ 已建 |
| 槽边往事风（日常小事/记录/自嘲） | 手绘水彩 或 Zine 拼贴 | 两者皆可 | ✅ 已建 |
| 新世相风（失败/被拒/集体情绪/输的感受） | Zine 拼贴（档案感） | `andiii-zine-style` | ✅ 已建（2026-08-03） |
| 深度/文艺/读书笔记/电影观后感 | Zine 拼贴（破碎拼贴+微文本） | `andiii-zine-style` | ✅ 已建 |
| L先生说风（焦虑/拖延/自律/方法论） | 石墨极简 | `andiii-minimal-style` | ✅ 已建（2026-08-03） |
| 喜茶风（新中式/茶饮/生活美学） | 新中式茶饮（米白/茶色/水墨/印章） | `andiii-heytear-style` | ✅ 已建（2026-08-03 子 agent 蒸馏） |
| 潦草风（手账/随性/涂鸦） | 涂鸦手账 / sketchy | `andiii-sketchy-style` | ✅ 已建（2026-08-03 子 agent 蒸馏） |
| 观点/评论/深度随笔（黑白编辑插画感/克制叙事/讽刺） | 黑白针管笔线条（relaxed black-pen） | `antibes-holiday` | ✅ 已装（2026-08-06，haorantang97/antibes-holiday 195⭐，MIT） |
| 教程/清单/盘点 | 信息图 / 示意图 | ⚠️ **不走 AI 生图**（生图文字乱码）——用 gzh-design 排版组件或 HTML/SVG | 备注 |

## 调用姿势（配图层）

```text
1. 文章文风已由写作层路由表确定（如 MorningRocks 风）
2. 查本路由表 → 得配图风格 + 引擎（如 andiii-image-style）
3. skill_view(name='<引擎>') → **设计推理（design-reasoning.md 6 项，必做）** → 编译四段式 prompt → 质检门 → 生成 → 视觉复核 → 用户确认
4. 路由表状态为 ❌ 的风格：暂时回退手绘水彩或通用 prompt，并提示用户该风格待蒸馏
```

## 风格蒸馏排队（用户点名/调研沉淀）

| 风格 | 来源 | 方法 |
|---|---|---|
| 喜茶风 | 用户点名（新中式茶饮） | 按 zine-poster 改版方法论蒸馏四件套（色彩：米白/茶色/金棕；纹理：宣纸/水墨/印章；排版：书法字居中/竖排；规避：禁网红奶茶店风） |
| 潦草风 | 用户点名（涂鸦手账） | 蒸馏四件套（sketchy 线条/手写体/胶带贴纸/随性构图） |
| Mondo 风 | joeseesun/qiaomu-mondo-poster-design（1K⭐） | 20 位传奇海报设计师风格库，电影/专辑封面向 |
| Editorial/Swiss | op7418/guizang-social-card-skill（5.8K⭐） | 电子杂志/瑞士网格，克制版面，适合方法论/产品 |
| Nano Banana prompt 库 | YouMind-OpenLab（1.8K⭐） | 1 万条 prompt 弹药，模型无关，作素材不作战术 |
| GPT-Image2 Gallery | wuyoscar（4.1K⭐） | Watercolor/Ink 分类 prompt 词表（水彩引擎已吸收） |

> 蒸馏方法：复制现有引擎 SKILL.md → 换四件套（色彩/纹理/排版/规避）→ 改 frontmatter → 过质检门验证 → 登记本路由表。
