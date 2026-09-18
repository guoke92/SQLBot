---
type: dict
title: funding_exception_resolution.product_code
page_key: funding_exception_resolution__product_code
belong: dicts
status: draft
anchors: [funding_exception_resolution.product_code]
sources: ['database_profile:funding_exception_resolution.product_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [funding_exception_resolution]
---

# funding_exception_resolution.product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `funding_exception_resolution.product_code`，表页 [[tables/funding_exception_resolution]]。

## 取值

```ground:dict
dict: funding_exception_resolution__product_code
fields: [funding_exception_resolution.product_code]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
triage: hold
needs_review: true
```
