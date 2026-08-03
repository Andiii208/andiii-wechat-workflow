# 公众号排版主题路由（gzh-design）

> G1 决策门定稿（2026-08-03，用户拍板）。配合 wechat-content-automation 写作层的**风格路由表**使用：写作定了文风，排版跟着路由定主题。写作层路由见 SKILL.md「风格路由（自动匹配）」。

## 路由表

| 写作风格 / 话题关键词 | gzh-design 主题 | 特性档位 | 状态 |
|---|---|---|---|
| 日常小事/记录（槽边往事风） | 留白禅意 | 素 | ✅ 已实测 |
| 诗意/很美/黄昏/夜晚（MorningRocks 风） | 留白禅意 | 标准 | ✅ 已实测 |
| 焦虑/拖延/自律/观点（L先生说风） | 石墨极简 | 全套 | ✅ 已实测 |
| 情感命名（WhatYouNeed 风） | 留白禅意 | 标准 | ✅ 已实测 |
| 失败/集体情绪（新世相风） | 石墨极简 | 全套 | ⏳ 未实测，先用建议值 |
| 教程/工具盘点/清单 | 摸鱼绿 | 全套 | ⏳ 未实测（gzh-design 官方强项场景） |
| 数据复盘/报告 | 石墨极简 或 摸鱼绿 | 全套 | ⏳ 未实测 |

- 主题清单/色值/组件库文件以 `gzh-design-skill/references/theme-index.md` 为单一来源
- 所有主题不满足时：走 gzh-design 的**主题生成器**（一句话/参考图现造一套并登记，见其 SKILL.md「自定义主题生成」）

## 特性档位定义

| 档位 | 导读目录卡 | 章节编号 | 关键词下划线 | 结构化组件（列表/卡片/标签） |
|---|---|---|---|---|
| 素 | 不生成 | 保留（文章有 `##` 时） | 每段 0–1 处，低频 | 按需，克制 |
| 标准 | 3+ 章节时生成 | 保留 | 每段 1–2 处 | 按需 |
| 全套 | 3+ 章节时生成 | 保留（末章 ∞ 变体） | 每段 1–3 处 | 按内容充分使用 |

## 签名约定（G1 定稿：动态收尾版）

- 每篇文章尾部：**按文章内容写一句收尾**（4–15 字，与文章呼应、可回扣标题/意象；不升华、不鸡汤、不说教）+ `—— Andiii碎碎念`
- **不使用**"点赞在看转发三连"类 CTA
- 写砸了（套路感/强行升华/与内容无关）→ 改回固定文案 `我是 Andiii碎碎念。`，并在交付时说明
- gzh-design 组件库签名区模板用对应主题的签名组件（留白禅意=组件15，石墨极简=组件16），按上述文案替换

## 图片规范

- **构图铁律（用户 2026-08-03 拍板）**：公众号配图一律**宽幅横构图**——竖图/竖版感构图浪费横向面积、影响观感。生成 prompt 必须显式写「宽幅横向构图，16:9 电影画幅，主体横向分布」，并在 prompt 里用横向元素锚定构图（道路横向贯穿 / 人物偏侧 + 大片留白 / 地平线压低 / 街道横向延伸）。光生成 landscape 比例不够——Wan2.7 出图默认 1344×768 是横的，但构图若把主体堆在中部仍会有「竖版感」，用户会要求重做
- **规格**：封面 `cover.png` 裁到 2.35:1 ≈ 900×383（必须提供）；内文图统一裁到 **16:9 ≈ 900×506**，quality 82-85。裁剪脚本：中心裁剪到目标比例 → `Image.LANCZOS` resize → 存 jpg（PNG 原图 1MB+，jpg 压到 30-90KB）
- 配图密度（用户 2026-08-03 实测，第二次被纠正「图片太少了」）：观点/散文类**宁可多不可少**——按**每个逻辑意象块一图**（1500 字散文配到 7 张用户才满意，3 张被嫌少）。散文无 `##` 章节时，按意象切块：开场意象、理想画面、现实落差、金句意象、机制意象、剪辑意象、真实时刻收尾
- 图序与节奏：正文段落/金句 → 图 → 说明文字（`— 一句话说明`，居中，与意象呼应，如「— 深夜两点半，聊到饿了才点的外卖」），每张图都有说明文字
- 正文图片**一律本地相对路径**，与 HTML 文件同目录（wechat-api.ts 以 HTML 所在目录为 baseDir 解析并自动上传）
- 图片标签：`max-width:100%;height:auto;display:block;margin:0 auto`，不用 `width:100%`（小图会糊）

### 生图链路（2026-08-03 用户确认）

