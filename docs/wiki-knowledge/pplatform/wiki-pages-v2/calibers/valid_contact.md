---
type: caliber
title: 有效联系人（可展示）
page_key: caliber/valid_contact
domain: 微信生态/小程序/扫脸
status: draft
aliases: [有效联系人, 可展示联系人]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:PlatFormUserApplication.java
contract_version: "0.1"
---

# 有效联系人（可展示）

判定联系人是否可展示的口径：启用且账号状态为 ADD 或 EFFECT；随后按 productTypes 过滤 `is_freeze='N'` 的 SysCustUserRel。

## 需求背景

联系人列表需剔除游客与停用账号，并叠加经办人冻结过滤，保证展示与可操作对象一致。

## 版本演进

v0.1 记录基础谓词与冻结叠加过滤。

```ground:caliber
name: 有效联系人（可展示）
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: "listCompanyUser 按企业 id 查联系人；再按 productTypes 过滤 is_freeze='N' 的 SysCustUserRel。"
evidence: code_path:PlatFormUserApplication.java#listCompanyUser
```

相关：[[cust_person_info]]、[[operator_freeze_state]]、[[face_intent_subject]]。