---
type: concept
title: 认证状态/打款验证状态
page_key: auth-state
domain: 企业银行账户与第三方银行
status: published
aliases: ["authState", "auth_state", "小额打款验证状态"]
oid: 1
sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "cust_account_info.auth_state"
field_targets: ["cust_account_info.auth_state"]
adjudication: boundary
also_confused_with: ["cust_company_info.cust_build_status 企业认证状态", "cust_company_info.cust_status 企业状态"]
boundary: "账户级打款验证状态，不是企业认证或企业状态"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

术语“认证状态/打款验证状态”指账户层面小额打款验证的当前状态。该术语桥将其映射到 `cust_account_info.auth_state`，并强调与企业认证状态、企业状态的区别。

## 需求背景

账户验证状态贯穿打款申请、受理、确认等业务环节。为避免与更上层的企业认证概念混淆，该术语桥明确了字段的账户级范围。

## 版本演进

本概念契约 v0 基于语义分析建立，划分账户级状态与企业级状态的边界。

[[cust-account-info-auth-state]] 状态机描述该字段的流转。

相关：[[cust_account_info]]
