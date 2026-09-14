---
type: caliber
title: 游客
page_key: person-guest
domain: 客户联系人管理
status: draft
aliases:
  - 游客口径
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.pagePerson"
contract_version: "0.1"
belong: calibers
---

游客口径即按 [[tables/cust_person_info]] 的 `user_type = 'accountGuest'` 过滤。

## 需求背景

游客多为企业变更等流程中预生成的低权限记录，用于临时承载人员信息，权限低于经办人。列表分页查询需要能按该角色单独筛选，见 [[concepts/guest]]。

```ground:caliber
caliber: 游客
predicate: "cust_person_info.user_type = 'accountGuest'"
scope: 获取游客角色联系人
evidence: "code:CustPersonApplication.pagePerson"
```

## 版本演进

- v0：首次登记。

相关：[[tables/cust_person_info]]、[[concepts/guest]]、[[concepts/contact-person]]。