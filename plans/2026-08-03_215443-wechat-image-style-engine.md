# 公众号配图风格引擎化改造方案（Andiii 手绘水彩风）

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 把用户已确认的手绘水彩审美（纸纹/笔触/晕染，拒 flat 极简/炭黑金/美术馆海报风）从"聊天里的偏好"升级为工作流里的**可替换风格引擎**，并借鉴调研到的生图 skills 机制（taste-skill 反 slop 清单、zine-poster 引擎可替换架构、nano-banana-pro 按场景 prompt 推荐、guizang 双尺寸封面、ljg「铸」金句卡），一次性提升 Andiii碎碎念公众号所有配图（封面/内文图/金句卡）的出图下限。

**Architecture:** 新建独立 skill `andiii-image-style`（风格引擎：色彩+纹理+排版+规避四件套 + 四段式 prompt 编译模板 + 按主题水彩 prompt 弹药库 + prompt 层质检门脚本），作为 baoyu-cover-image / baoyu-article-illustrator 与底层图生后端之间的"品味前置层"。wechat-content-automation 主链路在 ② 配图层插入引擎加载与质检门调用；封面升级为 21:9 首图 + 1:1 分享图双尺寸协议；写作流程末端追加文末金句卡子流程。引擎文件模型无关（Wan2.7-Image / Agnes / baoyu 多后端通吃）。

**Tech Stack:** Hermes skills（SKILL.md + references/ + scripts/），Python 3（质检脚本，仅标准库），现有后端：Hermes 内置 image_generate（Wan2.7-Image 主）+ Agnes API（备）+ baoyu-image-gen（多后端调度）。

---

## 背景与上下文

### 现状管线（wechat-content-automation v1.4.2）

```
用户: QQ/TUI 发送主题
  ↓
① 写作层: andiii-writing-style + humanizer → 带 frontmatter 的 .md
  ↓
② 配图层: external-ai-media-api / baoyu-image-gen 生成封面
   → baoyu-article-illustrator 生成内文配图（每逻辑意象块一图, 16:9 横构图）
  ↓
③ 发布层: gzh-design 排版（theme-routing 路由）→ baoyu-post-to-wechat 推草稿箱
```

### 关键文件

