---
type: rule
title: 已存在企业不回溯覆盖
page_key: no_backtrack_overwrite
domain: 租户迁移
status: draft
aliases: [不回溯覆盖, 以系统为准不更新]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
belong: rules
---

当上游报文比库内数据旧、且企业已是 BUILD_SUCCESS 时，直接返回不更新，落"以系统为准"。这条规则是迁移与日常变更的边界：迁移不能把产融侧更新过的企业信息回退成旧值。

```ground:rule
name: 已存在企业不回溯覆盖
content: "若上游 updateTime 早于库内 update_time 且 cust_build_status=BUILD_SUCCESS，则『以系统为准，不更新』直接返回"
impact: "防止迁移把产融侧更新的企业信息回退成旧值"
field_targets:
  - cust_company_info.update_time
  - cust_company_info.cust_build_status
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

迁移报文可能包含历史时点数据，若直接覆盖会覆盖掉迁移后在产融侧发生的合法变更。

## 版本演进

由"按字段存在即更新"演进为"以 update_time 比较 + 生效状态判断"的双条件保护；尚未覆盖未生效企业的回溯场景。

相关：[[cust_company_info]]、[[migratory_company_status_mapping]]。