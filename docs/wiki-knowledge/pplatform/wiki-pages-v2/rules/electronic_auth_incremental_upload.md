---
type: rule
title: 电子授权书增量上传
page_key: electronic_auth_incremental_upload
domain: 文件/附件/媒体
status: draft
aliases: [电子授权书仅新增]
oid: 1
scope:
  databases: [unknown]
sources: ["code:CustMediaFacade.java:uploadElectronicAuthMediaFile"]
contract_version: "0.1"
belong: rules
---
A0050 电子授权书仅新增不删除，禁止写入 A0004，禁止调用 deleteFileByCatgId；同一流程已存在时跳过，从而保证幂等并避免覆盖历史授权书。相关分类口径见 [[media_catg_a0050]]、[[media_catg_a0004]]。

## 需求背景
本期语义分析未提供需求文档主张；规则来自代码证据。

## 版本演进
v0 初版：规则来自 uploadElectronicAuthMediaFile 证据；无 action=uncovered 的文档主张。

```ground:rule
name: 电子授权书增量上传
content: A0050 电子授权书仅新增不删除，禁止写入 A0004，禁止调用 deleteFileByCatgId；同流程已存在时跳过。
impact: 避免覆盖历史授权书，保证幂等
field_targets: [media_file.catg_id, media_file.specify_file_name]
evidence: CustMediaFacade.java:uploadElectronicAuthMediaFile
```

关联：[[media_catg_a0050]]、[[media_catg_a0004]]、[[media_file]]、[[dual_side_media_upload]]。