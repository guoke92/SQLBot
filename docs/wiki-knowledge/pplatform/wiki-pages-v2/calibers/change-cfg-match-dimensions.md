---
type: caliber
title: 企业变更配置匹配维度
page_key: change-cfg-match-dimensions
domain: 企业变更与运营变更
status: draft
aliases: [变更项匹配口径, 配置四维匹配]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustChangeApplication.java:list
contract_version: "0.1"
belong: calibers
---

变更项清单按「端类型 + 认证方式 + 客户类型 + 是否总公司 + 有效标记」匹配 [[tables.cust_change_cfg]]；其中企业类型按 `head_company` 细分，个人类型不叠加该维度。落地规则见 [[rules.change-cfg-identity-match]]，有效标记口径见 [[calibers.change-cfg-enable]]，配置字段含义见配置表页。

## 需求背景

同一次变更在不同端、不同认证方式下的材料要求与可选范围不同，因此配置表以多维组合表达适用性；个人客户没有「是否总公司」概念，匹配时必须去掉该维度，否则会取不到配置。

## 版本演进

v0.1：首次登记，口径来自 `CustChangeApplication.list` 的查询条件拼装。

```ground:caliber
name: 企业变更配置匹配维度
predicate: "cust_change_cfg.client_type = ? AND cust_change_cfg.identify_style = ? AND cust_change_cfg.cust_type = ? AND cust_change_cfg.head_company = ? AND cust_change_cfg.enable = 'Y'"
scope: 企业类型按 head_company 细分；个人类型不叠加 head_company
evidence: code_path:CustChangeApplication.java:list
```