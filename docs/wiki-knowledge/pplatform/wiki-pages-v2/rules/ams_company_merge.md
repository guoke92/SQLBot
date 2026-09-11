---
type: rule
title: AMS 企业合并迁移
page_key: ams_company_merge
domain: 租户迁移
status: draft
aliases: [AMS 企业已存在合并, 企业合并迁移规则]
oid: 1
scope:
  databases: [未提供]
sources:
  - code_path:PlatFormMigratoryApplication.java:migratoryCust
  - reqdoc:产融平台数据迁移涉及的改造需求V1.2
contract_version: "0.1"
---

当迁移过来的企业在目标侧已存在时，不能简单新建，而要走合并分支：在产品为 AMS 的前提下，补齐新增的管理员、操作员与角色，并处理协议与影像件迁移。

```ground:rule
name: AMS 企业合并迁移
content: 当产品为 AMS 且企业已存在时，执行合并逻辑：补充新增的管理员、操作员、角色，并处理协议和影像迁移。
impact: 企业数据合并
field_targets:
  - cust_company_info
  - cust_person_info
  - cust_role_info
  - cust_project_rel
evidence: "code_path:PlatFormMigratoryApplication.java:migratoryCust"
```

## 需求背景

需求文档《产融平台数据迁移涉及的改造需求V1.2》提出了更激进的合并策略：先导出存在多条建档数据的企业，通过 RPA 抓取最新的企业关键字段，对比定位建档数据中最准确的一条；若关键字段都一致，则取建档时间最晚/变更时间最晚的一条，影像件也随之取对应的一套。语义分析将该主张标记为 prose_only，差异为：代码中对于 AMS 产品且企业已存在时确有合并逻辑（补充管理员、操作员、角色等），但未实现“RPA 抓取最新字段并对比选择最准确一条”的策略。**合并规则以代码为准**，需求描述仅作背景；该差异不写入锚点块。

## 版本演进

- v0（草稿）：以代码证据固定合并规则的实现范围；需求侧 RPA 择优策略未覆盖，待产品与研发确认是否演进。

关联页面：[[company_sync_lock]]、[[migratory_cust]]、[[migratory_user_record_init]]。