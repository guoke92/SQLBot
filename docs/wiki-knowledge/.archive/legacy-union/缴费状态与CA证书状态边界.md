---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-fee-collection@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 缴费状态与CA证书状态边界
page_key: 缴费状态与CA证书状态边界
domain: CA认证与服务费
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.ca_status
---
# 缴费状态与CA证书状态边界

pay_status 回答"服务费缴没缴"，ca_status 回答"CA 证书有没有效"——同名 EXPIRED 不同义（服务费过期 vs 证书过期）。portalCheck 是缴费+证书双条件组合校验。

```ground:rule
rule: pay-vs-ca-status-boundary
field_targets:
- ca_fee_company.pay_status
- ca_fee_company.ca_status
impact: query_constraint
content: pay_status 回答"服务费缴没缴"，ca_status 回答"CA 证书有没有效"——同名 EXPIRED 不同义（服务费过期 vs 证书过期）。portalCheck
  是缴费+证书双条件组合校验。
scope: 查CA过期/服务费过期类问题
```

## 关联
- [[ca_fee_company]]
