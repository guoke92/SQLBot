---
type: table
title: tenant_project（租户项目表）
page_key: table.tenant_project
domain: 平台内部服务对接
status: draft
aliases:
  - tenant_project
  - 租户项目表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[tenant_project]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

租户下的项目实体，承接产品编码与项目状态，是企业—项目关联（[[tables/cust_project_rel]]）的另一端。

## 需求背景

项目列表展示时需要回带产品名称，名称来源为 [[tables/platform_product]]。项目状态生效值为 EFFECTIVE。

## 版本演进

v0：首次成页。

```ground:table
table: tenant_project
columns:
  - field: tenant_id / platform_product_code / product_id / name
    meaning: "所属租户 id / 平台产品编码 / 产品 id / 项目名"
    evidence: code
  - field: project_status / enable / db_tenant_code
    meaning: "项目状态（EFFECTIVE 生效）/ 有效标志 / 租户编码"
    evidence: code
```
## 关联表

- [[ca_fee_project_config]]：tenant_project.id → ca_fee_project_config.project_id（write-flow:CaFeeProjectConfigService.java，confirmed）
- [[cust_project_rel]]：tenant_project.ref_tenant_project_platform_product → cust_project_rel.ref_cust_project_rel_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[platform_product]]：tenant_project.ref_tenant_project_platform_product → platform_product.code（ref-convention:TenantProjectDO.java，suggested）
- [[tenant_product]]：tenant_project.ref_tenant_project_tenant_code → tenant_product.ref_tenant_product_tenant_setting_config（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project_approval]]：tenant_project.code → tenant_project_approval.ref_tenant_project_approval_tenant_project（ref-convention:TenantProjectApprovalDO.java，suggested）
