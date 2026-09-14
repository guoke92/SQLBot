---
type: process
title: 企业联系人类型机（user_type）
page_key: cust_person_user_type_fsm
domain: 数据权限与组织
status: draft
aliases: [联系人类型机, user_type, UserTypeEnum]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
state_field: cust_person_info.user_type
belong: processes
---

企业联系人类型机，承载于 [[tables/cust_person_info]].user_type。Java 名是 admin / operator / guest，落库是 `UserTypeEnum.getDictKey()`：`accountAdmin`（企业管理员）/ `accountNormal`（经办人）/ `accountGuest`（游客）。`accountGuest` → `accountNormal` 发生在新增/编辑经办人时（AMS 以外来源默认认证通过）；`accountGuest` → `accountAdmin` 发生在建档成功赋予管理员权限时（endueCompanyAdminUser）。

管理员的变更是「冻结旧记录 + 新建记录」而非原地改字段：旧管理员置 enable=N、status=FREEZE，新管理员另起一条记录。这一模式决定了查询时必须叠加 [[calibers/company_admin]] 的启用过滤，否则会把历史管理员算进来。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张；全部状态与流转证据来自 CustPersonApplication 与 CustCompanyInfoApplication。

## 版本演进

v0：依据 code 证据建模。

```ground:process
name: 企业联系人类型机
field: cust_person_info.user_type
states:
  - value: accountAdmin
    label: 企业管理员
    source: code_enum
  - value: accountNormal
    label: 经办人
    source: code_enum
  - value: accountGuest
    label: 游客
    source: code_enum
transitions:
  - from: accountGuest
    event: 新增/编辑经办人（AMS 以外来源默认认证通过）
    to: accountNormal
    evidence: code_path:CustPersonApplication.java#insertOrUpdatePerson
  - from: accountGuest
    event: 建档成功赋予管理员权限
    to: accountAdmin
    evidence: code_path:CustCompanyInfoApplication.java#endueCompanyAdminUser
  - from: accountAdmin
    event: 管理员变更：旧管理员置 enable=N/status=FREEZE，新建管理员记录
    to: accountAdmin
    evidence: code_path:CustPersonApplication.java#ifNessaryFrzAdm
  - from: accountAdmin
    event: 简易认证管理员换手机号：旧记录冻结、新记录生效
    to: accountAdmin
    evidence: code_path:CustPersonApplication.java#simpleChangePerson
```