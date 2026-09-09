---
type: caliber
title: "审批进行中"
page_key: approval_in_progress
belong: calibers
domain: "tenant-project"
status: published
aliases: ["审批中口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project_approval.enable, tenant_project_approval.wf_status]
scope:
  databases: [lowcode_pplatform]
---

审批进行中口径用于防止重复发起审批，限定审批状态为 PENDING 或 RUNNING 且逻辑有效的记录。

## 需求背景
该口径来源于发起审批前的校验逻辑。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "审批进行中"
predicate: "tenant_project_approval.wf_status IN ('PENDING','RUNNING') AND tenant_project_approval.enable = 'Y'"
scope: "防止重复发起审批"
evidence: "code_path:ProjectApprovalApplication.java:assertNoApproval"
```

相关：[[tenant_project_approval]] [[approval_submit_only_pending]]