---
type: concept
title: 审核通过
page_key: check_pass
domain: 准入接入与接入密钥
status: draft
aliases:
  - CUST_CHECK_PASS
  - 已通过
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAuditMsgService.java:getCustBuildStatus
  - db:cust_company_info.check_status
contract_version: "0.1"
maps_to: cust_company_info.check_status = 'CUST_CHECK_PASS'
also_confused_with:
  - cust_company_info.cust_build_status = 'BUILD_SUCCESS'
adjudication: boundary
boundary: check_status是运营中台审核态；cust_build_status是本地建档态，审核通过时联动BUILD_SUCCESS。
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 审核通过

## 业务定位

「审核通过」是运营中台给出的审核结论，落在 [[tables/cust_company_info|cust_company_info]] 的 `check_status = 'CUST_CHECK_PASS'`，由回调（`CustAuditMsgService`）更新。

## 边界与混淆

- 与 [[concepts/build_success|建档成功]]（`cust_build_status = 'BUILD_SUCCESS'`）的区别：前者是外部审核态，后者是本地建档态；审核通过会联动本地建档态变为 `BUILD_SUCCESS`，但两者字段、责任方不同。

状态流转见 [[processes/cust_check_status_state_machine|运营审核状态机]]。

## 需求背景

对外展示与内部推进依赖不同的状态字段，需同时保留审核结论与本地推进结果。

## 版本演进

暂无该值变更的证据。

相关：[[cust_company_info]]
