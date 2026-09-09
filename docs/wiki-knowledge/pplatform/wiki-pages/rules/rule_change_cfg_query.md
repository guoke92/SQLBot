---
type: rule
title: 变更配置查询规则
page_key: rule_change_cfg_query
belong: rules
domain: 企业变更与运营变更
status: published
aliases: []
oid: 1

sources: ["CustChangeApplication.list", "enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_change_cfg.client_type, cust_change_cfg.cust_type, cust_change_cfg.enable, cust_change_cfg.head_company, cust_change_cfg.identify_style]
coverage_note: 变更配置
scope:
  databases: [lowcode_pplatform]
---

该规则定义查询变更配置时的过滤逻辑：企业类型需根据认证方式、是否总公司进一步筛选，个人类型则不考虑总公司；同时必须匹配端类型且启用状态为 Y。它直接决定了不同场景下可展示的变更项集合。

## 需求背景

暂无特定需求声明。

```ground:rule
name: "变更配置查询规则"
content: "查询变更配置时，企业类型（ENTERPRISE）需过滤 head_company 和 identify_style，个人类型（INDIVIDUALS）不过滤 head_company；同时必须匹配 client_type 和 enable='Y'"
impact: "决定不同认证方式、是否总公司、端类型下可申请的变更项"
field_targets:
  - "cust_change_cfg.client_type"
  - "cust_change_cfg.identify_style"
  - "cust_change_cfg.head_company"
  - "cust_change_cfg.cust_type"
  - "cust_change_cfg.enable"
evidence: "code_path:CustChangeApplication.list"
```

## 版本演进

暂无。

相关：[[cust_change_cfg]]
