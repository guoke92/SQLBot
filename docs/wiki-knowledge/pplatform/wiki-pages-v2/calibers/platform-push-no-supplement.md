---
type: caliber
title: 外部推送企业免补签授权书
page_key: caliber.platform_push_no_supplement
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM_PUSH 免补签
  - 平台推送企业免签
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
---

数据来源为外部平台推送（`cust_source='PLATFORM_PUSH'`）的企业，视为授权关系已由来源系统保证，判定链路直接返回「不需签约」，不再考察 [[tables/authorization_agreement|平台级授权记录]] 或补签标志位。该口径与 [[calibers/migratory-no-supplement]] 是并列的两条免补签捷径。

## 需求背景
外部平台推送的企业不允许在产融侧再次提示补签授权书，否则会造成来源系统与产融侧授权状态不一致的重复签署。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 外部推送企业免补签授权书
predicate: "cust_company_info.cust_source = 'PLATFORM_PUSH'"
scope: "授权书补签判定（enableCompanyManagerAuthAggrement / hasCompanySignedAuthAggrement 直接返回不需签约）"
evidence: "code_path:CustAuthAgreementDomainService.java#enableCompanyManagerAuthAggrement"
```