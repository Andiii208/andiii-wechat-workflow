---
name: andiii-sketchy-style
description: Andiii碎碎念配图风格引擎 — 潦草随性的手账涂鸦风（sketchy doodle journal：铅笔/马克笔线条、抖动线、胶带贴纸、涂改划掉、白纸或牛皮纸底）。像随手翻开的笔记本，不是精致插画。适合日常碎碎念/随感/小事记录类文章。生成封面（16:9 首图+1:1 分享图）、内文配图前加载本 skill，过质检门后再送图生后端。触发词：潦草风、涂鸦、手账、随性手绘、sketchy、涂涂画画。
version: 1.0.0
author: Andiii208
license: MIT
tags: [image-generation, sketchy, doodle, journal, style-engine]
related_skills: [wechat-content-automation, andiii-image-style]
---

# Andiii Sketchy 潦草手账风格引擎 v1.0

Andiii 碎碎念配图风格库第三枚引擎（水彩 → zine → sketchy）。**风格定位**：潦草随性的手账涂鸦感——铅笔/马克笔线条、抖动线、胶带贴纸、涂改划掉、白纸或牛皮纸底。像随手翻开的笔记本，不是精致插画。

与姊妹引擎的区别——水彩是"湿的、晕染的、柔软的"，zine 是"干的、拼贴的、有印刷颗粒的"，**sketchy 是"随手画的、带手劲的、有橡皮擦痕的"**：线条歪、笔触露、涂了又改，保留"正在画"的现场感。适合日常碎碎念/随感/小事记录类文章。

## 零、风格是参考，不是限制（用户 2026-08-03 明确）

本引擎的视觉规则是**灵感起点**，不是约束框：
- 默认按本引擎四件套走（保证气质底线）
- 但允许**跨风格借用 / 混搭 / 偏离**——当主题或用户意图更适合时（如喜茶底 + 极简构图、zine 拼贴 + 一处水彩晕染、潦草线条 + 水墨质感）
- 质检门（质感/雷区底线）仍然生效；**风格本身是软的**
- 目的：以风格激发更多创意，不是按模板死板执行

## 一、四件套引擎

### 1. 色彩
- 白纸或牛皮纸底 + 铅笔灰线条主导
- 至多 **1-2 个低饱和马克笔色**（旧蓝/砖红/橄榄绿/焦黄），只做点缀，不做大面积色块
- 写法：`muted palette with [旧蓝|砖红|橄榄绿|焦黄] marker accents on [白纸|牛皮纸]`
- **禁止**精致高饱和商业插画色

### 2. 纹理
- sketchy 抖动线条、scribble 乱线、doodle 小涂鸦、胶带、涂改痕迹、马克笔笔触、铅笔线条
- 质检门硬性要求：每 prompt **≥2 纹理词 + 1 纸感词**（sketchy/scribble/doodle/胶带/涂改/马克笔/铅笔 已入质检门词表）

### 3. 排版
- **默认无图内文字**（不写任何文字）
- 仅用户明确要求时才上手写体潦草字：可以划线划掉、手写箭头、圆圈标注；文字歪斜不齐、大小不一

### 4. 规避（硬）
flat vector、minimalist line art、charcoal、gold foil、gallery poster、vivid gradient、glassmorphism、neon glow、3d render、anime style、精致矢量插画、完美平滑线条、高饱和、渐变紫、日系动漫、可爱卡通
> **质检门豁免规则**：规避项在 prompt 里必须逐个写 `避免X`（质检门对"避免X/不要X/no X/avoid X"表述豁免）——不能合并成一串"避免A、B、C"，否则 B/C 会被判命中。即写 `避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通`。

## 二、四段式 Prompt 模板

```text
P1 画布与纸感: [16:9 横版] 全幅[白纸|牛皮纸]底, [70%-85%]留白, [纸感词]+[sketchy/scribble/doodle 等纹理词×≥2], 视觉簇位于[位置]不贴边, 画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2 主体隐喻: [主题转译意象]（[锚点类型]）, [潦草勾勒/涂改划掉/胶带粘贴/手绘圈注 处理]
P3 文字与色彩: 无图内文字（不写任何文字）, muted palette with [1-2 个低饱和马克笔色] marker accents, 铅笔灰线条贯穿
P4 氛围与规避: 随性、松弛、手账感、日常感、留白呼吸感, 避免[规避项逐个加"避免"前缀]
```

P2 是自由发挥点：主题转成一个能"画在笔记本上"的小意象（杯子/伞/一团乱线），不要堆场景。

## 三、变体引擎（每轴选一项，随机性必须改变视觉语法）

- **Layout Family（布局 8）**：center-doodle / lower-left-cluster / corner-scrawl / margin-notes / full-page-scatter / top-strip / side-column / diagonal-flow
- **Image Anchor（锚点 8）**：coffee-cup doodle / sticky note / torn washi tape strip / pencil-sketched object / circled word / scribbled arrow / hand-drawn frame / tiny character doodle
- **Typography Mode（文字 7）**：no text / one scrawled word / crossed-out line / circled label / arrow + label / margin note / almost textless
- **Texture Mode（纹理 8）**：sketchy jitter lines / scribble hatching / doodle marks / washi tape / correction-fluid splotch / marker stroke / pencil shading / paper crease fold
- **Mood Mode（情绪 7）**：relaxed / rainy / cozy / nostalgic / silly / tired / morning

连续出图避免雷同：换 Layout + Texture 轴即可大变样。

## 四、弹药库（5 主题模板，槽位 {} 可替换）

