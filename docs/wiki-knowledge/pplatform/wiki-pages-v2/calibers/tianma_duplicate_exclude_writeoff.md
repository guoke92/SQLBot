---
type: caliber
title: 天马重复校验排除已注销
page_key: tianma_duplicate_exclude_writeoff
domain: 准入接入与接入密钥
status: draft
aliases:
  - WRITEOFF 不参与天马重复校验
  - 天马渠道重复放宽
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValueOfTianma
contract_version: "0.1"
belong: calibers
---

# 天马重复校验排除已注销

## 业务定位

该口径规定：天马渠道在按企业名称、统一社会信用代码及其组合做重复校验时，[[tables/cust_company_info|cust_company_info]] 中 `cust_status = 'WRITEOFF'`（已注销）的企业被排除，允许同名/同码企业重新接入。

## 需求背景

天马渠道的历史客户可能已注销，注销主体不应阻塞新企业的接入建档，因此该校验分支需要放开注销记录；这与 [[calibers/duplicate_build_exclude_build_fail|重复建档排除失败建档]] 是两条不同维度（主体状态 vs 建档状态）的排除口径。

## 版本演进

仅天马渠道（`validateSetValueOfTianma`）具备该排除逻辑，属渠道差异化策略。

```ground:caliber
name: 天马重复校验排除已注销
predicate: "cust_company_info.cust_status = 'WRITEOFF'"
scope: 天马建档名称/信用代码/组合重复校验时排除WRITEOFF
evidence: "code:CustAccessApplication.validateSetValueOfTianma"
```