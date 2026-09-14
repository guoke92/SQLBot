---
type: process
title: 客户生命周期状态机（cust_company_info.cust_status）
page_key: cust_status_machine
domain: 平台内部服务对接
status: draft
aliases:
  - 客户生命周期状态
  - cust_status
  - 企业状态机
oid: 1
scope:
  databases: []
sources:
  - semantic:state_machines[客户生命周期状态]
  - semantic:field_semantics[cust_company_info.cust_status]
contract_version: "0.1"
belong: processes
---

企业作为「客户」的生命周期状态：新增、变更中、生效、冻结、注销。它独立于建档状态，但在建档成功时被同步推进为 EFFECT。

## 需求背景

冻结/解冻/注销均由客户中心发起并同步（custStatusSync）。进入 CHANGE 后，换取运营中台 token 的企业 id 来源发生变化（见 [[rules/change_status_token_source]]）。状态类更新一律限定主数据（见 [[rules/status_update_main_data_type]]）。

## 版本演进

v0：按语义分析给出的状态与转换证据首次成页。

```ground:process
name: 客户生命周期状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/待处理（新建企业与自主注册初始态）
    source: code_enum
  - value: CHANGE
    label: 变更中（走变更流程，token 取变更记录上的运营中台 id）
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
  - from: ADD
    event: "建档成功"
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus(custStatus=EFFECT) / #confirmCustInfoForSimpleAuth"
  - from: EFFECT
    event: "冻结企业"
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java#freeze → #custStatusOperator + #custStatusSync(CustStatusEnum.FREEZE)"
  - from: FREEZE
    event: "解冻企业"
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java#unfreeze → #custStatusSync(CustStatusEnum.EFFECT)"
  - from: EFFECT
    event: "注销/停用企业"
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java#diable → #custStatusOperator(WRITEOFF) + #custStatusSync(CustStatusEnum.WRITEOFF)"
  - from: ADD
    event: "发起变更流程"
    to: CHANGE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/oper/facade/cust/OperCustFacade.java#queryCustAutoCheck(process!=CHECK → CustStatusEnum.CHANGE)"
```