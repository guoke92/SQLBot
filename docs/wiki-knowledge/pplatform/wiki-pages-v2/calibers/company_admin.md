---
type: caliber
title: 企业管理员
page_key: caliber.company_admin
domain: 数据权限与组织
status: draft
aliases: [企业管理员, admin 口径]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「企业管理员」口径由 user_type='admin' 与 enable='Y' 两个条件共同构成。因为管理员的更换是「冻结旧记录 + 新建记录」（见 [[processes/cust_person_user_type_fsm]]），缺少 enable 过滤会把历史管理员当成现任管理员。该口径是数据权限保存鉴权、数据权限查询默认 ALL、组织绑定三处的前置判定，直接决定 [[processes/data_permission_type_fsm]] 是否能落到 ALL。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（DataPermissionApplication）成文。

```ground:caliber
name: 企业管理员
predicate: "cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y'"
scope: 数据权限保存鉴权、数据权限查询默认 ALL、组织绑定
evidence: code_path:DataPermissionApplication.java#assertCurrentUserIsAdminOfTargetCompany / #isEnterpriseAdmin
```