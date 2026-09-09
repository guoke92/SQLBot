---
type: rule
title: "上线审批仅 PENDING 可发起/暂存"
page_key: approval_submit_only_pending
belong: rules
domain: "tenant-project"
status: published
aliases: ["审批提交状态校验"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project_approval.wf_status]
scope:
  databases: [lowcode_pplatform]
---

正式提交或暂存上线审批前必须校验 wf_status=PENDING，否则抛出 BaseException。该规则阻断非待审批状态的操作。

## 需求背景
规则来源于 ProjectApprovalApplication.submit 方法，确保审批状态合规。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "上线审批仅 PENDING 可发起/暂存"
content: "正式提交或暂存上线审批前必须校验 wf_status=PENDING，否则抛 BaseException"
impact: "阻断非待审批状态操作"
field_targets:
  - "tenant_project_approval.wf_status"
evidence: "code_path:ProjectApprovalApplication.java:submit"
```

相关：[[tenant_project_approval]] [[project_online_approval_workflow]] [[approval_in_progress]]