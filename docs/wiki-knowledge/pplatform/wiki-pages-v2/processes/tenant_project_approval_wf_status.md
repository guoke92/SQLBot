---
type: process
title: 项目上线审批工作流状态
page_key: tenant_project_approval_wf_status
domain: 微企链立项与项目审批
status: draft
aliases:
  - wf_status
  - 上线审批工作流状态
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - db:tenant_project_approval
  - code_path:ProjectApprovalApplication.java
contract_version: "0.1"
belong: processes
---

[[tenant_project_approval]] 上的工作流状态，描述一次上线审批从草稿待发起，到审批中，再到终态（通过或拒绝）的推进。它是重新发起、项目生效、AMS 推送等一系列动作的触发条件。

```ground:process
name: 项目上线审批工作流状态
field: tenant_project_approval.wf_status
states:
  - value: PENDING
    label: 待发起
    source: code_enum
  - value: RUNNING
    label: 审批中
    source: code_enum
  - value: FINISHED
    label: 审批通过
    source: code_enum
  - value: TERMINATED
    label: 审批拒绝
    source: code_enum
  - value: REVOKED
    label: 已撤销
    source: db_dist
transitions:
  - from: PENDING
    event: 启动工作流
    to: RUNNING
    evidence: code_path:ProjectApprovalApplication.java:startWorkflowAndUpdateStatus
  - from: RUNNING
    event: 审批通过
    to: FINISHED
    evidence: code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus
  - from: RUNNING
    event: 审批拒绝/驳回
    to: TERMINATED
    evidence: code_path:ProjectApprovalApplication.java:handleFlowAndNodeStatus
```

## 需求背景

暂存不启动工作流、提交才生成审批编号并启动，见 [[rules/online_approval_submit]]；重新发起时新审批以 `PENDING` 起步并置 `is_latest=Y`，见 [[rules/reinitiate_online_approval_copy]]；终态 `FINISHED` 触发项目生效与下游推送，见 [[rules/effective_project_on_approval_finished]] 与 [[rules/push_to_ams]]；仅 `RUNNING` 且为最新版本的审批会被业务系统定位到，见 [[calibers/running_latest_approval]]。

## 版本演进

代码枚举声明了 PENDING/RUNNING/FINISHED/TERMINATED 四个值，DB 分布中另有 `REVOKED`（已撤销）未被枚举覆盖，该状态的产生入口与后续处理在本次分析中未见证据。