| 文件 | 角色 |
|---|---|
| `D:\tools\hermes\skills\productivity\wechat-content-automation\SKILL.md` | 主链路（本次修改 ② 配图层） |
| `D:\tools\hermes\skills\productivity\wechat-content-automation\references\inline-illustration-workflow.md` | 内文配图工作流（本次接入引擎） |
| `D:\tools\hermes\skills\productivity\wechat-content-automation\references\theme-routing.md` | 排版主题路由（含图片规范，G1 定稿 2026-08-03） |
| `D:\tools\hermes\skills\baoyu-cover-image\` | 封面生成（5 维度 + 11 色板 + 7 渲染） |
| `D:\tools\hermes\skills\baoyu-article-illustrator\` | 内文配图 |
| `D:\tools\hermes\skills\baoyu-image-gen\` | 多后端调度（DashScope/MiniMax/Seedream/OpenRouter/GPT-Image-2） |
| `D:\tools\hermes\skills\productivity\external-ai-media-api\scripts\agnes_image.py` | Agnes 生图脚本（agnes-image-2.1-flash，1792x1024） |

### 调研结论（2026-08-03，GitHub API 实测 star）

| 借鉴来源 | Stars | 借鉴的机制 | 落到本方案的模块 |
|---|---|---|---|
| Leonxlnx/taste-skill | 70.8K | 反 slop 检查清单（出图前选锚点、出图后对照检查） | Phase 3 质检门 |
| moonlin1213 muted-zine-poster（改版案例） | 35 | 风格=可替换引擎（色彩/纹理/排版/规避四件套，共用管线） | Phase 1 引擎文件 |
| wuyoscar/GPT-Image2-Skill | 4.1K | Watercolor 分类 gallery 的专业水彩词表 | Phase 2 弹药库词汇 |
| YouMind-OpenLab/nano-banana-pro-prompts | 1.8K | 按场景推荐 prompt 模板库 | Phase 2 弹药库机制 |
| op7418/guizang-social-card-skill | 5.8K | 公众号 21:9 + 1:1 封面对双尺寸协议 | Phase 4 双尺寸封面 |
| lijigang/ljg-skills（「铸」） | 6.7K | 内容→可视化大字卡片 | Phase 5 金句卡 |

### 用户已确认的审美约束（从记忆/会话提取，写引擎时的硬输入）

- ✅ 手绘水彩风：纸纹、笔触、晕染（水彩边缘晕开）
- ✅ 简约感·艺术感·高级感；拒绝过度约束风格，偏好 AI 自由发挥
- ❌ flat 极简线稿、炭黑金海报、美术馆海报风、渐变紫、玻璃拟态、无意义光效、通用 3D 图标感、日系插画模板脸
- 📐 封面标题文字必须居中安全区（微信 1:1 裁切不截断）
- 🖼 内文配图全部宽幅横构图 16:9，prompt 显式指定横向元素锚定构图
- 图片数量：宁多不可少（1500 字散文实测 7 张满意），每逻辑意象块一图，图下跟一行居中说明文字
- 图序与意象对应：正文 → 金句 → 图

### 环境约束（写方案时已核实的硬事实）

- ⚠️ aux vision（vision_analyze 辅助模型）401 不可用 → **图片质检不能依赖 vision 模型**，质检门做在 prompt 层（生成前）+ 人工确认兜底（生成后）
- ⚠️ Hermes 内置 image_generate = Wan2.7-Image（TokenRhythm 中转），reasoning_effort 只收 low~max；中文文字渲染能力需实测（封面标题文字风险点）
- ⚠️ Agnes 401 根因是掩码 key；真实 key 在 Hermes 主配置 .env（约 51 字符）
- ✅ 微信草稿链路已验证（HTML 输入分支 span leaf 样式保留）

---

## 任务拆解

### Phase 0：校准与准备（30 min）

#### Task 0.1：确立主力出图后端

**Objective:** 决定引擎 prompt 的默认口径（Wan2.7-Image 主 vs Agnes 备），不确定就实测。

**Files:**
- 无新文件（产出：决策记录写进 Task 0.3 的 NOTES 文件）

**Step 1:** 用引擎草稿 prompt（见 Phase 1 模板雏形）分别调用：
- 内置 `image_generate`（Wan2.7-Image，portrait 比例）
- Agnes `agnes_image.py`（1792x1024）

**Step 2:** 对比中文标题文字渲染与晕染质感，确定 `default_backend`。

**Expected:** 一个明确的主后端 + 一条备用链路（记录到 NOTES）。

#### Task 0.2：收集审美锚点样例

**Objective:** 从历史已确认的封面/配图中挑 2-3 张用户点头过的图，作为引擎校准参考（存到引擎 refs/）。

**Files:**
- 从用户历史文章目录（会话记录/`cover-image/{topic-slug}/`）找已确认的封面
- 复制到 `andiii-image-style/assets/anchors/`

**Step 1:** session_search 或询问用户：最近哪几张封面是他觉得"对味"的。
**Step 2:** 拷入锚点目录，命名 `anchor-01-watercolor-rain.md + .png` 格式（每张配一个描述文件：为什么对味、用了什么纹理/配色）。
**Expected:** 2-3 组锚点文件，引擎写规则时对照。

#### Task 0.3：创建方案 NOTES 文件

**Objective:** 记录 Phase 0 决策，避免后续实现者重复踩坑。

**Files:**
- Create: `D:\tools\hermes\skills\creative\andiii-image-style\references\NOTES.md`

**Step 1:** 写入：主力后端结论、Wan2.7 中文文字实测结论、锚点清单、Agnes key 读取方式（指向 agnes-image-gen.md）。
**Step 2:** 提交。

```bash
git add -A && git commit -m "docs: image style engine phase0 decisions"
```

---

### Phase 1：风格引擎核心（最大杠杆，2-3 h）

#### Task 1.1：创建 andiii-image-style skill 骨架

**Objective:** skill 目录 + frontmatter + 结构就位。

**Files:**
- Create: `D:\tools\hermes\skills\creative\andiii-image-style\SKILL.md`

**Step 1:** 写 frontmatter：

```yaml
---
name: andiii-image-style
description: Andiii碎碎念公众号配图风格引擎 — 手绘水彩风（纸纹/笔触/晕染）。生成封面/内文配图/金句卡前必须先加载本 skill，按四件套引擎（色彩/纹理/排版/规避）编译四段式 prompt，过质检门后再送图生后端。触发词：封面、配图、金句卡、水彩、生成图。
---
```

**Step 2:** 正文骨架：引擎总述 → 四件套规则 → 四段式编译模板 → 工作流（编译→质检→生成→复查）→ 输出格式。
**Expected:** `skill_view(name='andiii-image-style')` 可正常加载。

#### Task 1.2：色彩引擎

**Objective:** 定义唯一的默认配色策略（暖米纸色系 + 低饱和水彩晕染），含禁用词表。

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 色彩引擎 章节）

**Step 1:** 写规则：
- 基底：米白/浅燕麦/暖灰纸色，占画面 55%-75%
- 晕染色：1-2 个低饱和水彩主色（鼠尾草绿/陶土橙/雾霾蓝/旧黄），以水彩晕染/湿画法存在，非平涂色块
- 墨色：灰墨/暖棕墨，低对比
- **禁用词表**（prompt 中禁止出现）：`flat vector`、`minimalist line art`、`charcoal`、`gold foil`、`gallery poster`、`vivid gradient`、`glassmorphism`、`neon glow`、`3D render`、`anime style`、`matte poster`、`swiss grid`
- 借鉴 muted-zine 的写法：色块占比量化（晕染区 10%-25%，留白 55%-75%），防模型乱来

**Step 2:** 参照 Task 0.2 锚点图校准色值描述（写色名不写 hex，因为模型吃语义色名）。

#### Task 1.3：纹理引擎

**Objective:** 纸纹/笔触/晕染的专业描述词表（中英对照）。

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 纹理引擎 章节）

**Step 1:** 从 GPT-Image2-Skill Watercolor gallery 提取标准词表（实测存在的写法）：
- `cold-pressed paper texture`（冷压纸纹）、`wet-on-wet blooms`（湿接湿晕染）、`granulating pigments`（颗粒沉淀颜料）、`visible brush strokes`（可见笔触）、`watercolor edge bleeding`（水痕边缘渗开）、`paper fiber`（纸纤维）、`subtle paint splatter`（轻微溅墨）、`washed out edges`（边缘洗淡）
**Step 2:** 规定：每个 prompt 必须包含 ≥2 个纹理词 + 1 个纸感词，写进编译模板的 paragraph 1。

#### Task 1.4：排版引擎（封面）

**Objective:** 封面标题文字规则：居中安全区 + 字体 + 字号层级。

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 排版引擎 章节）

**Step 1:** 写规则：
- 标题：中文 ≤10 字，垂直居中，左右各留 ≥15% 安全边距（微信 1:1 裁切不截断）
- 字体：手写感/宋体（prompt 用 `handwritten Chinese calligraphy` 或 `Song-style serif`，视 Wan2.7 实测效果定）
- 副标题/落款：小号灰墨，居下
- 无标题变体：`--text none` 时允许纯视觉（用 baoyu-cover-image 的 text 维度控制）
**Step 2:** 写入双尺寸说明的占位（细节 Phase 4 补）。

#### Task 1.5：规避清单（反 AI 味检查门规则）

**Objective:** 硬规避 + 软规避两级清单，作为质检门的规则源。

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 规避清单 章节）

**Step 1:** 硬规避（命中即 FAIL）：Task 1.2 禁用词表 + 构图雷区（全出血商业海报、logo/CTA、玻璃拟态、3D、霓虹、日系动漫脸、时尚杂志大片感）
**Step 2:** 软规避（命中即 WARN）：`high saturation`、`clean white background`、`stock photo`、`gradient`、`drop shadow`、`bokeh`
**Step 3:** 明确"AI 自由发挥"的边界：引擎只管品味下限，构图/隐喻交给模型自由发挥（用户偏好），只锁配色/纹理/排版三件事。

#### Task 1.6：四段式 prompt 编译模板

**Objective:** 借鉴 zine-poster 的四段式结构，写成可填槽模板。

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# Prompt 编译模板 章节）

**Step 1:** 模板（所有配图统一走这个形状）：

```text
P1 画布与纸感: [画布比例 16:9 或 1:1 或 21:9] 全幅[纸色]底, [留白比例]留白, [纸纹词]+[纹理词], 主体簇位于[位置], 占画面[比例]
P2 主体隐喻: [主题转译的意象]（[锚点类型: 旧照片/剪纸/标本/剪影/水彩晕染物]）, [锚点处理: 边缘渗开/洗淡/纸感]
P3 文字与色彩: [标题文字或说明文字, 字体, 位置], [晕染色1]+[晕染色2] 以[湿画法/晕染条/洗淡照片区]存在, [印刷缺陷/纸缺陷: 轻微溅墨/水痕]
P4 氛围与规避: 安静的、诗意的、日记感的、记忆感的, 避免[规避清单命中项]
```

**Step 2:** 规定：P2 的"主题转译"是唯一自由发挥点（写隐喻，不写场景堆砌）。

#### Task 1.7：引擎自测

**Objective:** 用引擎编译 1 个封面 prompt + 1 个配图 prompt，出图对照引擎检查。

**Files:**
- 输出到 `andiii-image-style\outputs\test\`

**Step 1:** 主题"雨天旧书店"编译 → 过质检（Task 3 未建时人工对照清单）→ 生成。
**Step 2:** 逐条对照四件套：配色达标？纸纹可见？标题居中？无雷区？
**Expected:** 用户确认 1 张对味的图，引擎定稿。

---

### Phase 2：水彩 prompt 弹药库（1-1.5 h）

#### Task 2.1：创建弹药库文件

**Files:**
- Create: `andiii-image-style\references\watercolor-prompt-library.md`

**Step 1:** 结构：`## 主题 | 模板 | 变体槽位`。按用户公众号常见选题分 10 类：
雨天、旧物/旧书、食物/深夜食堂、情绪/独处、城市/通勤、四季、阅读、夜晚/失眠、离别/想念、日常小事。
**Step 2:** 每类 2 个模板（一个偏意象，一个偏物件），都过引擎四段式，标注晕染色主色与纹理词。
**Step 3:** 模板 = 槽位式（`{主体}`、`{色调}`、`{情绪}`），生成时填槽，禁止整段复制（借鉴 zine-poster 的"用结构不用样例词"原则）。

