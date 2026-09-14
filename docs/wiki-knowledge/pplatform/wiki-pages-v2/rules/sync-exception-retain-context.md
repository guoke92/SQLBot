---
type: rule
title: 同步异常保留上下文不吞
page_key: sync-exception-retain-context
domain: 平台事件监听与同步
status: draft
aliases:
  - custClientSyncService.error
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:syncByRole
  - db:client_api_sync_error
  - "reqdoc:失败数据写入 ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
contract_version: "0.1"
belong: rules
---

异常处理规则：同步失败经 `custClientSyncService.error(e, rpcSync)` 落库 [[tables/client_api_sync_error]] 后抛出，保留上下文用于后续重放与排查。

## 需求背景
同步失败若被静默吞掉，上游无法感知、下游无法重放。落库保留 `service_class_name` 与 `param`（入参原文）使失败可追溯、可重放；「失败数据写入 ClientApiSyncErrorDO，调用异常 → error(...) → 落库」这一文档主张已在代码层证实（`CustSyncService.java:syncByRole`），双源锚点见 frontmatter sources。

## 版本演进
- v0 契约：规则取自 `CustSyncService.syncByRole`；失败记录后续如何被重放，见 [[tables/client_api_sync_error]] 的 ## 版本演进（含未证实主张）。

```ground:rule
name: 同步异常保留上下文不吞
content: "同步失败经 custClientSyncService.error(e, rpcSync) 落库 client_api_sync_error 后抛出，用于后续重放与排查"
impact: 同步失败可追溯、可重试
field_targets:
  - client_api_sync_error.service_class_name
  - client_api_sync_error.param
evidence: "CustSyncService.java:syncByRole + reqdoc:失败数据写入ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
related_pages:
  - tables/client_api_sync_error
  - concepts/sync-error-record
  - calibers/client-sync-error-all-disabled
```