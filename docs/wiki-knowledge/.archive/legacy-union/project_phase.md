---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:wechat-project-initiation@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 项目阶段
page_key: project_phase
domain: 项目审批
aliases:
- 立项阶段
- 实施
- 运营
- 挂起
- 项目阶段初值
- 持续运营
- 阶段升级
anchors:
- project_phase
---
# 项目阶段

project_phase 由 sp_status 派生初值（1→INITIATION、2→IMPLEMENTATION、3/4/6/7→HANG、其他默认 IMPLEMENTATION）；洞察回写时升级：仅 sp_status=2 处理，HANG 不覆盖，无首笔落地时间→IMPLEMENTATION、有→OPERATION。仅状态=2 处理洞察回写。

```ground:enum
enum: project_phase
fields:
- wechat_project_approval_apply.project_phase
values:
  INITIATION:
    label: 立项阶段
  IMPLEMENTATION:
    label: 实施阶段
  OPERATION:
    label: 运营阶段
  HANG:
    label: 挂起
```

## 关联
- [[wechat_project_approval_apply|wechat_project_approval_apply]]
