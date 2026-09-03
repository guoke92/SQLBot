---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-build-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 企业角色是 JSON 数组
page_key: 企业角色是-JSON-数组
domain: 客户与建档
field_targets:
- cust_company_info.cust_company_type
---
# 企业角色是 JSON 数组

cust_company_info.cust_company_type 存 JSON 数组字符串（如 ["CORE"]）， 一家企业可兼具多角色；匹配须用包含（LIKE/JSON contains）而非相等。

```ground:rule
rule: company-type-json
field_targets:
- cust_company_info.cust_company_type
impact: query_constraint
content: cust_company_info.cust_company_type 存 JSON 数组字符串（如 ["CORE"]）， 一家企业可兼具多角色；匹配须用包含（LIKE/JSON
  contains）而非相等。
scope: 按企业角色（核心企业/供应商/资金方）过滤
```

## 关联
- [[cust_company_info]]
