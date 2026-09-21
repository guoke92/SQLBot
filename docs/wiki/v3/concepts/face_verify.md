---
type: concept
title: 人脸识别认证
page_key: face_verify
belong: concepts
domain: cust
status: draft
aliases: [活体人脸, 微信扫码人脸]
maps_to: cust_certification_info__certification_type.FACE_VERIFY
field_targets: [cust_certification_info__certification_type.FACE_VERIFY, cust_certification_info.certification_type]
sources: ['code_path:CustCertificationTypeEnum.java:17', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_certification_info]
also_confused_with: [account_admin, skip_realname]
adjudication: boundary
---

# 人脸识别认证

CustCertificationTypeEnum.FACE_VERIFY=人脸识别认证，落在证照/核验表 certification_type。
document_claim:人脸识别认证.md
document_claim:非身份证件短信认证.md：非身份证走人脸失败后的短信确认，在运营中台；本库 certification_type 仍是 FACE_VERIFY。
不是证件类型 CRET_ID，也不是管理员 user_type，也不是经办人 skip_auth_flag。

## 页面链接

- [[tables/cust_certification_info]]
- [[dicts/cust_certification_info__certification_type]]
- [[concepts/account_admin]]
- [[concepts/skip_realname]]
