---
type: concept
title: 经办人
page_key: operator_user
domain: 经办人/联系人/管理员管理
status: draft
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: concepts
field_targets:
  - cust_person_info.user_type
maps_to: cust_person_info.user_type
adjudication: boundary
also_confused_with: [cust_oper_change_record.after_operator_id]
---

经办人是 `user_type='accountNormal'`。运营人员变更里的 operator 是运营中台人员，不是经办人。
