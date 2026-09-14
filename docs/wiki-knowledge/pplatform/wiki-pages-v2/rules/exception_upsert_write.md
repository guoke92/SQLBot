---
type: rule
title: 异常解析-upsert写入
page_key: exception_upsert_write
domain: funding
status: draft
aliases:
  - 异常解析写入规则
  - 异常解析 upsert
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#doUpsertAll"
contract_version: "0.1"
belong: rules
---

# 异常解析-upsert写入

## 业务定位

全部校验通过后，在**单个事务**内执行 `saveOrUpdateBatch`，统一置 `enable='Y'`，同时生成 `exception_no` 并回填创建人/更新人。三件事必须同事务：有效标识、编号生成、审计字段——否则会出现「有编号但不可见」或「可见但无编号」的脏数据。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。编号生成规则见 [[tables/funding_exception_resolution]] 的 `exception_no` 字段说明。

```ground:rule
rule: 异常解析-upsert写入
content: "全部校验通过后在单事务内 saveOrUpdateBatch，置 enable='Y'，并生成 exceptionNo、回填创建/更新人"
impact: "保证写入一致性"
field_targets:
  - funding_exception_resolution.enable
  - funding_exception_resolution.exception_no
evidence: "code:ExceptionResolutionApplication#doUpsertAll"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 口径：[[calibers/exception_resolution_valid_enable_y]]
- 规则：[[rules/exception_import_all_or_nothing]]