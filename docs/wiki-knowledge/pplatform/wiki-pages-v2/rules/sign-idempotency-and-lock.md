---
type: rule
title: 签署幂等与并发控制
page_key: sign-idempotency-and-lock
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署幂等规则
  - executeOfflineElectronicAuthSignSafely
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
belong: rules
---

签署动作以已完成标记 + 分布式锁双重保护：`cust_auth_sign_done:{sourceMainId}:{appNo}` 表示该单据已签署完成，`cust_auth_sign_after_audit:{sourceMainId}:{appNo}` 为审核后签署的 Redis 分布式锁（获取超时默认 1000ms、锁超时默认 120000ms）。签署成功才写 done 标记，失败仅记日志。键来源见 [[tables/cust_company_info]]（`id` / `app_no`）。

## 需求背景
审核回调可能重复或并发触发，签署是不可逆的对外动作（[[concepts/offline-electronic-auth]]），因此必须幂等；同时签署失败不得回滚审核主流程，故失败只记日志而不抛出。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则；本次分析未提供 document_claim（未证实主张）。

```ground:rule
name: 签署幂等与并发控制
content: "以 cust_auth_sign_done:{sourceMainId}:{appNo} 作为已完成标记，以 cust_auth_sign_after_audit:{sourceMainId}:{appNo} 做 Redis 分布式锁（默认获取超时 1000ms、锁超时 120000ms）；签署成功才写 done 标记，失败仅记日志。"
impact: "重复回调/并发回调不会重复签署；签署失败不回滚审核主流程"
field_targets:
  - cust_company_info.id
  - cust_company_info.app_no
evidence: "code_path:CustAuthSignOrchestrationApplication.java#executeOfflineElectronicAuthSignSafely"
```