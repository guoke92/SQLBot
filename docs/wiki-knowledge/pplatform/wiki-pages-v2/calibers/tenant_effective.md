---
type: caliber
title: 已生效租户口径（status='Y'）
page_key: tenant_effective
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [已生效租户, status='Y', 生效租户列表]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.listActicveAll"
  - "db:tenant_setting_config.status Y=124 / N=240"
contract_version: "0.1"
belong: calibers
---

「已生效租户」用于生效租户列表与导出状态展示，判定条件为 `status='Y'`。该值只由 [[tenant_status_effective]] 状态机在八项配置校验通过后回写，因此它同时是一份「配置齐备度」的代理指标。

与 [[tenant_pending_effective]] 互为补集（注意空状态不落在 N 上）。表结构见 [[tenant_setting_config]]。

## 需求背景
运营与导出场景需要一份可信的生效租户名单，直接用状态列筛选，避免每次重算配置齐备度。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 已生效租户
predicate: "tenant_setting_config.status = 'Y'"
scope: "activeList() 生效租户列表、导出状态展示"
evidence: "code:TenantDomainService.listActicveAll；db:Y=124 / N=240"
```