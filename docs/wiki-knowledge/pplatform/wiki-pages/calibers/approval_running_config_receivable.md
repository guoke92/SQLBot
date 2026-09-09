---
type: caliber
title: "审批中且可接收业务配置"
page_key: approval_running_config_receivable
belong: calibers
domain: "tenant-project"
status: published
aliases: ["业务配置接收口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project_approval.wf_status, tenant_project_approval_flow.node_code, tenant_project_approval_flow.node_status]
sources: ["enrich:wiki-admin"]
scope:
  databases: [lowcode_pplatform]
---

审批中且可接收业务配置口径用于业务系统推送项目运营配置落库，限定审批状态为 RUNNING，节点状态为 APPROVING，且节点编码在指定集合内。

## 需求背景
该口径支撑业务配置推送的落库校验。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "审批中且可接收业务配置"
predicate: "tenant_project_approval.wf_status = 'RUNNING' AND tenant_project_approval_flow.node_status = 'APPROVING' AND tenant_project_approval_flow.node_code IN ('PROJECT_MANAGER','PROJECT_CONFIG')"
scope: "业务系统推送项目运营配置落库"
evidence: "code_path:ProjectBusinessConfigApplication.java:savePush"
```

相关：[[tenant_project_approval_flow]] [[project_online_approval_node_status]] [[formal_submit_requires_valid_nodes_and_files]]

相关：[[tenant_project_approval]]
