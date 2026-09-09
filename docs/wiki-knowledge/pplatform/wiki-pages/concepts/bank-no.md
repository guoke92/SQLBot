---
type: concept
title: 联行号
page_key: bank-no
belong: concepts
domain: 企业银行账户与第三方银行
status: published
aliases: ["bankNo", "bank_no", "cnapsCode"]
oid: 1
sources: ["db", "code"]
contract_version: "0.1"
maps_to: "cust_account_info.bank_no"
field_targets: ["cust_account_info.bank_no"]
adjudication: boundary
also_confused_with: ["银行总行代码 bank_code", "银行ID bank_id"]
boundary: "bank_no用于中金打款银行身份；bank_code为总行代码；bank_id为银行ID"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“联行号”指用于中金打款申请时银行身份的标识。该术语桥将其映射到 `cust_account_info.bank_no`，并与银行总行代码、银行ID划清边界。

## 需求背景

在向银行发起打款申请时，系统需要提供联行号（cnapsCode）以定位开户行。代码中 `bank_no` 字段承载该值，而 `bank_code` 与 `bank_id` 分别用于不同场景，容易混淆。该术语桥定义了明确语义。

## 版本演进

本概念契约 v0 基于数据库与代码证据建立，区分三个银行相关标识。

[[cust_account_info]] 表字段 `bank_no` 是该概念的物理承载。