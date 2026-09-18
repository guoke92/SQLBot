---
type: dict
title: platform_product_client.status
page_key: platform_product_client__status
belong: dicts
status: draft
anchors: [platform_product_client.status]
sources: ['database_profile:platform_product_client.status']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [platform_product_client]
---

# platform_product_client.status

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `platform_product_client.status`，表页 [[tables/platform_product_client]]。

## 取值

```ground:dict
dict: platform_product_client__status
fields: [platform_product_client.status]
values:
  Y: {trust: proposed}
triage: hold
needs_review: true
```
