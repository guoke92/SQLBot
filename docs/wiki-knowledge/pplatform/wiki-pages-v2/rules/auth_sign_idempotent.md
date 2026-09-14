---
type: rule
title: 授权书签署幂等（Redis 锁 + 完成标记）
page_key: auth_sign_idempotent
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署幂等
  - 授权书签署防重
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
belong: rules
---

签署动作必须幂等：先用完成标记判重，再用分布式锁抢执行权，成功后写完成标记；签署失败只记日志、不回滚主流程。这让 [[ca_delayed_compensation_sign]] 的补偿触发与正常触发可以安全并存。

```ground:rule
name: 授权书签署幂等（Redis 锁 + 完成标记）
content: "签署前用 cust_auth_sign_done:{sourceMainId}:{appNo} 判重，再用 cust_auth_sign_after_audit:{sourceMainId}:{appNo} 抢锁（acquire-timeout 1000ms / lock-timeout 120000ms）执行，成功后写 done 标记；签署失败仅记日志不回滚主流程"
impact: "避免重复签署与并发重复提交"
field_targets: []
evidence: "code:CustAuthSignOrchestrationApplication.java:executeOfflineElectronicAuthSignSafely"
```