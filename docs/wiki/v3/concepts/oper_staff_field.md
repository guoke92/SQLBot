---
type: concept
title: 联系人运营人员
page_key: oper_staff_field
belong: concepts
domain: cust
status: draft
aliases: [企业信息维护-运营人员字段, 运营人员取值逻辑优化, 运营人员]
maps_to: cust_person_info.operator_realname
field_targets: [cust_person_info.operator_id, cust_person_info.operator_realname]
sources: ['code_path:CustPersonApplication.java:900', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [archive_handby, oper_change_trace]
adjudication: boundary
---

# 联系人运营人员

document_claim:企业信息维护-运营人员字段.md#11 / 运营人员取值逻辑优化.md#19：列表「运营人员」是联系人 operator_id / operator_realname。
手动更换走 changePersonOperator。变更历史在 cust_oper_change_record，不是这两列本身。不是建档经办人 handby_person_name。

## 页面链接

- [[tables/cust_person_info]]
- [[concepts/archive_handby]]
- [[concepts/oper_change_trace]]
