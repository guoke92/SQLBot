---
type: caliber
title: 存量迁移企业免补签授权书
page_key: caliber.migratory_no_supplement
domain: 授权协议与电子授权
status: draft
aliases:
  - MIGRATORY 免补签
  - 存量迁移免签口径
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
---

存量迁移企业只有在 `auth_aggrement_supplement_flag='N'`（走新渠道、不需补签）时才免补签；旧渠道迁移会置 `'Y'` 表示需补签，且该标志可被 `updateAuthAggrementFlag` 人工翻转。因此该口径是「来源 + 标志位」的合取，与来源单一条件的 [[calibers/platform-push-no-supplement]] 不同。

## 需求背景
存量迁移分新旧渠道：走新渠道的协议已在迁移中落库，无需补签；走旧渠道的协议未能完整迁移，必须保留补签入口，故用独立标志位而非来源单一判定。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 存量迁移企业免补签授权书
predicate: "cust_company_info.cust_source = 'MIGRATORY' AND cust_company_info.auth_aggrement_supplement_flag = 'N'"
scope: "授权书补签判定"
evidence: "code_path:CustAuthAgreementDomainService.java#enableCompanyManagerAuthAggrement"
```