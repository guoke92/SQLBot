---
type: rule
title: 管理员变更冻结旧管理员
page_key: rule.admin_change_freeze
domain: 客户联系人管理
status: draft
aliases:
  - 管理员换人规则
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.ifNessaryFrzAdm"
  - "code:CustPersonApplication.simpleChangePerson"
contract_version: "0.1"
---

管理员变更时，旧管理员记录被置为冻结状态，并删除其在系统中的角色关联；同时新增一条管理员记录并赋予权限，确保同一时间只有一个有效管理员。

## 需求背景

需求文档主张「管理员变更时需冻结旧管理员并新增管理员」（code_path:CustPersonApplication.java:ifNessaryFrzAdm + reqdoc:管理员变更时需冻结旧管理员并新增管理员），代码在管理员生效判断与简易认证变更手机号两条路径上均会触发冻结。业务上要求换人过程不出现权限空档，因此冻结与新增在同一次操作内完成；冻结后的记录仍是有效联系人（[[calibers/valid-person]]），状态语义见 [[processes/person-account-status]]。

```ground:rule
rule: 管理员变更冻结旧管理员
content: 管理员变更时，旧管理员记录被置为冻结状态，并删除其在系统中的角色关联；同时新增一条管理员记录并赋予权限
impact: 确保同一时间只有一个有效管理员
field_targets:
  - cust_person_info.status
  - cust_person_info.enable
  - cust_person_info.user_id
evidence: "code:CustPersonApplication.ifNessaryFrzAdm + code:CustPersonApplication.simpleChangePerson + code_path:CustPersonApplication.java:ifNessaryFrzAdm + reqdoc:管理员变更时需冻结旧管理员并新增管理员"
```

## 版本演进

- v0：首次登记。

相关：[[processes/person-account-status]]、[[rules/admin-uniqueness]]、[[concepts/admin]]、[[tables/cust_person_info]]。