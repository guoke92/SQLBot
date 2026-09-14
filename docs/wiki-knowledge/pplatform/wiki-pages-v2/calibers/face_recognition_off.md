---
type: caliber
title: 人脸识别关闭
page_key: face_recognition_off
domain: notification
status: draft
aliases: [faceRecognition=no 口径]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.face_recognition
contract_version: "0.1"
belong: calibers
---

face_recognition='no' 表示该企业不启用人脸识别作为认证手段。本口径仅有 DB 单行样本证据，代码侧未在本次分析中取得判断位置。

## 需求背景
人脸识别属于可选认证强度配置，需求侧允许企业关闭以适配不同地区的合规要求。

## 版本演进
- 仅 DB 样本支撑；若后续取到代码判断位置，应补充到本页证据。

```ground:caliber
name: 人脸识别关闭
predicate: cust_setting_config.face_recognition = 'no'
scope: 企业认证配置
evidence: db
```