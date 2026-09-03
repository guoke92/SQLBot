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
title: enable 不是认证结果
page_key: enable-不是认证结果
domain: 企业建档
field_targets:
- cust_certification_info.enable
- cust_certification_info.auto_verify_status
- cust_certification_info.manual_verify_status
---
# enable 不是认证结果

enable 仅表示认证记录是否启用，认证是否通过必须看自动或人工结果字段。

```ground:rule
rule: enable-is-not-pass
field_targets:
- cust_certification_info.enable
- cust_certification_info.auto_verify_status
- cust_certification_info.manual_verify_status
impact: query_constraint
content: enable 仅表示认证记录是否启用，认证是否通过必须看自动或人工结果字段。
scope: 认证通过、认证失败及待核查统计
```

## 关联
- [[cust_certification_info]]
