---
type: rule
title: "导入时集团公司和成员单位字段校验"
page_key: import-data-validation
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
field_targets: [cust_company_info.certification_no]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

导入集团数据时，对必填项和格式进行校验，保证导入数据质量，尤其是统一社会信用代码格式符合国家标准。

## 需求背景

- 导入集团数据进行必填和格式校验，统一社会信用代码格式需符合国家标准。

## 版本演进

- 暂无变更。

```ground:rule
name: 导入时集团公司和成员单位字段校验
content: 对集团导入数据进行必填和格式校验，统一社会信用代码格式需符合国家标准
impact: 保证导入数据质量
field_targets:
  - cust_company_info.certification_no
evidence: code_path:CustGroupRelApplication.checkExcelData, validateCertificationNo
```

相关：[[cust_company_info]] [[cust_group_rel]]