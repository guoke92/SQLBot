---
type: caliber
title: 真实运营方
page_key: caliber.real_operator
domain: 数据权限与组织
status: draft
aliases: [真实运营方, test_data 过滤]
oid: 1
scope:
  databases: [base]
sources: [code]
contract_version: "0.1"
---

「真实运营方」是 [[calibers/platform_operator_company]] 之上的排除口径：当同一租户存在多个运营方时，排除 test_data='Y' 的测试运营方。判定需要兼容 test_data 为空的情况，即空值不算测试数据。

## 需求背景

语义分析中未出现 reqdoc_claims 条目，本页暂无需求文档主张。

## 版本演进

v0：依据 code 证据（CustGroupRelApplication#queryTenantOperatorCompany）成文。

```ground:caliber
name: 真实运营方
predicate: "test_data ！= 'Y'"
scope: 同一租户存在多个运营方时的过滤（兼容 test_data 为空）
evidence: code_path:CustGroupRelApplication.java#queryTenantOperatorCompany
```