---
type: rule
title: 平台运营方豁免
page_key: platform_operator_exemption
domain: 平台产品配置
status: draft
aliases: [运营方豁免, custProductInclusion]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#gotoProductSupplierByCompanyType
  - code:CustProductDomainService.java#custProductInclusion
contract_version: "0.1"
belong: rules
---

平台运营方不参与项目状态检查，且在 `custProductInclusion` 中直接返回 true，因此可进入并开通全部产品。判定依据是企业的角色类型（[[company_type]]）。

## 需求背景

该豁免是 [[project_effective_check]] 与 [[cust_role_combine_antifraud]] 的例外分支，保障运营侧不受业务闸口限制。

## 版本演进

- 初版规则，无历史变更。

```ground:rule
name: 平台运营方豁免
content: "平台运营方不检查项目状态，且在 custProductInclusion 中直接返回 true"
impact: 运营方可进入/开通全部产品
field_targets:
  - cust_company_info.cust_company_type
evidence: "code_path:PlatformProductApplication.java#gotoProductSupplierByCompanyType;CustProductDomainService.java#custProductInclusion"
```

关联：[[project_effective_check]]、[[cust_role_combine_antifraud]]、[[company_type]]