#### Task 2.2：词汇表附录

**Files:**
- Modify: `watercolor-prompt-library.md`（附录：水彩专业词汇中英对照，30 词）

**Step 1:** 从 GPT-Image2-Skill gallery + 实测可用词整理，标注每个词的"生效语境"（哪些词 Wan2.7 吃、哪些 Agnes 吃，Task 0.1 实测后填）。

#### Task 2.3：弹药库实测

**Step 1:** 抽 3 类主题各出 1 图，确认模板可用性，修失效模板。
**Expected:** 10 类 × 2 模板全部过质检门 + 出图可用。

---

### Phase 3：出图质检门（1-1.5 h）

#### Task 3.1：质检脚本 v1

**Objective:** 生成前 prompt 层检查（不依赖 vision）。

**Files:**
- Create: `andiii-image-style\scripts\check_engine_prompt.py`

**Step 1:** 功能（纯标准库）：
- 输入：prompt 文本（stdin 或文件）
- 检查 A（必备要素）：是否含 ≥1 纸感词、≥2 纹理词、画布比例声明、主体位置声明
- 检查 B（硬规避）：命中 Task 1.5 硬规避词 → FAIL
- 检查 C（软规避）：命中软规避词 → WARN
- 输出：`PASS / WARN(n) / FAIL(m)` + 命中明细

