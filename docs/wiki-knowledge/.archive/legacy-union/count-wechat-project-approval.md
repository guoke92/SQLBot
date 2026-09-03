---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 企微项目审批有多少
page_key: count-wechat-project-approval
domain: 项目管理
anchors:
- wechat_project_approval_apply
---
# 企微项目审批有多少

问法：企微项目审批有多少

```ground:pattern
pattern: count-wechat-project-approval
question: 企微项目审批有多少
sql: SELECT COUNT(DISTINCT id) AS cnt FROM wechat_project_approval_apply WHERE enable
  = 'Y'
verification: PENDING_VALIDATION
```

## 关联
- [[wechat_project_approval_apply]]
