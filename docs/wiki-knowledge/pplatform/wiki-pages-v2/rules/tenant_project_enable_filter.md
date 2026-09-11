---
type: rule
title: 租户项目仅取有效记录
page_key: rules/tenant_project_enable_filter
domain: 租户项目
status: draft
aliases: [enable='Y', 租户项目逻辑删除]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
contract_version: "0.1"
---

该规则规定 [[tables/tenant_project]] 的读取一律限定 enable='Y'，删除走 domainService.delete（逻辑删除）。它决定上游看到的项目集合，是 [[calibers/project_effective]] 的实现依据。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则影响项目列表、导出与按产品同步等所有查询场景。

## 版本演进
以逻辑删除替代物理删除后，任何绕过 enable 过滤的自定义 SQL 都会读到已删除项目，属需要长期守住的约束；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 租户项目读取限定 enable='Y'
table: tenant_project
fields: [enable]
statement: 代码查询与导出普遍限定 enable='Y'，删除操作调用 domainService.delete
evidence: code
```