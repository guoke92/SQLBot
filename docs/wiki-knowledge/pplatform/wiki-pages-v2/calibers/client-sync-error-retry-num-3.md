---
type: caliber
title: 客户端同步失败默认重试上限
page_key: calibers/client-sync-error-retry-num-3
domain: 平台事件监听与同步
status: draft
aliases:
  - retry_num=3 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
contract_version: "0.1"
---

该口径描述客户端同步失败记录的重试次数取值特征：DB 实测全部为 3，与补偿链路的默认重试上限（默认 3，见 [[rules/compensation-max-retry]]）数值一致。

## 需求背景
失败重试需要可预期上限。`retry_num` 在 DB 中恒定，说明当前实现不区分单条记录的实际重试次数，而是以固定值表达上限；因此取数时不能据 `retry_num` 做「重试进度」分析。字段语义的歧义见本页 REVIEW。

## 版本演进
- v0 契约：按 DB 实测沉淀，全部为 3。

```ground:caliber
name: 客户端同步失败默认重试上限
predicate: "client_api_sync_error.retry_num = 3"
scope: DB实测全部为3
evidence: db
related_pages:
  - tables/client_api_sync_error
  - rules/compensation-max-retry
```

---REVIEW: caliber | 客户端同步失败默认重试上限---
`retry_num` 的语义在被测数据中无法区分「已重试次数」与「重试上限」（恒为 3）；本页按「默认重试上限」口径沉淀，与 [[rules/compensation-max-retry]] 的 maxRetryCount=3 是否同一配置项待确认。
---END REVIEW---