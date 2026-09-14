---
type: rule
title: 企业状态级联到联系人
page_key: company_status_cascade_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [freeze, diable, userStatusSync, 级联冻结]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustCompanyInfoApplication.java#freeze,#diable,#userStatusSync"]
contract_version: "0.1"
belong: rules
---

企业级操作会级联到联系人账号：冻结企业同时冻结企业管理员；注销企业冻结全部用户，并按 company_type 逐个同步用户状态（[[cust_company_info]]、[[valid_person]]）。

## 需求背景
- 级联冻结后联系人 enable 变化，所有按 enable=Y 的查询随之失效（[[valid_person]]）。
- 企业删除时还会以 sys_cust_user_rel.is_freeze='N' 判断能否清理 sys_user（[[not_frozen_rel]]）。

## 版本演进
- 当前版本冻结与注销走不同级联范围（管理员 vs 全部用户），同步粒度按 company_type 区分。

```ground:rule
name: 企业状态级联到联系人
content: "冻结企业同时冻结企业管理员；注销企业冻结全部用户并按 company_type 逐个同步用户状态"
impact: 企业级操作对联系人账号的连带影响
field_targets:
  - cust_person_info.enable
  - cust_company_info.cust_status
evidence: "code_path:CustCompanyInfoApplication.java#freeze,#diable,#userStatusSync"
```

相关页面：[[cust_company_info]]、[[cust_person_info]]、[[valid_person]]、[[not_frozen_rel]]。