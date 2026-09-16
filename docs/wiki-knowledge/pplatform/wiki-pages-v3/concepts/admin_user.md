---
type: concept
title: 管理员
page_key: admin_user
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
also_confused_with: [cust_person_info.company_type]
---

用户说「管理员」落到联系人 `user_type='accountAdmin'`。企业角色 CORE/SUPPLIER 不是管理员身份。有效口径见 [[effective_admin]]。
