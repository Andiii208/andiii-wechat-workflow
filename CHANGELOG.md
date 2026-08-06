# Changelog

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
