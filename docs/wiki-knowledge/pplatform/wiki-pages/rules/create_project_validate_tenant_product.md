---
type: rule
title: "创建项目校验租户与产品"
page_key: "rule/create_project_validate_tenant_product"
domain: "tenant-project"
status: published
aliases: ["创建项目校验"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.ref_tenant_project_product_code, tenant_project.ref_tenant_project_tenant_code]
scope:
  databases: [lowcode_pplatform]
---

创建租户项目前必须校验租户存在且租户已开通对应产品，否则抛出 BaseException。该规则阻断项目创建。

## 需求背景
规则来源于 TenantProjectApplication.create 中的校验逻辑，确保租户与产品关系有效。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "创建项目校验租户与产品"
content: "创建租户项目前必须校验租户存在且租户已开通对应产品，否则抛 BaseException"
impact: "阻断项目创建"
field_targets:
  - "tenant_project.ref_tenant_project_tenant_code"
  - "tenant_project.ref_tenant_project_product_code"
evidence: "code_path:TenantProjectApplication.java:create -> tenantService.getByCode / tenantProductDao.getByCode"
```

相关：[[tenant_project]] [[tenant_project_approval]]