---
type: rule
title: CA升级授权书双端上传
page_key: CA升级授权书双端上传
domain: 文件媒体与附件
status: published
aliases: []
oid: 1
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---
本页记录规则「CA升级授权书双端上传」。该规则保证 CA 升级授权书在运营中台与产融影像树双端数据一致。

## 需求背景
代码路径 `CustMediaFacade.java:uploadCaUpgradeAuthMediaFile` 显示：CA 升级授权书 A0049 先上传运营中台，再上传产融影像树，逻辑与普通授权书一致。该规则与 [[CA升级授权书影像]] 对应。

## 版本演进
v0.1 固化当前代码规则。后续可补充双端失败补偿机制。

```ground:rule
name: CA升级授权书双端上传
content: "CA升级授权书A0049先上传运营中台，再上传产融影像树，逻辑与普通授权书一致"
impact: "双端数据一致"
field_targets:
  - MediaFile.catgId
  - MediaFile.busiKey
evidence: "code_path:CustMediaFacade.java:uploadCaUpgradeAuthMediaFile"
```