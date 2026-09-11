---
type: process
title: 企业客户状态机（cust_company_info.cust_status）
page_key: processes/cust_company_info_cust_status
domain: 企业画像
status: draft
aliases:
  - CustStatusEnum 流程
  - 企业客户状态流转
  - cust_status
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

# 企业客户状态机（cust_company_info.cust_status）

该状态机描述[[tables/cust_company_info]]中 `custStatus` 字段（对应 `CustStatusEnum`）的取值与流转，刻画企业作为「客户」的生命周期：新增 → 生效 → 冻结／解冻 → 注销。

主干是：建档认证成功后由 `ADD`（新增）进入 `EFFECT`（生效），入口方法为 `updateCustBuildStatus`。生效后的运营动作有三类：冻结（`freeze`）与解冻（`unfreeze`）在 `EFFECT` 与 `FREEZE` 之间往返；注销（`diable`）把 `EFFECT` 推向 `WRITEOFF`。`WRITEOFF` 有一条自环迁移：注销时冻结企业下所有用户（`custStatusOperator`），记录在案但不改变企业自身状态。

本状态机是[[calibers/company_effect]]（企业生效口径）的组成条件之一：只有 `cust_status = 'EFFECT'` 且认证成功、主数据、逻辑有效的企业才进入生效查询集合。它与[[processes/cust_company_info_cust_build_status]]的衔接点即 `ADD → EFFECT` 这一步。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据。待业务补充：`FAILURE`（失败）状态由哪些业务动作写入、达到该状态后能否恢复。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 企业客户状态
field: cust_company_info.cust_status
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
  - value: FAILURE
    label: 失败
    source: code_enum
transitions:
  - from: ADD
    event: 建档认证成功
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java:freeze
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:unfreeze
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:diable
  - from: WRITEOFF
    event: 注销时冻结企业下所有用户
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:custStatusOperator
```

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[concepts/company_profile]]、[[calibers/company_effect]]。