---
type: concept
title: 电子签章
page_key: e_signature
domain: 客户中心
status: draft
aliases:
  - CA开通
  - CFCA
  - 上上签
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:isOpenCa
contract_version: "0.1"
maps_to: cust_company_info.need_register_ca
also_confused_with:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.need_register_ca]
---

「电子签章」相关字段都在 [[cust_company_info]]：need_register_ca 表示是否需要开通（Y/N/P），ca_register_status 表示 CFCA/电子签章的实际开通状态，bs_register_status 表示上上签的实际开通状态。三者不可混用——「需不需要」与「通没通」是不同问题，供应商也有 CFCA 与上上签之分。开通阻断口径见 [[ca_open_block]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。