---
type: rule
title: "正式提交必须有有效审批节点和文件"
page_key: "rule/formal_submit_requires_valid_nodes_and_files"
domain: "tenant-project"
status: published
aliases: ["提交节点文件校验"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

非草稿提交时审批流程至少一个有效审批节点，且 MA003 审批文件目录和 OA_BUSI_PRICE 文件目录必须有文件。该规则阻断提交。

## 需求背景
规则来源于 ProjectApprovalApplication.validateSubmitFlowApprovers 方法，保证提交时审批流程完整。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "正式提交必须有有效审批节点和文件"
content: "非草稿提交时审批流程至少一个有效审批节点，且 MA003 审批文件目录和 OA_BUSI_PRICE 文件目录必须有文件"
impact: "阻断提交"
field_targets:
  - "tenant_project_approval_flow.id"
  - "media 文件"
evidence: "code_path:ProjectApprovalApplication.java:validateSubmitFlowApprovers"
```

相关：[[tenant_project_approval_flow]] [[project_online_approval_node_status]] [[approval_running_config_receivable]]