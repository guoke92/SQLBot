---
type: caliber
title: 重复建档排除失败建档
page_key: duplicate_build_exclude_build_fail
domain: 准入接入与接入密钥
status: draft
aliases:
  - BUILD_FAIL 不参与重复校验
  - 失败建档可重提
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.initCust
contract_version: "0.1"
belong: calibers
---

# 重复建档排除失败建档

## 业务定位

该口径规定：同租户同统一社会信用代码的重复建档校验中，[[tables/cust_company_info|cust_company_info]] 里 `cust_build_status = 'BUILD_FAIL'` 的记录被排除，即失败建档不阻塞客户重新提交。

## 需求背景

审核拒绝后客户需要修改并重新发起建档（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]] 中 `BUILD_FAIL → CUST_CONFIRM_AWAIT`），因此失败态不能作为重复拦截依据。

## 版本演进

口径同时出现在校验入口（`validateSetValue`）与建档初始化（`initCust`）两处，未发现分支差异。

```ground:caliber
name: 重复建档排除失败建档
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: 同租户同统一社会信用代码重复建档校验时排除BUILD_FAIL
evidence: "code:CustAccessApplication.validateSetValue/CustAccessApplication.initCust"
```