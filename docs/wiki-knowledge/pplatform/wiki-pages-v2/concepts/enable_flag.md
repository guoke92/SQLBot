---
type: concept
title: 启用标识
page_key: enable_flag
domain: 平台事件监听与同步
status: draft
aliases:
  - enable
  - EnableEnum
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
maps_to: client_api_sync_error.enable
field_targets:
  - client_api_sync_error.enable
  - cust_company_info.enable
  - cust_person_info.enable
adjudication: synonym
also_confused_with:
  - cust_company_info.enable
belong: concepts
field_targets: [client_api_sync_error.enable]
---

各表的 `enable` 统一由 `EnableEnum(Y/N)` 表达，但在本主题内落库写法并不统一，是跨表比对的主要噪声来源。

## 需求背景

- [[client_api_sync_error]]：结构默认 Y，但存量失败记录全为 N（失败登记后置 N），见 [[sync_error_retained_scope]]。
- [[cust_person_info]] / [[sys_cust_user_rel]]：经办人删除时写 `EnableEnum.N.name()`，而另有代码路径直接写字面量 `'Y'`。
- [[cust_company_info]]：企业启用标识，同属 EnableEnum 语义。

## 版本演进

- 写值风格从字面量逐步收敛到枚举：`name()`、`getDictKey()`、字面量三者并存，见页末 REVIEW。