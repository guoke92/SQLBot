---
type: rule
title: 渠道建档统一入站入口
page_key: channel_archive_unified_entry
domain: 外部渠道与银行对接
status: draft
aliases:
  - /cloud/std/cust/channelArchive
  - AlipayAntArchiveController
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:AlipayAntArchiveController
  - code:AlipayAntArchiveService#channelArchive
contract_version: "0.1"
belong: rules
---

# 渠道建档统一入站入口

## 业务定位

渠道建档统一使用与渠道无关的固定路径 `POST /cloud/std/cust/channelArchive`，由 `AlipayAntArchiveController`（`@RequestMapping("/cloud/std/cust")` + `@PostMapping("/channelArchive")`）承接；具体的 `channel` 由请求体决定，`AlipayAntArchiveService` 会强制 `setChannel(AlipayAntCloudChannel.ALIPAY_ANT)`。该入口刻意避开 `/cloud/std/cust/importNonIndependentCompanyInfo`。

## 需求背景

每接入一个新渠道都改网关与 URL 会带来路由与鉴权配置的重复维护。代码采取的方案是把渠道识别下沉到请求体，路径保持唯一，从而让新增渠道只需新增 Request / Service 层解析，网关与路径不需变更。这与"渠道 ≠ URL 路径"的边界判定一致，见 [[concepts/channel]]。

## 版本演进

- v0.1（本页首版）：规则来自代码语义分析，尚无需求文档或变更单佐证。

```ground:rule
name: 渠道建档统一入站入口
content: "渠道建档使用与渠道无关的固定路径 POST /cloud/std/cust/channelArchive，channel 由请求体决定（AlipayAntArchiveService 强制 setChannel(AlipayAntCloudChannel.ALIPAY_ANT)），便于后续渠道复用同一 URL；刻意避开 /cloud/std/cust/importNonIndependentCompanyInfo"
impact: 新增渠道只需新增 Request/Service 层解析，网关与路径不需变更
field_targets:
  - cust_company_info.db_tenant_code
evidence: "code:AlipayAntArchiveController（类注释 + @RequestMapping(\"/cloud/std/cust\") + @PostMapping(\"/channelArchive\")）, AlipayAntArchiveService#channelArchive"
```

## 关联页面

- 概念：[[concepts/channel]]、[[concepts/reg_archive]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/all_tenant_context]]
- 规则：[[rules/nonstandard_inbound_all_tenant]]
- 载体表：[[tables/cust_company_info]]