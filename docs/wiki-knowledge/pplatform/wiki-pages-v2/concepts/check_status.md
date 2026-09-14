---
type: concept
title: 审核状态
page_key: check_status
domain: 外部渠道与银行对接
status: draft
aliases:
  - checkStatus
  - CheckStatus
  - CUST_CHECK_*
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.getCheckStatus
  - code:CustAccessApplication.terminateBuildingFlow
contract_version: "0.1"
maps_to: cust_company_info.check_status
also_confused_with:
  - cust_company_info.cust_build_status
adjudication: boundary
belong: concepts
field_targets: [cust_company_info.check_status]
sources: ["enrich:wiki-admin"]
---

审核状态是运营流程状态，落库为枚举 `.name()`，读取用 `CheckStatus.getByName`。

## 需求背景
对外状态映射以本字段优先（PASS→CUSTS003+AUTH0003、CHECKING→CUSTS002+AUTH0001、REJECT→CUSTS004+AUTH0001），为空时回落到建档状态；终止建档会把审核置为 CUST_CHECK_REJECT。状态机见 [[cust_check_status]]，与建档的边界见 [[company_archive]]。

## 版本演进
暂无版本演进记录。

相关：[[cust_company_info]]
