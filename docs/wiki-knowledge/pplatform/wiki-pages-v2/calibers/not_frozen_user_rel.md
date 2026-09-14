---
type: caliber
title: 未冻结用户关联
page_key: not_frozen_user_rel
domain: 平台内部服务对接
status: draft
aliases:
  - 未冻结关联口径
  - 权限关系过滤
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
belong: calibers
---

「未冻结用户关联」是查询 [[sys_cust_user_rel]] 关系时的过滤条件：`is_freeze = 'N'`。它把经办人冻结状态机（见 [[operator_freeze_flow]]）的当前取值翻译成查询语义——被冻结的关系仍然保留在表中，但不应参与用户列表与权限判定。该口径通常与联系人口径 [[valid_person]] 一起使用。

## 需求背景
冻结是运营侧的临时处置手段，关系数据需要保留以便解冻；如果把冻结实现为删除，将无法恢复且会丢失角色与产品配置，因此在读取侧统一附加未冻结条件更安全。

## 版本演进
- v0.1（本页）：口径谓词来自代码语义分析。

```ground:caliber
name: 未冻结用户关联
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 查询有效用户关联关系
evidence: "code_path:PlatFormUserApplication.java:listCompanyUser"
```