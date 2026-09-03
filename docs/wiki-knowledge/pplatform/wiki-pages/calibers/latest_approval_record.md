---
type: caliber
title: "最新审批记录"
page_key: "caliber/latest_approval_record"
domain: "tenant-project"
status: published
aliases: ["最新审批口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project_approval.enable, tenant_project_approval.is_latest]
scope:
  databases: [lowcode_pplatform]
---

最新审批记录口径用于项目最新上线审批的查询、复制和详情，限定 is_latest 与 enable 均为 Y 的记录。

## 需求背景
该口径确保业务操作针对项目最新的审批记录。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "最新审批记录"
predicate: "tenant_project_approval.is_latest = 'Y' AND tenant_project_approval.enable = 'Y'"
scope: "项目最新上线审批查询/复制/详情"
evidence: "code_path:ProjectApprovalApplication.java:findLatestApprovalByProjectCode"
```

相关：[[tenant_project_approval]] [[project_online_approval_workflow]]