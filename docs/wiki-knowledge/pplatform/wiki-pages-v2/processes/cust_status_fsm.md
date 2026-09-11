---
type: process
title: 企业经营状态机（cust_status）
page_key: process.cust_status_fsm
domain: 数据权限与组织
status: draft
aliases: [企业经营状态机, cust_status, CustStatusEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_company_info.cust_status
---

企业经营状态机，承载于 [[tables/cust_company_info]].cust_status，取值来自代码枚举 CustStatusEnum：ADD / EFFECT / FREEZE / WRITEOFF / CHANGE。建档成功会把企业从 ADD 推进到 EFFECT（见 [[processes/cust_build_status_fsm]]）；冻结与解冻分别联动冻结/解冻企业管理员（见 [[calibers/company_admin]]）；注销前必须先冻结企业下全部用户，见 [[rules/writeoff_freeze_all_users]]。

企业信息变更会进入 CHANGE（变更在途），由 CustPersonApplication#adminChangeSaveOrUpdate 触发。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustCompanyInfoApplication 与 CustPersonApplication。

## 版本演进

v0：依据 code 证据建模。

```ground:process
name: 企业经营状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待生效
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更在途
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功生效
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java#updateCustBuildStatus
  - from: EFFECT
    event: 冻结企业（同时冻结企业管理员）
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java#freeze
  - from: FREEZE
    event: 解冻企业（同时解冻企业管理员）
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java#unfreeze
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator
  - from: WRITEOFF
    event: 注销前先冻结企业下全部用户
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java#custStatusOperator(freezeCustAllUsers)
  - from: EFFECT
    event: 发起企业信息变更
    to: CHANGE
    evidence: code_path:CustPersonApplication.java#adminChangeSaveOrUpdate
```