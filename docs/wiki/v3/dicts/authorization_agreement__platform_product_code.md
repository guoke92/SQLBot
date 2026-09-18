---
type: dict
title: authorization_agreement.platform_product_code
page_key: authorization_agreement__platform_product_code
belong: dicts
status: draft
anchors: [authorization_agreement.platform_product_code]
sources: ['database_profile:authorization_agreement.platform_product_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [authorization_agreement]
---

# authorization_agreement.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `authorization_agreement.platform_product_code`，表页 [[tables/authorization_agreement]]。

## 取值

```ground:dict
dict: authorization_agreement__platform_product_code
fields: [authorization_agreement.platform_product_code]
values:
  PLATFORM: {trust: proposed}
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  AMS: {trust: proposed}
  STORAGE: {trust: proposed}
  BEECREDIT: {trust: proposed}
  VOUCHER: {trust: proposed}
  pplatform: {trust: proposed}
  RVSFACTOR: {trust: proposed}
triage: keep
```
