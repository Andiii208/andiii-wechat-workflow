# Security

## 报告安全问题

本仓库为个人工作流规则仓库,公开托管于 GitHub。若发现安全相关问题(如凭据泄露、可疑代码),请通过以下方式联系:

- GitHub Issues(公开):<https://github.com/Andiii208/andiii-wechat-workflow/issues>
- 或直接联系仓库所有者

## 凭据纪律

- 本仓库**禁止提交**任何真实凭据:微信 AppSecret / AppID、API Key、Token、个人私密素材。
- 占位符规范:`WECHAT_APP_SECRET_REDACTED`、`REDACTED`、`your_app_secret`。
- 凭据只存在于本机 `.env` / `~/.baoyu-skills/.env`(gitignored)。

## 已启用防护

- GitHub Secret Scanning / Push Protection(仓库设置)
- CI:gitleaks 全历史扫描 + `scripts/validate_repo.py` secret pattern 快扫,推送自动执行
- 历史泄露响应流程见 `skills/wechat-content-automation/references/secret-leak-response.md`
