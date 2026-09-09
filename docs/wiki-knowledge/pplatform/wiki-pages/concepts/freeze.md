---
type: concept
title: 冻结
page_key: freeze
belong: concepts
domain: 企业建档与准入
status: published
aliases: [禁用]
oid: 1

sources: ["db", "code", "enrich:wiki-admin"]
contract_version: "0.1"
maps_to: cust_status = 'FREEZE' 或 cust_person_info.status = 'FREEZE'
also_confused_with: ["注销", "失效"]
adjudication: boundary
boundary: 冻结是临时状态，可解冻；注销是终态（WRITEOFF）
field_targets: []
scope:
  databases: [lowcode_pplatform]
---

# 冻结

冻结是一种临时受限状态，可同时出现在企业客户生命周期 `cust_status = 'FREEZE'` 和人员状态 `cust_person_info.status = 'FREEZE'`。冻结可以解冻，区别于终态注销（WRITEOFF）。

## 需求背景

冻结操作常被描述为“禁用”，但数据侧应视为可逆状态。企业冻结/解冻由 [[customer-lifecycle-status-machine]] 管理，操作合法性见 [[company-status-operation-legal-check]] 规则。

## 版本演进

本概念来自语义分析中的术语桥，边界定义为冻结可逆、注销终态。

相关概念：[[auth-status]]

相关：[[cust_person_info]]
