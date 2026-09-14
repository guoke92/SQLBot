---
type: rule
title: 异常解析-唯一键去重
page_key: exception_unique_key_dedup
domain: funding
status: draft
aliases:
  - 异常解析重复校验
  - 异常解析配置信息已存在
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication#checkBeforeSave"
contract_version: "0.1"
belong: rules
---

# 异常解析-唯一键去重

## 业务定位

当 `(product_code, funding_party_code, error_keyword)` 命中已有记录时，报错「异常解析配置信息已存在」并拒绝写入。该判定与 DB 唯一约束 `funding_exception_resolution_un` 一一对应（口径见 [[calibers/exception_resolution_unique_config]]），代码层提前拦截是为了给出可读的错误提示，而不是把唯一约束异常抛给运营。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析-唯一键去重
content: "(product_code, funding_party_code, error_keyword) 命中原有记录时报「异常解析配置信息已存在」"
impact: "防止重复配置"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: "db:funding_exception_resolution_un; code:ExceptionResolutionApplication#checkBeforeSave"
```

## 关联

- 口径：[[calibers/exception_resolution_unique_config]]
- 规则：[[rules/exception_import_all_or_nothing]]