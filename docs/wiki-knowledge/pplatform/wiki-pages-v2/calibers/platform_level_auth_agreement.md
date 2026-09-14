---
type: caliber
title: 平台级授权确认书
page_key: platform_level_auth_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM 授权书
  - 平台授权书口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
belong: calibers
---

用于把「平台级」授权确认书与业务线产品授权书分开。命中该口径的记录代表企业管理员对产融平台的授权，与 `ACFLOW/AMS/ORDER/RVSFACTOR_PC` 等业务线产品码并列存在于同一张 [[authorization_agreement]] 表中。

补签判定中，平台级授权书与存量产品授权是两条并列的检查项，见 [[migratory_supplement_exemption]]；不要把这里的 `PLATFORM` 与协议迁移里的产品协议 [[product_protocol]] 混为一谈。

```ground:caliber
name: 平台级授权确认书
predicate: "authorization_agreement.platform_product_code = 'PLATFORM'"
scope: "产融平台管理员授权书（PLATFORM_PRODUCT_TYPE），与业务线产品码并列"
evidence: "code:CustAuthAgreementDomainService.java:PLATFORM_PRODUCT_TYPE + db:PLATFORM=25156"
```