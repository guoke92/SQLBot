---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:op-user-coverage@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: top_flag 不在运营人员表
page_key: top_flag-不在运营人员表
domain: operation
field_targets:
- operation_user.operation_id
- tenant_project.top_flag
---
# top_flag 不在运营人员表

operation_user 没有 top_flag。置顶问数必须落在 tenant_project / wec_* / cust_project_rel。

```ground:rule
rule: top-flag-not-on-op-user
field_targets:
- operation_user.operation_id
- tenant_project.top_flag
impact: query_constraint
content: operation_user 没有 top_flag。置顶问数必须落在 tenant_project / wec_* / cust_project_rel。
scope: 置顶项目、离职置顶
```

## 关联
- [[operation_user]]
- [[tenant_project]]
