---
type: caliber
title: 经办人
page_key: normal_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountNormal, 经办人口径]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type 分布(4205)", "code:CustPersonController.java#getOperInfo"]
contract_version: "0.1"
belong: calibers
---

"经办人"口径 = user_type='accountNormal'，用于经办人列表与实名认证待办判定。注意 [[cust_person_info]] 是表级统称，接口入参常直接叫 CustPersonInfoDO，并不代表该行就是经办人（[[contact_person]]）。

## 需求背景
- 经办人列表需排除游客，避免游客污染分页结果（[[exclude_guest]]）。
- 经办人实名认证待办与免认证白名单均围绕该口径展开（[[phone_realname_status]]、[[skip_realname_auth_whitelist]]）。

## 版本演进
- 当前版本经办人在关联重建中固定使用 ROLE_CODE_NORMAL（[[rel_rebuild_precondition]]）。

```ground:caliber
name: 经办人
predicate: "cust_person_info.user_type = 'accountNormal'"
scope: 经办人列表、实名认证待办判定
evidence: "db:cust_person_info.user_type 分布(4205) + code:CustPersonController.java#getOperInfo"
```

相关页面：[[cust_person_info]]、[[contact_person]]、[[company_admin]]、[[exclude_guest]]。