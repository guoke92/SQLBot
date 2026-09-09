---
type: concept
title: 收费协议
page_key: fee_agreement
belong: concepts
domain: CA证书收费与订单
status: published
aliases: ["协议", "agreement"]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: "ca_fee_order.agreement_signed/agreement_version/agreement_file_path"
field_targets: []
adjudication: synonym
also_confused_with: []
scope:
  databases: [lowcode_pplatform]
---

“收费协议”是 CA 服务费收取前需企业签署的协议，关联签署状态、签署版本和签章后协议文件路径。

## 需求背景

支付前必须签署协议，订单中需记录协议签署状态、版本与文件证据，以控制支付流程并留存合规凭证。

## 版本演进

v0.1 草稿：作为术语桥接建立，后续可补充协议模板与版本管理规则。

相关：[[ca_fee_order]]、[[agreement_signing_precondition]]