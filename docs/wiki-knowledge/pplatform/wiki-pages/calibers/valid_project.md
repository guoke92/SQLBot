---
type: caliber
title: "有效项目"
page_key: "caliber/valid_project"
domain: "tenant-project"
status: published
aliases: ["有效项目口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.enable]
scope:
  databases: [lowcode_pplatform]
---

有效项目口径用于项目导出、分页及详情查询，限定逻辑有效标识为 Y 的项目。

## 需求背景
该口径源于导出和查询场景，确保只对有效项目进行操作。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "有效项目"
predicate: "tenant_project.enable = 'Y'"
scope: "项目导出/分页/详情查询"
evidence: "code_path:TenantProjectApplication.java:exportProjectInfo -> queryWrapper.eq(enable,'Y')"
```

相关：[[tenant_project]] [[tenant-effective-condition-check]]