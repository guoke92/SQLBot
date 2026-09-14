---
type: caliber
title: 排除游客
page_key: exclude_guest
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountGuest, 非游客]
oid: 1
scope.databases: [unknown]
sources: ["code:CustPersonApplication.java#pagePerson"]
contract_version: "0.1"
belong: calibers
---

"排除游客"口径用于联系人分页与运营人汇总：查询条件为 user_type <> 'accountGuest'，避免游客记录进入业务列表（[[normal_person]]、[[contact_person]]）。

## 需求背景
- 游客（user_type=accountGuest）与经办人共用 [[cust_person_info]] 表，若不过滤会污染经办人列表与运营人统计口径。

## 版本演进
- 当前版本以 .ne("user_type", UserTypeEnum.guest.getDictKey()) 实现，属于代码侧显式排除而非 SQL 视图。

```ground:caliber
name: 排除游客
predicate: "cust_person_info.user_type <> 'accountGuest'"
scope: 联系人分页、运营人汇总，避免游客污染列表
evidence: "code:CustPersonApplication.java#pagePerson(.ne(\"user_type\", UserTypeEnum.guest.getDictKey()))"
```

相关页面：[[cust_person_info]]、[[normal_person]]、[[contact_person]]、[[valid_person]]。