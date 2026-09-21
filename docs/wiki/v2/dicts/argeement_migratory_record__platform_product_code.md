---
type: dict
title: argeement_migratory_record.platform_product_code
page_key: argeement_migratory_record__platform_product_code
belong: dicts
status: draft
anchors: [argeement_migratory_record.platform_product_code]
sources: ['database_profile:argeement_migratory_record.platform_product_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [argeement_migratory_record]
---

# argeement_migratory_record.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `argeement_migratory_record.platform_product_code`，表页 [[tables/argeement_migratory_record]]。

## 取值

```ground:dict
dict: argeement_migratory_record__platform_product_code
fields: [argeement_migratory_record.platform_product_code]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  AMS: {trust: proposed}
  BEECREDIT: {trust: proposed}
  STORAGE: {trust: proposed}
  VOUCHER: {trust: proposed}
triage: hold
needs_review: true
```
