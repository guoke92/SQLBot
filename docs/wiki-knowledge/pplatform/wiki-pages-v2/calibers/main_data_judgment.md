---
type: caliber
title: 主数据判定
page_key: main_data_judgment
domain: 企业建档与认证
status: draft
aliases:
  - 主数据口径
  - data_type 主数据
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
contract_version: "0.1"
belong: calibers
---

[[tables/cust_company_info]] 同表承载主数据（'1'）、记录数据（'0'）与流程申请数据（'2'）。凡是对"企业本身"的状态变更与生效企业查询，都必须先限定为主数据，否则会把流程数据的中间态误当作企业状态。

```ground:caliber
name: 主数据判定
predicate: cust_company_info.data_type = '1'
scope: 状态变更/生效企业查询均限定主数据
evidence: code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus
```

## 需求背景

状态回写（`updateCustBuildStatus`）与生效企业清单（[[calibers/effect_company_scope]]）都建立在主数据口径之上；离开该口径，`cust_status` 的 `EFFECT` 与 `cust_build_status` 的 `BUILD_SUCCESS` 会失去唯一指向。

## 版本演进

v0 初稿：口径固化自写值点 `data_type='1'`，与 DB 中 '0'/'2' 的取值分布一致。

关联：[[calibers/judge_have_applying_record]]、[[rules/status_update_optimistic_match]]、[[rules/apply_data_archive_to_main]]。