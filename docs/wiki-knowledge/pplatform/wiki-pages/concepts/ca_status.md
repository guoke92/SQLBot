---
type: concept
title: CA签章状态
page_key: ca_status
belong: concepts
domain: CA证书收费与订单
status: published
aliases: ["ca_status", "证书状态"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_company.ca_status"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“CA签章状态”描述企业的 CA 证书/签章当前状态。其取值如 NORMAL/CANCELLED/UNKNOWN 等，业务上应与缴费状态区分。

## 需求背景

在企业台账中需要独立记录 CA 签章状态，以便在证书异常或注销时影响收费与续费策略。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充状态取值与签章业务流程的映射。

相关：[[ca_fee_company]]