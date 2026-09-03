---
type: rule
title: 企业用户列表AMS产品过滤
page_key: rule_query_user_list_ams_product_filter
domain: customer
status: published
aliases: []
oid: 1
sources: []
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则规定查询企业用户列表前需先校验租户是否开通AMS互通产品，未开通则返回空。

## 需求背景

`queryUserList` 先查询租户是否开通AMS互通产品，未开通直接返回空列表；仅开通时返回企业管理员和经办人。这保证了AMS侧查询联系人受租户产品开通控制。

## 版本演进

规则来自代码路径 `CustCompanyQueryApplication.queryUserList`。

```ground:rule
name: 企业用户列表AMS产品过滤
content: "queryUserList先查询租户是否开通AMS互通产品，未开通直接返回空列表；仅开通时返回企业管理员和经办人"
impact: AMS侧查询联系人受租户产品开通控制
field_targets:
  - "tenant_interworking_product"
  - "cust_person_info"
evidence: "code_path:CustCompanyQueryApplication.queryUserList"
```