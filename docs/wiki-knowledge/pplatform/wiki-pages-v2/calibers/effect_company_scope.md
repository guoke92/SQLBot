---
type: caliber
title: 生效企业口径
page_key: effect_company_scope
domain: 企业建档与认证
status: draft
aliases:
  - 生效企业
  - getTenantCodesWithEffectCompany
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
contract_version: "0.1"
belong: calibers
---

用于产出"拥有至少一家生效企业"的租户集合。四个条件同时成立才算生效：流程状态认证成功、生命周期生效、是主数据、且企业启用。

```ground:caliber
name: 生效企业口径
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'
scope: 有生效企业的租户集合
evidence: code_path:CustCompanyUtilApplication.java:getTenantCodesWithEffectCompany
```

## 需求背景

该清单是下游能力（如门户/推送/权限）判断"租户是否已真正开业"的输入，因此必须同时约束流程状态与生命周期状态，不能只看 [[concepts/build_success]] 其中一个字段。

## 版本演进

v0 初稿：口径固化自写值点条件，无历史版本。注意与影像批处理的宽口径 [[calibers/build_success_company_scope]] 不同——后者不校验 `cust_status`。

关联：[[tables/cust_company_info]]、[[processes/cust_status_state_machine]]、[[calibers/main_data_judgment]]。