---
type: concept
title: 登录账号
page_key: login_account_term
belong: concepts
domain: cust
status: draft
aliases: [非手机号账号登录, 账号名称]
maps_to: cust_person_info.user_name
field_targets: [cust_person_info.user_name]
sources: ['code_path:UserInfoFacade.java:238', 'document_claim:docs/wiki-knowledge/pplatform/req-index/concepts/产品需求规格说明书_产融平台V1.0.0.md']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
related: [cust_person_info]
also_confused_with: [account_operator]
adjudication: boundary
---

# 登录账号

document_claim:非手机号账号登录.md#14：登录可用账号名而不只是手机号。catalog 注释「登录账号」。
现网从 SSO userName/loginName 回写；运营回调新建管理员时常把手机号写入该列。问登录名看 user_name，不是 user_type。

## 页面链接

- [[tables/cust_person_info]]
- [[concepts/account_operator]]
