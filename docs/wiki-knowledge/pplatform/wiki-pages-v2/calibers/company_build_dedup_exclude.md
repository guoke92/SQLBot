---
type: caliber
title: 企业重复建档排除条件
page_key: company_build_dedup_exclude
domain: 准入接入
status: draft
aliases: [重复建档排除, cust_build_status != BUILD_FAIL]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
belong: calibers
---

「企业重复建档排除条件」是重复建档校验的取数口径：判定“已存在企业”时，只统计 `cust_company_info.cust_build_status != 'BUILD_FAIL'` 的记录。也就是说，处于建档失败态的企业不算作“已建档”，允许重新发起。

该口径服务于 [[rules/company_build_duplicate_check]] 与 [[rules/tianma_company_build_duplicate_check]]；与状态取值的关系见流程页 [[processes/cust_company_info_cust_build_status]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；口径定义来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版口径，来源为 `validateSetValue`。

```ground:caliber
name: 企业重复建档排除条件
predicate: "cust_company_info.cust_build_status != 'BUILD_FAIL'"
scope: 企业重复建档校验
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```