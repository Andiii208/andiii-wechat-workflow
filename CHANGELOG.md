# Changelog

## v0.3.0 — 2026-08-20 同步体系审计修复

全面审计仓库↔Hermes runtime 双向一致性后落地:聚合引擎落仓、硬编码路径根除、同步脚本盲区补全。

### 数据安全(最重要)
- **`ai-image-style-engine`(聚合引擎母版)落仓**——此前完全在同步体系之外(`andiii-*` 前缀匹配扫不到),含 3 份 runtime 独有活文档推回仓库:`heytear-real-style.md`(2026-08-05 用户拍板的真实喜茶风配方)、`external-skill-porting.md`、`tait-crt-interface.md` + `batch_gate_check.py`
- `references/learnings/design-image-studio-anti-slop.md` 纳入 REF_MAP 注入(此前是仓库↔runtime 双向孤儿,永不部署也永不推回)

### 可移植性
- **6 个引擎 SKILL.md 共 7 处硬编码绝对路径 `D:/tools/andiii-wechat-workflow/...` 改为相对引用**——引擎不再依赖仓库存在于本机固定路径;`design-reasoning.md` 统一指向 Hermes 注入副本(仓库权威源仍为顶层 `references/`)

### 同步脚本(sync_to_hermes.sh / push_back_to_repo.sh)
- sync:新增 `ai-image-style-engine` 整目录同步段(非 andiii-* 前缀,原自动发现漏掉)
- sync:复核(verify)补盲区——WCA 32 个 references、writing references、GZH assets/docs/README/LICENSE/CONTRIBUTING、AIE 全部此前"复制但不复核"的文件
- sync:gzh-design-skill 同步范围扩展——assets/theme-previews/、docs/、docs/gallery/、README/README.en/LICENSE/CONTRIBUTING(此前快照有但 sync 永不管理,无声漂移)
- push_back:DIR_PAIRS 加 ai-image-style-engine;INJECTED/FILE_PAIRS 补 design-reasoning + learnings 注入副本(防误报"仓库缺失");find 覆盖 `.html`(gzh-design gallery/theme-previews 反向可推回)

### CI
- py_compile 补 4 个此前漏检脚本:`check_crt_prompt.py`、`finalize_crt.py`(CRT 质检门)、`clean_lesson2.py`、`sync_theme_routing_fix.py` + 新落仓的 `batch_gate_check.py`

## v0.2.0 — 2026-08-06 工程加固

依据第三方 Review(2026-08-06)落地,将仓库从"配置备份"升级为"可验证、可回滚、CI 守护的发布源"。

### 安全
- LICENSE(MIT) + NOTICE.md(上游许可证全核实:gzh-design AGPL-3.0、baoyu-skills/muted-zine/human-writing/gc-minimal MIT、wechatDownload 待核实)
- gitleaks 全历史扫描(25 commits 无泄露);脱敏 `wechat-ecosystem-projects-2026-08.md` 真实公网 IP
- GitHub Actions:gitleaks 全历史扫描每次 push 自动跑
- `.gitignore` 新增 `.local/`(同步备份/本地状态)

### 部署(scripts/sync_to_hermes.sh 重写)
- 自动收集引擎清单(新增引擎无需改脚本)
- `HERMES_HOME` 环境变量可覆盖
- 覆盖前自动备份到 `.local/backup/<ts>/`(保留相对路径结构,防同名覆盖)
- mtime 活文档守卫(仓库→Hermes 单向,拦截未推回活文档)
- 拷贝失败即失败(不再静默吞错)
- `--prune` 陈旧文件清理(带活文档守卫,删除前备份)
- 同步后逐文件 cmp 复核

### 脚本修复
- `check_engine_prompt.py`:退出码三态化(0 PASS/1 FAIL/2 WARN/3 错误)+ `--format json` + 负向豁免升级("不要使用高饱和"不再误报)
- `crop_image.py`:补 LANCZOS resize(`--width 900`)、EXIF orientation、参数校验、`.jpg` 扩展名强制、原子写、输出验证
- 新增 `scripts/validate_repo.py`:broken link / SKILL references / secret pattern / frontmatter 版本漂移校验

### 文档与一致性
- README 修正:多引擎架构、16:9→2.35:1、404 引用(`references/wechat-pipeline.md`)移除、依赖内外分类
- 版本对齐:`andiii-image-style` 1.0.0→1.5.0(与 NOTES 一致)、`andiii-writing-style` 1.1.0→1.2.0
- `wechat-content-automation` SKILL.md:运行时安装细节外移指向 setup-notes.md
- Hermes 侧 10 个实战活文档推回仓库(references 补齐,消除仓库/运行副本分叉)

### 已知限制
- 质检门词表为全引擎共用,未做 per-engine profile(石墨/针管笔等非纸张风格需要时再引入)
- 负向豁免为全文级:同一词在豁免句+正向句同时出现时整体豁免
