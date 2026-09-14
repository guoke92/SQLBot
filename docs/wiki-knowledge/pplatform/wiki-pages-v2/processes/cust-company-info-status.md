---
type: process
title: 企业生命周期状态机（cust_company_info.cust_status）
page_key: cust-company-info-status
domain: 企业变更与运营变更
status: draft
aliases: [企业状态, CustStatusEnum, 企业生命周期]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code_path:CustCompanyInfoApplication.java:freeze
  - code_path:CustCompanyInfoApplication.java:unfreeze
  - code_path:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
belong: processes
---

企业生命周期状态由 `CustStatusEnum` 定义，挂在 [[tables.cust_company_info]] 的 `cust_status` 上：新增/待提交（`ADD`）、变更中（`CHANGE`）、已生效（`EFFECT`）、已冻结（`FREEZE`）、已注销（`WRITEOFF`）。冻结、解冻、注销分别由 `CustCompanyInfoApplication.freeze`、`unfreeze`、`diable` 驱动并调用 `custStatusSync` 落状态。`CHANGE` 是变更在途的判定依据，见 [[calibers.company-change-on-way]] 与 [[rules.change-on-way-company]]。

## 需求背景

变更链路只依赖 `CHANGE` 这一个中间态来判断「企业是否已有在途变更」；冻结与注销属于企业维度的运营动作，与变更单状态 [[concepts.change-status]] 分属不同层面：前者描述企业生命周期，后者描述单次变更申请的审批进度。

## 版本演进

v0.1：首次登记，状态取值与迁移均来自代码枚举与状态同步调用点。

```ground:process
name: 企业生命周期状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待提交
    source: code_enum
  - value: CHANGE
    label: 变更中（存在在途变更）
    source: code_enum
  - value: EFFECT
    label: 已生效
    source: code_enum
  - value: FREEZE
    label: 已冻结
    source: code_enum
  - value: WRITEOFF
    label: 已注销
    source: code_enum
transitions:
  - from: EFFECT
    event: freeze
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze + custStatusSync(FREEZE->CustStatusEnum.FREEZE)"
  - from: FREEZE
    event: unfreeze
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze + custStatusSync(UNFREEZE->CustStatusEnum.EFFECT)"
  - from: EFFECT
    event: diable（注销）
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable + custStatusSync(DISABLE->CustStatusEnum.WRITEOFF)"
```