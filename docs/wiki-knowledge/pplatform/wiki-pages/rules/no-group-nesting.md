---
type: rule
title: "新增子级关系时企业若已是集团公司则不允许作为子级"
page_key: no-group-nesting
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_company_info.cust_company_type]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

该规则防止集团嵌套，即已经是集团公司的企业不能再作为其他集团的子级。

## 需求背景

- 当企业 `cust_company_type` 包含 `CORPORATION_COMPANY` 时，不能将其添加为其他集团的子级。

## 版本演进

- 暂无变更。

```ground:rule
name: 新增子级关系时企业若已是集团公司则不允许作为子级
content: 当企业 cust_company_type 包含 CORPORATION_COMPANY 时，不能将其添加为其他集团的子级
impact: 防止集团嵌套
field_targets:
  - cust_company_info.cust_company_type
evidence: code_path:CustGroupRelApplication.addExistSubCustGroupRel
```

相关：[[cust_company_info]] [[company-role]] [[group]]