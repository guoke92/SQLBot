---
type: enum
title: activate_status
page_key: activate_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [未激活, 已激活]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["code:pplatform-web", "db:db-profile.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: enums
related: [person_status_flow, role_status_flow]
---

# activate_status

联系人 `status` 用 `CustPersonStatusConstant`，角色 `status` 用 `CustRoleStatusConstant`：ADD 未激活 / EFFECT 已激活 / WRITEOFF 注销 / FREEZE 冻结。键与企业 [[cust_status]] 相同，中文不是「新增/生效」。库中联系人 `status` 另有 1 条 `N`，不能当正式过滤。

```ground:enum
enum: activate_status
fields:
  - cust_person_info.status
  - cust_role_info.status
values:
  "ADD":
    label: "未激活"
  "EFFECT":
    label: "已激活"
  "WRITEOFF":
    label: "注销"
  "FREEZE":
    label: "冻结"
```
