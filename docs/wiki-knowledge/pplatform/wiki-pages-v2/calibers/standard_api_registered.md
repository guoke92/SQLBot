---
type: caliber
title: 标准接口已建档口径
page_key: calibers/standard_api_registered
domain: 外部渠道与银行对接
status: draft
aliases:
  - 标准接口已建档口径
  - 企业已建档！
  - REG_EXIST_EXCEPTION
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValue
contract_version: "0.1"
---

# 标准接口已建档口径

## 业务定位

该口径是标准开放接口建档的前置校验：以「统一社会信用代码 + 数据租户」为组合键统计存量记录，且排除 `cust_build_status = 'BUILD_FAIL'` 的记录；命中即判定"企业已建档"，抛 `REG_EXIST_EXCEPTION`（提示语『企业已建档！』）。它是 `independentReg` / `dependentReg` 两条入口共用的拦截规则。

## 需求背景

同一租户下同一统一社会信用代码只允许存在一条有效建档记录，否则后续银行账户查询、清分配置等以 `certification_no` 为键的下游能力会出现歧义（参见 [[calibers/bocom_account_existence]]）。因此标准接口在入口处即做拦截，而不依赖下游。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 标准接口已建档口径
predicate: "count(cust_company_info.certification_no = ? AND cust_company_info.db_tenant_code = ? AND cust_company_info.cust_build_status <> 'BUILD_FAIL') <> 0"
scope: independentReg/dependentReg 前置校验，命中抛 REG_EXIST_EXCEPTION『企业已建档！』
evidence: "code:CustAccessApplication#validateSetValue"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/build_fail_reusable]]、[[calibers/channel_tenant_mapping]]、[[calibers/cust_company_info_enable_active]]
- 术语：[[concepts/reg_archive]]、[[concepts/company_status_fields]]