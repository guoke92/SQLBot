---
type: concept
title: 工作流审核
page_key: workflow_check
domain: 客户中心
status: draft
aliases:
  - 运营中台审核
  - 工作流审核执行器
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
maps_to: cust_company_info.check_status
also_confused_with:
  - cust_change_record.status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.check_status]
---

「工作流审核」指运营中台对建档提交的审核环节，结果写入 [[cust_company_info]] 的 check_status（按 CheckStatus 枚举 .name()）。它不指客户变更审核——后者写入 [[cust_change_record]].status，属于不同表的不同列，切勿混用。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。