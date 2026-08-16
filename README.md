# Andiii碎碎念 · 公众号内容自动化工作流

微信公众号内容自动化全流程：**文风蒸馏 → 写作 → 多引擎配图路由 → 排版 → 推草稿箱**。

由 Hermes Agent 驱动（DeepSeek 写作 + Wan2.7-Image 生图 + 小米 MiMo 视觉质检），用户只需发一个主题。

## 架构

```
用户: QQ/TUI 发送主题
    ↓
① 写作层: Hermes + DeepSeek 写正文 (Markdown)
   → andiii-writing-style 文风引擎（槽边往事/MorningRocks/新世相…风格路由）
   → humanizer 去AI味（34种AI写作模式扫描）
    ↓
② 配图层: 多引擎路由（水彩/Zine/喜茶/潦草/石墨极简/黑白针管笔）← 本仓库核心
   → image-style-routing.md 文风→配图风格→引擎 路由
   → design-reasoning.md 设计意图层 + 各引擎四件套编译 prompt
   → check_engine_prompt.py 质检门（无 vision 依赖）
   → Wan2.7-Image 生成封面（16:9 首图裁 2.35:1 + 1:1 分享图）+ 内文配图 + 金句卡
    ↓
③ 发布层:
   → gzh-design 排版（theme-routing 主题路由, validate_gzh_html.py 0 ERROR 放行）
   → baoyu-post-to-wechat 推草稿箱（微信开发者平台 API）
    ↓
公众号助手 App → 草稿箱 → 发布
```

## 组件

| 组件 | 位置 | 说明 |
|---|---|---|
| 水彩风格引擎 | `skills/andiii-image-style/` | 手绘水彩风四件套 + 四段式编译 + 弹药库 10 类 + 质检门脚本 |
| Zine 拼贴引擎 | `skills/andiii-zine-style/` | 低饱和拼贴/档案感（适配 moonlin1213/muted-zine-poster-v01，MIT） |
| 新中式茶饮引擎 | `skills/andiii-heytear-style/` | 喜茶风（宣纸/水墨/茶汤色/印章），子 agent 蒸馏 |
| 潦草手账引擎 | `skills/andiii-sketchy-style/` | sketchy 涂鸦手账（白纸/牛皮纸/胶带/马克笔），子 agent 蒸馏 |
| 石墨极简引擎 | `skills/andiii-minimal-style/` | 灰阶理性/细线/大留白（L先生说风向） |
| 配图风格路由表 | `references/image-style-routing.md` | **文风 → 配图风格 → 引擎** 路由（配图层先路由后选引擎；风格是参考不是限制） |
| 设计推理层 | `references/design-reasoning.md` | 艺术感保障：6 项设计意图模板 + 艺术指导词表 + anti-slop 抢救手册（全部引擎工作流第 0 步必做） |
| 去 AI 味手册 | `references/de-ai-craft.md` | 文案去 AI 味：结构层手术 + 声音层 + 第二人称适配（配 humanizer 语言层 34 模式） |
| 调研存档 | `references/learnings/` | design-image-studio anti-slop 等外部 skill 精华存档 |
| 方案文档 | `plans/` | 风格引擎化改造完整实施方案 |
| 排版路由 | `references/theme-routing.md` | gzh-design 主题路由（留白禅意/石墨极简/摸鱼绿…+ 档位） |
| 排版引擎 | `skills/gzh-design-skill/` | gzh-design 装配快照（上游 isjiamu/gzh-design-skill + 本地定制 6 套主题库 + validate 脚本；AGPL-3.0 见 NOTICE.md） |
| 主链路编排 | `skills/wechat-content-automation/` | 全流程编排 skill（写作→配图→排版→推送，本仓库内） |
| 同步脚本 | `scripts/sync_to_hermes.sh` | 仓库→Hermes 单向部署（自动备份/内容校验/陈旧文件清理，改完仓库必跑） |

> 生成产物（图片/HTML）不入库（见 .gitignore）；引擎测试样例在 `outputs/` 本地保留。

## 依赖（Hermes skills）

**本仓库内**（随仓库同步部署）：`andiii-writing-style`、`wechat-content-automation`、`gzh-design-skill`（AGPL 装配快照）、五个 andiii-* 视觉引擎。

**外部运行依赖**（Hermes 侧安装，本仓库仅路由引用）：
- `baoyu-post-to-wechat` / `baoyu-cover-image` / `baoyu-article-illustrator` — 推送与配图调度（baoyu-skills，MIT）
- `antibes-holiday` — 黑白针管笔引擎（MIT）
- `human-writing`（check_prose.py 文字质检门，MIT）+ `humanizer`（去 AI 味）
- `external-ai-media-api` — 生图 API 调度
- 运行环境：Bun / Python3 / Pillow

许可证边界与上游清单见 `NOTICE.md`。

## 快速使用

```bash
# 引擎自检
echo "一份水彩封面 prompt" | python skills/andiii-image-style/scripts/check_engine_prompt.py

# 引擎改动后同步到 Hermes（仓库为主副本，必跑）
bash scripts/sync_to_hermes.sh

# 完整流程（在 Hermes 里）
"用公众号工作流写一篇关于 XX 的文章"
```

## License

MIT（见根目录 `LICENSE`；上游依赖与许可证边界见 `NOTICE.md`）
