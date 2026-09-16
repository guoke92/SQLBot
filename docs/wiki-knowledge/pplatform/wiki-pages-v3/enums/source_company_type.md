---
type: enum
title: source_company_type
page_key: source_company_type
domain: CA证书收费
status: draft
aliases: [企业角色]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:CustCompanyTypeEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# source_company_type

收费侧企业角色，落在 [[ca_fee_company]].source_company_type 与 [[ca_fee_order]].company_type。displayName 取 `CustCompanyTypeEnum`（本窗库值只有下面三个）。

```ground:enum
enum: source_company_type
fields: [ca_fee_company.source_company_type, ca_fee_order.company_type]
values:
  "CORE":
    label: "核心企业"
  "PROJECT_COMPANY":
    label: "项目公司"
  "SUPPLIER":
    label: "供应商"
```
