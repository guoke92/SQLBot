---
type: rule
title: 运营配置更新规则
page_key: operation-config-update-rule
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [运营配置更新规则, updateOperationConfigById]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.default_project_id, tenant_setting_config.op_update_time, tenant_setting_config.op_update_user, tenant_setting_config.operator_, tenant_setting_config.project_code_required, tenant_setting_config.send_email]
scope:
  databases: [lowcode_pplatform]
---

该规则描述租户运营相关字段的更新方式，包括将空字符串转为 NULL、保留原更新时间/更新人到运营更新人字段，并记录操作人。

## 需求背景

运营人员在维护租户邮件发送、项目码必填、默认项目等配置时，需要有统一的更新规则，确保数据一致性与审计可追溯。

## 版本演进

- 初版（v0.1）：基于 `TenantDomainService.updateOperationConfigById` 实现。

```ground:rule
name: 运营配置更新规则
content: "更新运营相关字段；空字符串转为NULL；保留原update_time/update_user到op_update_time/op_update_user；记录操作人"
impact: 更新tenant_setting_config运营字段
field_targets:
  - tenant_setting_config.operator_*
  - tenant_setting_config.send_email
  - tenant_setting_config.project_code_required
  - tenant_setting_config.default_project_id
  - tenant_setting_config.op_update_user
  - tenant_setting_config.op_update_time
evidence: "code_path:TenantDomainService.updateOperationConfigById"
```

[[tenant_setting_config]] [[bg_color]] [[任务状态]]