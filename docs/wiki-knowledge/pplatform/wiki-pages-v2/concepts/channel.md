---
type: concept
title: 渠道（channel）
page_key: concepts/channel
domain: 外部渠道与银行对接
status: draft
aliases:
  - channel
  - CloudChannel
  - AlipayAntCloudChannel
  - cust_access_secret.channel
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CloudChannel
  - code:AlipayAntCloudChannel
  - code:AlipayAntArchiveController
contract_version: "0.1"
maps_to: "渠道字典键：代码中可见 CloudChannel.TIANMA.getDictKey()（天马）与 AlipayAntCloudChannel.ALIPAY_ANT（支付宝蚂蚁）；同时用作 cust_access_secret 的渠道键与 SFTP 配置（cust_sftp.channel）的键"
field_targets:
  - cust_company_info.db_tenant_code
adjudication: boundary
boundary: "渠道 ≠ URL 路径：AlipayAntArchiveController 注释明确『路径与 channel 无关，channel 完全由请求体决定』，而天马走独立 /tianma 路径。判定渠道应以渠道密钥表/请求体 channel 字段为准"
also_confused_with:
  - HTTP 路径（/tianma、/cloud/std/cust/channelArchive）
sources: ["enrich:wiki-admin"]
---

# 渠道（channel）

## 业务定位

"渠道"指的是外部接入来源的字典键，在代码中表现为 `CloudChannel.TIANMA.getDictKey()` 与 `AlipayAntCloudChannel.ALIPAY_ANT`。它同时是三个地方的键：渠道密钥表 `cust_access_secret` 的渠道键、SFTP 配置 `cust_sftp.channel` 的键，以及入站报文中标识来源的字段。渠道决定企业数据落到哪个租户，落库字段为 `cust_company_info.db_tenant_code`（见 [[calibers/channel_tenant_mapping]]）。

## 需求背景

平台需要以统一方式承载多个外部渠道（天马、支付宝蚂蚁等）的建档与查询请求。为避免每接一个渠道就改一次网关与路径，渠道被设计为"由请求体携带的字段"而非"由 URL 携带的字段"：统一入站入口见 [[rules/channel_archive_unified_entry]]，租户解析见 [[calibers/channel_tenant_mapping]]。

## 边界澄清

渠道 ≠ HTTP 路径。`AlipayAntArchiveController` 的类注释明确『路径与 channel 无关，channel 完全由请求体决定』，而天马渠道走的是独立 `/tianma` 路径。做渠道判定时应以渠道密钥表或请求体 `channel` 字段为准，不能以 URL 前缀推断。渠道建档与标准建档的入口差异见 [[concepts/reg_archive]]。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/all_tenant_context]]
- 规则：[[rules/channel_archive_unified_entry]]、[[rules/tianma_channel_key]]
- 概念：[[concepts/reg_archive]]、[[concepts/tianma_inbound_outbound]]
- 载体表：[[tables/cust_company_info]]

相关：[[cust_sftp]]
