---
type: concept
title: 签章中台证书状态
page_key: cert_status
domain: CA证书认证
status: draft
aliases: [certStatus, rawCertStatus]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
maps_to: cust_company_info.ca_register_status
field_targets:
  - cust_company_info.ca_register_status
  - ca_certification_info.submit_status
adjudication: boundary
also_confused_with:
  - ca_certification_info.submit_status
belong: concepts
field_targets: [cust_company_info.ca_register_status]
sources: ["enrich:wiki-admin"]
---

签章中台返回的证书生命周期状态，经 mapSignCenterStatus 归一为 NORMAL / APPLYING / CANCELLED / EXPIRED / FAIL / UNKNOWN，详见 [[sign_center_cert_status]]。

**边界（boundary）**：中台 NORMAL/APPLYING 视为产融 ca_register_status 有效；CANCELLED/EXPIRED/FAIL 触发回写 N；submit_status 只描述本系统到中台的一次上送，不代表证书生命周期。因此不能用 [[ca_submit_status]] 的 SUCCESS 推断证书有效，也不能用证书 CANCELLED 推断上送失败——两者是不同维度的事件。

## 需求背景

归一结果是 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的输入之一，也是 [[ca_register_status]] 由 Y 回写 N 的触发源。

## 版本演进

- v0：首次沉淀归一集合与"上送态 ≠ 证书态"的边界。

关联页面：[[sign_center_cert_status]]、[[ca_register_status]]、[[ca_submit_status]]、[[need_register_ca_judgement]]、[[ca_certificate]]。

相关：[[cust_company_info]]
