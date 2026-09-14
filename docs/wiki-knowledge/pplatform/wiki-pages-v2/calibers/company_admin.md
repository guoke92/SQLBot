---
type: caliber
title: 企业管理员
page_key: company_admin
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountAdmin, 管理员口径]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type 分布(55375)", "code:CustPersonApplication.java#listCompanyManagerUserId"]
contract_version: "0.1"
belong: calibers
---

"企业管理员"口径 = user_type='accountAdmin'，用于管理员定位、管理员唯一性校验与关联重建。它与平台运营人员（operator_id）是两个完全不同的实体，后者来自运营中台（[[operator]]、[[admin]]）。

## 需求背景
- 管理员定位需要叠加 enable 与 company_type 条件，才能得到某企业某角色下的唯一有效管理员（[[valid_person]]、[[unique_admin_per_company_role]]）。
- 关联重建时管理员角色码由 company_type 映射得到（[[rel_rebuild_precondition]]）。

## 版本演进
- DB 分布显示 accountAdmin 记录数（55375）远多于 accountNormal（4205），说明历史冻结行被大量保留。

```ground:caliber
name: 企业管理员
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 管理员定位、管理员唯一性校验、关联重建
evidence: "db:cust_person_info.user_type 分布(55375) + code:CustPersonApplication.java#listCompanyManagerUserId"
```

相关页面：[[cust_person_info]]、[[admin]]、[[normal_person]]、[[unique_admin_per_company_role]]。