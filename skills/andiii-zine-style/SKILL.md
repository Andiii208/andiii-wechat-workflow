---
name: andiii-zine-style
description: Andiii碎碎念配图风格引擎 — 低饱和拼贴 Zine 风（档案感/破碎拼贴/实验字体/旧纸印刷缺陷）。适配自 moonlin1213/muted-zine-poster-v01（MIT，上游 LiamGvchi/gc-minimal-zine-poster）。适合深度/文艺/集体情绪/读书笔记类文章。生成封面（16:9 首图+1:1 分享图）、内文配图、金句卡前加载本 skill，过质检门后再送图生后端。触发词：zine、拼贴、档案感、破碎拼贴。
version: 1.0.0
author: Andiii208 (upstream: moonlin1213, LiamGvchi)
license: MIT
tags: [image-generation, zine, collage, poster, style-engine]
related_skills: [wechat-content-automation, andiii-image-style]
---

# Andiii Zine 拼贴风格引擎 v1.0

基于 **moonlin1213/muted-zine-poster-v01**（作者改版自 LiamGvchi/gc-minimal-zine-poster 的 `gc-minimal-zine-poster-v0-1`，MIT）适配到 Andiii 公众号工作流：保留上游全部编译逻辑，接入质检门/视觉复核/双尺寸封面。

**风格定位**：低饱和、档案感、破碎拼贴、梦核。与手绘水彩（andiii-image-style）的区别——水彩是"湿的、晕染的、柔软的"，zine 是"干的、拼贴的、有印刷颗粒的"。适合深度/文艺/集体情绪/读书笔记类文章。

## 零、风格是参考，不是限制（用户 2026-08-03 明确）

本引擎的视觉规则是**灵感起点**，不是约束框：
- 默认按本引擎四件套走（保证气质底线）
- 但允许**跨风格借用 / 混搭 / 偏离**——当主题或用户意图更适合时（如喜茶底 + 极简构图、zine 拼贴 + 一处水彩晕染、潦草线条 + 水墨质感）
- 质检门（质感/雷区底线）仍然生效；**风格本身是软的**
- 目的：以风格激发更多创意，不是按模板死板执行

## 一、Prompt Compiler（上游核心，保留）

把用户内容编译成图生 prompt（Standard Mode）。**用规则不用样例词**。

### First-Principles Prompt Fields（9 问，顺序作答）

1. **Canvas**：竖版或横版画布；全幅旧纸；无边框无 mockup
2. **Attention Geometry**：70%-90% 纯纸留白；单个视觉簇占 8%-25%；居中/中上/中下/左下/右上，不贴边
3. **Image Anchor**：主题转成一个物件/碎片/照片裁切/标本/剪纸/剪影/旧印刷插图/质感窗/小概念关系
4. **Anchor Treatment**：低对比、影印柔化、撕边、halftone、扫描线、risograph 颗粒、xerox 磨损、油墨渗开、轻微套印错位；整体保持 muted，**不引入高饱和锚点**
5. **Typography System**：小号衬线/打字机/等宽字体；一句短可读短语；可选微型日期/地点/天气/签名；半可读微文本或碎片字母；文字可漂移/贴边/模糊/套印错位/重复成行/竖排
6. **Color Logic（Muted）**：纸色+灰黑墨主导；最多一个极淡 wash（浅米/淡黄/淡蓝灰/柔灰绿），以纸带/斜条/稀释照片区存在，**禁止色块**；禁用 `cobalt/ultramarine/vivid/saturated/high-chroma` 类词；有 wash 时写 `muted palette with a pale [color] wash`，不写 near-monochrome
7. **Reproduction Texture**：平板扫描旧纸观感；哑光吸墨纸；漫射光；低-中对比；无硬阴影无 3D
8. **Emotional Temperature**：安静、诗意、怀旧、稀疏、日记感、档案感、疏离、记忆感
9. **Hard Avoids**：全出血场景、商业标题层级、产品广告、logo/CTA、光泽 mockup、干净 UI 白、电影打光、3D、霓虹、可爱卡通、时尚杂志戏剧感、密集剪贴簿、太多颜色、长段干净文字、任何高饱和色块

