---
type: caliber
title: 建档失败可复用口径
page_key: calibers/build_fail_reusable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 建档失败可复用口径
  - BUILD_FAIL 复用
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#initCust
  - code:CustAccessApplication#initCustOfTianma
  - code:CustAccessApplication#validateSetValueOfTianma
contract_version: "0.1"
---

# 建档失败可复用口径

## 业务定位

该口径规定：当存量企业记录的 `cust_build_status = 'BUILD_FAIL'` 时，建档初始化允许复用这条旧记录覆盖写，而不是新建一条企业记录。天马渠道的重复校验也对 `BUILD_FAIL` 放行。它是渠道重复建档能"重开一次"的数据层基础。

## 需求背景

渠道入站建档可能中途失败，若每次重试都新建记录，会产生同一统一社会信用代码下的多条企业记录。因此在 `initCust` / `initCustOfTianma` 中把 `BUILD_FAIL`（以及 `WRITEOFF`，见 [[calibers/non_writeoff]]）旧记录纳入可覆盖写的范围。与之相对的拦截口径是 [[calibers/standard_api_registered]]。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 建档失败可复用口径
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: initCust/initCustOfTianma 允许复用旧企业记录（BUILD_FAIL 或 WRITEOFF）覆盖写；天马重复校验对 BUILD_FAIL 放行
evidence: "code:CustAccessApplication#initCust / #initCustOfTianma / #validateSetValueOfTianma"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 流程：[[processes/cust_build_status_machine]]
- 相关口径：[[calibers/standard_api_registered]]、[[calibers/non_writeoff]]、[[calibers/cust_company_info_enable_active]]
- 术语：[[concepts/reg_archive]]