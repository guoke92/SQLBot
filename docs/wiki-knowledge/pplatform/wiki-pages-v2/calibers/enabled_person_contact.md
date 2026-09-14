---
type: caliber
title: 启用联系人
page_key: enabled_person_contact
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - 有效经办人
oid: 1
scope:
  databases: [unknown]
sources:
  - code:UserFacade.java:handUserList
contract_version: "0.1"
belong: calibers
---

口径“启用联系人”：用户列表补全用户类型/邮箱时，只取 [[cust_person_info.enable]] = 'Y' 的经办人（联系人）记录。

## 需求背景

用户列表需要补全用户类型与邮箱，只有启用态联系人参与补全；经办人状态另有
ADD/EFFECT 生命周期（[[cust_person_info_status_state]]）。

## 版本演进

- v0（草稿）：口径来自代码查询条件。

```ground:caliber
name: 启用联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 用户列表补全用户类型/邮箱
evidence: "code_path:UserFacade.java:handUserList"
```

相关：[[cust_person_info]]、[[cust_person_info_status_state]]。