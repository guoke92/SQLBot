---
type: rule
title: 变更项配置匹配
page_key: change_cfg_match
domain: 企业变更与运营变更
status: draft
aliases: [配置过滤, 可用变更项匹配]
oid: 1
scope:
  databases: ["unknown"]
sources:
  - code:CustChangeApplication.java
contract_version: "0.1"
belong: rules
---

规则内容：企业客户按 `client_type + identify_style + cust_type + head_company + enable='Y'` 过滤（[[valid_change_cfg]]）；个人客户（`clientType=INDIVIDUALS`）不按 `head_company` 过滤，`headCompany` 取自当前登录用户 `companyCode` 对应企业。

## 需求背景

同一套变更能力要按端、认证方式、客户类型、公司维度差异化发布；个人客户无总分公司概念，必须走另一条过滤分支。

## 版本演进

v0.1：首次固化过滤键与个人客户分支。

```ground:rule
name: 变更项配置匹配
content: "企业客户按 client_type + identify_style + cust_type + head_company + enable='Y' 过滤；个人客户(clientType=INDIVIDUALS)不按 head_company 过滤，headCompany 取自当前登录用户 companyCode 对应企业"
impact: 决定企业可见的变更项清单
field_targets:
  - cust_change_cfg.client_type
  - cust_change_cfg.identify_style
  - cust_change_cfg.cust_type
  - cust_change_cfg.head_company
  - cust_change_cfg.enable
evidence: "code_path:CustChangeApplication.java#list"
```

相关页面：[[cust_change_cfg]]、[[valid_change_cfg]]、[[cust_company_info]]、[[change_item_code]]。