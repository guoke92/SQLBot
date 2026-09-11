---
type: rule
title: 企业重复建档校验
page_key: rule.company_build_duplicate_check
domain: 准入接入
status: draft
aliases: [重复建档, 企业已建档]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
contract_version: "0.1"
---

在同一租户下，若统一社会信用代码已存在于 `cust_company_info`，且该企业的建档状态不满足排除条件，则判定为重复建档，抛出“企业已建档！”。

“已存在”的取数口径不是“存在即可”，而是 [[calibers/company_build_dedup_exclude]]：只有 `cust_build_status != 'BUILD_FAIL'` 的记录才计入，建档失败的企业允许重新发起。状态取值与流转见 [[processes/cust_company_info_cust_build_status]]。针对天马渠道还有更细的分支，见 [[rules/tianma_company_build_duplicate_check]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValue` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValue`。

```ground:rule
name: 企业重复建档校验
content: 同一租户下，统一社会信用代码已存在且cust_build_status != 'BUILD_FAIL'时，抛出'企业已建档！'
impact: 防止重复建档
field_targets:
  - cust_company_info.certification_no
  - cust_company_info.db_tenant_code
  - cust_company_info.cust_build_status
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValue"
```