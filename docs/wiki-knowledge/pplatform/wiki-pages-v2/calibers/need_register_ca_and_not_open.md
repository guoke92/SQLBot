---
type: caliber
title: 需开通CA且未开通
page_key: need_register_ca_and_not_open
domain: 企业建档与认证
status: draft
aliases:
  - 待签 CFCA 协议
  - selectCustNeedSingCfca
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:ApplyCompanyInfoApplication.java:selectCustNeedSingCfca
contract_version: "0.1"
belong: calibers
---

筛出"业务上需要开通电子签章、但当前尚未开通"的企业，用于判断客户是否还需签署 CFCA 协议。两个条件必须同时成立：需求标记为 Y，开通状态为 N（`P` 开通中不算）。

```ground:caliber
name: 需开通CA且未开通
predicate: cust_company_info.need_register_ca = 'Y' AND cust_company_info.ca_register_status = 'N'
scope: 判断客户是否需签署 CFCA 协议
evidence: code_path:ApplyCompanyInfoApplication.java:selectCustNeedSingCfca
```

## 需求背景

电子签章开通是认证链路的后续动作，简易认证被强制不开通 CA（见 [[rules/simple_auth_no_ca]]），因此该口径与 [[tables/cust_company_info]] 上的 `need_register_ca` / `ca_register_status` 写值点强耦合。上上签侧有对称字段 `need_register_bs` / `bs_register_status`。

## 版本演进

v0 初稿：口径固化自 `selectCustNeedSingCfca`。`ca_register_status='P'`（开通中）被排除的合理性待确认。

关联：[[concepts/identify_style]]、[[rules/simple_auth_no_ca]]。