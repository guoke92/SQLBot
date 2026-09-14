---
type: concept
title: 建档
page_key: cust-build
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业建档
  - build
  - custBuildStatus
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
  - "reqdoc:企业注册/激活流程中同步用户到SSO与AMS运营中台"
  - "reqdoc:企业准入存在人工审核、驳回后可修改重新提交的流程"
contract_version: "0.1"
maps_to: "企业认证/准入的建档流程与 cust_company_info.cust_build_status"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.cust_company_type
adjudication:
  kind: synonym
  boundary: "产融侧建档状态（CustBuildStatusEnum）与运营中台审核状态（OperApiConstants.CheckStatus：CUST_CHECK_PASS/REJECT/INIT等）是两套状态体系，通过回调对齐。"
also_confused_with:
  - 运营中台建档审核回调
sources: ["enrich:wiki-admin"]
belong: concepts
---

「建档」在业务口径中指企业认证/准入的完整流程（提交、审核、退回、驳回重提、通过），在数据口径上落为 `cust_company_info.cust_build_status`。它与运营中台的「建档审核」不同源：产融侧用 CustBuildStatusEnum，运营中台用 OperApiConstants.CheckStatus，二者通过回调对齐，不能直接比等。

## 需求背景
企业准入存在人工审核、驳回后可修改重新提交的流程，状态迁移由 `CustCompanyInfoApplication.messageNotify` 驱动；审核通过由 `updateCustBuildStatus` 落终态；简易认证经 `submitForSimpleAuth` 走 AWAIT_CUST_CONFIRM 分支。企业注册/激活流程中还需同步用户到 SSO 与 AMS 运营中台（`CustPersonApplication.insertOrUpdatePerson` + `CustSyncEventProvider.syncOperatorUser`），因此建档不是单系统内部状态，而是跨系统回调收敛的结果。

## 版本演进
- v0 契约：状态与迁移见 [[processes/cust-company-build-status]]；终态口径见 [[calibers/build-success-company]]；回调侧去重见 [[rules/reject-pass-callback-workflow]]。

---REVIEW: concept | 建档---
产融侧 CustBuildStatusEnum 与运营中台 CheckStatus 的对齐关系（逐一映射还是仅里程碑对齐）在语义分析中未给出逐项映射表，本页仅保留「两套体系」的边界结论，待补映射关系。
---END REVIEW---

相关：[[cust_company_info]]
