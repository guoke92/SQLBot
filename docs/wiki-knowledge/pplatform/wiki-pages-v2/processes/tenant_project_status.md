---
type: process
title: 租户项目启停流转
page_key: processes/tenant_project_status
domain: 租户项目
status: draft
aliases: [租户项目状态, tenant_project.project_status, 项目生效失效]
oid: 1
scope:
  databases: []
sources:
  - code:TenantProjectApplication
  - code:ProjectApprovalApplication
  - code:ProjectStatusEnum
contract_version: "0.1"
---

租户项目状态记录在 [[tables/tenant_project]] 的 project_status 列，代码中只有两个值：ProjectStatusEnum.EFFECTIVE（已生效）与 ProjectStatusEnum.INVLIAD（已失效）。项目可通过 effective/invalid 双向操作，也可由上线审批完成自动回到生效，见 [[rules/effective_on_approval_finished]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，该流程要解决的是「项目建好后由谁、在什么条件下对外生效」的问题，审批链路见 [[processes/project_approval_workflow_status]]。

## 版本演进
- project_status 的枚举拼写为 INVLIAD（非 INVALID），属代码既有拼写，改动前需评估兼容。
- 「未生效」仅作为迁移起点出现，没有对应的枚举字面量。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 租户项目状态
field: tenant_project.project_status
states:
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
  - value: INVLIAD
    label: 已失效
    source: code_enum
transitions:
  - from: 未生效
    event: effective 生效项目
    to: EFFECTIVE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:effective"
  - from: EFFECTIVE
    event: invalid 失效项目
    to: INVLIAD
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:invalid"
  - from: INVLIAD
    event: 上线审批完成通过后 effectiveProjectOnApprovalFinished 调 effective
    to: EFFECTIVE
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
```

有效性的口径（enable 与 project_status 的组合）见 [[calibers/project_effective]]。