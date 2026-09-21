---
type: dict
title: cust_auth_application.platform_product_code
page_key: cust_auth_application__platform_product_code
belong: dicts
status: draft
anchors: [cust_auth_application.platform_product_code]
sources: ['database_profile:cust_auth_application.platform_product_code']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_auth_application]
---

# cust_auth_application.platform_product_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_auth_application.platform_product_code`，表页 [[tables/cust_auth_application]]。

## 取值

```ground:dict
dict: cust_auth_application__platform_product_code
fields: [cust_auth_application.platform_product_code]
values:
  ACFLOW: {trust: proposed}
  RVSFACTOR_PC: {trust: proposed}
  ORDER: {trust: proposed}
  BEECREDIT: {trust: proposed}
  DRAFTQA: {trust: proposed}
  VOUCHER: {trust: proposed}
  STORAGE: {trust: proposed}
  DRAFT: {trust: proposed}
triage: hold
needs_review: true
```
