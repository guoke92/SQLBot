---
type: concept
title: 建档经办人
page_key: archive_handby
belong: concepts
domain: cust
status: draft
aliases: [建档经办人名字]
maps_to: cust_person_info.handby_person_name
field_targets: [cust_person_info.handby_person, cust_person_info.handby_person_name]
sources: ['code_path:CustPersonApplication.java:1788', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [oper_staff_field, account_operator]
adjudication: boundary
---

# 建档经办人

document_claim:运营人员取值逻辑优化.md#19：内管「建档经办人」与「运营人员」分列。catalog 注释「建档经办人名字」。
自主认证+供应商且为空时展示 --。不是 user_type=accountNormal，也不是 operator_realname。

## 页面链接

- [[tables/cust_person_info]]
- [[concepts/account_operator]]
- [[concepts/oper_staff_field]]
