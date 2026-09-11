---
type: process
title: 经办人产品关联冻结状态机（sys_cust_user_rel.is_freeze）
page_key: process.operator_freeze
domain: 平台内部服务对接
status: draft
aliases:
  - 经办人冻结
  - is_freeze
  - 授权冻结状态
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[经办人产品关联冻结状态]
  - semantic:field_semantics[sys_cust_user_rel.is_freeze]
contract_version: "0.1"
---

经办人与产品之间授权关系的冻结状态，只有「未冻结 / 已冻结」两态，由运营侧的冻结与解冻操作驱动。

## 需求背景

冻结影响下游联系人可用性：经办人无产品权限时 [[tables/cust_person_info]].enable 被置 'N'，解冻时恢复 'Y'（见 [[rules/operator_permission_disable]]）。冻结状态取值语义与 UserFreezeEnum 对齐。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页；语义分析中该状态机的转换列表末尾存在截断，仅收录完整可读的转换（见文末 REVIEW）。

```ground:process
name: 经办人产品关联冻结状态
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 未冻结
    source: code_enum
  - value: Y
    label: 已冻结
    source: code_enum
transitions:
  - from: N
    event: "冻结经办人（operationType=FREEZE）"
    to: Y
    evidence: "code_path:CustCompanyInfoApplication 同仓 PlatFormUserApplication.java#freezeOrThawOperatorUser(sysCustUserRelDO.setIsFreeze(\"Y\"))"
  - from: Y
    event: "解冻经办人（operationType=THAW）"
    to: N
    evidence: "code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser(THAW 分支 setIsFreeze(\"N\"))"
```