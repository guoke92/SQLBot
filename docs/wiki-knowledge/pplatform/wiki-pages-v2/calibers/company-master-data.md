---
type: caliber
title: 主数据企业
page_key: caliber.company-master-data
domain: 企业变更与运营变更
status: draft
aliases: [data_type=1, 主数据口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
---

「主数据企业」是 [[tables.cust_company_info]] 上 `data_type = '1'` 的口径，用于限定建档/认证状态流转更新的作用范围（`1`=主数据、`0`=记录数据）。相关字段语义见企业客户信息表页。

## 需求背景

同一企业在库中可能存在记录数据行，状态流转只应作用于主数据行，否则会污染历史/记录数据；因此更新条件显式限定 `data_type = '1'`。

## 版本演进

v0.1：首次登记，口径来自 `CustCompanyInfoApplication.appenUpdateCustBulidStatus`。

```ground:caliber
name: 主数据企业
predicate: "cust_company_info.data_type = '1'"
scope: 建档/认证状态流转更新的过滤条件
evidence: code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
```