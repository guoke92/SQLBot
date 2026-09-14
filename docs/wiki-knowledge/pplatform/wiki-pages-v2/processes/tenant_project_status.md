---
type: process
title: 租户项目状态流转
page_key: tenant_project_status
domain: 租户项目
status: draft
aliases: [项目状态流转, tenant_project.project_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectStatusEnum
  - code:TenantProjectApplication
  - code:ProjectApprovalApplication
contract_version: "0.1"
belong: processes
---

描述 [[tenant_project]] 的 `project_status` 生命周期。取值定义见 [[ProjectStatusEnum]]，单态口径见 [[project_to_be_effective]]、[[project_effective]]、[[project_invalid]]。该状态与 [[project_approval_wf_status]] 存在耦合：上线审批终态通过会驱动项目生效或重新生效，而非新增项目正式发起上线审批会使已生效项目转为已失效。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目创建后处于待生效，需显式生效才能被业务引用；已生效项目在再次上线审批期间会先失效，审批通过后再回到已生效。

## 版本演进
语义分析未记录该状态机的版本演进。

```ground:process
name: 租户项目状态
field: tenant_project.project_status
states:
  - value: "0"
    label: 待生效
    source: code_enum
  - value: "1"
    label: 已生效
    source: code_enum
  - value: "2"
    label: 已失效
    source: code_enum
transitions:
  - from: "0"
    event: 项目生效
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:effective"
  - from: "1"
    event: 项目失效
    to: "2"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/TenantProjectApplication.java:invalid"
  - from: "1"
    event: 上线审批终态通过
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
  - from: "2"
    event: 上线审批终态通过重新生效
    to: "1"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished"
  - from: "1"
    event: 非新增项目正式发起上线审批
    to: "2"
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:663"
```