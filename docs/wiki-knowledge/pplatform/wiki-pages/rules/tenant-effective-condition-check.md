---
type: rule
title: 租户生效条件校验
page_key: tenant-effective-condition-check
belong: rules
domain: tenant-config-operation-email
status: published
aliases: [租户生效条件校验, effective]
oid: 1
sources: [code]
contract_version: "0.1"
field_targets: [tenant_setting_config.status]
scope:
  databases: [lowcode_pplatform]
---

租户生效前必须完成多项配置校验，包括合同模板、消息模板、平台运营方、产品配置、门户页配置、基础信息配置等。全部通过后设置 `status=Y`。

## 需求背景

租户进入生效状态前，需要确保相关依赖配置齐备。若任一校验未通过，返回 `WindowAlertDTO` 提示并保持 `status` 不变。

## 版本演进

- 初版（v0.1）：由 `TenantDomainService.effective` 实现。

```ground:rule
name: 租户生效条件校验
content: "校验合同模板、消息模板（通知/待办/短信）、平台运营方、产品配置、门户页配置、基础信息配置，全部通过后设置status=Y"
impact: 未通过时返回WindowAlertDTO提示，不更新status
field_targets:
  - tenant_setting_config.status
evidence: "code_path:TenantDomainService.effective"
```

[[tenant_setting_config]] [[任务状态]] [[tenant-status]]