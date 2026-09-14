---
type: caliber
title: 建档成功企业口径(影像批处理)
page_key: build_success_company_scope
domain: 企业建档与认证
status: draft
aliases:
  - 建档成功企业
  - getAllBuildSuccessCompanies
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CompanyImageUpdateJobHandler.java:getAllBuildSuccessCompanies
contract_version: "0.1"
belong: calibers
---

影像更新批处理的扫描范围口径：只要流程状态为认证成功且企业启用即纳入，不区分生命周期状态，也不强求主数据标识。相比 [[calibers/effect_company_scope]] 更宽，用于保证已认证企业的影像被持续补齐。

```ground:caliber
name: 建档成功企业口径(影像批处理)
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.enable = 'Y'
scope: CompanyImageUpdateJobHandler 扫描范围
evidence: code_path:CompanyImageUpdateJobHandler.java:getAllBuildSuccessCompanies
```

## 需求背景

批处理需要在冻结、变更中等状态下仍能扫描到已认证企业，因此刻意不放 `cust_status` 条件；这也意味着它不能被复用作"生效企业"判断。

## 版本演进

v0 初稿：口径固化自批处理写值点。与生效企业口径的差异已显式记录，供后续判断是否为有意的宽口径。

关联：[[calibers/effect_company_scope]]、[[tables/cust_company_info]]。