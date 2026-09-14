---
type: caliber
title: 授权书补签开关
page_key: auth_agreement_supplement_flag
domain: 授权协议与电子授权
status: draft
aliases:
  - 补签开关
  - auth_aggrement_supplement_flag=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
belong: calibers
---

存量迁移企业是否仍需补签平台授权书的口径。它与 `cust_source=MIGRATORY` 组合使用：本字段为 N 且来源为迁移，则视为新渠道迁移企业、免签，见 [[migratory_supplement_exemption]] 与 [[cust_company_info]]。

```ground:caliber
name: 授权书补签开关
predicate: "cust_company_info.auth_aggrement_supplement_flag = 'Y'"
scope: "存量迁移企业是否仍需补签平台授权书；N 且 cust_source=MIGRATORY 则免签"
evidence: "code:CustAuthAgreementDomainService.java:enableCompanyManagerAuthAggrement"
```