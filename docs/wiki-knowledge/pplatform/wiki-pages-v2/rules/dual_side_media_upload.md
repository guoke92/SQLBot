---
type: rule
title: 双端影像上传
page_key: dual_side_media_upload
domain: 文件/附件/媒体
status: draft
aliases: [运营中台与产融双写]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadCustContractFile/uploadCaUpgradeAuthMediaFile/uploadElectronicAuthMediaFile"]
contract_version: "0.1"
belong: rules
---
上传授权书、CA 升级授权书、电子授权书时先上传运营中台，再上传产融影像树，保证两端影像数据一致。分类口径见 [[media_catg_a0004]]、[[media_catg_a0049]]、[[media_catg_a0050]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadCustContractFile / uploadCaUpgradeAuthMediaFile / uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 双端影像上传
content: 上传授权书/CA升级授权书/电子授权书时，先上传运营中台，再上传产融影像树。
impact: 保证运营中台与产融影像数据一致
field_targets: [media_file.busi_key, media_file.catg_id]
evidence: CustMediaFacade.java:uploadCustContractFile/uploadCaUpgradeAuthMediaFile/uploadElectronicAuthMediaFile
```

关联：[[media_file]]、[[busi_key]]、[[catg_id]]、[[media_catg_a0049]]、[[media_catg_a0050]]。