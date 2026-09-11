---
type: concept
title: 录入方式
page_key: build_type
domain: 企业建档与认证
status: draft
aliases:
  - cust_build_type
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_build_type
contract_version: "0.1"
maps_to: cust_company_info.cust_build_type
adjudication: boundary
also_confused_with:
  - 认证方式
boundary: 录入方式表示数据由谁录入（平台/客户端/简易）；认证方式表示认证流程类型。
sources: ["enrich:wiki-admin"]
---

“录入方式”指 `cust_company_info.cust_build_type`，表示企业数据由谁录入：`AGW_BUILD`（平台录入）、`PC_BUILD`（客户端录入）、`SIMPLE`（简易录入）。

它与 [[identify_style]]（认证方式）经常被混用，因为二者常常同时出现在建档入口。裁定边界为：录入方式描述**数据录入主体/通道**，认证方式描述**认证流程类型**；后者决定状态机走向（见 [[enterprise_auth_status_machine]]）。

## 需求背景

暂无需求文档主张。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与认证方式的边界。

相关：[[cust_company_info]]
