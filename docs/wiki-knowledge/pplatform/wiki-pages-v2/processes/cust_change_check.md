---
type: process
title: 客户变更审核状态机
page_key: cust_change_check
domain: 客户中心
status: draft
aliases:
  - 变更审核流转
  - cust_change_record.status 流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
belong: processes
---

客户变更审核状态机描述 [[cust_change_record]].status 在运营中台审核回调下的流转，是 [[back_to_custom]]、[[reject]] 术语在变更路径上的落地过程。状态来源为 OperApiConstants.CheckStatus（code_const）。

```ground:process
name: 客户变更审核状态机
field: cust_change_record.status
states:
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_const
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_const
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_const
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户确认
    source: code_const
  - value: returnCust-yyyy-MM-dd HH:mm
    label: 退回客户（自行变更路径动态状态）
    source: code_const
transitions:
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核通过
    to: CUST_CHECK_PASS
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核拒绝
    to: CUST_CHECK_REJECT
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 运营中台退回待客户确认
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 审核意见包含“退回”且 alterMode=SELF_ALTER
    to: returnCust-yyyy-MM-dd HH:mm
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。