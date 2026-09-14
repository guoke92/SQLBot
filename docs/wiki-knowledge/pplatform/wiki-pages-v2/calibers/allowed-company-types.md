---
type: caliber
title: 可触发电子授权签署的企业类型
page_key: allowed-company-types
domain: 授权协议与电子授权
status: draft
aliases:
  - 允许签署的企业类型
  - ALLOWED_COMPANY_TYPE_KEYS
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: calibers
---

签署编排只对企业角色为供应商（`SUPPLIER`）、核心企业（`CORE`）、金融机构（`FINANCE`）、项目公司（`PROJECT_COMPANY`）的企业开放。该口径与 [[calibers/offline-electronic-auth-trigger]] 是合取关系，同时使用 [[tables/cust_change_record|company_type]] 相关的角色语义。

## 需求背景
电子授权书目前只覆盖参与授信/融资主链路的四类企业角色，其余角色保持原线下流程，避免一次性扩大灰度范围。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 可触发电子授权签署的企业类型
predicate: "cust_company_info.cust_company_type ∈ {'SUPPLIER','CORE','FINANCE','PROJECT_COMPANY'}"
scope: "电子授权书签署编排"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#ALLOWED_COMPANY_TYPE_KEYS"
```