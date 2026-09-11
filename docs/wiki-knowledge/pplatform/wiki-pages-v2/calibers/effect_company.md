---
type: caliber
title: "已生效企业口径"
page_key: "calibers/effect_company"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业有效性口径"
  - "生效企业判定"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code:code_path:CustCompanyIfoEnchanceService.java:listEffectCompany,listEffectCompanyByTenantAndType"
contract_version: "0.1"
---

本口径是企业「有效性」的统一判定：同时满足建档成功、客户状态生效、数据标识与启用标识，才被计入已生效企业。任一条件不满足（如处于变更中、已注销、已失效）都不计入。与之相对的是变更在途阻断口径 [[calibers/change_in_flight_block]]。

## 需求背景

需求文档要求企业准入通过后才可用，本口径是「已通过」在查询层面的落地判定；统计口径若漏掉 `cust_build_status` 或 `cust_status` 任一条件，会把变更中/失效企业算作生效。

## 版本演进

- 口径以 predicate 形式在多处查询复用，新增查询入口时应复用同一 predicate，避免派生口径漂移，见 [[tables/cust_company_info]]。

```ground:caliber
name: "已生效企业口径"
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'"
scope: "listEffectCompany / listEffectCompanyByTenantAndType 等企业有效性查询"
evidence: "code:code_path:CustCompanyIfoEnchanceService.java:listEffectCompany,listEffectCompanyByTenantAndType"
```

相关：[[tables/cust_company_info]]、[[processes/company_build_status_machine]]、[[concepts/build_status]]。