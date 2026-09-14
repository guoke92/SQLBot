---
type: process
title: 联系人账号状态（status）
page_key: cust_person_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [账号状态, status, ADD, EFFECT, FREEZE]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.status", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
belong: processes
---

联系人账号状态描述一条联系人记录从新增到生效、再到被冻结的生命周期。它与 enable（Y/N）配合使用：管理员换人时旧记录的 status 置 FREEZE 且 enable 置 N，新记录置 EFFECT，因此"当前有效管理员"实际是 status/enable 两个口径叠加的结果（[[valid_person]]、[[company_admin]]、[[admin_change_freeze_create]]）。

## 需求背景
- 管理员唯一性依赖冻结旧记录，而不是删除旧记录，历史留痕与审计由此保证（[[unique_admin_per_company_role]]）。
- 简易认证路径换手机号同样走"冻结 + 新建"，但触发条件与普通变更不同（[[simple_auth_phone_change]]）。

## 版本演进
- 当前版本已支持新增即 ADD、变更即 FREEZE/EFFECT 的完整闭环；冻结同时会删除其在 sys 的角色关联（[[rel_rebuild_precondition]]）。

```ground:process
name: 联系人账号状态
field: cust_person_info.status
states:
  - value: ADD
    label: 新增待生效
    source: db_dist
  - value: EFFECT
    label: 生效
    source: db_dist
  - value: FREEZE
    label: 冻结
    source: db_dist
transitions:
  - from: ""
    event: "新建联系人/法人同步为管理员（新增时置 ADD）"
    to: ADD
    evidence: "code_path:CustPersonApplication.java:saveFromCustLegal"
  - from: EFFECT
    event: "管理员变更（旧管理员冻结：enable=N, status=FREEZE）"
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm"
  - from: ""
    event: "生成新管理员记录"
    to: EFFECT
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm(cpf.setStatus(CustPersonStatusConstant.EFFECT))"
  - from: EFFECT
    event: "简易认证变更管理员且手机号变化"
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:simpleChangePerson(setStatus(CustPersonStatusConstant.FREEZE))"
```

相关页面：[[cust_person_info]]、[[admin_change_freeze_create]]、[[simple_auth_phone_change]]、[[company_status_cascade_person]]。