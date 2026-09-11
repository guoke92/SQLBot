---
type: process
title: 项目上线审批节点状态流转
page_key: processes/project_approval_node_status
domain: 租户项目
status: draft
aliases: [项目上线审批节点状态, tenant_project_approval_flow.node_status, node_status]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
---

项目上线审批节点状态记录在 [[tables/tenant_project_approval_flow]] 的 node_status 列，随工作流推进由待处理变为审批中，节点通过后置为已通过。该状态同时是后补合作协议判断的前置条件，见 [[rules/back_agreement_check]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。从证据看，节点状态的用途是：让业务在「业务经理节点通过」这一刻得知可以开始判断后补合作协议。

## 版本演进
- 状态字面量只有 PENDING/APPROVING/APPROVED 三个，未见「驳回」态，驳回后的落库方式待确认。
- 未提供版本记录；无 (document_claim，未证实) 主张。

```ground:state_machine
name: 项目上线审批节点状态
field: tenant_project_approval_flow.node_status
states:
  - value: PENDING
    label: 待处理
    source: code_enum
  - value: APPROVING
    label: 审批中
    source: code_enum
  - value: APPROVED
    label: 已通过
    source: code_enum
transitions:
  - from: PENDING
    event: handleFlowAndNodeStatus 写入节点状态
    to: APPROVING
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:handleFlowAndNodeStatus"
  - from: APPROVING
    event: 业务经理节点通过且 is_back_agreement=Y 触发后补合作协议判断
    to: APPROVED
    evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:isStartBackAgreement"
```