---
type: scenario
title: 租户迁移
page_key: tenant_migration
domain: 租户迁移
status: draft
aliases: [推数, 迁入]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:租户迁移"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_migarory_log]
field_targets:
  - tenant_migarory_log.status
  - tenant_migarory_log.direction
---

# 租户迁移

问「迁移失败 / 出向可重推 / 存量用户未首登」时进入本场景。表名拼写以库为准（`migarory`）。

**主档** [[tenant_migarory_log]]。`pushByLog` 只处理 `direction='OUT'`。  
**从属** [[migratory_user_record]]：`is_login='N'` 表示迁移用户尚未首登。  
`tenant_migarory_log_bak` 无 Java 引用，本窗不展开。迁移来源企业在主档 `cust_source='MIGRATORY'`。

```ground:scenario
scenario: tenant_migration
hubs:
- table: tenant_migarory_log
  role: master
  grain: 一次迁移/推数
  window:
  - id
  - enable
  - create_time
  - update_time
  - direction
  - status
  - type
  - name
  - req_no
  - platform_product_code
- table: migratory_user_record
  role: users
  grain: 一个迁移用户
  window:
  - id
  - enable
  - create_time
  - update_time
  - user_id
  - is_login
  - db_tenant_code
shared:
- table: cust_company_info
  role: migrated_company
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - cust_source
  - cust_status
  - cust_build_status
lifecycle:
- enum: enable
  process: migratory_log_status_flow
  field: tenant_migarory_log.status
```
