---
type: dict
title: ca_cfca_upgrade_report.db_tenant_code
page_key: ca_cfca_upgrade_report__db_tenant_code
belong: dicts
status: draft
anchors: [ca_cfca_upgrade_report.db_tenant_code]
sources: ['database_profile:ca_cfca_upgrade_report.db_tenant_code']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [ca_cfca_upgrade_report]
---

# ca_cfca_upgrade_report.db_tenant_code

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。 初审 hold：证据不足，保留待人工确认（测库单值不构成排除依据）。
物理列 `ca_cfca_upgrade_report.db_tenant_code`，表页 [[tables/ca_cfca_upgrade_report]]。

## 取值

```ground:dict
dict: ca_cfca_upgrade_report__db_tenant_code
fields: [ca_cfca_upgrade_report.db_tenant_code]
values:
  beehive-scf.qhhrly.cn: {trust: proposed}
  LN1: {trust: proposed}
  sdhsg.beehive-scf.qhhrly.cn: {trust: proposed}
  minmetals: {trust: proposed}
  cdrcb.beehive-scf.qhhrly.cn: {trust: proposed}
triage: hold
needs_review: true
```
