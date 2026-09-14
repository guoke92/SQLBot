---
type: caliber
title: 电子授权书分类
page_key: media_catg_a0050
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0050, 电子授权书]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
belong: calibers
---
影像树中电子授权书分类口径，仅新增不删除，规则见 [[electronic_auth_incremental_upload]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: 电子授权书分类
predicate: media_file.catg_id = 'A0050'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[electronic_auth_incremental_upload]]。