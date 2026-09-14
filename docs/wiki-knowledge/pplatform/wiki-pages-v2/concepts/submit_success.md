---
type: concept
title: 上送成功（术语）
page_key: submit_success
domain: 微信生态/小程序/扫脸
status: draft
aliases:
  - SUCCESS
  - cbsSubmitBizData 成功
oid: 1
scope:
  databases:
    - lowcode_pplatform_cust
sources:
  - "term_bridge:上送成功"
  - lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/cfca/impl/CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
maps_to: ca_certification_info.submit_status='SUCCESS'
field_targets:
  - ca_certification_info.submit_status
adjudication: boundary
also_confused_with:
  - ca_certification_info.submit_status='PENDING'
  - ca_certification_info.submit_status='FAIL'
belong: concepts
sources: ["enrich:wiki-admin"]
---

# 上送成功（术语）

## 业务定位

「上送成功」指签章中台接收成功并落库成功，对应 `ca_certification_info.submit_status = 'SUCCESS'`，判定条件为 `cbsSubmitBizData` 返回 DBaaS `code = 0/200` 且 `biz.status = SAVED`。

## 需求背景

业务口径中的「成功」容易被理解为「请求已发出」，而系统口径是「DBaaS 受理并保存成功」，因此需要区分 `PENDING` 与 `FAIL`。

## 版本演进

从代码可见，成功态可重复上送而保持 `SUCCESS`；失败态由 `markFailed` 追加原因不改状态值，见 [[processes/ca_submit_status|CFCA 上送状态]]。

## 边界

- `SUCCESS`：上送成功，见 [[calibers/ca_submit_success|CA 上送成功]]。
- `PENDING`：仅落库未上送，见 [[calibers/ca_submit_pending|CA 待上送]]。
- `FAIL`：上送异常或失败，需重试时依赖幂等规则。

相关：[[ca_certification_info]]
