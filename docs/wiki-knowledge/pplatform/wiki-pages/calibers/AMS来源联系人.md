---
type: caliber
title: AMS来源联系人
page_key: caliber_ams_source_contact
domain: customer
status: published
aliases: ["第三方联系人"]
oid: 1
sources: ["enrich:wiki-admin"]
contract_version: "0.1"
field_targets: [cust_person_info.source]
scope:
  databases: [lowcode_pplatform]
---

该口径定义AMS来源联系人的判定条件：`cust_person_info.source = 'AMS'`。用于区分第三方同步来源，查询用户列表时AMS来源直接视为已同步。

## 需求背景

在AMS对接场景下，联系人可能来自AMS系统同步或其他内部新增，来源字段决定了后续的同步状态判定和实名认证处理流程。

## 版本演进

口径来自代码证据，无文档声明冲突。

```ground:caliber
name: AMS来源联系人
predicate: "cust_person_info.source = 'AMS'"
scope: 用于区分第三方同步来源，查询用户列表时AMS来源直接视为已同步
evidence: code
```

相关：[[cust_person_info]]
