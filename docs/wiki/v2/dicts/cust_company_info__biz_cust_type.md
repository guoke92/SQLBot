---
type: dict
title: cust_company_info.biz_cust_type
page_key: cust_company_info__biz_cust_type
belong: dicts
status: draft
anchors: [cust_company_info.biz_cust_type]
sources: ['database_profile:cust_company_info.biz_cust_type']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
related: [cust_company_info]
---

# cust_company_info.biz_cust_type

L0 字典候选：profile 代码值；列注释无码→中文映射，故无 label。空值已丢弃。
物理列 `cust_company_info.biz_cust_type`，表页 [[tables/cust_company_info]]。

## 取值

```ground:dict
dict: cust_company_info__biz_cust_type
fields: [cust_company_info.biz_cust_type]
values:
  股份有限公司: {trust: proposed}
  有限责任公司: {trust: proposed}
  国有企业: {trust: proposed}
  个体户合伙企业: {trust: proposed}
  股份合作制企业: {trust: proposed}
  集体企业: {trust: proposed}
  联营企业: {trust: proposed}
  私营企业: {trust: proposed}
  企业法人: {trust: proposed}
  事业单位: {trust: proposed}
triage: keep
```
