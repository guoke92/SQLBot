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
title: 运营关联必须使用 operation_id
page_key: 运营关联必须使用-operation_id
domain: operation
field_targets:
- operation_user.operation_id
- wec_project_operation_rel.op_contact_a
- wec_project_cust_operation_rel.op_contact_a
---
# 运营关联必须使用 operation_id

业务关系的对接人字段与 operation_user.operation_id 比较，不用 operation_user.id；A 字段可等值匹配，B 字段可能是 JSON 数组。

```ground:rule
rule: operation-id-is-business-key
field_targets:
- operation_user.operation_id
- wec_project_operation_rel.op_contact_a
- wec_project_cust_operation_rel.op_contact_a
impact: query_constraint
content: 业务关系的对接人字段与 operation_user.operation_id 比较，不用 operation_user.id；A 字段可等值匹配，B
  字段可能是 JSON 数组。
scope: 运营覆盖关联、离职检查、运营组别同步
```

## 关联
- [[operation_user]]
- [[wec_project_cust_operation_rel]]
- [[wec_project_operation_rel]]