### 1. 日常（通勤/咖啡/小事）
```text
P1: 16:9 横版 全幅白纸底, 约 80% 留白, 白纸纸纹, sketchy 抖动线条与 scribble 乱线, 马克笔笔触, 视觉簇位于{位置}，不贴边，画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2: 主体：{日常小物：一杯咖啡/一串钥匙/一只猫}，潦草勾勒成手账 doodle，局部涂改划掉重画，旁边贴一段胶带
P3: 无图内文字（不写任何文字）；muted palette with {旧蓝|焦黄} marker accents，铅笔灰线条贯穿
P4: 氛围随性松弛、手账日记感、留白呼吸感；避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通
```

### 2. 雨天
```text
P1: 16:9 横版 全幅牛皮纸底, 约 75% 留白, 牛皮纸纸纹, doodle 小涂鸦与铅笔线条, scribble 乱线, 视觉簇位于{位置}，不贴边，画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2: 主体：{窗边的雨滴/一把歪斜的伞/湿漉漉的球鞋}，潦草勾勒成手账涂鸦，雨点用马克笔点出，局部涂改痕迹
P3: 无图内文字（不写任何文字）；muted palette with 旧蓝 marker accents（雨点），铅笔灰线条贯穿
P4: 氛围安静潮湿、雨天赖床感、手账随记感；避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通
```

### 3. 食物
```text
P1: 16:9 横版 全幅白纸底, 约 80% 留白, 白纸纸纹, sketchy 抖动线条与马克笔笔触, doodle 小涂鸦, 视觉簇位于{位置}，不贴边，画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2: 主体：{一碗热汤面/一块蛋糕/一碟饺子}，潦草勾勒成手账 doodle，{筷子}画歪了用涂改划掉重画，旁边贴胶带
P3: 无图内文字（不写任何文字）；muted palette with {砖红|焦黄} marker accents，铅笔灰线条贯穿
P4: 氛围松弛治愈、热气腾腾的手账感；避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通
```

### 4. 情绪
```text
P1: 16:9 横版 全幅牛皮纸底, 约 85% 留白, 牛皮纸纸纹, scribble 乱线与铅笔线条, 涂改痕迹, 视觉簇位于{位置}，不贴边，画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2: 主体：{一团乱线代表烦心事/被划掉又重画的太阳/歪斜的心形}，潦草手账 doodle，涂改划掉再重画，手写箭头指向重画处
P3: 无图内文字（不写任何文字）；muted palette with {旧蓝|橄榄绿} marker accents，铅笔灰线条贯穿
P4: 氛围情绪化但克制、乱中有序、手账自我对话感；避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通
```

### 5. 城市
```text
P1: 16:9 横版 全幅白纸底, 约 80% 留白, 白纸纸纹, sketchy 抖动线条与马克笔笔触, doodle 小涂鸦, 视觉簇位于{位置}，不贴边，画面顶部与底部边缘各保留纯纸色留白，便于安全裁切
P2: 主体：{一栋歪斜的楼/一辆公交车/街角的路灯}，潦草勾勒成手账 doodle，楼体线条涂改重画，旁边贴胶带
P3: 无图内文字（不写任何文字）；muted palette with {旧蓝|焦黄} marker accents，铅笔灰线条贯穿
P4: 氛围通勤日常、城市漫游感、随手速写手账感；避免精致矢量插画、避免完美平滑线条、避免高饱和、避免渐变紫、避免日系动漫、避免卡通
```

## 五、工作流（Andiii 适配层）

0. **设计推理（必做，≤60秒）**：读 `D:/tools/andiii-wechat-workflow/references/design-reasoning.md`，按 6 项模板作答（用途渠道/受众气质/视觉系统/主次层级/留白决策/方向承诺）——先定「为什么这么画」，再动手编译。
1. 转译主题 → 选变体配方（Layout/Anchor/Typography/Texture/Mood 各一）
2. 按四段式编译 prompt（P2 隐喻是自由发挥点，不写场景堆砌）
3. **质检门**：`echo "prompt" | python D:/tools/hermes/skills/creative/andiii-image-style/scripts/check_engine_prompt.py`（复用水彩引擎质检门，**PASS 才生成**；sketchy 的 胶带/涂改/马克笔/铅笔/sketchy/scribble/doodle 词已入词表）
   > ⚠️ 若 hermes 副本报 `FAIL: 纹理词 < 2`（旧词表缺潦草词），先改用 workflow 仓库版 `python D:/tools/andiii-wechat-workflow/skills/andiii-image-style/scripts/check_engine_prompt.py` 验证，并提醒主 agent 同步覆盖 hermes 副本。
4. **生成**：封面 16:9（附加宽松安全区约束句："画面顶部与底部边缘各保留纯纸色留白，便于安全裁切"）→ 中心裁 2.35:1；分享图 1:1；内文配图 16:9
5. **视觉复核**（固定问句）：主体完整未裁切 / 无硬雷区 / 潦草手绘感（抖动线、涂改、胶带）明显；封面裁后必复核
6. 交用户最终确认（审美以用户为准）

## 六、封面双尺寸与文件规范

- 首图：16:9 生成 → `crop_image.py --ratio 2.35:1 --anchor center` → `cover.jpg`
- 分享图：1:1 → `cover-square.jpg`
- **默认无文字** + 宽松安全区约束句（见工作流第 4 步）
- 统一 .jpg；裁剪用 `scripts/crop_image.py`（水彩引擎同款脚本）

## 七、风格细节

线条/元素/避雷/自查清单 → `references/sketchy-style-guide.md`
