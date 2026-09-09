---
type: rule
title: AMS新增联系人并发锁
page_key: rule_ams_add_contact_lock
belong: rules
domain: customer
status: published
aliases: []
oid: 1
sources: []
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

该规则描述AMS新增联系人接口的并发控制，使用Redis锁防止同企业同业务标签重复新增。

## 需求背景

在AMS第三方对接中，并发新增联系人可能导致重复记录。规则要求 `addEnterpriseContact` 接口使用Redis锁，key为 `PPB:ADDENTERPRISECONTACT:{companyName}-{bizLabel}`，加锁失败抛异常，finally释放锁。

## 版本演进

规则来自代码路径 `PlatFormAmsProviderImpl.addEnterpriseContact`，无文档声明冲突。

```ground:rule
name: AMS新增联系人并发锁
content: "addEnterpriseContact使用Redis锁，key=PPB:ADDENTERPRISECONTACT:{companyName}-{bizLabel}，加锁失败抛异常，finally释放锁"
impact: 防止同企业同业务标签重复新增联系人
field_targets:
  - "cust_person_info"
evidence: "code_path:PlatFormAmsProviderImpl.addEnterpriseContact"
```