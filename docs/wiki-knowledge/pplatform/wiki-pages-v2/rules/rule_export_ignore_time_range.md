---
type: rule
title: 资方规则列表/导出查询条件实际忽略时间区间
page_key: rule_export_ignore_time_range
domain: 资金规则与异常处理
status: draft
aliases:
  - 导出时间区间失效
  - parseTimeRange 死代码
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
belong: rules
---

[[funding_rule_info]] 的导出/列表查询中，create_time / update_time 的 ge / le 条件被注释掉，parseTimeRange 成为死代码，而 Controller 的 ApiOperation 注释仍宣称支持时间区间查询。

## 需求背景

行为表现为「静默忽略条件」而非报错，使用方按时间范围导出会得到全量结果，需以其他条件收敛范围。导出上限 50000 行、分页 500。

## 版本演进

v0 首次建立，登记实现与文档不一致的现状。

```ground:rule
name: 资方规则列表/导出查询条件实际忽略时间区间
content: buildExportQueryParam 中 create_time/update_time 的 ge/le 条件被注释掉，parseTimeRange 成为死代码；Controller 的 ApiOperation 注释仍宣称支持时间区间查询。
impact: 按创建/更新时间范围导出无效，只是忽略条件而非报错；导出上限 50000 行、分页 500
field_targets:
  - funding_rule_info.create_time
  - funding_rule_info.update_time
evidence: code_path:FundRuleInfoApplication.java:buildExportQueryParam:237
```