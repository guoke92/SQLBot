---
type: process
title: 租户生效状态
page_key: processes.tenant-status
domain: tenant-config-operation-email
status: published
aliases: [租户生效状态, tenant_setting_config.status]
oid: 1
sources: [db_dist, code]
contract_version: "0.1"
field_targets: [tenant_setting_config.status]
scope:
  databases: [lowcode_pplatform]
---

租户生效状态由 `tenant_setting_config.status` 字段表达，取值 N（未生效/待生效）与 Y（已生效）。状态切换由租户生效条件校验完成后触发，是租户运营流程中的关键节点。

## 需求背景

租户在完成基础配置与依赖校验后，需通过生效动作将状态从 N 切换为 Y，从而正式进入可用状态。该状态影响租户列表查询与业务操作边界。

## 版本演进

- 初版（v0.1）：由 `TenantDomainService.effective` 实现 N->Y 切换，具体行号未标。

```ground:process
name: 租户生效状态
field: tenant_setting_config.status
states:
  - value: N
    label: 未生效/待生效
    source: db_dist
  - value: Y
    label: 已生效
    source: db_dist
transitions:
  - from: N
    event: effective
    to: Y
    evidence: "code_path:TenantDomainService.effective:TenantDomainService.java:行号未标（设置status为BooleanEnum.Y）"
```

[[tenant_setting_config]] [[任务状态]]