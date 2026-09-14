---
type: rule
title: 企业授权书存在性判断
page_key: company_auth_media_existence
domain: 文件/附件/媒体
status: draft
aliases: [授权书存在性判断]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:hasAuthorizationAgreementMedia"]
contract_version: "0.1"
belong: rules
---
检查 A0004 分类下是否存在指定 companyId/personId 的影像，用于判断企业授权书是否已上传。分类口径见 [[media_catg_a0004]]，业务键见 [[busi_key]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 hasAuthorizationAgreementMedia 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 企业授权书存在性判断
content: 检查 A0004 分类下是否有指定 companyId/personId 的影像。
impact: 用于判断是否已上传企业授权书
field_targets: [media_file.catg_id, media_file.busi_key, media_file.user_busi_key]
evidence: CustMediaFacade.java:hasAuthorizationAgreementMedia
```

关联：[[media_catg_a0004]]、[[media_file]]、[[busi_key]]、[[catg_id]]。