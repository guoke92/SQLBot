---
type: process
title: 客户角色状态机（cust_role_info.status）
page_key: cust_role_status_machine
domain: 客户角色与端口
status: draft
aliases:
  - 角色状态流转
  - 角色冻结解冻注销
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:freeze
  - code_path:CustRoleApplication.java:unFreeze
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
  - code_path:CustCompanyIfoEnchanceService.java:setCustCompany
contract_version: "0.1"
belong: processes
---

客户角色状态机描述 ADD / EFFECT / FREEZE / WRITEOFF 之间的迁移路径，状态取值见 [[cust_role_status]]，载体表见 [[cust_role_info]]。

## 需求背景

角色创建（addRoleInfo）后落在 ADD，等待业务激活；冻结、解冻、注销分别把状态置为 FREEZE、EFFECT、WRITEOFF。批量按企业更新状态时跳过已 WRITEOFF 的记录，避免“复活”已注销角色（见 [[role_status_freeze_logout]]）。已安装状态的存量分布显示业务上绝大多数角色处于 ADD（34867）与 EFFECT（19791），FREEZE/WRITEOFF 为少数态。

## 版本演进

- v0（draft）：依据代码路径 + db_dist 首次成页；updateStatusByCustCompany 的目标状态为“传入状态”，属于参数化迁移，未在锚点块中枚举具体目标值。

```ground:process
name: 客户角色状态机
field: cust_role_info.status
states:
  - value: ADD
    label: 未激活
    source: code_enum
  - value: EFFECT
    label: 已激活
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: db_dist
  - value: WRITEOFF
    label: 注销
    source: db_dist
transitions:
  - from: "*"
    event: freeze
    to: FREEZE
    evidence: "code_path:CustRoleApplication.java:freeze -> operatorCustRoleStatus(role, CustRoleStatusConstant.FREEZE)"
  - from: FREEZE
    event: unFreeze
    to: EFFECT
    evidence: "code_path:CustRoleApplication.java:unFreeze -> operatorCustRoleStatus(role, CustRoleStatusConstant.EFFECT)"
  - from: "*"
    event: logout
    to: WRITEOFF
    evidence: "code_path:CustRoleApplication.java:logout -> operatorCustRoleStatus(role, CustRoleStatusConstant.WRITEOFF)"
  - from: "*"
    event: updateStatusByCustCompany
    to: 传入状态
    evidence: "code_path:CustRoleApplication.java:updateStatusByCustCompany，跳过已有 WRITEOFF 的记录"
  - from: 无
    event: addRoleInfo
    to: ADD
    evidence: "code_path:CustCompanyIfoEnchanceService.java:setCustCompany 中 custRoleInfoDO.setStatus(CustStatusEnum.ADD.getDictKey())"
```