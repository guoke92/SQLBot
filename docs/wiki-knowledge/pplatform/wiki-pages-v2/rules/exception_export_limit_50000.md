---
type: rule
title: 异常解析-导出上限50000
page_key: exception_export_limit_50000
domain: funding
status: draft
aliases:
  - 异常解析导出上限
  - 导出50000行限制
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
contract_version: "0.1"
belong: rules
---

# 异常解析-导出上限50000

## 业务定位

单次导出累计行数超过 **50000** 时抛 `BaseException`，提示用户缩小查询范围。该阈值是防止大批量导出导致 OOM 或超时的硬闸门，属**防护性规则**而非业务规则。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与导入侧的行数上限（[[rules/exception_import_row_limit_5000]]）成对出现，读写两侧均有规模约束。

```ground:rule
rule: 异常解析-导出上限50000
content: "单次导出累计行数超过 50000 抛 BaseException，提示缩小查询范围"
impact: "防 OOM/超时"
field_targets: []
evidence: "code:ExceptionResolutionApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_import_row_limit_5000]]、[[rules/exception_export_funding_party_name_acflow]]