---
type: caliber
title: 渠道启用过滤
page_key: channel_enable_filter
domain: 外部渠道与银行对接
status: draft
aliases:
  - 渠道启用口径
  - cust_access_secret.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
  - code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-alipay-ant/.../controller/AlipayAntArchiveController.java#channelArchive
contract_version: "0.1"
belong: calibers
---

渠道启用过滤是渠道鉴权与租户定位的前置口径：只有启用中的渠道才允许接入并解析出租户，否则直接拒绝。

## 需求背景
非标渠道建档复用统一入站 URL，channel 完全由请求体决定（首期支付宝蚂蚁），因此渠道有效性必须在解析请求体后立刻用本口径校验；命中后据 [[cust_access_secret]] 反查真实 dbTenantCode（见 [[tenant]]、[[channel]]）。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: 渠道启用过滤
predicate: "cust_access_secret.enable = 'Y'"
scope: 渠道鉴权、渠道→租户(dbTenantCode)定位、变更渠道校验
evidence: "code:CustAccessApplication.validateSetValue / validateChangeChannelAndTenant + code_path:lowcode-pplatform-openapi/lowcode-pplatform-openapi-non-standard-alipay-ant/.../controller/AlipayAntArchiveController.java#channelArchive + reqdoc:non-standard-channel-unified-ingress-url"
```