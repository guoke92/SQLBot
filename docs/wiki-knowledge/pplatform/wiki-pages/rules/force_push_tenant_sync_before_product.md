---
type: rule
title: 运营方开通产品推送前强制同步租户
page_key: force_push_tenant_sync_before_product
domain: 租户迁移
status: published
aliases: []
oid: 1
sources: ["code", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [tenant_migarory_log.type]
scope:
  databases: [lowcode_pplatform]
---

# 运营方开通产品推送前强制同步租户

业务定位：确保在运营方开通产品并推送至业务系统前，租户数据已经先行同步，降低下游数据不一致风险。

## 需求背景

运营方开通产品后、推送业务系统前，系统调用 `forcePushTenantSync` 确保租户信息先到达。此外，迁移客户时按产品自动开通产品（`PlatFormMigratoryApplication.java:migratoryCust` 中调用 `custProductApplicationService.autoActiveProduct`），体现了产品自动开通与租户同步的联动。

## 版本演进

暂无。

```ground:rule
name: 运营方开通产品推送前强制同步租户
content: 运营方开通产品后推送业务系统前，先调用 forcePushTenantSync 确保租户信息先到达
impact: 保障租户数据同步顺序，降低下游数据不一致风险
field_targets:
  - tenant_migarory_log.type
  - CustCompanyInfoDO.custCompanyType
evidence:
  - "code_path:CustProductDomainService.java:autoActiveProduct"
  - "code_path:PlatFormMigratoryApplication.java:migratoryCust 调用 custProductApplicationService.autoActiveProduct + reqdoc:迁移客户按产品自动开通产品"
```

相关：[[tenant_migarory_log]]
