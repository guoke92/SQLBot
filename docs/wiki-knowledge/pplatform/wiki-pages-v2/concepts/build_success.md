---
type: concept
title: 建档成功
page_key: build_success
domain: 准入接入与接入密钥
status: draft
aliases:
  - BUILD_SUCCESS
  - 已通过
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAuditMsgService.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
also_confused_with:
  - cust_company_info.cust_status = 'EFFECT'
adjudication: boundary
boundary: 建档成功同时可能将cust_status置EFFECT。
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 建档成功

## 业务定位

「建档成功」是本地建档流程的终态，落在 [[tables/cust_company_info|cust_company_info]] 的 `cust_build_status = 'BUILD_SUCCESS'`。审核通过回调与简易认证确认提交都会迁移到该状态（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]）。

## 边界与混淆

- 与 [[concepts/check_pass|审核通过]]（`check_status = 'CUST_CHECK_PASS'`）的区别：前者为本地结果，后者为运营中台结论。
- 与 `cust_status = 'EFFECT'` 的区别：建档成功可能同时推动企业主体状态置为 `EFFECT`（[[processes/cust_status_state_machine|企业状态机]]），但企业主体的冻结/注销不改变建档成功这一事实。

## 需求背景

建档结果是重复建档校验、后续业务开通的依据，需要与主体生命周期状态解耦保存。

## 版本演进

暂无该值变更的证据。

相关：[[cust_company_info]]
