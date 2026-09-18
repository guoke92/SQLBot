---
type: dict
title: wechat_project_approval_apply.db_tenant_code
page_key: wechat_project_approval_apply__db_tenant_code
belong: dicts
status: draft
anchors: [wechat_project_approval_apply.db_tenant_code]
sources: ['database_profile:wechat_project_approval_apply.db_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [wechat_project_approval_apply]
---

# wechat_project_approval_apply.db_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `wechat_project_approval_apply.db_tenant_code`，表页 [[tables/wechat_project_approval_apply]]。

## 取值

```ground:dict
dict: wechat_project_approval_apply__db_tenant_code
fields: [wechat_project_approval_apply.db_tenant_code]
values:
  base: {trust: proposed}
triage: hold
needs_review: true
```
