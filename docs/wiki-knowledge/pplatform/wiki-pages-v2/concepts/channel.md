---
type: concept
title: 渠道
page_key: channel
domain: 外部渠道与银行对接
status: draft
aliases:
  - channel
  - CloudChannel
  - AlipayAntCloudChannel
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:TianmaController
  - code:AlipayAntArchiveController
contract_version: "0.1"
maps_to: cust_access_secret.channel
also_confused_with:
  - cust_company_info.cust_from
  - cust_company_info.cust_source
adjudication: boundary
belong: concepts
field_targets: [cust_access_secret.channel]
sources: ["enrich:wiki-admin"]
---

> (document_claim，未证实)

「渠道」在本文主题中特指接入方标识，它同时决定租户（dbTenantCode）与影像 SFTP 通道，是路由与鉴权的第一维度。

## 需求背景
渠道由请求体传入，非标渠道复用统一入站 URL `/cloud/std/cust/channelArchive`，首期只对接支付宝蚂蚁；天马则走独立入口 `/tianma/companyArchive`。渠道有效性、租户映射与影像通道分别由 [[channel_enable_filter]]、[[tenant]]、[[sftp_channel_enable]] 约束。

## 版本演进
- (document_claim，未证实) BR-003 签名校验：参数排序拼接 + app_secret + MD5 32 位小写，由 CryptoService 统一实现、各渠道复用 Md5Utils/TianmaUtil。本次链路仅见 TianmaUtil.post 的调用点（TianmaService.companyArchiveDetail），未见 CryptoService/Md5Utils 实现，且该主张在语义分析中记录不完整，保留待确认。

相关：[[cust_access_secret]]
