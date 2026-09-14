---
type: rule
title: 待办不可重复发送
page_key: notice_no_duplicate
domain: 集团关系
status: draft
aliases:
  - 签署待办防重复
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
contract_version: "0.1"
belong: rules
---

# 待办不可重复发送

`queryLatelyNotice` 命中未处理待办时抛“企业存在未办理的待办事项，不支持重复发送”，阻断再次发起签署待办。

## 需求背景

成员单位签署待办（[[member_unit]]、[[cust_group_rel_status]]）重复推送会干扰用户并可能产生多份签署记录，因此要求同一关系上同一时刻只有一条未办理待办。

## 版本演进

- 判重依赖“最近待办”查询结果，未见到按关系 ID 的唯一约束，历史脏待办可能造成长期阻断。

```ground:rule
name: 待办不可重复发送
content: queryLatelyNotice 命中未处理待办时抛“企业存在未办理的待办事项，不支持重复发送”
impact: 阻断
field_targets:
  - cust_group_rel.id
evidence: code_path:CustGroupLicenseApplication.java:sendCustGroupRelNotice
```