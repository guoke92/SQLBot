---
type: rule
title: 天马渠道企业重复建档校验
page_key: tianma_company_build_duplicate_check
domain: 准入接入
status: draft
aliases: [天马渠道建档校验, 已通过其他方式完成建档, 正在通过其他方式建档]
oid: 1
scope:
  databases: [lowcode_pplatform_customer]
sources:
  - "code: lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValueOfTianma"
contract_version: "0.1"
belong: rules
---

天马渠道走独立的重复建档校验分支：与通用规则只比对统一社会信用代码不同，这里同时校验企业名称与统一社会信用代码。若命中已存在且非 `BUILD_FAIL` 的记录，则按 `cust_build_status` 的取值抛出不同提示——状态为 `BUILD_SUCCESS` 时提示“已通过其他方式完成建档”，其他状态提示“正在通过其他方式建档”。

其效果仍是防止重复建档，但把“失败态可重建”的口径 [[calibers/company_build_dedup_exclude]] 与状态机 [[processes/cust_company_info_cust_build_status]] 的取值差异显式暴露为不同话术。通用分支见 [[rules/company_build_duplicate_check]]。

## 需求背景

语义分析中的 `reqdoc_claims` 为空，本页暂无需求文档主张可锚定；规则内容来自 `CustAccessApplication.validateSetValueOfTianma` 的代码证据。

## 版本演进

- v0.1（本页）：首版规则，来源 `validateSetValueOfTianma`。

```ground:rule
name: 天马渠道企业重复建档校验
content: 对于天马渠道，校验企业名称和统一社会信用代码，如果已存在且非BUILD_FAIL，则根据cust_build_status抛出不同异常（BUILD_SUCCESS：已通过其他方式完成建档；其他：正在通过其他方式建档）
impact: 防止重复建档
field_targets:
  - cust_company_info.name
  - cust_company_info.certification_no
  - cust_company_info.db_tenant_code
  - cust_company_info.cust_build_status
evidence: "lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccessApplication.java:validateSetValueOfTianma"
```