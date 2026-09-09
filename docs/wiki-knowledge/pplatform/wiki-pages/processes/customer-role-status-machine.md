---
type: process
title: 客户企业角色状态机
page_key: customer-role-status-machine
belong: processes
domain: 客户角色与数据权限组织
status: published
aliases:
  - 客户角色状态机
  - cust_role_info.status
oid: 1
sources:
  - db_dist
  - code_enum
  - code_path
contract_version: "0.1"
field_targets: [cust_role_info.status]
scope:
  databases: [lowcode_pplatform]
---

本状态机描述客户企业角色 cust_role_info.status 的取值与流转规则，覆盖新增、生效、冻结、注销状态。

## 需求背景

支撑角色生命周期管理，冻结、解冻与注销操作由 CustRoleApplication 实现。

## 版本演进

初始语义抽取版本，后续需补充完整状态流转和审批关联。

```ground:process
name: 客户企业角色状态机
field: cust_role_info.status
states:
  - value: ADD
    label: 新增/初始
    source: db_dist
  - value: EFFECT
    label: 生效
    source: code_enum|db_dist
  - value: FREEZE
    label: 冻结
    source: code_enum|db_dist
  - value: WRITEOFF
    label: 注销
    source: code_enum|db_dist
transitions:
  - from: EFFECT
    event: freeze
    to: FREEZE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:freeze()
  - from: FREEZE
    event: unFreeze
    to: EFFECT
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:unFreeze()
  - from: EFFECT
    event: logout
    to: WRITEOFF
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustRoleApplication.java:logout()
```

相关页面：[[cust_role_info]] [[customer-role-status]]