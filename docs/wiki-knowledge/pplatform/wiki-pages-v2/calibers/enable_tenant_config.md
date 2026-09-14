---
type: caliber
title: 启用租户配置口径（enable='Y'）
page_key: enable_tenant_config
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [启用租户, enable='Y', 有效租户配置]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code:TenantDomainService.getFirstByDbTenantCode / getByTenantFlagEn / listAll / listActicveAll"
  - "db:tenant_setting_config.enable 364 行全为 Y"
contract_version: "0.1"
belong: calibers
---

「启用租户配置」是所有租户配置读取路径的共同前置条件：无论按 `db_tenant_code`、`tenant_flg_en`、`appTenantCode` 还是 `source + sourceId` 查询，命中结果都必须满足 `enable='Y'`。当前库内该列为全量 Y，因此该口径在数据上不产生过滤差异，但在契约上必须显式保留。

它与 [[tenant_effective]]（状态口径）正交：启用是「记录是否可用」，生效是「配置是否齐备」。表结构见 [[tenant_setting_config]]。

## 需求背景
租户停用后不应再被任何业务链路读取到配置，因此把启用判断下沉到统一的读取路径，避免各调用点自行处理。

## 版本演进
v0.1（本页）：首版契约，口径与证据来自语义分析；暂无历史版本记录。

```ground:caliber
name: 启用租户配置
predicate: "tenant_setting_config.enable = 'Y'"
scope: "所有按 dbTenantCode/tenantFlgEn/appTenantCode/source+sourceId 的租户配置读取路径"
evidence: "code:TenantDomainService.getFirstByDbTenantCode / getByTenantFlagEn / listAll / listActicveAll；db:enable 364 行全为 Y"
```