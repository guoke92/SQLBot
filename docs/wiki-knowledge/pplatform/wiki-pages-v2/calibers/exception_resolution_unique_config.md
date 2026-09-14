---
type: caliber
title: 异常解析-唯一配置口径
page_key: exception_resolution_unique_config
domain: funding
status: draft
aliases:
  - 异常解析唯一键
  - 异常解析三元组唯一
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication#checkBeforeSave"
contract_version: "0.1"
belong: calibers
---

# 异常解析-唯一配置口径

## 业务定位

[[tables/funding_exception_resolution]] 的业务唯一性是三元组 `product_code + funding_party_code + error_keyword`，物理上由唯一约束 `funding_exception_resolution_un` 保证。导入去重、保存前校验、upsert 写入全部以此三元组为准：命中已有记录即报「异常解析配置信息已存在」，而不是插入第二条。

注意该口径**不含 `enable`**：`enable` 只影响可读性，不影响唯一性判定。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 唯一索引与代码 `checkBeforeSave` 双保险，属同一口径的两处实现。

```ground:caliber
caliber: 异常解析-唯一配置
predicate: "funding_exception_resolution.product_code + funding_party_code + error_keyword 唯一"
scope: 导入去重/保存前校验/upsert
evidence: "db:funding_exception_resolution_un; code:ExceptionResolutionApplication#checkBeforeSave"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_unique_key_dedup]]、[[rules/exception_import_all_or_nothing]]