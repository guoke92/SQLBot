---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:enterprise-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 认证结果不是 enable
page_key: 认证结果不是-enable
domain: 企业建档
field_targets:
- cust_certification_info.auto_verify_status
- cust_certification_info.manual_verify_status
---
# 认证结果不是 enable

是否认证通过看 auto/manual_verify_status，enable 只表示行是否可用。

```ground:rule
rule: cert-status-not-enable
field_targets:
- cust_certification_info.auto_verify_status
- cust_certification_info.manual_verify_status
impact: query_constraint
content: 是否认证通过看 auto/manual_verify_status，enable 只表示行是否可用。
scope: 已认证企业、未认证企业
```

## 关联
- [[cust_certification_info]]
