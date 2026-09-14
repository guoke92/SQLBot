---
type: process
title: 企业审核状态机
page_key: cust_check_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - 审核状态
  - checkStatus
  - CheckStatus
  - CUST_CHECK_*
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.terminateBuildingFlow
  - code:CustAccessApplication.getCheckStatus
contract_version: "0.1"
belong: processes
---

审核状态是运营流程侧的状态主线，落库字段为 [[cust_company_info]].check_status，落库值为 CheckStatus 的 `.name()`、读取用 `CheckStatus.getByName`。

## 需求背景
对外状态查询以 check_status 优先映射（CUST_CHECK_PASS→CUSTS003+AUTH0003 等），为空时才回落到建档状态兜底；终止建档流程会把审核置为 CUST_CHECK_REJECT。终止后若未拉起中台流程，还需按 [[build_terminated_todo_compensation]] 补偿待办。与建档状态的边界见 [[check_status]] 与 [[company_archive]]。

## 版本演进
暂无版本演进记录。

```ground:process
name: 企业审核状态
field: cust_company_info.check_status
states:
  - value: CUST_CHECK_INIT
    label: 审核初始化
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户补件
    source: code_enum
  - value: CUST_BACK
    label: 退回
    source: code_enum
transitions:
  - from: "*"
    event: 终止建档流程
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustAccessApplication.terminateBuildingFlow → update.setCheckStatus(CheckStatus.CUST_CHECK_REJECT.name())"
  - from: CUST_CHECK_PASS
    event: 对外状态映射
    to: CUSTS003 + AUTH0003
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_PASS"
  - from: CUST_CHECK_CHECKING
    event: 对外状态映射
    to: CUSTS002 + AUTH0001
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_CHECKING"
  - from: CUST_CHECK_REJECT
    event: 对外状态映射
    to: CUSTS004 + AUTH0001
    evidence: "code_path:CustAccessApplication.getCheckStatus → case CUST_CHECK_REJECT"
```