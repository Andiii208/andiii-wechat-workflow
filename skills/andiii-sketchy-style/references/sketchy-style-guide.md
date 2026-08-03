# Andiii Sketchy 潦草手账风格细节指南

本文件是 andiii-sketchy-style 引擎的风格细节手册：线条怎么画、元素放什么、雷区在哪、质检门怎么自查。

## 一、线条（Lines）

潦草感的核心是"手劲"，所有线条都要有手绘的不完美：

- **抖动线 sketchy/jitter lines**：手抖般的重复短笔，轮廓不闭合、对不齐
- **复线 double-stroke**：轮廓画两遍，第二遍没对准，露出"画过又描"的痕迹
- **断线 broken lines**：断续不连，像笔离开纸面又落回去
- **乱线 scribble**：快速无规则排线，用来填充阴影或表达烦躁
- **铅笔线条 pencil lines**：浅灰、可擦、有深浅变化，保留橡皮擦痕
- **马克笔笔触 marker strokes**：一笔到底，带飞白/干笔效果
- **手绘框 hand-drawn frame**：歪扭的圆圈或方框圈住主体，像随手圈重点

## 二、元素（Elements）

每张图选 1-3 个点缀，不堆砌：

- **胶带**（washi tape / masking tape）：贴纸边角翘起，半透明或牛皮纸色，贴住角落或"盖住"画错的地方
- **涂改划掉**（crossed-out）：一条或几条乱线划掉旧稿，在旁边重画一个
- **涂改液**（correction-fluid splotch）：白色/米色小块盖住再重写，边缘不规则
- **便利贴**（sticky note）：一角卷起，贴在纸上
- **手写箭头**（hand-drawn arrow）：歪歪扭扭指向注释或重画处
- **圆圈标注**（circled note）：圈出重点
- **橡皮擦痕**（eraser smudge）：灰蒙蒙的擦痕，铅笔世界的专属
- **纸折痕/纸角卷曲**（paper crease / curled corner）：增加"这本笔记本被翻过"的真实感
- **订书钉/回形针**（staple / paperclip）：极偶尔，别多用
- **贴纸**（sticker）：低饱和旧贴纸，配色必须 muted

## 三、排版与文字（Typography）

- **默认无图内文字**（不写任何文字）——封面双尺寸一律无文字
- 仅用户明确要求文字时：手写体潦草字（scrawled handwriting），可以划线划掉、手写箭头、圆圈标注
- 文字歪斜不齐、大小不一、高低不齐；**禁止**工整排版、居中标题、商业层级

## 四、色彩（Color）

- 底：白纸（sketch paper / 白纸）或牛皮纸（牛皮纸 / kraft paper）
- 主线条：铅笔灰
- 点缀：至多 1-2 个低饱和马克笔色——旧蓝 / 砖红 / 橄榄绿 / 焦黄
- 整体低饱和 muted；**禁止**精致高饱和商业插画色

## 五、避雷（Hard Avoids）

以下词在 prompt 里一律写成"避免X"（逐个前缀，质检门豁免），或干脆不写：

flat vector 扁平矢量、minimalist line art 极简线稿、charcoal 炭笔素描感（太正式）、gold foil 金箔、gallery poster 画廊海报、vivid gradient 鲜艳渐变、glassmorphism 玻璃拟态、neon glow 霓虹、3d render、anime style 日系动漫、可爱卡通、精致矢量插画、完美平滑线条、高饱和、渐变紫、干净 UI 白、对称工整构图、商业标题层级、logo/CTA

## 六、质检门快速自查（生成前必过）

```bash
echo "prompt" | python D:/tools/hermes/skills/creative/andiii-image-style/scripts/check_engine_prompt.py
```

要求：
1. **纸感词 ≥1**：白纸 / 牛皮纸 / 纸纹 / sketch paper …
2. **纹理词 ≥2**：sketchy / scribble / doodle / 胶带 / 涂改 / 马克笔 / 铅笔 …
3. **画布比例声明**：16:9 / 1:1 …
4. **硬规避零命中**（"避免X"表述除外；规避项必须逐个写"避免"前缀，不能合并成"避免A、B、C"）

输出 `PASS`（退出码 0）才允许送生成；`FAIL` 时按上面 4 条逐个核对。

## 七、与姊妹引擎的边界

| 引擎 | 关键词 | 手感 |
|---|---|---|
| andiii-image-style（水彩） | 晕染、笔触、洗淡 | 湿、柔、软 |
| andiii-zine-style（拼贴） | 影印、risograph、撕边 | 干、旧、印刷颗粒 |
| **andiii-sketchy-style（潦草）** | **sketchy、scribble、涂改、胶带** | **随手、带手劲、橡皮擦痕** |

选题参考：日常碎碎念、通勤小事、雨天随感、食物、情绪日记、城市速写。深度/文艺/集体情绪类文章优先 zine，本引擎不抢戏。
