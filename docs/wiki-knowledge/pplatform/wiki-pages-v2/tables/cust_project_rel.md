---
type: table
title: cust_project_rel（企业—项目/产品关联表）
page_key: table.cust_project_rel
domain: 平台内部服务对接
status: draft
aliases:
  - cust_project_rel
  - 企业项目关联表
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_project_rel]
contract_version: "0.1"
sources: ["enrich:wiki-admin"]
---

企业与租户项目/产品的关联关系表，承载「哪个企业以什么角色开通了哪个产品」这一对接事实。

## 需求背景

项目与产品 id 以字符串形式存储，并与 [[tables/tenant_project]] 的 project_id、[[tables/platform_product]] 的 product_code 对齐（见 [[concepts/product_code_bridge]]）。tenant_code 与 db_tenant_code 同值写入，是租户隔离在关系表上的落点。

## 版本演进

v0：首次成页。

```ground:table
table: cust_project_rel
columns:
  - field: ref_cust_project_rel_cust_company_info
    meaning: "关联企业 code"
    evidence: code
  - field: project_id / product_id
    meaning: "关联租户项目 id / 产品 id（字符串存储）"
    evidence: code
  - field: tenant_code / db_tenant_code
    meaning: "租户编码（两者同值写入）"
    evidence: code
  - field: company_type
    meaning: "关联关系对应的企业角色"
    evidence: code
  - field: show_flag
    meaning: "是否展示 'Y'/'N'"
    evidence: code
  - field: enable
    meaning: "有效标志 'Y'/'N'"
    evidence: code
  - field: ref_cust_project_rel_platform_product / op_contact_a / op_contact_a_group
    meaning: "平台产品编码 / 运营对接人 / 运营对接人组"
    evidence: code
```
## 关联表

- [[ca_fee_company]]：cust_project_rel.ref_cust_project_rel_cust_company_info → ca_fee_company.code（java-eq:CaFeeRuleEngineService.java，suggested）
- [[cust_change_cfg]]：cust_project_rel.product_id → cust_change_cfg.id（write-flow:PlatFormMigratoryApplication.java，confirmed）
- [[cust_change_record]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_company_info.code（ref-convention:CustProjectRelDO.java，suggested）
- [[platform_product]]：cust_project_rel.ref_cust_project_rel_platform_product → platform_product.code（ref-convention:CustProjectRelDO.java，suggested）
- [[tenant_product]]：cust_project_rel.product_id → tenant_product.platform_product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[tenant_project]]：cust_project_rel.ref_cust_project_rel_platform_product → tenant_project.ref_tenant_project_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
