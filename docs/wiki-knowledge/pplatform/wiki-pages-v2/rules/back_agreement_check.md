---
type: rule
title: 后补合作协议判断触发条件
page_key: back_agreement_check
domain: 租户项目
status: draft
aliases: [is_back_agreement, 后补合作协议]
oid: 1
scope:
  databases: []
sources:
  - code:ProjectApprovalApplication
contract_version: "0.1"
belong: rules
---

该规则规定当 [[tables/tenant_project_approval_flow]] 中业务经理节点通过且 is_back_agreement=Y 时，触发后补合作协议的判断，对应节点状态进入 APPROVED，见 [[processes/project_approval_node_status]]。

## 需求背景
本次语义分析未提供需求文档主张，本节不含 (document_claim，未证实) 条目。该规则把审批节点结果与协议补签动作绑定，是审批链路的下游分支。

## 版本演进
触发条件同时依赖节点状态与 is_back_agreement 标志，说明协议补签是后加的可选分支；未提供版本记录，无 (document_claim，未证实) 主张。

```ground:rule
name: 后补合作协议判断触发条件
table: tenant_project_approval_flow
fields: [node_status]
statement: 业务经理节点通过且 is_back_agreement=Y 触发后补合作协议判断
evidence: "code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/approval/ProjectApprovalApplication.java:isStartBackAgreement"
```