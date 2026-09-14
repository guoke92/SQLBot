---
type: caliber
title: 刷脸意愿主体（客户管理员）
page_key: face_intent_subject
domain: 微信生态/小程序/扫脸
status: draft
aliases: [刷脸主体, 意愿认证主体]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
belong: calibers
---

# 刷脸意愿主体（客户管理员）

取当前登录用户在本企业中的管理员作为刷脸意愿主体：user_type=admin、enable=Y、ref_cust_company_info 匹配企业 code、user_id 匹配当前登录用户。

## 需求背景

刷脸意向须绑定到有身份的客户管理员，保证小程序扫码刷脸的发起主体可追溯。

## 版本演进

v0.1 记录该主体定位谓词。

```ground:caliber
name: 刷脸意愿主体（客户管理员）
predicate: "cust_person_info.user_type = 'accountAdmin' AND cust_person_info.enable = 'Y' AND cust_person_info.ref_cust_company_info = <企业 code> AND cust_person_info.user_id = <当前登录用户>"
scope: "getFaceQrCode / resolveFaceIntentPerson 取当前登录用户在本企业的管理员作为刷脸主体。"
evidence: code_path:FaceVerifyController.java#resolveFaceIntentPerson
```

相关：[[cust_person_info]]、[[cust_company_info]]、[[miniprogram_qrcode]]、[[face_scan]]。