- **主链路：Hermes 内置 `image_generate` 工具 = TokenRhythm Wan2.7-Image**（1344×768 起，够用）。用户配置为「Wan2.7-Image 为主，Hermes 为 fallback」——实际 image_generate 自带自动 fallback：某次 Wan2.7 失败时结果 provider 显示 `tokenrhythm→agnes` 自动切到 Agnes agnes-image-2.1-flash，无需手动干预
- 概念插画 prompt 风格：「极简、概念型、写意不写实」+「深蓝与暖橙色调 / 大量留白 / 无任何文字」+「氛围：一句话点题」。避免「现实主义/照片级」

### 更新草稿流程（重新推图/改文后）

wechat-api.ts 每次推**新**草稿（新 media_id），旧草稿不会自动删除 → 草稿箱堆积。推新后必须手动删旧：

```bash
# 用 ~/.baoyu-skills/.env 的 AppID/AppSecret 拿 token，调 draft/delete 删旧 media_id
python - <<'EOF'
import re, urllib.request, json
env = open(r'C:\Users\26895\.baoyu-skills\.env', encoding='utf-8').read()
appid = re.search(r'WECHAT_APP_ID\s*=\s*(\S+)', env).group(1)
secret = re.search(r'WECHAT_APP_SECRET\s*=\s*(\S+)', env).group(1)
tok = json.loads(urllib.request.urlopen(f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}').read())['access_token']
data = json.dumps({'media_id': '旧media_id'}).encode()
req = urllib.request.Request(f'https://api.weixin.qq.com/cgi-bin/draft/delete?access_token={tok}', data=data, headers={'Content-Type': 'application/json'})
print(json.loads(urllib.request.urlopen(req).read()))  # {'errcode': 0, 'errmsg': 'ok'}
EOF
```

图像处理注意：**用 `python`（3.11，PIL 12.3.0 可用）跑 PIL，不要用 `python3`**（hermes venv 的 PIL `_imaging` 损坏 ImportError）。

## 调用姿势（Hermes 执行顺序）

1. 写作层完成 → `article.md`（带 frontmatter: title/author/description）
2. 按本文档路由表选主题+档位（全自动模式，不再逐篇确认）
3. `skill_view(name='gzh-design')` 加载排版 skill，按其 SKILL.md 工作流执行：
   - 读 `theme-index.md` + 所选主题组件库 `theme-{id}.md` + `common-components.md`
   - 解析 Markdown → 按主题配方表装配 HTML（**组件一律从组件库取，不手写**）
   - 落盘 `{名}_排版_{主题}({id}).html`
   - **装配后必须去标签间空白**：`python3 -c "import re;open(p,'w').write(re.sub(r'>\s+<','><',open(p).read()))"`——span 之间的换行/缩进会渲染成空格，在 `text-align:justify` 下被拉伸，下划线词两侧间隙明显（2026-08-03 用户实测反馈）
   - **装配后交叉核对**：md 里的每个 `##` 标题、`>` 金句、`![]` 图片必须全部出现在 HTML 中（`grep -n "金句关键词" <html>` 比对）——2026-08 实测装配时漏过一句金句，校验脚本查不出（内容缺失不报错，只有 grep 能抓到）
4. 强制校验：`python3 <gzh-design-skill>/scripts/validate_gzh_html.py <html>` → **0 ERROR + 半角标点 0 WARN**
5. （可选，用户要看效果时）`wrap_preview.py` 生成 `_预览.html` 交付预览
6. 推送：`wechat-api.ts <html> --title ... --author "Andiii碎碎念" --summary ... --cover cover.png`（先 `--dry-run`）
7. 用户公众号助手 App 检查草稿 → 发布

## 字体约定（2026-08-03 定稿）

- **正文/全局字体：宋体衬线栈** `'Songti SC', 'Noto Serif CJK SC', 'Source Han Serif SC', 'SimSun', serif`（iOS 命中宋体，Android 主流命中思源宋体；旧机型回退 serif）
- 已写入 **全部 6 套主题**的组件库全局容器+骨架+文档行（zen-whitespace / graphite-minimal / moyu-green / moyu-ticket / red-white / olive-journal；olive 保留 IBM Plex Sans 拉丁优先，中文走宋体），排版时**不要覆盖/改回黑体栈**
- ⚠️ **字号无法锁死**：微信阅读器强制跟随用户"设置→通用→字体大小"整体缩放（无障碍产品行为），文章内禁 script 无法 hack；排版为纯流式布局，放大不崩，保证"放大后依然整齐"即可
- 代码块保持等宽字体（monospace），标题用主题自带衬线（zen 的 Noto Serif SC）

## 维护记录

- 2026-08-03：G1 定稿（路由/档位/动态收尾签名）；G2 验证 API 推送路径样式保留 ✅
- 2026-08-03：**首篇实战《旅游是去看的，旅行是去走的，度假是去躺的》已发布**（石墨极简·全套 + 4 张 Agnes 插画 + 动态收尾签名）——观点/洞察类走石墨极简链路全流程验证通过
- 未实测路由（WhatYouNeed/新世相/教程/数据）发过一篇后回来补状态
