---
type: rule
title: 简易认证换手机号即换人
page_key: simple_auth_phone_change
domain: 经办人/联系人/管理员管理
status: draft
aliases: [simpleChangePerson, 简易认证管理员变更]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#simpleChangePerson"]
contract_version: "0.1"
belong: rules
---

简易认证场景下判定"换人"的触发条件是手机号是否变化：手机号变化则冻结旧管理员、删角色关联、删组织用户、新建管理员记录、绑机构并直通授权书；手机号未变则仅更新，并同步登录邮箱（旧业务邮箱=登录邮箱，或仅关联一个企业时才同步）（[[admin_change_freeze_create]]、[[admin]]）。

## 需求背景
- 该路径与 UN0012/UN0013/UN0014 触发的普通变更路径并存，二者判定依据不同，不能互相替代（[[admin_change_freeze_create]]）。

## 版本演进
- 当前版本已包含手机号未变时的邮箱同步旁路逻辑。

```ground:rule
name: 简易认证换手机号即换人
content: "simpleChangePerson 中手机号变化：冻结旧管理员、删角色关联、删组织用户、新建管理员记录、绑机构并直通授权书；手机号未变时仅更新并同步登录邮箱（旧业务邮箱=登录邮箱或仅关联一个企业才同步）"
impact: 简易认证企业管理员变更路径
field_targets:
  - cust_person_info.phone
  - cust_person_info.enable
  - cust_person_info.status
evidence: "code_path:CustPersonApplication.java#simpleChangePerson"
```

相关页面：[[cust_person_info]]、[[admin_change_freeze_create]]、[[admin]]、[[cust_person_status]]。