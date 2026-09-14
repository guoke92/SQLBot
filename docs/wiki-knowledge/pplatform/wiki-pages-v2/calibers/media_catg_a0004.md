---
type: caliber
title: 授权书影像分类
page_key: media_catg_a0004
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0004, 授权书分类]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:hasAuthorizationAgreementMedia", "code:PlatFormMediaApplication.java:lookupCustMedia"]
contract_version: "0.1"
belong: calibers
---
影像树中企业授权书分类口径。该分类受按操作人过滤规则 [[catg_operator_filter]] 约束，并用于授权书存在性判断 [[company_auth_media_existence]]；规则 [[electronic_auth_incremental_upload]] 明确禁止向本分类写入电子授权书。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 lookupCustMedia、hasAuthorizationAgreementMedia 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 授权书影像分类
predicate: media_file.catg_id = 'A0004'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[company_auth_media_existence]]、[[catg_operator_filter]]。