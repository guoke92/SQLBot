---
type: concept
title: 联行号（bank_no）
page_key: concepts/bank-no
domain: 企业银行账户
status: draft
aliases: [bank_no, bankID, cnapsCode]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: cust_account_info.bank_no
field_targets:
  - cust_account_info.bank_no
  - cust_account_info.bank_code
  - cust_account_info.bank_code_name
  - cust_account_info.bank_branch_name
adjudication: boundary
also_confused_with:
  - bank_code（银行总行代码）
  - bank_id（银行ID）
  - bank_code_name（上送 bankName）
boundary: 代码把 bank_no 同时当作 bankID 与 cnapsCode 上送人行接口，bankName 取的是 bank_code_name（总行名称）而非开户行 branch 名称。
sources: ["enrich:wiki-admin"]
---

联行号是账户开户行的清算行号，落库字段为 `cust_account_info.bank_no`。在打款申请链路中，代码把该字段同时作为 `bankID` 与 `cnapsCode` 上送人行小额打款接口，即「一值两用」。账户表见 [[tables/cust_account_info]]，流程见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

银行侧接口需要清算行标识与银行名称；现有实现用 bank_no 顶替两个入参、用总行名称顶替开户行名称，任何按字段名直觉推断的口径（如认为 bankName 来自 bank_branch_name）都会与实际上送不一致。

## 版本演进

v0 契约按现状固化；`bank_branch_name` 未参与打款申请链路，后续版本若接入分支行维度需重新厘清三个字段的分工。

## 判定边界

代码把 bank_no 同时当作 bankID 与 cnapsCode 上送人行接口，bankName 取的是 bank_code_name（总行名称）而非开户行 branch 名称。

相关：[[cust_account_info]]
