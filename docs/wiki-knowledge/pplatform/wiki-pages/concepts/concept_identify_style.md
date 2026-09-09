---
type: concept
title: 认证方式
page_key: concept_identify_style
belong: concepts
domain: 企业变更与运营变更
status: published
aliases: ["identifyStyle"]
oid: 1

sources: ["db", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_company_info.identify_style"
field_targets: ["cust_company_info.identify_style"]
adjudication: "boundary"
also_confused_with: ["cust_build_status"]
coverage_note: 术语边界
scope:
  databases: [lowcode_pplatform]
---

“认证方式”表示企业采用的认证形式，存储于 `cust_company_info.identify_style`。取值语义以权威枚举页 [[identify_style]] 为准（INVITE=邀请认证、INVITE_AGW=邀请认证-内管录入、SIMPLE=简易认证、SELF=自主认证）。

## 需求背景

边界说明：`identify_style` 是认证方式；`cust_build_status` 是认证流程状态。

## 版本演进

暂无。

相关：[[cust_company_info]]