```python
#!/usr/bin/env python3
"""andiii-image-style 质检门 v1 — prompt 层检查（无 vision 依赖）"""
import sys, re

PAPER_WORDS = ["cold-pressed paper", "paper texture", "paper fiber", "aged paper", "washi", "水彩纸"]
TEXTURE_WORDS = ["brush stroke", "wet-on-wet", "granulating", "bloom", "bleeding", "splatter", "wash", "晕染", "笔触"]
HARD_BLOCK = ["flat vector", "minimalist line art", "charcoal", "gold foil", "gallery poster",
              "vivid gradient", "glassmorphism", "neon glow", "3d render", "anime style",
              "swiss grid", "matte poster", "cta", "logo"]
SOFT_WARN = ["high saturation", "clean white background", "stock photo", "gradient",
             "drop shadow", "bokeh", "photo-realistic"]

def check(text: str) -> tuple[str, list[str]]:
    issues = []
    if not any(w in text.lower() for w in PAPER_WORDS):
        issues.append(f"FAIL: 缺纸感词（{PAPER_WORDS[:3]}...）")
    if sum(1 for w in TEXTURE_WORDS if w in text.lower()) < 2:
        issues.append("FAIL: 纹理词 < 2 个")
    for w in HARD_BLOCK:
        if w in text.lower():
            issues.append(f"FAIL: 硬规避命中 [{w}]")
    for w in SOFT_WARN:
        if w in text.lower():
            issues.append(f"WARN: 软规避命中 [{w}]")
    return ("PASS" if not any(i.startswith("FAIL") for i in issues) else "FAIL", issues)

if __name__ == "__main__":
    text = sys.stdin.read()
    status, issues = check(text)
    print(status)
    for i in issues:
        print(" ", i)
    sys.exit(0 if status == "PASS" else 1)
```

