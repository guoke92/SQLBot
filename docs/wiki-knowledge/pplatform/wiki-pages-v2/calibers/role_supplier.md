---
type: caliber
title: 供应商角色
page_key: role_supplier
domain: 文件/附件/媒体
status: draft
aliases: [company_type=SUPPLIER]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java:createCustCompany"]
contract_version: "0.1"
belong: calibers
---
供应商角色口径，落在联系人的单个角色字段上；企业主表以 JSON 数组承载多角色，见 [[CustCompanyTypeEnum]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 createCustCompany 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 供应商角色
predicate: cust_person_info.company_type = 'SUPPLIER'
scope: 客户角色
evidence: code
```

关联：[[cust_person_info]]、[[cust_role_info]]、[[CustCompanyTypeEnum]]。