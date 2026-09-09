---
type: rule
title: 租户信息推送规则
page_key: tenant-info-push-rule
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [租户信息推送规则, pushTenant]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.pushing_status]
scope:
  databases: [lowcode_pplatform]
---

该规则控制租户信息推送事件的顺序：非 CREATED 事件必须等待 CREATED 事件推送成功（`pushing_status=Y`）后才允许推送，否则跳过。

## 需求背景

租户事件需要有序传递，先 CREATE 后 UPDATE 等，否则下游系统可能无法正确处理。通过 `pushing_status` 标记保证顺序。

## 版本演进

- 初版（v0.1）：由 `TenantAppliactionService.pushTenant` 实现。

```ground:rule
name: 租户信息推送规则
content: "非CREATED事件必须等待CREATED事件推送成功（pushing_status=Y）后才推送，否则跳过"
impact: 控制事件推送顺序
field_targets:
  - tenant_setting_config.pushing_status
evidence: "code_path:TenantAppliactionService.pushTenant"
```

[[tenant_setting_config]] [[pushed-created-event-tenant]]