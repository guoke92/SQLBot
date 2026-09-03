---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:customer-config@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: rule
title: 字段清单配置按 JSON 数组解释
page_key: 字段清单配置按-JSON-数组解释
domain: config
field_targets:
- cust_setting_config.key_word
- cust_setting_config.no_key_word
---
# 字段清单配置按 JSON 数组解释

key_word 与 no_key_word 由 JSON.parseArray 解析为字段名称集合，不应按普通逗号字符串直接统计。

```ground:rule
rule: json-field-list
field_targets:
- cust_setting_config.key_word
- cust_setting_config.no_key_word
impact: query_constraint
content: key_word 与 no_key_word 由 JSON.parseArray 解析为字段名称集合，不应按普通逗号字符串直接统计。
scope: 关键/非关键企业信息审核
```

## 关联
- [[cust_setting_config]]
