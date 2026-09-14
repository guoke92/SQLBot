---
type: rule
title: 跳过实名认证白名单
page_key: skip_realname_auth_whitelist
domain: 经办人/联系人/管理员管理
status: draft
aliases: [skip_auth_flag, HBLT, 免认证]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonController.java#skipRealNameAuth"]
contract_version: "0.1"
belong: rules
---

只有租户 mainTenantFlgEn=HBLT，或联系人 company_type ∈ {CORE, PROJECT_COMPANY} 时，才允许置 skip_auth_flag=Y；否则抛"不支持该角色的经办人跳过实名认证"（[[cust_person_info]]、[[phone_realname_status]]）。

## 需求背景
- 该规则限制免认证范围，避免任意角色绕过实名认证流程（[[skip_auth_flag]] 所在表见 [[cust_person_info]]）。

## 版本演进
- 当前版本的免认证白名单由租户标志与角色类型两个条件之一满足即可。

```ground:rule
name: 跳过实名认证白名单
content: "仅当租户 mainTenantFlgEn=HBLT 或 company_type ∈ {CORE, PROJECT_COMPANY} 时允许置 skip_auth_flag=Y，否则抛“不支持该角色的经办人跳过实名认证”"
impact: 限制免认证范围
field_targets:
  - cust_person_info.skip_auth_flag
  - cust_person_info.company_type
evidence: "code_path:CustPersonController.java#skipRealNameAuth"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[normal_person]]、[[contact_person]]。