**Step 2:** 验证：
- `echo "a minimal poster" | python check_engine_prompt.py` → FAIL（无纸感词）
- 用 Task 1.7 的引擎 prompt 测 → PASS
- 用 Task 1.5 雷区样例（含 "flat vector"）测 → FAIL

#### Task 3.2：接入封面/配图流程

**Files:**
- Modify: `andiii-image-style\SKILL.md`（工作流章节：编译 → `python scripts/check_engine_prompt.py` → WARN 必改、FAIL 必改 → 送后端）

**Step 1:** 规定：**PASS 才允许调 image_generate / baoyu 后端**；FAIL/WARN 先改 prompt。
**Step 2:** 出图后的人工复查清单（写在 SKILL.md）：标题居中？晕染在？纸纹在？无雷区？——用户确认制，不自动跳过。

---

### Phase 4：双尺寸封面协议（45 min）

#### Task 4.1：定义双尺寸规则

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 封面双尺寸协议 章节）

**Step 1:** 规则：
- 主封面：21:9（公众号首图，标题居中偏上安全区）
- 分享图：1:1（朋友圈/转发卡片，标题严格居中，左右 ≥15% 边距）
- 同一 prompt 出两版（改画布比例声明），不做后裁切（避免文字被裁）
**Step 2:** 标题安全区量化：1:1 下标题文字垂直居中于画面 40%-60% 区带内。

#### Task 4.2：更新主链路 SKILL.md

**Files:**
- Modify: `D:\tools\hermes\skills\productivity\wechat-content-automation\SKILL.md`

**Step 1:** ② 配图层流程改为：
1. `skill_view(name='andiii-image-style')`（引擎）
2. 编译四段式 prompt → 过 `check_engine_prompt.py` 质检门
3. 封面：一次出 21:9 + 1:1 两版（`cover.png` + `cover-square.png`）
4. 内文配图：每意象块一图，16:9，过质检门
5. 图下说明文字行（已有约定）
**Step 2:** 更新 frontmatter related_skills 加 `andiii-image-style`。

#### Task 4.3：验证双尺寸

**Step 1:** 实测一篇：出两版封面，检查 1:1 版标题完整（用户视觉确认）。
**Expected:** 用户确认 21:9 与 1:1 双版均可用。

---

### Phase 5：文末金句卡（45 min）

#### Task 5.1：金句卡规格

**Files:**
- Modify: `andiii-image-style\SKILL.md`（# 金句卡 章节）

**Step 1:** 规格：
- 尺寸 1:1（插入文末）或 9:16（独立分发备用）
- 内容：正文 1 句金句（≤20 字）+ 落款「——Andiii碎碎念」（沿用记忆中的落款约定）
- 视觉：水彩底 + 手写感大字 + 大留白（>60%），复用引擎四件套
- 引用规范：金句必须出自正文原句，不得编造（写作雷区：不编细节）

#### Task 5.2：接入写作流程末端

**Files:**
- Modify: `wechat-content-automation\SKILL.md`（① 写作层末端追加步骤）

