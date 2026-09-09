---
type: concept
title: 交易ID
page_key: trans-id
belong: concepts
domain: 企业银行账户与第三方银行
status: published
aliases: ["transId", "trans_id", "originalTxSN"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "cust_account_info.trans_id"
field_targets: ["cust_account_info.trans_id"]
adjudication: boundary
also_confused_with: ["trace_no 系统跟踪号"]
boundary: "trans_id为银行申请打款原交易流水号；trace_no为申请响应系统跟踪号"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“交易ID”指银行申请打款时原交易流水号，由银行返回。该术语桥映射到 `cust_account_info.trans_id`，同时与系统跟踪号 `trace_no` 区分。

## 需求背景

打款申请成功后，系统会记录银行交易流水号，用于后续查询与对账。业务上易将交易ID与系统跟踪号混淆，该术语桥明确了它们的不同来源和用途。

## 版本演进

本概念契约 v0 基于代码与数据库证据建立，清楚划分两个字段的语义。

[[cust_account_info]] 表字段 `trans_id` 是该概念的物理承载。