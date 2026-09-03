---
type: rule
title: 新增企业联系人并发锁
page_key: rules/enterprise-contact-concurrency-lock
domain: AMS联系人第三方对接
status: published
aliases: [联系人并发锁]
oid: 1
sources:
  - code
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

新增企业联系人接口使用 Redis 分布式锁，保证同一企业+品牌下新增联系人串行。

## 需求背景
AMS 通知产融新增企业联系人时，并发请求可能导致重复联系人。分布式锁 key 为 PPB:ADDENTERPRISECONTACT:{companyName}-{bizLabel}，确保同一企业+品牌下操作互斥。

## 版本演进
初始版本基于 PlatFormAmsProviderImpl.addEnterpriseContact 提取。

```ground:rule
name: 新增企业联系人并发锁
content: "新增企业联系人接口使用Redis分布式锁，锁key为 PPB:ADDENTERPRISECONTACT:{companyName}-{bizLabel}，避免并发冲突"
impact: "保证同一企业+品牌下新增联系人串行"
field_targets: []
evidence: "code_path:PlatFormAmsProviderImpl.addEnterpriseContact"
```

[[brand]] [[cust_person_info_do]] [[add_enterprise_contact_response_code]]