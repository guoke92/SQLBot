---
type: rule
title: 迁移企业状态映射
page_key: migratory_company_status_mapping
domain: 租户迁移
status: draft
aliases: [cust_status 映射, 迁移企业状态派生]
oid: 1
scope:
  databases: ["<待确认：语义分析未给出物理库名>"]
sources:
  - "code:PlatFormMigratoryApplication.java#setCompany"
contract_version: "0.1"
belong: rules
---

`cust_status` 是上游推送的事实，`cust_build_status`/`check_status` 是产融侧派生结果，映射只有两条：EFFECT→BUILD_SUCCESS + CUST_CHECK_PASS；ADD→INIT + null。派生口径见 [[on_the_way_company]]。

```ground:rule
name: 迁移企业状态映射
content: "cust_status=EFFECT → cust_build_status=BUILD_SUCCESS 且 check_status=CUST_CHECK_PASS；cust_status=ADD → cust_build_status=INIT 且 check_status=null"
impact: "在途企业不计入生效口径，避免误开通产品与审核状态"
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
  - cust_company_info.check_status
evidence: "code:PlatFormMigratoryApplication.java#setCompany"
```

## 需求背景

上游状态字典与产融内部状态字典不同，迁移必须做单向映射，绝不能让在途企业进入审核通过集合。

## 版本演进

映射规则固定为两条分支，未引入中间态；后续若增加上游状态需同步扩展映射并回归生效口径。

相关：[[cust_company_info]]、[[在途]]。