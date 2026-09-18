---
type: dict
title: cust_access_secret.channel
page_key: cust_access_secret__channel
belong: dicts
status: draft
anchors: [cust_access_secret.channel]
sources: ['database_profile:cust_access_secret.channel']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_access_secret]
---

# cust_access_secret.channel

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `cust_access_secret.channel`，表页 [[tables/cust_access_secret]]。

## 取值

```ground:dict
dict: cust_access_secret__channel
fields: [cust_access_secret.channel]
values:
  trinasolar: {trust: proposed}
  tianma: {trust: proposed}
  yhkj: {trust: proposed}
  dahua: {trust: proposed}
  lls: {trust: proposed}
  sny_test: {trust: proposed}
  trinapower: {trust: proposed}
  dahua-test: {trust: proposed}
  app_jkny: {trust: proposed}
  ZTSJ: {trust: proposed}
  alipayAnt-test: {trust: proposed}
  eascs: {trust: proposed}
  alipayAnt: {trust: proposed}
  meituan: {trust: proposed}
  longteng: {trust: proposed}
  sny: {trust: proposed}
  hbjg: {trust: proposed}
  app_bosc_shtl: {trust: proposed}
  bgy: {trust: proposed}
triage: hold
needs_review: true
```
