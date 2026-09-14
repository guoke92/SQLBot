---
type: rule
title: 电子签约版授权书幂等
page_key: electronic-auth-media-idempotent
domain: 文件/附件/媒体
status: draft
aliases: [A0050 幂等, 电子授权书去重, skipIfSameProcessExists]
oid: 1
scope:
  databases: [lls.media]
sources:
  - code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile
contract_version: "0.1"
belong: rules
---

# 电子签约版授权书幂等

## 业务定位

电子签约版授权书（[[calibers/electronic-auth-media-a0050]]）的写入是“追加式”的：`A0050` 上传前若 `skipIfSameProcessExists` 且按 `busiKey`/`userBusiKey`/`specifyFileName` 命中既有影像，则跳过；整体策略为仅新增不删除，禁止写入 `A0004`、禁止调用 `deleteFileByCatgId`。

使用方影响：电子授权书按流程号（`appNo`）累积，历史影像不会被覆盖或清除；如果期望“改一份就替换一份”，那是不成立的预期。

```ground:rule
name: 电子签约版授权书幂等
content: A0050 上传前若 skipIfSameProcessExists 且按 busiKey/userBusiKey/specifyFileName 命中既有影像，则跳过；仅新增不删除，禁止写入 A0004、禁止 deleteFileByCatgId。
impact: 电子授权书按流程号（appNo）追加，不覆盖历史。
field_targets:
  - MediaFile.catgId
  - MediaFile.specifyFileName
  - MediaFile.userBusiKey
evidence: "code_path:CustMediaFacade.java:uploadElectronicAuthMediaFile"
```

## 需求背景

（本页暂无 `reqdoc_claims` 类型的需求文档证据。）

与项目配置影像的“先清空再写入”策略形成对照，见 [[calibers/project-config-media]]。

## 版本演进

- v0（本页）：规则来自 [代码] 证据。