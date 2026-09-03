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
type: enum
title: 离职运营人员
page_key: operation_id
domain: operation
aliases:
- 已删除运营人员
anchors:
- operation_id
---
# 离职运营人员

TopFlag 检查使用 deleted='Y' 且 enable='Y' 的 operation_id 集合；字段名 deleted 是系统删除/离职标记。

```ground:enum
enum: operation_id
fields:
- operation_user.operation_id
- operation_user.deleted
- operation_user.enable
values:
  Y:
    label: 已删除/离职
  N:
    label: 未删除
```

## 关联
- [[operation_user|operation_user]]
