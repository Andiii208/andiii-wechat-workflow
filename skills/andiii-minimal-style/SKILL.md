---
name: andiii-minimal-style
description: Andiii碎碎念配图风格引擎 — 石墨极简风（灰阶/细线/大量留白/理性克制/高级感）。适合方法论/认知/观点/深度分析类文章（L先生说风）。生成封面（16:9 首图+1:1 分享图）、内文配图、金句卡前加载本 skill，过质检门后再送图生后端。触发词：极简、石墨、理性、留白、方法论、认知。
version: 1.0.0
author: Andiii208
license: MIT
tags: [image-generation, minimal, graphite, style-engine]
related_skills: [wechat-content-automation, andiii-image-style]
---

# Andiii 石墨极简风格引擎 v1.0

**风格定位**：石墨极简——灰阶理性、细线分割、大量留白、克制高级。像设计杂志的版面，不煽情不装饰。适合方法论/认知科学/观点/深度分析类文章（对应写作层 L先生说风）。与水彩（湿/晕染）、zine（干/拼贴）形成第三种气质：**净/理性**。

## 零、风格是参考，不是限制（用户 2026-08-03 明确）

本引擎的视觉规则是**灵感起点**，不是约束框：
- 默认按本引擎四件套走（保证气质底线）
- 但允许**跨风格借用 / 混搭 / 偏离**——当主题或用户意图更适合时（如喜茶底 + 极简构图、zine 拼贴 + 一处水彩晕染、潦草线条 + 水墨质感）
- 质检门（质感/雷区底线）仍然生效；**风格本身是软的**
- 目的：以风格激发更多创意，不是按模板死板执行

## 一、四件套引擎

### 色彩引擎
- 基底：白 / 浅灰（#F5F5F5 系）/ 暖灰纸色，占画面 70%-85%
- 墨色：石墨灰（#52525B 系）为主，近黑浅灰两级
- 点缀：至多一个低饱和点缀色（冷蓝 #4A6FA5 / 墨绿 #4A5D52 / 赭灰），以细线/小色块/几何形存在，占比 <5%
- 禁用：高饱和、暖色系大面积、渐变彩虹、霓虹

### 纹理引擎
每 prompt ≥2 纹理词 + 1 纸感词：
- 纸感：paper texture / 暖灰纸 / aged paper / 白纸
- 纹理：hairline 发丝线、grid lines 网格线、fine grain 细颗粒、cross-hatch 交叉排线、geometric shapes 几何形、subtle shadow 微妙投影、monochrome 单色层次

### 排版引擎（可选文字，默认无文字）
- 默认无图内文字（工作流原则）；用户要求时用无衬线（sans-serif）/等宽（monospace）字体，小号灰字，可配编号/坐标感小元素（01/02、x/y 轴感）
- 封面带字时：居中，左右 ≥15% 边距，垂直 25%-60% 可接受

### 规避清单（硬）
flat vector、minimalist line art（本风格可用但避免过度）、charcoal、gold foil、gallery poster、vivid gradient、glassmorphism、neon glow、3d render、anime style、水彩晕染感、拼贴碎片感、手绘笔触感、高饱和、渐变紫、日系动漫、装饰过度

## 二、四段式 prompt 模板

```text
P1 画布与纸感: [比例] 全幅[浅灰/白/暖灰纸]底, [70%-85%]留白, [纸感词]+[纹理词×2], 构图自由; 封面16:9附加"画面顶部与底部边缘各保留纯纸色留白，便于安全裁切"
P2 主体隐喻: [主题转译为抽象几何/器物/版式元素]（[锚点: 几何形/线条/留白负形/单一器物]）, [处理: 细线勾边/微妙投影/负空间]
P3 文字与色彩: 默认无文字; 带字时[无衬线小字, 位置], [石墨灰两级墨色], [点缀色以细线/小色块存在]
P4 氛围与规避: 理性、克制、留白、秩序感, 避免[水彩晕染/拼贴碎片/手绘笔触/高饱和]
```

## 三、变体引擎

