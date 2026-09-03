---
type: concept
title: "认证成功"
page_key: build-success
domain: 集团与关联关系
status: published
aliases: ["BUILD_SUCCESS", "审核通过"]
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
maps_to: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
field_targets: []
adjudication: boundary
also_confused_with: ["企业状态 EFFECT"]
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

“认证成功”指企业通过准入流程，`cust_build_status` 为 `BUILD_SUCCESS`。该状态是企业能够触发集团关系待办和协议操作的前提。

## 需求背景

- 认证状态描述企业准入流程，与“企业状态”（正常、冻结等）不同，后者描述企业生命周期。

## 版本演进

- 暂无变更。

相关：[[cust_company_info]] [[build-success-company]] [[auto-send-notice-on-build-success]]