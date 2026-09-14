---
type: rule
title: 同企业同角色唯一管理员
page_key: unique_admin_per_company_role
domain: 经办人/联系人/管理员管理
status: draft
aliases: [管理员唯一性, accountAdmin唯一]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#checkBeforeSave,#updateAuthorAndApply"]
contract_version: "0.1"
belong: rules
---

管理员新增/变更的前置校验：同一 company_type + ref_cust_company_info 下，user_type=accountAdmin 且 enable=Y 的记录数必须为 0，否则拒绝操作（[[company_admin]]、[[valid_person]]）。

## 需求背景
- 该校验把"角色"（company_type）与"身份"（user_type=accountAdmin）叠加，所以同一企业不同角色可以各有一个管理员。
- 变更场景下必须先冻结旧管理员，否则校验会命中自身（[[admin_change_freeze_create]]）。

## 版本演进
- 当前版本以 enable=Y 为统计条件，冻结记录不计入。

```ground:rule
name: 同企业同角色唯一管理员
content: "统计同一 company_type + ref_cust_company_info 下 user_type=accountAdmin 且 enable=Y 的记录数必须为 0，否则抛“当前企业已经存在该客户角色的管理员”"
impact: 管理员新增/变更前置校验
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
  - cust_person_info.enable
evidence: "code_path:CustPersonApplication.java#checkBeforeSave,#updateAuthorAndApply"
```

相关页面：[[cust_person_info]]、[[company_admin]]、[[admin_change_freeze_create]]、[[valid_person]]。