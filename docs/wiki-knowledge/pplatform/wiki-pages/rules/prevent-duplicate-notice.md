---
type: rule
title: "发送待办前校验是否存在未处理待办"
page_key: prevent-duplicate-notice
belong: rules
domain: 集团与关联关系
status: published
aliases: []
oid: 1
sources: ["语义分析"]
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 业务定位

发送集团成员单位协议通知前，检查是否已存在未处理待办，防止重复发送。

## 需求背景

- 发送集团成员单位协议通知前查询最近未处理待办，存在则不允许重复发送。

## 版本演进

- 暂无变更。

```ground:rule
name: 发送待办前校验是否存在未处理待办
content: 发送集团成员单位协议通知前查询最近未处理待办，存在则不允许重复发送
impact: 防止重复待办
field_targets:
  - noticeProvider.queryLatelyNotice
evidence: code_path:CustGroupLicenseApplication.sendCustGroupRelNotice
```

相关：[[cust_group_rel]] [[group-member-relation-status]]