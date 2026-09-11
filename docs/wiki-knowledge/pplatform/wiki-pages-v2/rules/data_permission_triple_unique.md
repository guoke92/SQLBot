---
type: rule
title: 数据权限按用户+企业+角色三维唯一
page_key: rule.data_permission_triple_unique
domain: 数据权限与组织
status: draft
aliases: [数据权限唯一三维]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

落到 [[tables/sys_cust_org_user_permission]] 的每一条权限记录，主体是 user_id + company_id + company_type 三元组。同一用户在不同企业、或同一企业不同角色下的权限互不影响，删除/更新权限必须三键齐备，只按 user_id 操作会跨企业串权。语义模型见 [[concepts/data_permission_triple]]。

## 需求背景

语义分析中未出现 reqdoc_claims 条目；本规则由字段语义（「与 company_id、company_type 构成唯一三维」）直接得出。

## 版本演进

v0：依据 code 证据成文。

```ground:rule
name: 数据权限三维唯一
statement: 数据权限的主体键是 user_id + company_id + company_type 三元组
condition: 读写 sys_cust_org_user_permission
action: 任何查询与更新都必须同时限定三个维度
evidence: code_path:DataPermissionApplication.java#getByUserCompanyType / #listByCompany
```