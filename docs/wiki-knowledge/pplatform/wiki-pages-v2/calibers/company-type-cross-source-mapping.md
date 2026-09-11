---
type: caliber
title: companyType 跨源映射口径
page_key: caliber.company-type-cross-source-mapping
domain: 项目报表/统计/上报
status: draft
aliases:
  - 角色跨源映射
  - processCompanyTypeBySource
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:ProjectReportController.java
contract_version: "0.1"
---

# companyType 跨源映射口径

项目企业报表的 companyType 查询参数需按来源转换：讯易链侧把 CORE 映射为 ce（XycCompanyType.CE）、FINANCE 映射为 cpt（XycCompanyType.CPT）；产融侧保持原值不变（见 [[calibers/project-ledger-source]]）。

## 需求背景

两套系统的角色编码体系不同，报表查询必须在进入各分支前完成转换，否则会出现「查得到产融、查不到讯易链」的错配。角色本身的多值/单值差异见 [[concepts/company-type]]，产融关联表字段定义见 [[tables/cust_project_rel]]。

## 版本演进

目前只对 CORE/FINANCE 两个角色建立了跨源映射，其余角色在报表查询中退化为不筛选（置 'a'），属映射覆盖不全的过渡状态。

```ground:caliber
name: "companyType 跨源映射口径"
predicate: "讯易链：CORE→ce（XycCompanyType.CE），FINANCE→cpt（XycCompanyType.CPT）；产融保持原值"
scope: "项目企业报表 companyType 查询参数转换"
evidence: "code_path:ProjectReportController.java:processCompanyTypeBySource"
```