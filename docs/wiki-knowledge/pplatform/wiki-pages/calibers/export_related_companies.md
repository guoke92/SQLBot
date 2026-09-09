---
type: caliber
title: "导出关联核心企业/金融机构"
page_key: export_related_companies
belong: calibers
domain: "tenant-project"
status: published
aliases: ["关联企业导出口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [cust_project_rel.company_type, cust_project_rel.enable]
scope:
  databases: [lowcode_pplatform]
---

导出关联核心企业/金融机构口径用于项目运营配置导出的关联企业 Sheet，限定关联公司角色为 CORE 或 FINANCE 且逻辑有效。

## 需求背景
该口径来源于导出业务场景。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "导出关联核心企业/金融机构"
predicate: "cust_project_rel.enable = 'Y' AND cust_project_rel.company_type IN ('CORE','FINANCE')"
scope: "项目运营配置导出关联企业 Sheet"
evidence: "code_path:TenantProjectApplication.java:queryRelatedCompanies"
```

相关：[[cust_project_rel]] [[tenant_project]]