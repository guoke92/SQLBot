---
type: process
title: 客户状态机（cust_status）
page_key: customer_status_machine
domain: 企业建档与认证
status: draft
aliases:
  - 客户生命周期状态机
  - 生效冻结注销流转
oid: 1
scope:
  databases: []
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:freeze
  - code:CustCompanyInfoApplication.java:unfreeze
  - code:CustCompanyInfoApplication.java:diable
  - db:cust_company_info.cust_status
contract_version: "0.1"
---

本流程描述 `cust_company_info.cust_status`（见 [[customer_status]]）的流转，表达企业作为客户实体的经营状态：新增（`ADD`）、生效（`EFFECT`）、冻结（`FREEZE`）、注销（`WRITEOFF`），另有一个数据库分布值“变更中”（`CHANGE`）。

该状态机的入口是认证成功：认证状态迁移到 `BUILD_SUCCESS` 时联动置为 `EFFECT`，见 [[enterprise_auth_status_machine]] 与 [[auth_success_sets_customer_effective]]。生效之后可被冻结、解冻、注销；冻结与注销会连带影响该企业下的用户，见 [[freeze_company_freezes_admin]] 与 [[writeoff_company_freezes_all_users]]。生效企业还需同时满足认证状态与启用标记，口径见 [[effective_company]]。

```ground:process
name: 客户状态机
field: cust_status
states:
  - value: ADD
    label: 新增
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
    label: 变更中
    source: db_dist
transitions:
  - from: ADD
    event: 认证成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```

## 需求背景

暂无需求文档主张。本状态机与认证状态机（[[enterprise_auth_status_machine]]）通过“认证成功 → 生效”这一条联动规则耦合，其余事件（冻结/解冻/注销）独立于认证流程。

## 版本演进

- v0.1：依据语义分析建立状态机页，登记 5 个状态（4 个代码枚举值 + 1 个数据库分布值）与 4 条流转及其代码证据。