---
type: rule
title: 待办未读口径
page_key: todo_unread_status
domain: notification
status: draft
aliases: [noticeStatus=0, 未读条件]
oid: 1
scope:
  databases: []
sources:
  - CustNoticeService.java:pageTodo
  - NoticeFacade.java:pageTodoCount
contract_version: "0.1"
belong: rules
---

待办查询与统计统一使用 noticeStatus='0' 作为未完成/未读条件，列表与计数共用同一口径。

## 需求背景
需求侧要求角标数量与列表内容一致，因此统计与分页必须共用同一状态条件。

## 版本演进
- 当前口径集中在两处调用点，未抽为常量，修改时需同时改分页与计数。

```ground:rule
name: 待办未读口径
content: 待办查询与统计使用 noticeStatus='0' 作为未完成/未读条件
impact: 待办数量统计口径
field_targets: []
evidence: CustNoticeService.java:pageTodo + NoticeFacade.java:pageTodoCount
```