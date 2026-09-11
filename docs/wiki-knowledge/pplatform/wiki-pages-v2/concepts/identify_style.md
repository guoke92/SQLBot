---
type: concept
title: 认证方式
page_key: identify_style
domain: 企业建档与认证
status: draft
aliases:
  - identify_style
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style
adjudication: boundary
also_confused_with:
  - 录入方式
boundary: 认证方式指 INVITE、INVITE_AGW、SELF、SIMPLE；录入方式指 AGW_BUILD、PC_BUILD、SIMPLE。
sources: ["enrich:wiki-admin"]
---

“认证方式”指 `cust_company_info.identify_style`，表示企业走的是哪一条**认证流程**：`INVITE`（邀请认证-客户录入）、`INVITE_AGW`（邀请认证-平台录入）、`SELF`（自主认证）、`SIMPLE`（简易认证）。

认证方式直接决定建档提交后的状态去向：`INVITE`/`SELF` 提交后进入待客户确认，`INVITE_AGW` 直接进入认证中，`SIMPLE` 走简易确认路径，见 [[enterprise_auth_status_machine]]。它常与 [[build_type]]（录入方式）混用，但后者描述的是**数据由谁录入**，不是认证流程类型；两者取值集合虽有重叠（如 `SIMPLE`），语义层面不同。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与录入方式的边界。

相关：[[cust_company_info]]
