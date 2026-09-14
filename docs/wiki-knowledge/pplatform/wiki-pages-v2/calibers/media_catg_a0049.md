---
type: caliber
title: CA升级授权书分类
page_key: media_catg_a0049
domain: 文件/附件/媒体
status: draft
aliases: [catgId=A0049, CA升级授权书]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadCaUpgradeAuthMediaFile"]
contract_version: "0.1"
belong: calibers
---
影像树中 CA 升级授权书分类口径，上传遵循双端上传规则 [[dual_side_media_upload]]。

## 需求背景
本期语义分析未提供需求文档主张；口径来自代码取值证据。

## 版本演进
v0 初版：口径来自 uploadCaUpgradeAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:caliber
name: CA升级授权书分类
predicate: media_file.catg_id = 'A0049'
scope: 影像树
evidence: code
```

关联：[[media_file]]、[[catg_id]]、[[dual_side_media_upload]]。