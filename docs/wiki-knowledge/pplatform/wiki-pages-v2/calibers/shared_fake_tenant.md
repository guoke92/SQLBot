---
type: caliber
title: 共享假租户
page_key: shared_fake_tenant
domain: 租户配置
status: draft
aliases:
  - 假租户
  - 共享租户
  - existEarlyLLsTenant
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.share_flag
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:existEarlyLLsTenant
contract_version: "0.1"
belong: calibers
---

共享假租户判定条件是 `share_flag='Y'` 且本次请求的 `tenant_flg_en` 与配置行不一致：此时 `syncTenant` 不写 `tenant_setting_config`，而改写 `tenant_setting_config_share`。该口径解释了为什么同一个 [[concepts/db_tenant_code]] 下可能存在多个 [[concepts/tenant_flg_en]]——共享租户复用同一数据租户，但以不同项目标识对外。

## 需求背景

同一数据库租户下要承载多个项目标识（品牌）的共享配置，若直接写主表会互相覆盖，因此引入独立的共享配置表与写入分支。

## 版本演进

v0.1：依据 `existEarlyLLsTenant` 与 `share_flag` 字段语义建立口径。

```yaml
caliber: 共享假租户
predicate: "tenant_setting_config.share_flag = 'Y' AND tenant_flg_en <> 请求 tenantFlgEn"
scope: syncTenant 时写入 tenant_setting_config_share 而非 tenant_setting_config
evidence: "code:TenantDomainService.java:existEarlyLLsTenant"
```

相关页面：[[tables/tenant_setting_config]]、[[concepts/db_tenant_code]]、[[concepts/tenant_flg_en]]、[[calibers/lls_self_tenant]]。