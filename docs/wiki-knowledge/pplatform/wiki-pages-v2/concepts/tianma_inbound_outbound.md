---
type: concept
title: 天马入站 / 天马出站
page_key: tianma_inbound_outbound
domain: 外部渠道与银行对接
status: draft
aliases:
  - TianmaService.companyArchive
  - TianmaService.companyArchiveDetail
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:TianmaService#companyArchive
  - code:TianmaService#companyArchiveDetail
  - code:TianmaConsumer
contract_version: "0.1"
maps_to: "companyArchive = 天马→产融入站建档；companyArchiveDetail = 产融→天马出站推送建档结果（baseUrl + TianmaConst.COMPANY_ARCHIVE_DETAIL）"
adjudication: boundary
boundary: "入站方法在 TianmaController 链路中真实生效；出站方法体存在，但其唯一调用方 TianmaConsumer 全类处于注释状态，出站链路当前不可用"
also_confused_with:
  - TianmaConsumer.platformCompanyAuditPassNotice（整类被注释）
belong: concepts
---

# 天马入站 / 天马出站

## 业务定位

天马渠道有方向相反的两条链路，方法名相近但语义不同：`TianmaService.companyArchive` 是**入站**建档——天马侧把企业信息推进产融，落库到 [[tables/cust_company_info]]；`TianmaService.companyArchiveDetail` 是**出站**推送——产融把建档结果回推天马（`baseUrl` + `TianmaConst.COMPANY_ARCHIVE_DETAIL`）。

## 需求背景

入站链路需要一套严格的参数校验与默认值补齐（见 [[rules/tianma_inbound_validation]]、[[rules/tianma_default_company_type]]），并以渠道键反查租户（[[rules/tianma_channel_key]]、[[calibers/channel_tenant_mapping]]）。入站建档与标准建档、渠道统一建档是三条并列入口，参见 [[concepts/reg_archive]]。

## 边界澄清

入站方法在 `TianmaController` 链路中真实生效；出站方法体虽然存在，但其唯一调用方 `TianmaConsumer` 全类处于注释状态，出站链路当前不可用。因此涉及"天马建档结果回推"的需求时，不能假设出站已生效——需要先确认该消费者是否恢复启用。

## 版本演进

- v0.1（本页首版）：术语映射与边界来自代码语义分析，尚无需求文档或变更单佐证。

## 关联页面

- 规则：[[rules/tianma_inbound_validation]]、[[rules/tianma_default_company_type]]、[[rules/tianma_channel_key]]
- 口径：[[calibers/channel_tenant_mapping]]、[[calibers/non_writeoff]]
- 概念：[[concepts/channel]]、[[concepts/reg_archive]]
- 载体表：[[tables/cust_company_info]]