- **布局**：single-object 单器物 / negative-space 负形 / grid-composition 网格 / diagonal-balance 斜向平衡 / typographic 版式 / centered-minimal 中心极简
- **锚点**：geometric shape 几何形 / single tool 单一器物（钢笔/杯子/书） / line art 线条 / monochrome photo 单色照片区 / abstract form 抽象形 / graph 图表形
- **文字模式**：无 / 编号小字 / 坐标感 / 短语（带字时）
- **纹理**：hairline / grid / fine grain / cross-hatch / subtle shadow / duotone 双色
- **情绪**：理性 / 克制 / 秩序 / 沉静 / 疏离 / 专注

## 四、工作流

0. **设计推理（必做，≤60秒）**：读 `D:/tools/andiii-wechat-workflow/references/design-reasoning.md`，按 6 项模板作答（用途渠道/受众气质/视觉系统/主次层级/留白决策/方向承诺）——先定「为什么这么画」，再动手编译。
1. 转译主题 → 选变体配方 → 四段式编译（P2 隐喻自由发挥）
2. **质检门**：`echo "prompt" | python D:/tools/hermes/skills/creative/andiii-image-style/scripts/check_engine_prompt.py`（PASS 才生成；本风格纹理词用 hairline/grid/fine grain/cross-hatch 等满足 ≥2 要求）
3. **生成**：封面 16:9（宽松安全区约束句）→ 中心裁 2.35:1；分享图 1:1；内文配图 16:9；统一 .jpg
4. **视觉复核**（MiMo 固定问句）：主体完整 / 无硬雷区 / 留白与克制感明显；封面裁后必复核
5. 用户最终确认（审美以用户为准）

## 五、弹药库（5 主题）

### M01 方法论/认知
```
P1 16:9 横构图，全幅浅灰纸底（paper texture），80%留白，hairline+fine grain，构图自由。安全区：上下边缘纯纸色留白。
P2 {方法论意象: 阶梯/齿轮/分叉路抽象为几何形}, 几何形锚点, 细线勾边, 微妙投影
P3 无文字, 石墨灰两级墨色, 冷蓝以细线存在
P4 理性、克制、秩序感, 避免水彩晕染感
```

### M02 观点/深度
```
P1 16:9 横构图，全幅白纸底（paper texture），75%留白，grid lines+subtle shadow，构图自由。安全区：上下边缘纯纸色留白。
P2 {观点意象: 天平/灯塔/独行剪影}, 单一器物锚点, 负空间
P3 无文字, 石墨灰墨色, 墨绿以小色块存在
P4 沉静、克制、疏离, 避免手绘笔触感
```

### M03 焦虑/自律（L先生向）
```
P1 16:9 横构图，全幅暖灰纸底（aged paper），80%留白，cross-hatch+fine grain，构图自由。安全区：上下边缘纯纸色留白。
P2 {焦虑意象: 缠绕的线/打结/钟表抽象形}, 抽象形锚点, 线条解构
P3 无文字, 石墨灰墨色, 冷蓝细线
P4 理性、秩序, 避免高饱和
```

### M04 书/阅读
```
P1 16:9 横构图，全幅浅灰纸底（paper texture），78%留白，hairline+grid lines，构图自由。安全区：上下边缘纯纸色留白。
P2 {阅读意象: 打开的书抽象化/书页展开的几何形}, 几何形锚点, 负空间
P3 无文字, 石墨灰两级墨色
P4 专注、沉静, 避免装饰过度
```

### M05 独处/思考
```
P1 16:9 横构图，全幅白纸底（paper texture），85%留白，fine grain+subtle shadow，构图自由。安全区：上下边缘纯纸色留白。
P2 {独处意象: 一把空椅子/窗的负形}, 负形锚点, 微妙投影
P3 无文字, 石墨灰墨色, 赭灰小色块
P4 疏离、克制、留白, 避免水彩晕染感
```

## 六、说明

- 教程/清单类文章的信息图**不走本引擎**（AI 生图文字会乱码）——用 gzh-design 排版组件或 HTML/SVG 生成（见路由表备注）
- 本引擎与 andiii-image-style（水彩）气质相反，路由时二选一
