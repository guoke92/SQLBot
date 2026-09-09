---
type: rule
title: "创建项目时自动创建上线审批草稿"
page_key: create_project_auto_create_approval_draft
belong: rules
domain: "tenant-project"
status: published
aliases: ["自动创建审批草稿"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.is_add, tenant_project_approval.wf_status]
scope:
  databases: [lowcode_pplatform]
---

当 isAdd=Y、上线审批挡板开启且平台产品支持在线审批时，项目创建后自动创建 wf_status=PENDING 的上线审批记录，并关联到项目的 project_approval_id。

## 需求背景
规则来源于项目创建后的自动化审批初始化逻辑，覆盖新增项目场景。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "创建项目时自动创建上线审批草稿"
content: "当 isAdd=Y、上线审批挡板开启且平台产品支持在线审批时，项目创建后自动创建 wf_status=PENDING 的上线审批记录"
impact: "tenant_project_approval 插入记录；项目project_approval_id 关联"
field_targets:
  - "tenant_project.is_add"
  - "tenant_project_approval.wf_status"
evidence: "code_path:TenantProjectApplication.java:tryCreateInitialApprovalOnProjectCreate + ProjectApprovalApplication.java:createInitialApproval"
```

相关：[[tenant_project]] [[tenant_project_approval]] [[project_online_approval_workflow]]