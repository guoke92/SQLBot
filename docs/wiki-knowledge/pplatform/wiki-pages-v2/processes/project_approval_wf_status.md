---
type: process
title: 项目上线审批工作流状态流转
page_key: project_approval_wf_status
domain: 租户项目
status: draft
aliases: [项目上线审批状态, tenant_project_approval.wf_status 状态机]
oid: 1
scope:
  databases: [lowcode-pplatform-customer-management]
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
belong: processes
---

描述 [[tenant_project_approval]] 的 `wf_status` 流转：待发起 → 审批中 → 已完成/已终止，暂存保持待发起。审批完成会触发 [[tenant_project_status]] 的生效/重新生效，口径见 [[approval_running]]。

## 需求背景
语义分析未附带需求文档锚点，依据代码证据归纳：项目上线必须先走审批，允许暂存（不进入 RUNNING），正式提交才启动工作流；终止与完成是两个不同终态。

## 版本演进
语义分析未记录该状态机的版本演进。

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
    label: 已完成
    source: code_enum
  - value: TERMINATED
    label: 已终止
    source: code_enum
transitions:
  - from: PENDING
    event: 正式提交并启动工作流
    to: RUNNING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:startWorkflowAndUpdateStatus"
  - from: PENDING
    event: 暂存
    to: PENDING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:submit"
  - from: RUNNING
    event: 审批完成
    to: FINISHED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: RUNNING
    event: 审批终止
    to: TERMINATED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
```

---REVIEW: process | 项目上线审批工作流状态流转---
语义分析未给出 `wf_status` 的枚举类名与表字段清单（仅给出字段引用），枚举页暂缺；需补充枚举类与完整取值后建 [[enums]] 页。
---END REVIEW---