---
type: scenario
title: 经办人与联系人
page_key: company_contact
domain: 经办人/联系人/管理员管理
status: draft
aliases: [管理员, 经办人, 联系人]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:page-plan.yaml:经办人/联系人/管理员管理"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: scenarios
hubs: [cust_person_info]
field_targets:
  - cust_person_info.user_type
  - cust_person_info.status
---

# 经办人与联系人

问「某企业管理员 / 有效经办人 / 未激活联系人」时进入本场景。

**主档** [[cust_person_info]]：一人绑定一家企业的一个企业角色切片（`company_type`）。联系人种类看 `user_type`（管理员/经办人/游客），不要和企业角色 `company_type` 互换。

**从属** [[cust_invite_info]]：邀请进度 `progress` 跟的是企业建档状态，不是联系人账号状态。  
`cust_user_rel` 计划内标记休眠，本窗不展开。

```ground:scenario
scenario: company_contact
hubs:
- table: cust_person_info
  role: master
  grain: 一人×一企×一企业角色
  window:
  - id
  - enable
  - create_time
  - update_time
  - ref_cust_company_info
  - cust_company_id
  - user_type
  - company_type
  - status
  - cust_build_status
  - face_status
  - phone_realname_status
  - real_name_result
  - name
  - phone
- table: cust_invite_info
  role: invite
  grain: 一条邀请
  window:
  - id
  - enable
  - create_time
  - update_time
  - name
  - contact_name
  - contact_phone
  - progress
  - channel_code
shared:
- table: cust_company_info
  role: identity
  window:
  - id
  - enable
  - create_time
  - update_time
  - code
  - name
  - cust_status
lifecycle:
- enum: activate_status
  process: person_status_flow
  field: cust_person_info.status
```
