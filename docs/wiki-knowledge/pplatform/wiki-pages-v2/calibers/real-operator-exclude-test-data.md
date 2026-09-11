---
type: caliber
title: 真实运营方（排除测试数据）口径
page_key: calibers/real-operator-exclude-test-data
domain: 企业集团关系
status: draft
aliases: [真实运营方, test_data != Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:queryTenantOperatorCompany
contract_version: "0.1"
---

真实运营方指租户下真正承担运营主体角色的企业，判定条件为 `cust_company_info.test_data != 'Y'`（排除测试数据），使用场景为：租户存在多个 PLATFORM_OPERATOR_COMPANY 时仅保留非测试运营方。

## 需求背景

测试租户中常并存多个运营方企业（PLATFORM_OPERATOR_COMPANY），若不做剔除会导致运营主体识别歧义（取到测试企业），因此对运营方查询追加 test_data 过滤。注意 `!= 'Y'` 对 NULL 值的处理需按各库比较语义核对，见文末 REVIEW。

## 版本演进

v0 契约按现状固化，该口径仅作用于运营方识别链路。

## 口径锚点

```ground:caliber
name: 真实运营方（排除测试数据）
predicate: cust_company_info.test_data != 'Y'
scope: 租户存在多个 PLATFORM_OPERATOR_COMPANY 时仅保留非测试运营方
evidence: code_path:CustGroupRelApplication.java:queryTenantOperatorCompany
```