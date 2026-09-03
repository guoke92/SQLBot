---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:tenant-project-lifecycle@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 项目状态不是 rule_status
page_key: 项目状态不是-rule_status
domain: 项目管理
field_targets:
- tenant_project.project_status
---
# 项目状态不是 rule_status

项目用 project_status 的 0/1/2；PENDING/ACTIVE/INACTIVE 属于 funding_rule_info.rule_status。

```ground:rule
rule: project-status-is-not-rule-status
field_targets:
- tenant_project.project_status
impact: query_constraint
content: 项目用 project_status 的 0/1/2；PENDING/ACTIVE/INACTIVE 属于 funding_rule_info.rule_status。
scope: 已生效项目、待生效项目
```

## 关联
- [[tenant_project]]
