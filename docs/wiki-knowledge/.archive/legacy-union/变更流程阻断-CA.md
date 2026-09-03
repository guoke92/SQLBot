---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 变更流程阻断 CA
page_key: 变更流程阻断-CA
domain: CA认证与服务费
field_targets:
- ca_certification_info.cust_id
---
# 变更流程阻断 CA

企业处于变更流程（cust_status=CHANGE 或 cust_build_status=CUST_CHANGE）时 pre4Step 直接阻断 CA 开通（'先走完变更流程再处理 CA 开通'）。

```ground:rule
rule: ca-block-during-change
field_targets:
- ca_certification_info.cust_id
impact: query_constraint
content: 企业处于变更流程（cust_status=CHANGE 或 cust_build_status=CUST_CHANGE）时 pre4Step 直接阻断
  CA 开通（'先走完变更流程再处理 CA 开通'）。
scope: CA 开通失败原因排查
```

## 关联
- [[ca_certification_info]]
