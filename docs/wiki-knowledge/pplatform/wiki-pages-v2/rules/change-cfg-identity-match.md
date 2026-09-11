---
type: rule
title: 变更配置按身份维度匹配
page_key: rule.change-cfg-identity-match
domain: 企业变更与运营变更
status: draft
aliases: [变更项清单匹配, 配置匹配规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
---

企业类型按 `client_type` + `identify_style` + `cust_type` + `head_company` + `enable='Y'` 匹配 [[tables.cust_change_cfg]]；个人类型不叠加 `head_company`。口径见 [[calibers.change-cfg-match-dimensions]] 与 [[calibers.change-cfg-enable]]，字段语义见配置表页，变更项标识见 [[concepts.item-code]]。

## 需求背景

不同端与认证方式下可变更的内容和所需材料不同，配置以多维组合表达适用性；个人客户不存在总公司概念，若仍拼入 `head_company` 条件将匹配不到任何配置，因此按客户类型分支处理。

## 版本演进

v0.1：首次登记，规则来自 `CustChangeApplication.list`。

```ground:rule
name: 变更配置按身份维度匹配
content: 企业类型按 client_type + identify_style + cust_type + head_company + enable='Y' 匹配；个人类型不叠加 head_company
impact: 决定不同端/认证方式/客户类型下可选的变更项清单
field_targets:
  - cust_change_cfg.client_type
  - cust_change_cfg.identify_style
  - cust_change_cfg.cust_type
  - cust_change_cfg.head_company
  - cust_change_cfg.enable
evidence: code_path:CustChangeApplication.java:list
```