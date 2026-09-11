---
type: caliber
title: 已生效租户
page_key: caliber.effective_tenant
domain: 租户配置
status: draft
aliases:
  - 已生效租户
  - activeList
oid: 1
scope:
  databases:
    - lowcode-pplatform-tenant-management
sources:
  - db:tenant_setting_config.status
  - code:lowcode-pplatform-tenant-management/src/main/java/com/lls/lowcode/pplatform/tenant/service/TenantDomainService.java:listActicveAll
contract_version: "0.1"
---

「已生效租户」= `status='Y'` 且 `enable='Y'`，用在生效租户列表（activeList）与租户生效校验上。由于 `status='N'`（待生效）在存量中占多数，漏写任一条件都会显著改变结果集，因此本口径必须两条件并列，不能退化为 [[calibers/enabled_tenant]]。

## 需求背景

租户从待生效到已生效是人工推进的过程（见 [[processes/tenant_status_effective]]），下游只应消费已生效租户，因此需要一个可直接下推到 SQL 的组合口径。

## 版本演进

v0.1：依据 `listActicveAll` 的查询条件建立口径。

```yaml
caliber: 已生效租户
predicate: "tenant_setting_config.status = 'Y' AND tenant_setting_config.enable = 'Y'"
scope: activeList 生效租户列表 / 租户生效校验
evidence: "code:TenantDomainService.java:listActicveAll"
```

相关页面：[[tables/tenant_setting_config]]、[[processes/tenant_status_effective]]、[[calibers/enabled_tenant]]、[[concepts/enable]]。