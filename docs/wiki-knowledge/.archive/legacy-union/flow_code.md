---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:project-online-approval@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 流程配置编码
page_key: flow_code
domain: 项目审批
aliases:
- 无需上线审批
- 标准流程
- 常规流程
anchors:
- flow_code
---
# 流程配置编码

NO_ONLINE 无需上线审批 / STANDARD 标准项目流程 / REGULAR 常规项目流程。

```ground:enum
enum: flow_code
fields:
- tenant_project_approval.flow_code
values:
  NO_ONLINE:
    label: 无需上线审批
  STANDARD:
    label: 标准项目流程
  REGULAR:
    label: 常规项目流程
```

## 关联
- [[tenant_project_approval|tenant_project_approval]]
