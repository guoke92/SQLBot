---
type: process
title: "租户项目生命周期"
page_key: "process/tenant_project_lifecycle"
domain: "tenant-project"
status: published
aliases: ["项目状态机"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

租户项目生命周期描述项目从生效到失效的状态变化及其触发事件，字段为 `tenant_project.project_status`。

## 需求背景
状态机基于 [代码] 枚举与转换逻辑提取，覆盖生效、失效及历史项目处理场景。

## 版本演进
v0.1 版本基于语义分析 [代码] 证据建立，后续需补充需求文档确认事件业务含义。

```ground:state_machine
name: "租户项目生命周期"
field: "tenant_project.project_status"
states:
  - value: "EFFECTIVE"
    label: "已生效"
    source: "code_enum"
  - value: "INVLIAD"
    label: "已失效"
    source: "code_enum"
transitions:
  - from: "__any__"
    event: "effective"
    to: "EFFECTIVE"
    evidence: "code_path:TenantProjectApplication.java:effective -> tenantProjectDomainService.effective"
  - from: "EFFECTIVE"
    event: "invalid"
    to: "INVLIAD"
    evidence: "code_path:TenantProjectApplication.java:invalid -> tenantProjectDomainService.invalid"
  - from: "__any__"
    event: "approval_finished"
    to: "EFFECTIVE"
    evidence: "code_path:ProjectApprovalApplication.java:effectiveProjectOnApprovalFinished -> TenantProjectApplication.effective"
  - from: "EFFECTIVE"
    event: "historical_submit"
    to: "INVLIAD"
    evidence: "code_path:ProjectApprovalApplication.java:invalidateHistoricalProjectOnSubmit -> TenantProjectApplication.invalid"
  - from: "INVLIAD"
    event: "historical_submit"
    to: "INVLIAD"
    evidence: "code_path:ProjectApprovalApplication.java:invalidateHistoricalProjectOnSubmit"
```

相关：[[tenant_project]] [[tenant-effective-condition-check]] [[invalid]] [[effective_project_becredit_requires_config]]