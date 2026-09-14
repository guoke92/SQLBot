---
type: concept
title: 非自主建档
page_key: dependent_reg
domain: 准入接入与接入密钥
status: draft
aliases:
  - dependentReg
  - 平台录入
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style = 'INVITE_AGW'
also_confused_with:
  - cust_company_info.identify_style = 'INVITE'
adjudication: boundary
boundary: dependentReg落INVITE_AGW，与自主建档INVITE不同。
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 非自主建档

## 业务定位

「非自主建档」指由平台/运营侧录入而非客户自主确认的建档流程，代码 `dependentReg` 分支把 [[tables/cust_company_info|cust_company_info]] 的 `identify_style` 置为 `INVITE_AGW`。

## 边界与混淆

与 [[concepts/independent_reg|自主建档]]（`INVITE`）是并列的两条流程入口；同一字段不同取值决定建档提交后直接进审核中还是先进待客户确认（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]）。

## 需求背景

平台代录场景无需客户确认，需缩短流程，因此与自主建档分成两条链路。

## 版本演进

暂无进一步版本演进证据。

相关：[[cust_company_info]]
