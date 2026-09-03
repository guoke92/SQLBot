---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: pattern
title: 已通过立项的项目清单
page_key: approved-initiation-list
domain: 项目审批
anchors:
- wechat_project_approval_apply
---
# 已通过立项的项目清单

问法：已通过立项的项目清单

```ground:pattern
pattern: approved-initiation-list
question: 已通过立项的项目清单
sql: SELECT sp_no, project_approval_name, sp_pass_time, bussiness_manager FROM wechat_project_approval_apply
  WHERE act_procinst_status = '2' AND enable = 'Y' ORDER BY sp_pass_time DESC
verification: PENDING_VALIDATION
```

## 关联
- [[wechat_project_approval_apply]]
