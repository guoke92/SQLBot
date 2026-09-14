---
type: concept
title: 拒绝
page_key: reject
domain: 客户中心
status: draft
aliases:
  - 驳回
  - REJECT
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
maps_to: "cust_company_info.check_status = 'CUST_CHECK_REJECT'"
also_confused_with:
  - "cust_change_record.status = 'CUST_CHECK_REJECT'"
  - "rtfState 包含‘拒绝’"
adjudication: synonym
belong: concepts
---

「拒绝/驳回」映射为 CheckStatus.CUST_CHECK_REJECT，按业务写企业侧或变更侧。与「审核通过」类似，同名常量在 [[cust_company_info]] 与 [[cust_change_record]] 中出现，需要按落库对象区分；此外 CustAuthValidatorProcessor 对 rtfState 文本包含「拒绝」的情形会直接 return，属流程侧分支而非落库值。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。