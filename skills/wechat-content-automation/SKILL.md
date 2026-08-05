---
name: wechat-content-automation
description: 微信公众号内容自动化 — 从选题、写作（含风格迁移）、配图、排版（gzh-design 主题路由）到推草稿箱的全流程。用户通过 QQ/TUI/Telegram 等平台发送主题，Hermes 自动完成写作→排版→发布。支持模仿特定公众号文风、生成封面/内文配图（需额外 API Key）。集成了 wechatDownload 批量采集工具 MCP。
version: 1.4.2
created_by: agent
tags:
  - wechat
  - 公众号
  - content-publishing
  - baoyu-skills
  - automation
related_skills:
  - andiii-writing-style
  - humanizer
  - baoyu-cover-image
  - baoyu-article-illustrator
  - baoyu-post-to-wechat
  - baoyu-image-gen
  - external-ai-media-api
  - gzh-design
  - andiii-image-style
---

# 微信公众号内容自动化工作流

## 参考文件

- `references/setup-notes.md` — 完整安装步骤记录（Bun/skill/凭证/白名单配置），用于排查或重装
- `references/style-reference-accounts.md` — 公众号文风参考库：按风格类型分类的参考号列表、蒸馏方法论、共鸣写作技巧。写作前查阅此文件选定目标风格。
- `references/collecting-source-articles.md` — 微信公众号文章采集指南：如何从开放网络获取目标公众号的原文（含浏览器工具用法、**wechatDownload 批量下载工具 MCP 集成**、**wechat-article-exporter 在线方案**、**长图文章 OCR 方案**、已实操案例的局限性），是风格分析的前置步骤。
- `references/style-distillation-workflow.md` — 文风蒸馏完整工作流：从抓文章→8维度分析→组内综合→风格签名→Hermes Skill 的全流程说明，含项目目录结构和各 Phase 任务定义。
- `references/inline-illustration-workflow.md` — 文章正文内文配图工作流：生成概念插图、嵌入markdown、发布注意事项。适用于用户要求"中间也要穿插图片"的场景。
- `references/wechat-ecosystem-projects-2026-08.md` — 公众号生态开源项目调研（2026-08）：doocs/md、gzh-design-skill、md2wechat-skill、markdown-nice 五项目实测星标/许可/维护状态与采纳结论；gzh-design-skill 接入进度（Phase 1 已装、Phase 2 A/B 实测已出、**G1/G2 已拍板通过**）+ 装配实操要点与踩坑；wechat-api.ts HTML 输入链路代码级核实事实。
- `references/theme-routing.md` — gzh-design 排版主题路由（G1 定稿 2026-08-03）：文风→主题+特性档位 素/标准/全套、动态收尾签名约定、图片规范、调用姿势。
- `references/music-article-workflow.md` — 音乐/歌曲类文章工作流（2026-08-04）：歌曲事实核查 4 项清单（专辑/作者/主题/歌词原句）、**iTunes Search API 获取高清专辑封面**（100x100bb→600/1200x1200bb 换参法）、封面 vision 验证陷阱、"top3/最爱"类文章结构模板。
- `references/agnes-image-gen.md` — Agnes 生图配置：模型、key 读取优先级、401 掩码 key 踩坑、调用示例。

## 整体架构

