---
type: caliber
title: 在途认证/变更流程判定
page_key: judge_have_applying_record
domain: 企业建档与认证
status: draft
aliases:
  - 在途流程判定
  - judgeHaveApplyingRecord
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
contract_version: "0.1"
belong: calibers
---

判定某企业主数据下是否还挂着一条未结束的流程申请数据，是"禁止重复变更"闸门的输入口径。判定只看流程数据（`data_type='2'`）且排除两个终态，因此处于待客户认证、审核中、变更中等任何中间态都算在途。

```ground:caliber
name: 在途认证/变更流程判定
predicate: cust_company_info.cust_build_status NOT IN ('BUILD_SUCCESS','BUILD_FAIL') AND cust_company_info.data_type = '2' AND cust_company_info.main_data_id = ?
scope: 企业是否存在在途流程，禁止重复变更
evidence: code_path:ApplyCompanyInfoApplication.java:judgeHaveApplyingRecord
```

## 需求背景

企业信息变更必须串行：上一次认证或变更流程未结束前不得再发起，否则主数据与流程数据会互相覆盖。该口径与 [[rules/applying_record_uniqueness]] 配套使用，依赖 [[tables/cust_company_info]] 上的 `data_type`、`main_data_id`、`cust_build_status` 三字段。

## 版本演进

v0 初稿：口径首次固化，无历史版本。限定条件（`data_type='2'` + `main_data_id` 绑定）是否对全部入口生效，待与发起链路复核。

关联：[[calibers/main_data_judgment]]、[[processes/cust_build_status_state_machine]]。