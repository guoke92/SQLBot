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
title: 在职运营人员
page_key: deleted
domain: operation
aliases:
- 有效运营人员
anchors:
- deleted
---
# 在职运营人员

operation_user.deleted='N' 且 enable='Y' 的人员；同步任务会把接口未返回且当前启用未删除记录标记 deleted='Y'。

```ground:enum
enum: deleted
fields:
- operation_user.deleted
- operation_user.enable
values:
  N:
    label: 未删除/在职
  Y:
    label: 已删除/离职
```

## 关联
- [[operation_user|operation_user]]
