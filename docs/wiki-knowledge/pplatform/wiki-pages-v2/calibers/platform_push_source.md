---
type: caliber
title: 平台推送来源
page_key: platform_push_source
domain: 文件/附件/媒体
status: draft
aliases: [PLATFORM_PUSH 口径]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:isdo"]
contract_version: "0.1"
belong: calibers
---
判定建档数据来自运营中台推送的口径，直接影响影像是否实时同步，见 [[build_media_sync_condition]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 CustMediaFacade.isdo 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 平台推送来源
predicate: cust_company_info.cust_source = 'PLATFORM_PUSH'
scope: 企业建档
evidence: code
```

关联：[[cust_company_info]]、[[CustSourceEnum]]、[[build_media_sync_condition]]。