---
type: rule
title: 运营人员变更不是企业变更单
page_key: oper_change_not_company_change
domain: 企业变更与运营变更
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: rules
field_targets:
  - cust_oper_change_record.change_type
  - cust_change_record.status
---

运营改派在 cust_oper_change_record；企业信息变更在 cust_change_record。

```ground:rule
name: 运营人员变更不是企业变更单
content: 运营改派在 cust_oper_change_record；企业信息变更在 cust_change_record。
field_targets: [cust_oper_change_record.change_type, cust_change_record.status]
evidence: "code_path:OperChangeRecordApplication.java:25"
```
