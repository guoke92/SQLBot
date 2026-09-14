---
type: concept
title: 退回
page_key: back_to_custom
domain: 客户中心
status: draft
aliases:
  - 退回客户
  - BACKTOCUSTOM
  - returnCust
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
maps_to: "cust_change_record.status = 'CUST_CHECK_BACKTOCUSTOM'"
also_confused_with:
  - "动态状态 returnCust-yyyy-MM-dd HH:mm"
adjudication: boundary
belong: concepts
---

「退回」有两类落库：标准退回客户确认为 [[cust_change_record]].status = CUST_CHECK_BACKTOCUSTOM；企业自行变更（alterMode=SELF_ALTER）且审核意见含「退回」时，写入动态值 returnCust-yyyy-MM-dd HH:mm。两者语义相近但取值形态不同，流转见 [[cust_change_check]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。