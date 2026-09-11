---
type: concept
title: 账户归属企业（ref_cust_company_info）
page_key: concepts/account-owner-company
domain: 企业银行账户
status: draft
aliases: [ref_cust_company_info, 客户账号信息]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: cust_account_info.ref_cust_company_info = cust_company_info.code
field_targets:
  - cust_account_info.ref_cust_company_info
  - cust_company_info.code
adjudication: boundary
also_confused_with:
  - cust_company_info.id
  - cust_id
boundary: 字段名与注释像“账号信息”，实际存企业编码；代码统一用 company.getCode() 赋值/查询，用企业主键 id 过滤会查不到数据。
sources: ["enrich:wiki-admin"]
---

「账户归属企业」是账户表与企业的关联语义：`cust_account_info.ref_cust_company_info` 存的是 `cust_company_info.code`（企业编码），不是企业主键 id。相关表见 [[tables/cust_account_info]]。

## 需求背景

账户的所有校验与口径（重复账户校验、默认账户唯一、企业维度统计）都依赖这个关联字段，因此它的取值语义必须唯一确定，否则会同时影响 [[rules/account-no-unique-per-company]] 与 [[calibers/default-repayment-account]] 的正确性。

## 版本演进

v0 契约按现状固化：关联值为企业编码，`cust_id` 语义仅属于集团关系表，两者不可互换。

## 判定边界

字段名与注释像「账号信息」，实际存企业编码；代码统一用 company.getCode() 赋值/查询，用企业主键 id 过滤会查不到数据。

相关：[[cust_account_info]] [[cust_company_info]]
