---
type: caliber
title: 关联审批编号下拉
page_key: related_approval_no_options
domain: 微企链立项与项目审批
status: draft
aliases:
  - 关联审批编号可选范围
oid: 1
scope:
  databases:
    - tenant_project
sources:
  - code_path:ProjectApprovalApplication.java:listRelatedApprovalNo
contract_version: "0.1"
belong: calibers
---

「关联审批编号」下拉的可选范围：仅列出处于审批中或审批通过、且为线上审批、且记录启用的上线审批。

```ground:caliber
name: 关联审批编号下拉
predicate: tenant_project_approval.wf_status IN ('RUNNING','FINISHED') AND tenant_project_approval.is_online_approval = 'Y' AND tenant_project_approval.enable = 'Y'
scope: 关联审批编号下拉
evidence: code_path:ProjectApprovalApplication.java:listRelatedApprovalNo
```

## 需求背景

该口径限定可被关联的审批编号只能是「进行中」或「已完成」的线上审批，见 [[tenant_project_approval]] 与 [[processes/tenant_project_approval_wf_status]]。

## 版本演进

当前语义分析未提供该口径的历史变更记录。