### Standard Prompt Shape（四段式）

```text
P1 画布与纸感: [比例] 全幅[纸色]底, [留白比例]留白, [纸感词]+[纹理词×2], 视觉簇位置与构图自由
P2 主体隐喻: [主题转译意象]（[锚点类型]）, [锚点处理: 影印柔化/撕边/油墨渗开/套印错位]
P3 文字与拼贴: [文字策略: 微文本/碎片字母/短语], [muted 色彩策略 + 淡 wash 形态], [印刷缺陷: xerox/risograph/halftone/scan noise]
P4 氛围与规避: 档案感、日记感、疏离、记忆感, 避免[规避项]
```

> 封面默认无大标题（沿用 andiii 工作流原则）；zine 的微文本/小字/日期作为氛围元素保留。

## 二、Variation Engine（上游核心，保留）

每个轴选一项，随机性必须改变视觉语法（不只换位置）。连续出图避免雷同：

- **Layout Family**：center-fragment / lower-left-float / upper-right-block / dual-panel / irregular-cutout / type-led / dot-orbit / single-specimen
- **Image Anchor**：tiny faded photo / torn-paper clipping / flat silhouette / old printed illustration / object specimen / translucent geometric overlay / abstract texture window / grayscale photo strip
- **Typography Mode**：fragmented floating letters / phrase pressed against edge / archive microtext with date-weather / diagonal scattered words / low-contrast gray ghost text / headline-as-object with letterpress / text inside paper strip / repeated text line / almost textless
- **Texture Mode**：xerox softness / risograph grain / letterpress ink bleed / halftone degradation / film grain / scan noise + paper fibers / aged paper mottling / soft motion blur on text
- **Mood Mode**：quiet / summer / solitude / childhood / seaside / afternoon / night / memory / slight surrealism

## 三、工作流（Andiii 适配层）

0. **设计推理（必做，≤60秒）**：读 `../ai-image-style-engine/references/design-reasoning.md`（Hermes 注入副本；仓库权威源为顶层 `references/design-reasoning.md`），按 6 项模板作答（用途渠道/受众气质/视觉系统/主次层级/留白决策/方向承诺）——先定「为什么这么画」，再动手编译。
1. 转译主题 → 选变体配方（Layout/Anchor/Typography/Texture/Mood 各一）
2. 按四段式编译 prompt（P2 隐喻是自由发挥点，不写场景堆砌）
3. **质检门**：`echo "prompt" | python D:/tools/hermes/skills/creative/andiii-image-style/scripts/check_engine_prompt.py`（复用水彩引擎质检门，PASS 才生成；zine 的 texture 词天然满足纹理词要求）
4. **生成**：封面 16:9（附加宽松安全区约束句："画面顶部与底部边缘各保留纯纸色留白，便于安全裁切"）→ 中心裁 2.35:1；分享图 1:1；内文配图 16:9
5. **视觉复核**（MiMo 固定问句）：主体完整未裁切 / 无硬雷区 / 印刷颗粒与拼贴感明显；封面裁后必复核
6. 交用户最终确认（审美以用户为准）

## 四、封面双尺寸与文件规范

- 首图：16:9 生成 → `crop_image.py --ratio 2.35:1 --anchor center` → `cover.jpg`
- 分享图：1:1 → `cover-square.jpg`
- 统一 .jpg；裁剪用 `scripts/crop_image.py`（水彩引擎同款脚本）

## 五、上游署名

- 本引擎适配自 [moonlin1213/muted-zine-poster-v01](https://github.com/moonlin1213/muted-zine-poster-v01)（MIT），其基于 [LiamGvchi/gc-minimal-zine-poster](https://github.com/LiamGvchi/gc-minimal-zine-poster)（MIT）
- 上游完整 SKILL.md 存档于 `references/muted-zine-upstream.md`
- 上游 Quality Gate / Negative Constraints 全文见 `references/muted-zine-upstream.md`（本引擎沿用其精神，不再复制）
