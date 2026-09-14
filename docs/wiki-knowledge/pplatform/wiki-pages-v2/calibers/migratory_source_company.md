---
type: caliber
title: 迁移来源企业
page_key: migratory_source_company
domain: 租户迁移
status: draft
aliases: [迁移企业口径, cust_source=MIGRATORY]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
belong: calibers
---

所有经迁移接口落库的企业统一打上来源标记，用于把迁移企业同平台建档、邀请建档区分开，是迁移范围统计与批量处理的基础口径。业务状态另行由 [[on_the_way_company]] 区分。

```ground:caliber
name: 迁移来源企业
predicate: "cust_company_info.cust_source = 'MIGRATORY'"
scope: "迁移接口落库企业统一标记来源，区别于平台建档/邀请建档"
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

迁移企业需要与平台自建企业区分，以便后续批量补签授权书、批量拉取协议、统计迁移进度。

## 版本演进

来源标记由代码固定写入枚举值，未开放给上游指定；迁移来源企业的后续治理动作（补签、协议）均由该标记驱动。