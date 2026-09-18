---
type: dict
title: platform_product_client.client_type
page_key: platform_product_client__client_type
belong: dicts
status: draft
anchors: [platform_product_client.client_type]
sources: ['database_profile:platform_product_client.client_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [platform_product_client]
---

# platform_product_client.client_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `platform_product_client.client_type`，表页 [[tables/platform_product_client]]。

## 取值

```ground:dict
dict: platform_product_client__client_type
fields: [platform_product_client.client_type]
values:
  AMS: {trust: proposed}
  ORDER: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  BEECREDIT: {trust: proposed}
  ACFLOW: {trust: proposed}
  DEALER: {trust: proposed}
triage: keep
```
