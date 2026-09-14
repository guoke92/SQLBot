---
type: caliber
title: 建档类签署仅限邀请/自主录入
page_key: build-scope-identify-styles
domain: 授权协议与电子授权
status: draft
aliases:
  - CHECK 分支认证方式白名单
  - ALLOWED_BUILD_IDENTIFY_STYLES
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: calibers
---

在 `processType=CHECK`（建档类）分支中，只有认证方式为 `INVITE`（邀请认证-客户录入）或 `SELF`（自主注册）才允许发起电子授权签署；`INVITE_AGW`（平台录入）与 `SIMPLE`（简易认证）不进入该分支。该口径与 [[calibers/offline-electronic-auth-trigger]] 共同作用，状态来源见 [[processes/cust_build_status]]。

## 需求背景
邀请-平台录入在企业侧天然对应线下签署流程，简易认证则无流程实例（`act_procinst_id` 为空不落授权记录），二者均不适合走线上电子签署编排。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 建档类签署仅限邀请/自主录入
predicate: "cust_company_info.identify_style ∈ {'INVITE','SELF'}"
scope: "processType=CHECK 分支"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#ALLOWED_BUILD_IDENTIFY_STYLES"
```