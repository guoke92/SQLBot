---
type: concept
title: 认证状态
page_key: auth-status
domain: 企业建档与准入
status: published
aliases: [建档状态, 认证流程状态]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with: ["cust_status（客户状态）", "check_status（审核状态）"]
adjudication: boundary
boundary: cust_build_status 跟踪认证流程阶段，cust_status 为客户生命周期状态，check_status 为运营审核指令状态
field_targets: []
scope:
  databases: [lowcode_pplatform]
---

# 认证状态

认证状态是指企业认证流程所处的阶段，字段为 `cust_company_info.cust_build_status`。它与客户生命周期状态 `cust_status`、运营审核状态 `check_status` 是三个独立但易混淆的状态维度。

## 需求背景

“建档状态”“认证流程状态”在业务中常混用，数据侧统一为 `cust_build_status`。认证状态由 [[enterprise-auth-status-machine]] 定义，客户状态由 [[customer-lifecycle-status-machine]] 定义。

## 版本演进

本概念来自语义分析中的术语桥，边界定义为三状态字段区分。

相关概念：[[freeze]]、[[enterprise-customer]]；相关表：[[cust_company_info]]