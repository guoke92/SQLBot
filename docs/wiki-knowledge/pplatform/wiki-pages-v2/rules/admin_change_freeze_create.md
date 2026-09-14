---
type: rule
title: 管理员换人=冻结旧+新建
page_key: admin_change_freeze_create
domain: 经办人/联系人/管理员管理
status: draft
aliases: [ifNessaryFrzAdm, UN0012, UN0013, UN0014]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#ifNessaryFrzAdm"]
contract_version: "0.1"
belong: rules
---

管理员换人由 isAdminChange（外部 alterTypes 命中 UN0012/UN0013/UN0014）触发：旧记录 enable=N、status=FREEZE，删除其在 sys 的角色关联，再复制生成新记录（status=EFFECT，清空 userId/userName），最后绑组织与授权协议（[[cust_person_status]]、[[admin]]）。

## 需求背景
- 该实现保证同一时刻只有一个有效管理员用户，同时保留历史留痕（[[unique_admin_per_company_role]]、[[valid_person]]）。
- 新记录清空 userId/userName，意味着换人后需重新建立登录用户关联（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本已覆盖冻结、解绑、复制、绑组织与授权协议的完整链路。

```ground:rule
name: 管理员换人=冻结旧+新建
content: "isAdminChange(ext alterTypes 命中 UN0012/UN0013/UN0014) 时：旧记录 enable=N、status=FREEZE，删除其在 sys 的角色关联，复制生成新记录（status=EFFECT, 清空 userId/userName），再绑组织与授权协议"
impact: 同一时刻只有一个有效管理员用户
field_targets:
  - cust_person_info.enable
  - cust_person_info.status
  - cust_person_info.user_id
evidence: "code_path:CustPersonApplication.java#ifNessaryFrzAdm"
```

相关页面：[[cust_person_info]]、[[cust_person_status]]、[[admin]]、[[unique_admin_per_company_role]]。