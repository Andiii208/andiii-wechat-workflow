# NOTES — 引擎建设决策记录

## Phase 0 决策（2026-08-03）

### 主力后端：Wan2.7-Image（内置 image_generate）✅ 定案
- 中文标题渲染**实测通过**（"雨天旧书店"五字清晰准确，无错字乱码）
- 水彩质感实测到位（纸纹/晕染/笔触全部呈现）
- 封面走**图内文字**方案（不用排版层叠文字备选）

### 备选后端：Agnes（agnes-image-2.1-flash）
- ⚠️ 直连 `apihub.agnes-ai.com` **超时**（WinError 10060，墙外 API）
- 需要走 CLIProxyAPI 中转（Docker，TCP 转发绕 Clash）才能测
- 暂缓，非必需

### 视觉质检：小米 MiMo v2.5（auxiliary.vision）
- provider=xiaomi, model=mimo-v2.5（Hermes `_PROVIDER_VISION_MODELS` 写死此模型）
- **坑**：`.env` 必须用官方 base_url `https://api.xiaomimimo.com/v1`（OpenAI 兼容）
- **坑**：Token Plan 的 `tp-` key 与 sk key 不能混用；base_url 指向 token-plan-cn 时 sk key 会 401
- **坑**：Hermes 实际读 `D:\tools\hermes\.env`（不是 `~/.hermes/.env`）；改 env 后需重启应用才生效（进程缓存）
- 视觉可用后，出图复查可部分自动化（但仍以用户确认为准）

### 锚点图
- 待补充：用户已确认的对味封面 2-3 张 → `assets/anchors/`（每张配描述 md）

## 引擎版本
- v1.0.0：四件套 + 四段式模板 + 弹药库 10 类 + 质检门脚本 + 双尺寸 + 金句卡
