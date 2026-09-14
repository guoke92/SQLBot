---
type: caliber
title: 资方规则-有效信息口径
page_key: funding_rule_info_valid_enable_y
domain: funding
status: draft
aliases:
  - 资方规则有效信息
  - rule_info enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#exportRecords"
  - "db:funding_rule_info"
contract_version: "0.1"
belong: calibers
---

# 资方规则-有效信息口径

## 业务定位

资方规则主表的读取口径为 `enable = 'Y'`，导出与查询均按此过滤。与异常解析一致，`enable` 是软删除开关，与 `rule_status` 正交：一条 `enable='Y'` 但 `rule_status='INACTIVE'` 的规则对运营可见、对 Dubbo 外部不可见（见 [[calibers/funding_rule_info_active_rule]]）。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 资方规则-有效信息
predicate: "funding_rule_info.enable = 'Y'"
scope: 导出/查询
evidence: "code:FundRuleInfoApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 口径：[[calibers/funding_rule_info_active_rule]]