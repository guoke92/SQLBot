---
type: concept
title: 经办人跳过实名认证
page_key: skip_realname
belong: concepts
domain: cust
status: draft
aliases: [经办人实名认证, skip_auth_flag]
maps_to: cust_person_info.skip_auth_flag
field_targets: [cust_person_info.skip_auth_flag]
sources: ['code_path:CustPersonController.java:643', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [account_operator, face_verify, main_custom_flg]
adjudication: boundary
---

# 经办人跳过实名认证

document_claim:经办人实名认证.md#15：经办人首次登录要实名。catalog 注释「跳过实名认证标识」。
现网 skip_auth_flag=Y 表示已跳过；HBLT 等主定制可跳过。不是管理员人脸 FACE_VERIFY。

## 页面链接

- [[tables/cust_person_info]]
- [[dicts/cust_person_info__skip_auth_flag]]
- [[concepts/account_operator]]
- [[concepts/face_verify]]
- [[concepts/main_custom_flg]]
