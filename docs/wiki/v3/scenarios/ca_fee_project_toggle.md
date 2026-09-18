---
type: scenario
title: 项目开启或关闭 CA 收费
page_key: ca_fee_project_toggle
belong: scenarios
domain: ca_fee
status: draft
aliases: [收费开关]
sources: ['code_path:l1_intermediate']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [ca_fee_project_config, tenant_project]
---

# 项目开启或关闭 CA 收费

保存项目配置写 charge_enabled。开启后异步扫描存量建单；关闭关待缴订单。

```ground:scenario
scenario: ca_fee_project_toggle
hubs:
- table: ca_fee_project_config
  role: master
shared:
- table: tenant_project
  role: project
```

## 页面链接

- [[tables/ca_fee_project_config]]
- [[tables/tenant_project]]
