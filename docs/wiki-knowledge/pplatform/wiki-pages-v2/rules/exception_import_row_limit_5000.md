---
type: rule
title: 异常解析导入-行数上限5000
page_key: exception_import_row_limit_5000
domain: funding
status: draft
aliases:
  - 导入行数超过上限
  - 导入5000行限制
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionImportListener"
contract_version: "0.1"
belong: rules
---

# 异常解析导入-行数上限5000

## 业务定位

单次导入数据行超过 **5000** 时直接抛「导入行数超过上限」，在文件解析阶段就终止，不进入后续校验。与导出上限一起构成异常解析的规模护栏。

## 需求背景

无语义分析挂载的需求文档锚点。该限制在 `ExceptionResolutionImportListener`（EasyExcel 监听器）中生效，说明是按行累计触发的。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析导入-行数上限5000
content: "单次导入数据行超过 5000 抛「导入行数超过上限」"
impact: "控制单批导入规模"
field_targets: []
evidence: "code:ExceptionResolutionImportListener"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_export_limit_50000]]、[[rules/exception_import_all_or_nothing]]