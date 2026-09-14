---
type: rule
title: 迁移人员手机号加密匹配
page_key: migratory_person_phone_encrypt_match
domain: 租户迁移
status: draft
aliases: [手机号加密匹配, 加密列去重]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setPersonAdm"
  - "code:PlatFormMigratoryApplication.java#setPersonOper"
contract_version: "0.1"
belong: rules
---

人员去重与覆盖不能直接比明文：查询时以 `encryptAndBase64Str(phone)` 后 `eq` 匹配 `cust_person_info.phone`，命中则先删旧记录再插。相关表见 [[cust_person_info]]。

```ground:rule
name: 迁移人员手机号加密匹配
content: "以 metaDataEncryptionHandler/IMetaDataEncryptionService.encryptAndBase64Str(phone) 后 .eq 查询 cust_person_info.phone（已存在则先删旧记录再插）"
impact: "保证加密列上的去重与覆盖正确"
field_targets:
  - cust_person_info.phone
  - cust_person_info.ref_cust_company_info
evidence: "code:PlatFormMigratoryApplication.java#setPersonAdm,#setPersonOper"
```

## 需求背景

人员手机号属敏感信息，落库加密；迁移的增量判定必须与存储形态一致，否则会产生重复人员或漏更新。

## 版本演进

由明文匹配演进为加密匹配；覆盖方式为"删旧插新"，与 [[ams_migratory_dedup]] 的增量补齐逻辑配合使用。

相关：[[cust_person_info]]、[[ams_migratory_dedup]]。