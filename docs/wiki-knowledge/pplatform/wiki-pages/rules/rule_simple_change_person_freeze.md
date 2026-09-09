---
type: rule
title: 简易认证管理员变更冻结旧用户规则
page_key: rule_simple_change_person_freeze
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustPersonApplication.simpleChangePerson", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.enable, cust_person_info.phone, cust_person_info.status]
coverage_note: 联系人/个人用户
scope:
  databases: [lowcode_pplatform]
---

该规则用于简易认证场景下管理员手机号变更：冻结原管理员记录，删除角色关系，新增管理员记录，复制影像，补充授权书，并推送变更到运营中台，确保新老用户交替的正确性与安全性。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "简易认证管理员变更冻结旧用户规则"
content: "simpleChangePerson 中若手机号变更，冻结原管理员记录（enable=N, status=FREEZE），删除角色关系，新增管理员记录，复制影像，补充授权书，并推送变更到运营中台"
impact: "确保管理员变更后新用户可登录且旧用户失效"
field_targets:
  - "cust_person_info.enable"
  - "cust_person_info.status"
  - "cust_person_info.phone"
evidence: "code_path:CustPersonApplication.simpleChangePerson"
```

## 版本演进

暂无。

相关：[[cust_person_info]]
