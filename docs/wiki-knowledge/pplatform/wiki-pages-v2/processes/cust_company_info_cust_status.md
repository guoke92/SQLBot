---
type: process
title: 企业客户生命周期状态机 (cust_company_info.cust_status)
page_key: cust_company_info_cust_status
domain: 企业变更与运营变更
status: draft
aliases: [企业生命周期状态机, cust_status, 企业状态流转]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustChangeApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: processes
---

本状态机描述企业客户主体（[[cust_company_info]]）的生命周期流转，其中 `CHANGE`（变更中）是与本主题直接相关的态：企业一旦发起变更，主体被打上 `CHANGE`，变更入口与页面跳转随之变化（[[company_in_change]]、[[change_on_way]]）。

注意本状态机的 `status` 与企业准入审核状态 `check_status` 是两条独立的轴，见 [[change_status]]。

## 需求背景

企业既有日常运营态（生效/冻结/注销），也有变更在途态。把「变更中」建模为企业级状态而非仅记录级状态，是为了让入口、待办页、重复发起校验都能用同一字段判定，避免并发发起多次变更。

## 版本演进

v0.1：首次抽取五个状态与四条迁移；文档主张「已冻结或已注销不允许变更」未被代码覆盖，见 [[change_precheck]]。

```ground:process
name: 企业客户生命周期状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 待建档/新增
    source: code_const
  - value: EFFECT
    label: 已生效
    source: code_const
  - value: FREEZE
    label: 已冻结
    source: code_const
  - value: WRITEOFF
    label: 已注销
    source: code_const
  - value: CHANGE
    label: 变更中
    source: code_const
transitions:
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java#freeze→custStatusOperator(CustStatusOperatorConstant.FREEZE)"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#unfreeze→custStatusOperator(UNFREEZE)"
  - from: EFFECT
    event: 注销
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java#diable→custStatusOperator(DISABLE)"
  - from: EFFECT
    event: 发起企业变更（运营中台同步变更状态）
    to: CHANGE
    evidence: "code_path:CustChangeApplication.java#getRedirectPage(判定 cust_status=CHANGE) + CustCompanyInfoApplication.java#doIfNecessaryChange(operCustFacade.change)"
```

相关页面：[[cust_company_info]]、[[company_in_change]]、[[change_on_way]]、[[change_status]]、[[cust_company_info_cust_build_status]]。