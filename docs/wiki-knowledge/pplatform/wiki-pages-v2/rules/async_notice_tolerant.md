---
type: rule
title: 签署待办异步容错发送
page_key: async_notice_tolerant
domain: 集团关系
status: draft
aliases:
  - 待办异步发送
oid: 1
scope:
  databases:
    - customer_management
sources:
  - code
  - reqdoc
contract_version: "0.1"
belong: rules
---

# 签署待办异步容错发送

签署待办通过 `@Async("custGroupThreadPool")` 异步发送，并在事务提交后（`TransactionSynchronization.afterCommit`）触发；发送异常仅 `log.warn`，不阻断主流程。

## 需求背景

需求文档要求：“消息异步发送，不阻塞主流程；发送失败记录日志，不抛出异常。”代码实现与该主张一致：异步线程池 + 事务提交后回调 + catch 记 warn，保证集团关系落库不被通知失败回滚，见 [[cust_group_rel_status]]、[[notice_no_duplicate]]。

## 版本演进

- 需求文档另有主张“所有通知同步发送站内信，用户登录后可查看站内信”。**该主张为 document_claim，未证实**：当前证据只覆盖 `noticeProvider`/`complete` 的待办发送与消除，站内信落库链路未出现在给出的文件中。
- 由于异常被吞掉，通知失败只在日志可见，运营排查需以日志为准。

```ground:rule
name: 签署待办异步容错发送
content: '@Async 线程池 + 事务提交后 afterCommit 触发，异常仅 log.warn 不阻断主流程'
impact: 异步/容错
field_targets:
  - cust_group_rel.status
evidence: code_path:CustGroupRelApplication.java:sendCustGroupRelNotice + reqdoc:msg-async-not-block
```