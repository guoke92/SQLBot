---
type: process
title: 联系人账号状态
page_key: process.person_account_status
domain: 客户联系人管理
status: draft
aliases:
  - 联系人 status 状态机
  - 账号激活流程
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code_path:CustPersonApplication.java:ifNessaryFrzAdm"
  - "code_path:CustPersonApplication.java:simpleChangePerson"
contract_version: "0.1"
---

联系人账号状态描述一个联系人记录从「新增/待激活」到「生效」，以及因管理员变更被「冻结」的过程，落在 [[tables/cust_person_info]] 的 `status` 字段上。该状态与逻辑删除标识 `enable` 相互独立：被冻结的记录仍是启用记录，查询需结合 [[calibers/valid-person]] 的判定。

## 需求背景

管理员首次生效、经办人激活都体现为 `EFFECT`；当企业管理员被更换，或经办人在简易认证流程中变更手机号时，旧记录必须被冻结而不是删除，以保证历史可追溯且同一时间只有一个有效管理员（见 [[rules/admin-change-freeze]]、[[rules/admin-uniqueness]]）。

```ground:process
process: 联系人账号状态
field: cust_person_info.status
states:
  - value: ADD
    label: 待激活/新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: N
    label: "未知（DB中存在1条，代码未声明）"
    source: db_dist
transitions:
  - from: ADD
    event: 管理员生效
    to: EFFECT
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm"
  - from: EFFECT
    event: 管理员变更冻结旧管理员
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm"
  - from: EFFECT
    event: 简易认证变更手机号冻结旧管理员
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:simpleChangePerson"
```

## 版本演进

- v0：首次登记。DB 实际值中存在 1 条 `N`，代码枚举未声明该值，暂记为未知状态，待确认是否历史脏数据。

相关：[[tables/cust_person_info]]、[[rules/admin-change-freeze]]、[[calibers/valid-person]]。