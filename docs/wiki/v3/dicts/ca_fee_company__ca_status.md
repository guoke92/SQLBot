---
type: dict
title: ca_fee_company.ca_status
page_key: ca_fee_company__ca_status
belong: dicts
status: draft
anchors: [ca_fee_company.ca_status]
sources: ['database_profile:ca_fee_company.ca_status', 'database_schema:ca_fee_company.ca_status',
  'code_path:CaFeeCertStatusEnum.java:15', 'code_path:CaFeeCertStatusEnum.java:17',
  'code_path:CaFeeCertStatusEnum.java:19', 'code_path:CaFeeCertStatusEnum.java:16',
  'code_path:CaFeeCertStatusEnum.java:18']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [ca_fee_company]
---

# ca_fee_company.ca_status

L1 字典：label 来自源码 displayName/常量注释（confirmed）。L0 注释猜词已被代码覆盖。
物理列 `ca_fee_company.ca_status`，表页 [[tables/ca_fee_company]]。

## 取值

```ground:dict
dict: ca_fee_company__ca_status
fields: [ca_fee_company.ca_status]
values:
  NORMAL: {trust: confirmed, label: 有效, evidence: 'code_path:CaFeeCertStatusEnum.java:15'}
  CANCELLED: {trust: confirmed, label: 已注销, evidence: 'code_path:CaFeeCertStatusEnum.java:17'}
  UNKNOWN: {trust: confirmed, label: 未注册, evidence: 'code_path:CaFeeCertStatusEnum.java:19'}
  EXPIRED: {trust: confirmed, label: 已过期, evidence: 'code_path:CaFeeCertStatusEnum.java:16'}
  UNREGISTERED: {trust: confirmed, label: 未注册, evidence: 'code_path:CaFeeCertStatusEnum.java:18'}
triage: keep
```
