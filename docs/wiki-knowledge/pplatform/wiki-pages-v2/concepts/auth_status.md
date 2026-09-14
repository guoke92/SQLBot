---
type: concept
title: 认证状态
page_key: auth_status
domain: 企业建档与认证
status: draft
aliases:
  - 建档状态
  - cust_build_status
oid: 1
scope:
  databases: []
sources:
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
adjudication: boundary
also_confused_with:
  - 客户状态
  - 审核状态
boundary: 认证状态描述企业建档审核的进度；客户状态描述企业生命周期状态；审核状态描述运营中台单次审核结果。
belong: concepts
field_targets: [cust_company_info.cust_build_status]
---

“认证状态”（也称建档状态）指 `cust_company_info.cust_build_status`，描述一个企业从初始化（`INIT`）到认证成功（`BUILD_SUCCESS`）/认证失败（`BUILD_FAIL`）的全流程进度。它是建档流程的主状态，流转细节见 [[enterprise_auth_status_machine]]。

该概念最容易与 [[customer_status]]（客户状态）和 [[check_status]]（审核状态）混用。裁定边界为：认证状态是企业建档审核的**整体进度**；客户状态是企业作为客户的**生命周期状态**（生效、冻结、注销）；审核状态是运营中台对**单次提交**的审核结果。三者存放于同一张表 [[cust_company_info]] 的不同字段，参与不同的判定口径（如 [[effective_company]] 同时要求认证状态与客户状态）。

## 需求背景

暂无需求文档主张。术语桥证据来源于数据库字段语义与代码枚举常量（`CustBuildStatusConstant`）。

## 版本演进

- v0.1：依据语义分析建立 concept 页，裁定与客户状态、审核状态的边界。