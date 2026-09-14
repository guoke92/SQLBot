---
type: caliber
title: 迁移占位审批状态口径（act_procinst_status='N'）
page_key: tenant_migratory_approval_placeholder
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [迁移占位审批状态, act_procinst_status='N']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.syncTenant#L217"
  - "db:act_procinst_status N=204"
contract_version: "0.1"
belong: calibers
---

迁移租户落库时把审批流程实例状态写为 N，形成「占位审批」状态，用以避免触发新增 create 事件。它是迁移链路与自建链路的区分口径之一。

迁移链路整体见 [[tenant_status_effective]] 的空状态迁移；表结构见 [[tenant_setting_config]]。

## 需求背景
存量迁移不允许再次对外广播新增事件，因此需要一个可识别的占位审批状态来短路事件触发。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 迁移占位审批状态
predicate: "tenant_setting_config.act_procinst_status = 'N'"
scope: "syncTenant 迁移租户，避免触发新增 create 事件"
evidence: "code:TenantAppliactionService.syncTenant#L217；db:N=204"
```