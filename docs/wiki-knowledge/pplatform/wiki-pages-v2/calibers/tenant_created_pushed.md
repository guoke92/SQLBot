---
type: caliber
title: 创建事件已推送口径（pushing_status='Y'）
page_key: tenant_created_pushed
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [创建事件已推送, pushing_status='Y']
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantAppliactionService.pushTenant"
contract_version: "0.1"
belong: calibers
---

「创建事件已推送」是租户事件推送链路的门控口径：只有 `pushing_status='Y'`（即 CREATED 事件已推送完成）的租户，才允许继续推送变更、生效等非 CREATED 事件。它保证事件顺序，避免下游先收到变更再收到创建。

表结构见 [[tenant_setting_config]]。

## 需求背景
租户事件按创建先行、变更/生效后至的顺序消费，必须有一个已推送标记做顺序门控。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 创建事件已推送
predicate: "tenant_setting_config.pushing_status = 'Y'"
scope: "pushTenant / pushTenantSync 中非 CREATED 事件的推送门控"
evidence: "code:TenantAppliactionService.pushTenant"
```