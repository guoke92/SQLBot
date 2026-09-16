---
type: scenario
title: 租户配置
page_key: tenant_config
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [租户设置, 灰度, 短链]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:租户配置/灰度/运营邮件", "code:page-plan.yaml:通知/验证码/短链"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [tenant_setting_config]
field_targets:
  - tenant_setting_config.status
  - tenant_setting_config.enable
---

# 租户配置

问「已生效租户 / 灰度开关 / 异步导入任务 / 短链」时进入本场景。

**主档** [[tenant_setting_config]]：读取普遍要求 `enable='Y'`。`status='Y'` 是已生效租户（`listActicveAll`）。`bg_color` 为灰度色值，不是 enable。  
从属：共享行 [[tenant_setting_config_share]]、异步任务 [[async_io_task]]、短链 [[short_link]]。  
`cust_message_send_policy` 库空且无 DO，本窗不展开。`open_sso_channel` 无业务写入，登录通道不在本表。

```ground:scenario
scenario: tenant_config
hubs:
- table: tenant_setting_config
  role: master
  grain: 一个租户配置
  window:
  - id
  - enable
  - create_time
  - update_time
  - status
  - bg_color
  - send_email
  - share_flag
  - source
  - db_tenant_code
- table: tenant_setting_config_share
  role: share
  grain: 共享配置行
  window:
  - id
  - enable
  - create_time
  - update_time
- table: async_io_task
  role: jobs
  grain: 一次导入导出
  window:
  - id
  - enable
  - create_time
  - update_time
  - status
  - is_deleted
- table: short_link
  role: links
  grain: 一条短链
  window:
  - id
  - enable
  - create_time
  - update_time
  - number
  - type
  - is_forever
  - expire_time
lifecycle:
- enum: async_io_status
  process: async_io_task_flow
shared: []
```
