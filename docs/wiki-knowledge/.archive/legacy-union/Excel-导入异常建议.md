---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:exception-resolution@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: process
title: Excel 导入异常建议
page_key: Excel-导入异常建议
domain: funding
aliases: []
---
# Excel 导入异常建议



```ground:process
process: Excel 导入异常建议
stages:
- stage: Excel 导入异常建议
  trigger: POST /fund-web/exceptionInfo/importForExceptInput
  effects:
  - op: upsert
    table: funding_exception_resolution
    fields:
    - product_code
    - funding_party_code
    - funding_party_name
    - error_keyword
    - error_reason
    - suggestion
    - exception_no
    - enable
  transitions: []
```

## 关联
- [[funding_exception_resolution]]
