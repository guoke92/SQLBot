---
type: concept
title: 电子签章开通
page_key: electronic_seal_activation
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 开通
  - CFCA 注册
  - 上上签开通
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
adjudication: boundary
also_confused_with:
  - cust_company_info.need_register_ca
  - cust_company_info.need_register_bs
belong: concepts
sources: ["enrich:wiki-admin"]
---

必须区分两组字段：`need_register_*` 是“要不要开”的意愿标识，`*_register_status` 是“已经开了”的落库结果；签署判定要求两者同时为 Y（见 [[need_register_ca]]、[[cfca_registered]]）。另外 CFCA（PAPER_LESS）与上上签（BEST_SIGN，AMS 使用）是两个并列的签章通道，不能只检查其中一个。

## 需求背景
电子授权书签署要求企业具备可用签章能力，因此产品侧先采集意愿（`need_register_ca` / `need_register_bs`），再由签章开通流程回写结果状态；两者不同步是“签署被跳过”的常见原因，对应的补偿逻辑见 [[ca_delayed_compensation_sign]]。

## 版本演进
上上签字段（`need_register_bs` / `bs_register_status`）说明签章通道由单一 CFCA 扩展为多通道，且迁移开通时会同时把 `bs_register_status` 与 `ca_register_status` 置 Y；简易认证链路则禁止开通 CA，见 [[simple_identify_disable_ca]]。

相关：[[cust_company_info]]
