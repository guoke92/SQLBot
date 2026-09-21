---
type: dict
title: cust_sftp.user_name
page_key: cust_sftp__user_name
belong: dicts
status: draft
anchors: [cust_sftp.user_name]
sources: ['database_profile:cust_sftp.user_name']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
related: [cust_sftp]
---

# cust_sftp.user_name

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认。
物理列 `cust_sftp.user_name`，表页 [[tables/cust_sftp]]。

## 取值

```ground:dict
dict: cust_sftp__user_name
fields: [cust_sftp.user_name]
values:
  app_bosc_shtl: {trust: proposed}
  app_sny_202607235624: {trust: proposed}
  app_alipayAnt_202606301619: {trust: proposed}
  app_dahua2026041601: {trust: proposed}
  app_bgy_20250306: {trust: proposed}
  app_cclocal_601636163: {trust: proposed}
  app_ztsj_2026033169: {trust: proposed}
  app_JingKeNengY926_20240614: {trust: proposed}
  app_eascs_2022070823: {trust: proposed}
  app_trinasolar_2023051522: {trust: proposed}
  app_ofhbjg_20260409: {trust: proposed}
  app_LongTengYC_609152804: {trust: proposed}
  meituan: {trust: proposed}
triage: hold
needs_review: true
```
