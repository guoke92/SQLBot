---
type: enum
title: open_status
page_key: open_status
domain: CA证书认证
status: draft
aliases: [开通状态, ca_register_status]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:OpenStatus.java", "code:ProductOpenStatusEnum.java", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [ca_register_status_flow, tenant_product_open_flow, interworking_open_flow]
---

# open_status

Y 已开通 / P 开通中 / N 未开通。同一套键出现在：

- 企业 CA：[[cust_company_info]].ca_register_status（`OpenStatus`，流转 [[ca_register_status_flow]]）
- 租户通用产品：[[tenant_product]].open_status（`ProductOpenStatusEnum`，流转 [[tenant_product_open_flow]]）
- 租户互通产品：[[tenant_interworking_product]].open_status（流转 [[interworking_open_flow]]）

列各有自己的过程。企业开通产品用 [[cust_product_active]]（NOT_OPENED/OPENING/OPENED），不要接到本字典。含 `P`，不是 [[enable]]。收费台账证书观感是 [[ca_status]]。

```ground:enum
enum: open_status
fields:
  - cust_company_info.ca_register_status
  - tenant_product.open_status
  - tenant_interworking_product.open_status
values:
  "Y":
    label: "已开通"
  "P":
    label: "开通中"
  "N":
    label: "未开通"
```