```
用户: QQ/TUI 发送主题
    ↓
⓪ 素材先行（2026-08-04 用户确认，最大杠杆）：
   → 收到主题先别动笔，问 3-5 个针对性问题（"这事发生在什么时候？当时什么感觉？有没有一个具体的画面？"），挖出真实颗粒再写
   → 用户给的任何一句话、一个场景都是锚点，全文围着锚点转，不另起炉灶
   → 只给主题没给素材 → 先坦白缺什么，不硬写。硬写出来的必是 AI 味
   → 写作意图三问：写给谁看？想让他读完产生什么感觉？为什么是今天写这篇？答不上来就先不写
    ↓
① 写作层: Hermes + DeepSeek 写正文 (Markdown)
   → skill_view(name='andiii-writing-style') — 加载风格指南，查风格路由表
   → 按匹配风格写作，**默认停靠点（2026-08-03 明确）**：输出全文给用户审阅，用户确认后才进入配图/排版/推送；仅当用户明确说「直接做 / 你随意 / 不用审阅」才全自动跳过
   → skill_view(name='humanizer') — 去AI味语言层：扫描34种AI写作模式（排比过度、强行升华、虚假深度、值得注意的是类短语、否定排比、三连排比）
   → andiii-writing-style ⑦（de-ai-craft 手册）— 结构层手术 + 声音层 + 人称适配（"我"→"你/我们"），详见 andiii-writing-style/references/de-ai-craft.md
   → 输出带 frontmatter 的 .md 文件
   → 正文定稿后: 挑 1-2 句最有嚼劲的原句（≤20字, 不得编造/改写）→ andiii-image-style 编译金句卡 prompt → 质检 → 生成 1:1 金句卡 → 插入文末「就到这里，下次见。」之前
    ↓
② 配图层 (可选): 
   → **先路由后选引擎（2026-08-03）**：查 `references/image-style-routing.md`（配图风格路由表）→ 按文章文风定配图风格 → 加载对应引擎：
       ✅ **本地已有副本**（2026-08-04 已落盘）——权威源在 GitHub 仓库 Andiii208/andiii-wechat-workflow/references/image-style-routing.md，本地副本由 sync 脚本维护；若怀疑过时，用 MCP `mcp__github__get_file_contents`(owner=Andiii208, repo=andiii-wechat-workflow, path=references/image-style-routing.md) 对比
       andiii-image-style（手绘水彩） / andiii-zine-style（Zine 拼贴） / andiii-sketchy-style（潦草手账） / andiii-minimal-style（石墨极简） / andiii-heytear-style（喜茶拙趣） / antibes-holiday（黑白针管笔, 2026-08-06 装）
   → 引擎流程: 编译四段式 prompt → 质检门 `check_engine_prompt.py`（PASS 才允许生成）
   → 封面: 内置 image_generate（Wan2.7-Image 主力, 中文标题渲染已实测可用）一次出两版
       cover.jpg (16:9 生成→2.35:1 中心裁, 默认无文字+宽松安全区) + cover-square.jpg (1:1)
   → 内文配图: 每逻辑意象块一图, 16:9 横构图
   → 文末金句卡: 1:1（水彩风: 水彩底手写大字; zine 风: 拼贴+微文本）
   → 备选后端: Agnes API (agnes-image-2.1-flash) 直连超时需 CLIProxyAPI 中转, 详见 references/agnes-image-gen.md
    ↓
③ 发布层: 排版 + 推送 (2026-08-03 起两段式)
   → ③a 排版层: gzh-design skill
       → 按 references/theme-routing.md 路由选主题+档位 (留白禅意/石墨极简/摸鱼绿...)
       → Markdown → 粘贴式 HTML (全内联样式, span leaf 包裹)
       → ⚠️ md 中的落款段落（「就到这里，下次见。」+「——Andiii碎碎念」）排版时**并入签名区**，不得在正文中再保留一份（防双写，2026-08-03 明确）
       → 强制跑 validate_gzh_html.py: 0 ERROR + 半角标点 0 WARN 才放行
       → 产物: {名}_排版_{主题}({id}).html + _预览.html (人工兜底)
   → ③b 推送层: baoyu-post-to-wechat (wechat-api.ts, HTML 输入分支)
       → 自动上传正文图片 (uploadImagesInHtml) + 封面图
       → 创建草稿箱 (draft/add) — 已实测 (2026-08-03): span leaf 样式经 API 路径保留 ✅
    ↓
用户: 公众号助手 App → 草稿箱 → 点发布
```

## 前提条件

