---
type: enum
title: company_type
page_key: company_type
domain: 客户角色与端口
status: draft
aliases: [供应商, 核心企业, 金融机构]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
---

# company_type

`CustCompanyTypeEnum`。同一字典出现在企业主档 `cust_company_type`、联系人 `company_type`、角色 `role_type`、产品端口 `company_type_code`。问「企业是供应商」看企业或角色切片；问「谁是管理员」看 [[user_type]]。

```ground:enum
enum: company_type
fields:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
  - cust_role_info.role_type
  - platform_product_cust_role.company_type_code
  - cust_project_rel.company_type
values:
  "SUPPLIER":
    label: "供应商"
  "DEALER":
    label: "经销商"
  "PROJECT_COMPANY":
    label: "项目公司"
  "CORE":
    label: "核心企业"
  "CORE_MANAGER":
    label: "核心企业管理机构"
  "FINANCE":
    label: "金融机构"
  "PLATFORM_OPERATOR_COMPANY":
    label: "平台运营方"
  "CORE_FUNCTIONAL_DEPARTMENT":
    label: "核心企业职能部门"
  "CORE_SUB":
    label: "核心企业子公司"
  "CORE_BRANCH":
    label: "核心企业分公司"
  "FACTOR_COMPANY":
    label: "保理买卖方"
  "PLATFORM_COMPANY":
    label: "平台方"
  "CORPORATION_COMPANY":
    label: "集团公司"
```
