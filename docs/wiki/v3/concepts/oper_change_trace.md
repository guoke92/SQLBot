---
type: concept
title: 运营人员变更留痕
page_key: oper_change_trace
belong: concepts
domain: cust
status: draft
aliases: [变更运营轨迹, 变更记录tab]
maps_to: cust_oper_change_record.change_type
field_targets: [cust_oper_change_record.change_type, cust_oper_change_record.person_id,
  cust_oper_change_record.company_id]
sources: ['code_path:OperChangeRecordApplication.java:46', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
related: [cust_oper_change_record]
also_confused_with: [admin_change_topic, oper_staff_field]
adjudication: boundary
---

# 运营人员变更留痕

需求「变更运营轨迹留痕」钉的是联系人运营人员变更历史，落在 cust_oper_change_record。
按 person_id 倒序查；company_id 是企业主键拷贝。不是管理员冻旧建新，也不是企业冻结留痕。

## 页面链接

- [[tables/cust_oper_change_record]]
- [[dicts/cust_oper_change_record__change_type]]
- [[concepts/admin_change_topic]]
- [[concepts/oper_staff_field]]