**Step 1:** 正文定稿后：从文中挑 1-2 句最有嚼劲的 → 编译金句卡 prompt → 质检 → 生成 → 插入文末（`就到这里，下次见。` 之前）。
**Step 2:** 金句卡也进 `--cover` 上传链路（正文图片自动上传已支持本地相对路径）。

#### Task 5.3：验证

**Step 1:** 实测一篇含金句卡，检查：文字无错字（Wan2.7 中文渲染风险点）、构图符合引擎、插入位置正确。

---

### Phase 6：集成收尾（1 h）

#### Task 6.1：更新 inline-illustration-workflow.md

**Files:**
- Modify: `wechat-content-automation\references\inline-illustration-workflow.md`

**Step 1:** 加入：引擎加载、质检门、双尺寸、金句卡的引用与调用姿势；保留现有"python 锚点 replace 插图片"踩坑记录。

#### Task 6.2：更新 theme-routing.md 图片规范

**Files:**
- Modify: `wechat-content-automation\references\theme-routing.md`

**Step 1:** 图片规范章节加一行：所有配图必须经 `andiii-image-style` 引擎编译 + 质检门，指向引擎 SKILL.md。

#### Task 6.3：端到端实测

**Step 1:** 完整跑一篇：选题 → 写作 → 封面双尺寸 → 内文配图（≥4 张）→ 金句卡 → gzh-design 排版 → validate_gzh_html.py（0 ERROR）→ dry-run → 推草稿箱。
**Step 2:** 用户验收：封面标题居中、配图对味、金句卡无错字、草稿箱内容完整。
**Expected:** 全链路一次通过，用户确认后 Phase 6 完成。

---

## 验证总纲

| 层 | 验证方式 | 通过标准 |
|---|---|---|
| 引擎规则 | 人工逐条对照锚点图 | 色彩/纹理/排版三件事全部可执行 |
| 质检脚本 | 3 组样例（雷区/引擎/空） | FAIL 例必 FAIL，PASS 例必 PASS |
| 弹药库 | 10 类抽 3 类实测 | 出图可用且过质检门 |
| 双尺寸 | 1 篇实测 | 1:1 标题完整居中 |
| 金句卡 | 1 篇实测 | 文字正确、位置正确 |
| 端到端 | 全链路 1 篇 | 推草稿箱成功，用户确认 |

## 风险与权衡

| 风险 | 影响 | 缓解 |
|---|---|---|
| Wan2.7-Image 中文标题渲染差（封面文字变形/错字） | 封面返工 | Task 0.1 实测；备选：Agnes 1792x1024、或封面标题改用 baoyu-cover-image `--text none` + 排版层叠文字（gzh-design 已有能力） |
| 无 vision 模型 → 图片质检只能靠 prompt 层 + 人工 | 雷区偶发漏网 | 质检门锁 prompt 层；出图后人工复查清单兜底；雷区词表随实测持续补（Phase 3 后迭代） |
| 引擎规则过死 → 违背用户"偏好 AI 自由发挥" | 图变套路化 | 引擎只锁配色/纹理/排版三件事，P2 隐喻与构图完全自由；规避清单只拦"雷区"不拦"风格" |
| 弹药库模板被整段复制 → 图同质化 | 读者审美疲劳 | 模板槽位化 + 每图必改 P2 隐喻；质检门检查 P2 非空 |
| 金句卡中文手写字体渲染失败 | 错字尴尬 | 字体用 Wan2.7 实测可行的描述；失败则回退宋体/无字体变体 |

## 开放问题

1. **封面标题进图内 vs 排版层叠文字**：Wan2.7 实测后决定。若图内文字不稳，走"图内只出意象 + gzh-design 排版叠标题"，双尺寸协议需同步调整。
2. **金句卡数量**：每篇 1 张 vs 2 张？（先 1 张起步，用户反馈后加）
3. **弹药库是否需要用户参与选题**：10 类主题是否覆盖用户实际选题分布？首次实测后按真实选题增补。
4. **引擎是否做"风格切换"接口**（喜茶风/潦草风将来要换引擎）：本次只做手绘水彩一版，但四件套结构天然支持复制成 `andiii-image-style-heytear` 等新引擎——本期不做，留结构。
