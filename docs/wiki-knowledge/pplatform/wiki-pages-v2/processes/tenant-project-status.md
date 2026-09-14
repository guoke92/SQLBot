---
type: process
title: 租户项目状态机
page_key: tenant-project-status
domain: 微企链立项与项目审批
status: draft
aliases:
  - 租户项目状态
  - tenant_project.project_status
oid: 1
scope:
  databases:
    - 未在语义分析中给出物理库名
sources:
  - code_path:ProjectApprovalApplication.java#effectiveProjectOnApprovalFinished
  - code_path:ProjectApprovalApplication.java#invalidateHistoricalProjectOnSubmit
contract_version: "0.1"
belong: processes
---

租户项目状态是上线审批的下游结果：审批走到终态通过时，对应租户项目被置为已生效；非新增项目正式发起上线审批时，历史项目被置为已失效。也就是说，同一个项目在「重新走一遍上线审批」的过程中会先失效、通过后再生效。

本状态机所依附的表 `tenant_project` 未在本次语义分析中给出字段级证据，其表名字面也未在 DB 实测中出现，因此本页状态与流转按 DO `TenantProjectDO` 与系统文档标注，仅作结构登记，不作为字段级契约使用。上游见 [[processes/project-approval-workflow-status]]。

## 需求背景

本次语义分析未提供需求文档（reqdoc）主张，本章无已证实的需求来源。

## 版本演进

- 失效路径 `invalidateHistoricalProjectOnSubmit` 在本次给出的代码切片内未见调用点，需核实调用方（见文末 REVIEW）。
- 枚举名拼写 `ProjectStatusEnum.INVLIAD`（已失效）按代码原样登记，疑为历史拼写。

```ground:process
name: 租户项目状态（表名字面未在本层 DB 实测出现，按 DO TenantProjectDO/系统文档标注）
field: tenant_project.project_status
states:
  - value: ProjectStatusEnum.EFFECTIVE
    label: 已生效
    source: code_enum
  - value: ProjectStatusEnum.INVLIAD
    label: 已失效（代码枚举拼写如此）
    source: code_enum
transitions:
  - from: "—"
    event: 上线审批终态通过 effectiveProjectOnApprovalFinished → tenantProjectApplication.effective
    to: ProjectStatusEnum.EFFECTIVE
    evidence: "code_path:ProjectApprovalApplication.java#effectiveProjectOnApprovalFinished"
  - from: ProjectStatusEnum.EFFECTIVE/ProjectStatusEnum.INVLIAD
    event: 非新增项目正式发起上线审批 invalidateHistoricalProjectOnSubmit → tenantProjectApplication.invalid
    to: ProjectStatusEnum.INVLIAD
    evidence: "code_path:ProjectApprovalApplication.java#invalidateHistoricalProjectOnSubmit（注意：该方法在当前给出的代码切片内未见调用点，需核实调用方）"
```