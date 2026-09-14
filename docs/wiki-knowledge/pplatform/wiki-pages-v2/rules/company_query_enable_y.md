---
type: rule
title: 企业查询一律附加 enable='Y'
page_key: company_query_enable_y
domain: 平台内部服务对接
status: draft
aliases:
  - 企业查询有效标志规则
oid: 1
scope:
  databases: []
sources:
  - semantic:field_semantics[cust_company_info.enable]
contract_version: "0.1"
belong: rules
---

查询企业数据时必须附加 enable='Y' 条件，否则会取到逻辑删除或失效的企业行。

## 需求背景

该约束是企业表（[[tables/cust_company_info]]）的基础过滤条件，各服务读取企业信息时均应遵守；与之配套的主数据过滤见 [[rules/status_update_main_data_type]]。

## 版本演进

v0：首次成页。

```ground:rule
name: 企业查询一律附加 enable='Y'
field: cust_company_info.enable
condition: "查询一律 .eq(enable, 'Y')"
effect: "过滤掉非有效企业行"
evidence: code
```