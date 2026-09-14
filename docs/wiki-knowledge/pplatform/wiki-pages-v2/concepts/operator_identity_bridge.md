---
type: concept
title: 运营人员标识桥（operation_user ↔ cust_person_info）
page_key: operator_identity_bridge
domain: 数据权限与组织
status: draft
aliases: [运营人员标识桥, operator_id, operator_realname, operator]
oid: 1
scope:
  databases: [base]
sources: [db, code, "enrich:wiki-admin"]
contract_version: "0.1"
maps_to:
  - operation_user.operation_id
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
field_targets:
  - table: operation_user
    field: operation_id
    meaning: 运营中台人员ID（对接运营中台的用户标识，产融侧 cust_person_info.operator_id 存放的值）
    evidence: db
  - table: operation_user
    field: operation_name
    meaning: 运营人员姓名（产融侧 cust_person_info.operator_realname 的来源）
    evidence: db
  - table: cust_person_info
    field: operator_id
    meaning: 归属运营人员ID（指向 operation_user.operation_id）
    evidence: code
  - table: cust_person_info
    field: operator_realname
    meaning: 归属运营人员姓名（冗余自 operation_user.operation_name）
    evidence: code
  - table: cust_person_info
    field: operator
    meaning: 归属运营人员登录名
    evidence: code
adjudication: 产融侧只存 operation_id（非 operation_user.id），operator_realname 是姓名冗余；引用运营人员必须走 operation_id 而非主键 id。
also_confused_with: [operation_user.id, organization_id]
belong: concepts
---

术语桥：运营人员归属跨两个域——运营中台侧的 [[tables/operation_user]] 与产融侧的 [[tables/cust_person_info]]。产融侧 cust_person_info.operator_id 存放的是 operation_user.operation_id，而不是该表主键 id；operator_realname 则是 operation_name 的冗余快照。这意味着在 operation_user 上做关联时必须避开 id 主键，否则会连到错误的运营人员。

姓名是冗余字段，源端改名后产融侧不会自动跟随，需要以 operation_id 为准反查 [[tables/operation_user]] 的 operation_name。运营人员展示口径见 [[calibers/non_guest_user]]。

相关：[[operation_user]]
