---
type: caliber
title: 管理员
page_key: person-admin
domain: 客户联系人管理
status: draft
aliases:
  - 管理员口径
oid: 1
scope:
  databases: ["<未提供>"]
sources:
  - "code:CustPersonApplication.getAdminByCustCodeCompanyType"
contract_version: "0.1"
belong: calibers
---

管理员口径即按 [[tables/cust_person_info]] 的 `user_type = 'accountAdmin'` 过滤。取企业管理员时通常还要叠加企业与公司类型条件，见 [[rules/admin-uniqueness]]。

## 需求背景

企业侧的权限判定（谁能管理企业、谁能操作变更）都以管理员记录为入口，因此需要一个稳定的取数口径，避免把平台侧运营人员（`operator*` 字段）误当管理员，语义边界见 [[concepts/admin]]。

```ground:caliber
caliber: 管理员
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 获取企业管理员
evidence: "code:CustPersonApplication.getAdminByCustCodeCompanyType"
```

## 版本演进

- v0：首次登记。

相关：[[tables/cust_person_info]]、[[concepts/admin]]、[[rules/admin-uniqueness]]、[[rules/admin-change-freeze]]。