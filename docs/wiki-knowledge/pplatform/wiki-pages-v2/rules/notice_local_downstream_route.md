---
type: rule
title: 站内信本地与下游路由
page_key: notice_local_downstream_route
domain: notification
status: draft
aliases: [resolveLocalNoticeSystem, 待办路由]
oid: 1
scope:
  databases: []
sources:
  - CustNoticeService.java:resolveLocalNoticeSystem
contract_version: "0.1"
belong: rules
---

CustNoticeService.pageTodo 对 ACCOUNT_PRODUCT 映射本地 system=pplatform，BEECREDIT 映射本地 system=BEECREDIT，其余产品走 Dubbo 下游产品查询待办。

## 需求背景
站内信与待办分属不同产品线，部分产品数据在本库、部分在下游，需求侧要求查询时按产品自动路由，避免全量聚合。被否证的需求主张：「所有通知同步发送站内信」——代码中 sendAllMessageForSubmit 是分别发送站内信、待办、短信，并未统一强制站内信，故该主张不成立。

## 版本演进
- 本地映射当前为硬编码产品码集合，新增本地产品需改代码；下游路由依赖 Dubbo 可用性。

```ground:rule
name: 站内信本地与下游路由
content: CustNoticeService.pageTodo 对 ACCOUNT_PRODUCT 映射本地 system=pplatform，BEECREDIT 映射本地 system=BEECREDIT，其余走 Dubbo 下游产品
impact: 决定待办查询走本库还是下游
field_targets: []
evidence: CustNoticeService.java:resolveLocalNoticeSystem
```