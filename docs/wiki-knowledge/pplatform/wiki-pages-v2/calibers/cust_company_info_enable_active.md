---
type: caliber
title: 企业有效口径
page_key: calibers/cust_company_info_enable_active
domain: 外部渠道与银行对接
status: draft
aliases:
  - 企业有效口径
  - enable=Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustAccessApplication#query
  - code:CustAccessApplication#batchQuery
  - code:CustAccessApplication#changeCompanyInfo
contract_version: "0.1"
---

# 企业有效口径

## 业务定位

`enable = 'Y'` 是 `cust_company_info` 上最基础、覆盖最广的过滤口径：所有标准开放接口的查询 / 变更 / 重复校验都带该条件，取值来自 `EnableEnum`。它回答的是"这条企业记录当前是否有效"，与 `cust_status`（新增/变更/注销）不是一回事——注销企业仍可能是 `enable='Y'` 的有效记录。

## 需求背景

渠道与银行对接场景下，企业记录存在覆盖写、复用等写路径（见 [[calibers/build_fail_reusable]]），因此查询侧需要一个稳定的"有效记录"锚点，避免把历史失效记录读出来。`enable` 承担该职责，所有查询均带 `enable='Y'`。

## 版本演进

- v0.1（本页首版）：口径来自代码语义分析，尚无需求文档或变更单佐证。

```ground:caliber
name: 企业有效口径
predicate: "cust_company_info.enable = 'Y'"
scope: 所有标准开放接口查询/变更/重复校验
evidence: "code:CustAccessApplication#query / #batchQuery / #changeCompanyInfo（eq(CustCompanyInfoDO::getEnable, EnableEnum.Y.name())）"
```

## 关联页面

- 载体表：[[tables/cust_company_info]]
- 相关口径：[[calibers/non_writeoff]]、[[calibers/standard_api_registered]]、[[calibers/batch_query_limit]]
- 术语：[[concepts/company_status_fields]]