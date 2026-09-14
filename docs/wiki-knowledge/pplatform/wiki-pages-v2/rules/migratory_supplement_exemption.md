---
type: rule
title: 存量迁移企业授权书补签的豁免
page_key: migratory_supplement_exemption
domain: 授权协议与电子授权
status: draft
aliases:
  - 迁移企业免补签
  - 补签豁免规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
belong: rules
---

决定迁移/外部企业在开通产品时是否弹补签授权书：`cust_source=PLATFORM_PUSH`（外部平台推送）一律视为已授权；`cust_source=MIGRATORY` 且 [[auth_agreement_supplement_flag]] 为 N（新渠道迁移）无需签署；其余情况仍需检查平台授权（[[platform_level_auth_agreement]]）或存量产品授权。

```ground:rule
name: 存量迁移企业授权书补签的豁免
content: "cust_source=PLATFORM_PUSH（外部平台推送）一律视为已授权；cust_source=MIGRATORY 且 auth_aggrement_supplement_flag=N（新渠道迁移）不需要签署；其余情况需检查平台授权(PLATFORM)或存量产品授权"
impact: "决定迁移/外部企业在开通产品时是否弹补签授权书"
field_targets:
  - cust_company_info.cust_source
  - cust_company_info.auth_aggrement_supplement_flag
  - cust_company_info.migarory_auth_aggrement_flag
evidence: "code:CustAuthAgreementDomainService.java:enableCompanyManagerAuthAggrement"
```