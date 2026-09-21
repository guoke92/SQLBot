---
type: concept
title: 直推企业变更单
page_key: direct_init_change_record
belong: concepts
domain: cust
status: draft
aliases: [直推变更, oper_channel直推, 渠道直推变更]
maps_to: cust_change_record.oper_channel
field_targets: [cust_change_record.oper_channel, cust_change_record.status, cust_change_record.need_resign_auth]
sources: ['code_path:ChannelChangeDirectRecordService.java:148', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_change_record]
also_confused_with: [change_item_code, cross_tenant_resign, authorization_book, direct_init_access_mode,
  direct_init_need_resign]
adjudication: boundary
---

# 直推企业变更单

直推变更走同表 cust_change_record，oper_channel=DIRECT_INIT（与 access_mode 码相同，但是另一列）。
status 库内写 CheckStatus（CUST_CHECK_PASS / CUST_CHECK_BACKTOCUSTOM），对外 HTTP 映射 CustBuildStatusEnum；不要把 HTTP 建档码当成本列库值。
企业表 check_status / cust_build_status 由 DirectInitAccessModes 另行同步，与变更单 status 同枚举族但不同行。
不是运营中台 oper_channel=operation-pplatform-* 的常规变更通道。

## 页面链接

- [[tables/cust_change_record]]
- [[dicts/cust_change_record__need_resign_auth]]
- [[dicts/cust_change_record__oper_channel]]
- [[dicts/cust_change_record__status]]
- [[concepts/authorization_book]]
- [[concepts/change_item_code]]
- [[concepts/cross_tenant_resign]]
- [[concepts/direct_init_access_mode]]
- [[concepts/direct_init_need_resign]]
