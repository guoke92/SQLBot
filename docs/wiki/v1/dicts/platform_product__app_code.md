---
type: dict
title: platform_product.app_code
page_key: platform_product__app_code
belong: dicts
status: draft
anchors: [platform_product.app_code]
sources: ['database_profile:platform_product.app_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [platform_product]
---

# platform_product.app_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `platform_product.app_code`，表页 [[tables/platform_product]]。

## 取值

```ground:dict
dict: platform_product__app_code
fields: [platform_product.app_code]
values:
  be1b5de568064ef1bc2f01c8105df7b2: {trust: proposed}
  8b6020c4034a47ad9a9a216e29a23616: {trust: proposed}
triage: hold
needs_review: true
```
