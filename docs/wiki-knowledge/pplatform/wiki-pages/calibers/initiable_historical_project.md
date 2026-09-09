---
type: caliber
title: "可发起历史项目"
page_key: initiable_historical_project
belong: calibers
domain: "tenant-project"
status: published
aliases: ["历史项目可选口径"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.enable, tenant_project.project_status]
scope:
  databases: [lowcode_pplatform]
---

可发起历史项目口径用于历史项目发起上线审批向导中的可选项目列表，限定有效且项目状态在生效或失效的项目。

## 需求背景
该口径支撑历史项目重新发起审批的场景。证据来自 [代码]。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:caliber
name: "可发起历史项目"
predicate: "tenant_project.enable = 'Y' AND tenant_project.project_status IN ('EFFECTIVE','INVLIAD')"
scope: "历史项目发起上线审批向导可选项目"
evidence: "code_path:ProjectApprovalApplication.java:listApprovalSelectableProjects"
```

相关：[[tenant_project]] [[tenant_project_lifecycle]] [[approval_submit_only_pending]]