### 微信公众平台
- 已注册微信公众号
- 已在 **微信开发者平台** (https://developers.weixin.qq.com) 开启开发者密码
  - 入口：扫码登录 → 我的业务 → 公众号 → 基础信息 → 开发密钥
  - ⚠️ 2025年12月起，开发接口管理已从 mp.weixin.qq.com 迁移至开发者平台
- **IP 白名单** 需添加 Hermes 所在机器的出口 IP
  - 如有梯子，建议梯子 IP 和直连 IP 都加
  - 检查出口 IP: `curl -s ifconfig.me`
  - 微信 API 看到的实际 IP 可从错误信息 `invalid ip xxx.xxx.xxx.xxx` 得知
- 需要：`AppID` + `AppSecret`

### 运行时
- **Bun** (v1.x): 全局安装 `npm install -g bun`
- **baoyu-post-to-wechat** skill: 已安装到 Hermes skills 目录
  - 安装方式：`git clone` baoyu-skills 仓库 → 复制 `skills/baoyu-post-to-wechat/` 到 Hermes skills 目录
  - 注：`hermes skills install` 在国内可能因 raw.githubusercontent.com 被屏蔽而超时，改用 git clone 方式
- 凭证文件: `~/.baoyu-skills/.env`
  ```
  WECHAT_APP_ID=your_app_id
  WECHAT_APP_SECRET=your_app_secret
  ```
- 偏好设置: `~/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md`
  ```
  default_author: 公众号名称
  need_open_comment: 1
  only_fans_can_comment: 0
  default_publish_method: api
  ```

## 写作规范

### 风格路由（自动匹配）

不用固定一种风格。根据用户的话题自动判断最适合的写法：

| 用户说的话题关键词 | 自动匹配的风格 | 参考来源 |
|-------------------|--------------|---------|
| 小事/日常/今天遇到/看到/闻到/听到 | **槽边往事风** — 从具体场景切入，思考过程当戏写，极短段落 | A组 |
| 很美/安静/黄昏/夜晚/宇宙/风/云/海/诗 | **MorningRocks 风** — "想象一下"开头，诗意+留白，每节一个金句 | A组 |
| 困惑/选择/毕业/考研/工作/未来/面试/考试 | **我要WhatYouNeed风** — 命名共情，把你的小习惯翻译成心理学概念 | B组 |
| 迷茫/勇气/人生选择/想做又不敢/长文反思 | **杂乱无章风** — 用自己的真实困境示范"高处的迷茫"，脆弱换信任 | B组 |
| 焦虑/拖延/自律/习惯/想不通 | **L先生说风** — 痛点→机制→方案，用认知科学降低自责感 | B组 |
| 失败/被拒/悲伤/集体情绪/输的感受 | **新世相风** — 让"输家"的故事被看见，用真实案例替代说教 | B组 |
| 读书/电影/看到一篇文章/想起一句话 | **MorningRocks × 我要WhatYouNeed混合风** — 跨领域联结+情感命名 | A+B |
| 记录/今天/日常/普通的一天 | **槽边往事 × 杂乱无章混合风** — 个人叙事+自嘲解构 | A+B |

不同风格在以下维度有差异：

| 维度 | 槽边往事风 | MorningRocks 风 | 我要WhatYouNeed风 | 杂乱无章风 | L先生说风 | 新世相风 |
|------|-----------|----------------|------------------|-----------|-----------|---------|
| 标题 | 为什么+日常现象 | 名词短语+留白 | "其实……才是……" | 抽象品质词+句号 | 痛点疑问句+承诺 | 宏大场景+否定常规 |
| 开头 | 场景切入+"我不服" | "想象一下"场景 | 从微小物品切入 | 个人困境自述 | 先否定无效方法 | Sayings编者按 |
| 人称 | "我"极高 | "你"极高 | "我们"为主 | "我"极高 | "你"极高 | "我"低频 |
| 段落 | 2-6行，关键句独立成段 | 中短段落+小标题 | 中短段落+插画 | 极短段落+空行 | 2-4行中等长度 | 极短段落+GIF |
| 配图 | 无 | AI插画2-6张 | 插画/摄影混合 | 手绘线条+GIF | Unsplash头图+分隔线 | 大量真实GIF |
| 金句 | 排比→反转收尾 | 每节一个断言 | 情感命名式金句 | 蓄力→释放单句 | 原理→结论断言 | 他人之口说观点 |
| "你"频率 | 低 | 高 | 中 | 中 | 极高 | 低 |
| "我"频率 | 极高 | 中 | 低 | 极高 | 极低 | 低 |

用户也可以手动指定：`用槽边往事那种风格，主题：今天在食堂`

### 风格迁移（核心：个人表达 → 引发共鸣）

写作前：

1. **应用风格路由**：根据用户话题自动匹配风格方向

2. **查阅参考库**：读取 `references/style-reference-accounts.md` 查看风格分类、具体号的特征和蒸馏方法

3. **风格蒸馏**（如果指定了具体参考号）：
   - 先采集样文：见 `references/collecting-source-articles.md`。部分号可通过浏览器工具直接抓取（如 MorningRocks）；部分号仅微信生态内传播（酒鬼诗人、海听等），需客户端关注后手动收集。
   - 扒该号4-6篇文章，拆解10个维度：标题风格、开头方式、段落节奏、语气调性、用词习惯、金句密度、结尾方式、选题范围、配图规律、内容结构\n   - 浓缩成一段"风格提示词"
   - 浓缩成一段"风格提示词"

4. **写作核心原则**：用参考号的**表达方式**，说用户的**真实感受** → 引发共鸣，不是抄袭

5. **自检三问**（写完后）：
   - 这句话是我真的想说的，还是为了"好看"写的？
   - 如果朋友读到，会觉得这是"我"写的吗？
   - 有没有一句话能让读者停下来想一会儿？

### 文章 frontmatter
```yaml
---
title: 文章标题
author: Andiii碎碎念
coverImage: ./cover.png  # 封面图路径
description: 摘要（自动截断至120字符）
---
```

### 发布命令 (gzh-design 排版 → API 推送)
```bash
# 第1步 排版: 加载 gzh-design skill, 按 theme-routing.md 路由选主题/档位,
#        跑 validate_gzh_html.py 至 0 ERROR + 0 WARN, 产出 {名}_排版_{主题}({id}).html

# 第2步 推送前 dry-run 验证 (不碰微信):
cd /path/to/article && npx -y bun "D:/tools/hermes/skills/baoyu-post-to-wechat/scripts/wechat-api.ts" "article_排版_留白禅意(zen-whitespace).html" --title "标题" --author "Andiii碎碎念" --summary "摘要" --cover cover.png --dry-run

# 第3步 正式推草稿 (HTML 输入分支, 自动上传正文图片+封面):
npx -y bun "D:/tools/hermes/skills/baoyu-post-to-wechat/scripts/wechat-api.ts" "article_排版_留白禅意(zen-whitespace).html" --title "标题" --author "Andiii碎碎念" --summary "摘要" --cover cover.png

# ⚠️ 路径必须 Windows 格式 D:/tools/...（bun 不认 git-bash 的 /d/tools/...，会报 Module not found）

# 兜底: 旧 .md 直推链路仍可用 (--theme grace --color blue)
```

## 配图 (可选)

### 配图数量偏好（2026-08-03 用户两次实测反馈）
- 用户偏好**插图多，宁可多不可少**：观点/散文类文章按**每个逻辑意象块一图**配（1500 字散文实测 7 张满意；只放 3 张被纠正「图片太少了」），图下方跟一行居中说明文字（如"— 深夜两点半，聊到饿了才点的外卖"）
- 图序与意象对应：每意象块金句/段落后插图，节奏统一（正文 → 金句 → 图）
- **构图铁律**：全部配图必须宽幅横构图（16:9），prompt 显式指定横向元素锚定构图，详见 references/theme-routing.md 图片规范

### 支持的图生后端
baoyu-cover-image 和 baoyu-article-illustrator 是调度层，需要底层图生 API：

| 后端 | 需配置 | 国内可用 |
|------|--------|:--------:|
| DashScope (阿里通义万相) | 阿里云 API Key | ✅ 推荐 |
| MiniMax | MiniMax API Key | ✅ |
| Seedream (豆包/字节) | 豆包 API Key | ✅ |
| OpenRouter | OpenRouter Key | ✅ |
| OpenAI GPT Image 2 | OpenAI Key | ❌ 需翻墙 |

**不免费** — 每张图几分钱。如无 API Key，可跳过配图，仅用封面图（纯色/渐变方案）。

### Hermes 内置 image_gen
Hermes 已启用 `image_gen` 工具，如已配好 provider 可直接调度。baoyu 配图 Skill 的自动选择逻辑会优先检测 Hermes 原生工具。

## 工作流检查清单

- [ ] 微信开发者权限已开启（AppID + AppSecret）
- [ ] IP 白名单已配置
- [ ] Bun 已安装
- [ ] baoyu-post-to-wechat 已安装到 Hermes skills
- [ ] gzh-design-skill 已安装 (D:\tools\hermes\skills\productivity\gzh-design-skill)
- [ ] references/theme-routing.md 已配置（主题路由/特性档位/签名约定）
- [ ] `~/.baoyu-skills/.env` 凭证已配
- [ ] EXTEND.md 偏好已配
- [ ] （可选）图生 API Key 已配
- [ ] （可选）风格库参考文献已存入 references/

## Pitfalls

- ❌ **不要在 hermes skills install 超时后反复重试** — raw.githubusercontent.com 在国内常被屏蔽，改用 git clone
- ❌ **不要忘记 IP 白名单有两个可能 IP** — 梯子出口和直连出口，全部加上
- ⚠️ **40164 IP 白名单诊断**：Clash TUN 模式下 `api.weixin.qq.com` 走直连，微信报错里的 IP 是**宽带直连 IP**（`curl ifconfig.me` 看到的是代理出口，两者不同——**以微信报错里的 IP 为准**）；家庭宽带 IP 动态、会不定期失效 → 根治用 baoyu `--remote`（固定 IP 服务器出口）
- ⚠️ **IP 白名单填写位置（2026-08 实测，用户曾找不到）**：2025-12 起白名单管理已迁到微信开发者平台，mp 后台只提示"去开发者平台"不给路径——登录 https://developers.weixin.qq.com → **我的业务 → 公众号 → 基础信息 → 开发信息 → API IP 白名单** → 添加微信报错里的 IP → 保存（实测**立即生效**，无需等待）。注意：登录后默认在首页，需先点页面下方「我的业务」卡片进入
- ⚠️ **给用户看 HTML 预览（Windows）**：`open_preview` 面板可能不可见；Hermes 自带浏览器是无头模式用户看不到；`cmd start`/`explorer.exe` 对中文路径经代码页乱码后静默失败 → 兜底：复制到纯 ASCII 路径，或放桌面文件夹 + 图片 base64 内嵌自包含
- ⚠️ **git-bash MSYS 路径 ≠ Windows 原生程序路径**：终端里 `python`/`python3`（Windows 原生）和 `npx bun` 都不认 MSYS 格式——`/tmp/p.txt` → FileNotFoundError；`/d/tools/.../wechat-api.ts` → "Module not found"（文件明明存在）。传给原生程序一律用 `D:/tools/...` Windows 格式；prompt 临时文件写当前工作目录，别写 /tmp（2026-08-03 e2e 实测两个都踩过）
- ⚠️ **PIL 图片处理用系统 python**：Hermes venv 的 PIL 可能损坏（`ImportError: cannot import name '_imaging' from 'PIL'`），系统 python 3.11/3.12 的 PIL 12.x 正常。封面 2.35:1≈900×383 / 内文 16:9≈900×506 / jpg quality 82-85 的裁剪脚本用 `python`（系统）跑
- ⚠️ **图片统一 .jpg 扩展名**：PIL 存 JPEG 内容但命名 .png → wechat-api 报 `Format mismatch: cover.png declared as image/png, actual image/jpeg`（上传成功但难看）；封面/配图按实际格式命名
- ❌ **发布时必须有 cover image** — `--cover` 参数或 frontmatter.coverImage，否则报错
- ⚠️ **wechat-api.ts（API 方式）接受 .html 输入**（已代码级核实 v1.118.2）：HTML 直接读取，`<section>` 纯片段原样作正文；正文 `<img>` 自动上传（`media/uploadimg`）并重写为 https URL；元数据取 CLI `--title/--author/--summary`，或同目录同名 `.md`（`x.html`→`x.md`）的 frontmatter；`--dry-run` 在取 token 前返回、零风险验证全链路。⚠️ browser 方式仍只吃 markdown（占位符粘贴机制）
- ✅ **API 路径 span leaf 样式保留已实测通过**（2026-08-03）：gzh-design 排版产物 → wechat-api.ts HTML 分支 → draft/add → 公众号助手 App 检查正常（章节标题/衬线金句/下划线/END 分割线/图片/封面全部保留）
- ⚠️ **正文图片必须本地相对路径**（与 HTML 同目录）— 远程非 mmbiz URL 上传行为不确定
- ⚠️ **中文+括号文件名在 bash 中必须加引号**
- ⚠️ **gzh-design 校验必须 0 ERROR + 半角标点 0 WARN** — 半角标点是最高频返工点
- ⚠️ **gzh-design 为 AGPL-3.0** — 修改组件库后对外分发需开源，个人自用无碍
- ⚠️ **Agnes 生图模型（2026-08-03 核查）**：`agnes-image-2.1-flash` 即最新可用免费模型（Agnes Image 2.5 Preview 官网标 coming soon 未上线），**无需改名**；脚本 `external-ai-media-api/scripts/agnes_image.py` 存在（参数 prompt size model，读 Hermes 主配置 .env）；也可直接 curl `https://apihub.agnes-ai.com/v1/images/generations`（OpenAI 兼容，size 支持 "1792x1024"/"4K"）；`/v1/models` 端点不返回模型列表，查模型以 wiki.agnes-ai.com 为准；**401 根因**：key 曾被存成掩码占位符（如带省略号的 sk-hkq...xxx，长度仅 13 字符），真实 key 约 51 字符，从 Hermes 主配置 .env 取
- ⚠️ **gzh-design 装配后必须去标签间空白** — span 之间的换行/缩进会渲染成空格，在 `text-align:justify` 下被拉伸（下划线关键词两侧间隙明显，2026-08-03 用户实测反馈）；文字全在 span 内，安全做法：`re.sub(r'>\s+<','><',html)`，校验前执行（详见 theme-routing.md 调用姿势）
- ⚠️ **去空白后 HTML 变单行，patch 工具失效** — `re.sub(r'>\s+<','><',html)` 之后整个文件只有 1 行，`patch` 工具的多行 old_string 匹配不到（报 "Could not find a match"）。后续要往排版产物里插内容（如图片块），用 **python 锚点 replace**：`html.replace(锚点子串, 锚点 + 新块, 1)`，锚点取段落结尾的 `</span></p>` 片段，每处 replace 前 `assert anchor in html` 防静默漏插（2026-08-03 补 4 张图时踩过）
- ⚠️ **gzh-design 组件库文件是 CRLF 换行** — read_file 会误判 "Binary file cannot display"（theme-zen-whitespace.md / common-components.md 实测触发，实际是正常 UTF-8 无 null 字节）；用 `python3 -c "print(open(path,encoding='utf-8').read())"` 转储读取，校验脚本 validate_gzh_html.py 不受影响
- ⚠️ **AppSecret 只显示一次** — 启用开发者密码时立刻复制保存，丢失只能重置
### 写作陷阱（补充 andiii-writing-style 未覆盖但会话实测的）

- **概念列表/对比类主题先讨论再动笔** — 用户给"旅游/旅行/度假"这类多概念主题时，意图可能是"想讨论三者之间的区别"，而不是"写一篇文章"。先展开讨论（拆概念、给框架、抛角度），用户认可讨论后，文章方向从讨论结论里长出来再动笔。2026-08 实测：拿到"旅游/度假/旅行"直接写了一篇旅行文章，被纠正"我是说想讨论一下"。判断规则：主题是单个意象/事件 → 可写；主题是"多概念的对比"→ 先讨论。
- **POV 选错** — 用户拒绝虚构的"我"。没有用户提供的真实个人素材时，叙事主体一律用"你"（第二人称，对读者说话）。只有用户给了具体的亲身经历（如"大二那年我在操场走了三个小时"），才用"我"。用错"我"比用错"你"更致命，因为被识破是编的后整篇文章可信度归零。
- **扩写方向错误** — 用户接受"深挖一层"（分析why），拒绝"铺开细节"（更多场景描写）。改稿时宁可加一层分析，不要增加场景描写的量。多一个层次的洞察 > 多三句场景描写。
- **照片级构图不合适** — Agnes / baoyu-image-gen 的概念图生成效果最好的prompt是"极简、概念型、写意不写实"。避免要求"现实主义"/"照片级"。
- ⚠️ **歌曲/专辑事实必须搜索核实后再写（2026-08-04 实测）** — 用户会逐项核对。动笔前每首歌查：所属专辑+年份、词曲作者、歌词主题、**要引用的歌词原句**（一字不差）。金句式否定断言高危：想写《飞机场的10:30》"没有一句'我想你'"，实际歌词开头就有「我好想你」——差点写出事实错误。写法改对比：「最打动我的不是那句'我好想你'，是可乐剩一点给你」。专辑封面图获取/核查流程见 references/music-article-workflow.md。
- ⚠️ **部分公众号文章是长图（纯图片无文字层）或插画格式** — 我要WhatYouNeed 的漫画/插画文章即为图片格式，MCP 文本下载只抓到框架，正文需 vision_analyze OCR 提取。此类文章的风格分析需配合浏览器截图。
- ⚠️ **公众号文章在 WeChat 墙内** — web_extract 无法读取，需浏览器工具或 wechatDownload 配合电脑微信获取
- ✅ **已实操成功**：通过 wechatDownload 桌面端批量拉取了 MorningRocks（雨雪霏霏 / 公众号名「雨雪霏霏1015」）11 篇文章，全为文字可读，非长图
- ✅ **wechatDownload 已安装在 D:\tools\wechatDownload**，MCP 已配置。双击 exe → 勾选「启动MCP」→ Hermes 可通过 MCP 调它批量拉文章
- ✅ **Hermes 原生 MCP 工具可直接调用**（无需启动桌面端）：`mcp__wechat_download_mcp__wechat(url, config)` 单篇下载 + `mcp__wechat_download_mcp__wechat_collection(url, config)` 合集下载。输出文件存储在远端云存储，返回值含下载 URL。适合 Agent 自动化直接调用。
- **本地端口**：`http://127.0.0.1:4545/mcp`
- **Hermes Skill 已安装**：`wechat-article-downloader`
- **批量下载流程**：运行桌面端 → 贴文章链接获取公众号ID → 电脑微信打开链接获密钥 → 桌面端自动批量下载 → 文件存到 D:\tools\wechatDownload\下载\公众号名\
- ⚠️ **MCP 工具仅供单篇/合集下载**：`wechat`（单篇）和 `wechat_collection`（合集）可用；无 `batch_download_articles` MCP 工具。全量批量必须走桌面 GUI + 电脑微信密钥。
- ⚠️ **文风分析不需要全量**：每个号 4-6 篇代表性样文足够提取风格特征。不必为追求"全量"卡住分析进度。
