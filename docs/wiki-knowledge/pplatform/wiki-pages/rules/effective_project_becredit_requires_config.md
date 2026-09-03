---
type: rule
title: "生效项目前 BEECREDIT 必须完善项目配置"
page_key: "rule/effective_project_becredit_requires_config"
domain: "tenant-project"
status: published
aliases: ["BEECREDIT 配置校验"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.config_json, tenant_project.project_status]
scope:
  databases: [lowcode_pplatform]
---

信用卡产品（BEECREDIT）生效项目时，config_json 不能为空且每个项目配置状态须为 EFFECTIVE 或 Y；生效后跳过 PROJECT_SYNC 事件推送。该规则阻断 BEECREDIT 项目生效。

## 需求背景
规则来源于 TenantProjectApplication.effective 方法，确保 BEECREDIT 项目配置完备。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "生效项目前 BEECREDIT 必须完善项目配置"
content: "信用卡产品(BEECREDIT)生效项目时，config_json 不能为空且每个项目配置状态须为 EFFECTIVE 或 Y；生效后跳过 PROJECT_SYNC 事件推送"
impact: "阻断 BEECREDIT 项目生效"
field_targets:
  - "tenant_project.config_json"
  - "tenant_project.project_status"
evidence: "code_path:TenantProjectApplication.java:effective"
```

相关：[[tenant_project]] [[tenant_project_lifecycle]] [[tenant-effective-condition-check]]