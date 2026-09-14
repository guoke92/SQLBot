---
type: caliber
title: 作废客户排除
page_key: writeoff_excluded
domain: 外部渠道与银行对接
status: draft
aliases:
  - 作废件豁免
  - WRITEOFF 排除
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValueOfTianma
contract_version: "0.1"
belong: calibers
---

作废（WRITEOFF）企业在天马撞库校验中被排除，允许以同一信用代码重新建档。

## 需求背景
天马渠道建档查重按 notIn(WRITEOFF) 过滤，作废件不阻塞新申请；该口径与 [[build_fail_reusable]] 共同决定「同企业能否再次建档」，状态含义见 [[cust_status]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 作废客户排除
predicate: "cust_company_info.cust_status = 'WRITEOFF'"
scope: 天马撞库校验 notIn(WRITEOFF)，作废件允许重新建档
evidence: "code:CustAccessApplication.validateSetValueOfTianma"
```