---
type: caliber
title: 非游客用户
page_key: caliber.non_guest_user
domain: 数据权限与组织
status: draft
aliases: [非游客, user_type != guest]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「非游客用户」仅以 [[tables/cust_person_info]].user_type 不等于 guest 为条件，用于联系人分页与运营人员展示。它是比 [[calibers/company_admin]] 更宽的集合，不叠加 enable 过滤，因此其结果集会包含已冻结联系人，展示层需自行注意语义差异。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustPersonApplication）成文。

```ground:caliber
name: 非游客用户
predicate: "cust_person_info.user_type != 'guest'"
scope: 联系人分页、运营人员展示
evidence: code_path:CustPersonApplication.java#pagePerson / #getOperatorByCompanyCode
```