---
type: process
title: 企业建档/认证状态机
page_key: company_build_status
domain: 客户中心
status: draft
aliases:
  - 建档状态流转
  - cust_build_status 流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMsgSend
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
belong: processes
---

企业建档/认证状态机描述 [[cust_company_info]].cust_build_status 在邀请录入、客户确认、运营中台审核回调之间的流转，是 [[build]] 术语的落地过程。状态来源为 CustBuildStatusEnum（code_enum）。

```ground:process
name: 企业建档/认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中/建档中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败
    source: code_enum
  - value: CUST_CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证客户录入提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMsgSend
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台审核/客户确认提交
    to: CUST_BUILDING
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: 运营中台审核退回/待客户确认
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_CONFIRM_AWAIT
    event: CUST_CHECK_CHECKING 回调
    to: CUST_BUILDING
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_BACKTOCUSTOM 回调
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_PASS 回调
    to: BUILD_SUCCESS
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_REJECT 回调
    to: BUILD_FAIL
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。