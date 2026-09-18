---
type: dict
title: tenant_product.max_financing_amount
page_key: tenant_product__max_financing_amount
belong: dicts
status: draft
anchors: [tenant_product.max_financing_amount]
sources: ['database_profile:tenant_product.max_financing_amount']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [tenant_product]
---

# tenant_product.max_financing_amount

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `tenant_product.max_financing_amount`，表页 [[tables/tenant_product]]。

## 取值

```ground:dict
dict: tenant_product__max_financing_amount
fields: [tenant_product.max_financing_amount]
values:
  无上限: {trust: proposed}
  '0': {trust: proposed}
  10亿元: {trust: proposed}
  '99999': {trust: proposed}
  '9999999': {trust: proposed}
  '999999': {trust: proposed}
  '1000000': {trust: proposed}
  '999999999': {trust: proposed}
  '99999999999': {trust: proposed}
  '8888888888888': {trust: proposed}
  '100000': {trust: proposed}
  '10000000': {trust: proposed}
  以资金方审核结果为准: {trust: proposed}
  '500000': {trust: proposed}
  '9999999999999999999': {trust: proposed}
  '4': {trust: proposed}
  '100': {trust: proposed}
  '9999999999': {trust: proposed}
  '99999999': {trust: proposed}
  以资金方审核结果为准。: {trust: proposed}
  '1': {trust: proposed}
  '999999911': {trust: proposed}
  '999': {trust: proposed}
  '999999999999': {trust: proposed}
  '99999999999999': {trust: proposed}
  '20000000': {trust: proposed}
triage: hold
needs_review: true
```
