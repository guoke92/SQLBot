---
type: caliber
title: 服务期内
page_key: in_service_period
domain: CA证书收费
status: draft
aliases: [service_end >= 今日, 服务有效期覆盖今日]
oid: 1
scope:
  databases: ["<物理库名>"]
sources:
  - db:ca_fee_company
contract_version: "0.1"
belong: calibers
---

# 服务期内

## 业务定位

以[[tables/ca_fee_company]]的 `service_end >= CURDATE()` 判定，表示企业当前 CA 服务周期**覆盖当日**（服务截止日含当日）。这是"该企业现在是否还享有 CA 服务"的判据，与缴费状态（[[calibers/paid_company]]）相互独立：未缴费企业也可能仍在服务期内（享受已购周期）。

三个时间口径互斥且应成套使用：[[calibers/in_service_period]]（未到期）、[[calibers/expiring_soon]]（≤7 天将到期）、[[calibers/service_expired]]（已到期）。边界日为**含当日**，跨口径拼接时注意不要在 7 天窗口上重复计数。

## 需求背景

本次语义分析未提供需求文档主张（reqdoc 锚点），口径来自代码判定。

## 版本演进

- 本次语义分析未提供与本口径相关的需求文档变更主张（uncovered），无 `(document_claim，未证实)` 条目。

```ground:caliber
name: 服务期内
predicate: "ca_fee_company.service_end >= CURDATE()"
scope: ca_fee_company
evidence: code
```