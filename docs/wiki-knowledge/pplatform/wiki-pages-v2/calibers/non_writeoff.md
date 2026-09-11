---
type: caliber
title: 非注销企业口径
page_key: calibers/non_writeoff
domain: 外部渠道与银行对接
status: draft
aliases:
  - 非注销企业口径
  - notIn WRITEOFF
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#validateSetValueOfTianma
  - code:CustStatusConstant
contract_version: "0.1"
---

# 非注销企业口径

## 业务定位

该口径规定：天马渠道建档做企业重复校验时，需排除 `cust_status = 'WRITEOFF'`（已注销）的企业记录。它限定的是"哪些记录算作可冲突的存量企业"，只作用于天马建档校验路径 `validateSetValueOfTianma`，不是全局查询条件。

## 需求背景

天马入站建档需要允许对已注销企业重新建档，因此重复校验必须以 `notIn CustStatusConstant.WRITEOFF` 缩小存量集合；与它配合的是 [[calibers/build_fail_reusable]]（`BUILD_FAIL` 也放行）。二者共同决定天马渠道的"可复用/可重开"边界。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 非注销企业口径
predicate: "cust_company_info.cust_status <> 'WRITEOFF'"
scope: 天马建档重复校验（notIn CustStatusConstant.WRITEOFF）
evidence: "code:CustAccessApplication#validateSetValueOfTianma"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/build_fail_reusable]]、[[calibers/cust_company_info_enable_active]]
- 流程：[[processes/cust_status_machine]]
- 术语：[[concepts/tianma_inbound_outbound]]