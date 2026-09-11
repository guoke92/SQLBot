---
type: caliber
title: 启用租户
page_key: caliber.enabled_tenant
domain: 租户配置
status: draft
aliases:
  - 启用租户
  - enable='Y' 租户
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.enable
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java
contract_version: "0.1"
---

「启用租户」是所有租户查询的默认底座口径：`getFirstByDbTenantCode`、`getById`、`listActicveAll` 等入口都在 SQL 上拼接 `enable='Y'`。注意它与「生效」不是同一件事——`enable` 是记录启用态（存量数据实测全部为 Y），`status` 才是租户业务生效态，见 [[calibers/effective_tenant]]。

## 需求背景

租户记录存在停用需求，但历史数据几乎都是启用态，因此把 `enable` 固化为查询常量条件，避免各入口遗漏造成已停用租户被读取。

## 版本演进

v0.1：依据代码中统一过滤条件与 DB 实测分布（全为 Y）建立口径。

```yaml
caliber: 启用租户
predicate: "tenant_setting_config.enable = 'Y'"
scope: 所有租户查询（getFirstByDbTenantCode / getById / listActicveAll 等）
evidence: db + code:TenantDomainService.java
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/enable]]、[[calibers/effective_tenant]]。