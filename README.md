# Andiii碎碎念 · 公众号内容自动化工作流

微信公众号内容自动化全流程：**文风蒸馏 → 写作 → 水彩配图引擎 → 排版 → 推草稿箱**。

由 Hermes Agent 驱动（DeepSeek 写作 + Wan2.7-Image 生图 + 小米 MiMo 视觉质检），用户只需发一个主题。

## 架构

```
用户: QQ/TUI 发送主题
    ↓
① 写作层: Hermes + DeepSeek 写正文 (Markdown)
   → andiii-writing-style 文风引擎（槽边往事/MorningRocks/新世相…风格路由）
   → humanizer 去AI味（34种AI写作模式扫描）
    ↓
② 配图层: andiii-image-style 水彩风格引擎 ← 本仓库核心
   → 四件套引擎（色彩/纹理/排版/规避）编译四段式 prompt
   → check_engine_prompt.py 质检门（无 vision 依赖）
   → Wan2.7-Image 生成封面（21:9 首图 + 1:1 分享图）+ 内文配图 + 金句卡
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
| 方案文档 | `plans/` | 风格引擎化改造完整实施方案 |
| 排版路由 | `references/theme-routing.md` | gzh-design 主题路由（留白禅意/石墨极简/摸鱼绿…+ 档位） |
| 管线说明 | `references/wechat-pipeline.md` | 主链路各阶段说明与调用姿势 |
| 同步脚本 | `scripts/sync_to_hermes.sh` | 引擎 5 文件单向同步到 Hermes skills 目录（改完仓库必跑） |

> 生成产物（图片/HTML）不入库（见 .gitignore）；引擎测试样例在 `outputs/` 本地保留。

## 依赖（Hermes skills）

- `andiii-writing-style` — 文风引擎（本仓库外，Hermes skills 目录）
- `wechat-content-automation` — 主链路编排（Hermes skills 目录，引用了本仓库的引擎）
- `gzh-design` — 排版
- `baoyu-post-to-wechat` — 微信 API 推送
- `baoyu-cover-image` / `baoyu-article-illustrator` — 封面/配图调度层

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

MIT（衍生自 baoyu-skills / gzh-design 的部分遵循上游许可证）
