---
type: rule
title: 迁移协议记录幂等
page_key: agreement_record_idempotent
belong: rules
domain: 租户迁移
status: published
aliases: []
oid: 23
sources: [code]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

业务定位：避免重复生成协议拉取任务。

## 需求背景
协议迁移记录初始化需幂等。

## 版本演进
v0.1 基于代码证据。

```ground:rule
name: 迁移协议记录幂等
content: initAgreementMigratory 对每个产品按 cust_id+platform_product_code+agreement_type 计数，0 才插入初始化记录
impact: 避免重复生成协议拉取任务
field_targets: [argeement_migratory_record]
evidence: "code_path:PlatFormMigratoryApplication.java:setAgreementMigratory"
```

关联：[[argeement_migratory_record_status]]