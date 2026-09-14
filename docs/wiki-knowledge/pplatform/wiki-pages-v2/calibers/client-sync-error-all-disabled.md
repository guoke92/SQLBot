---
type: caliber
title: 客户端同步失败记录（全部停用态）
page_key: client-sync-error-all-disabled
domain: 平台事件监听与同步
status: draft
aliases:
  - enable='N' 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
contract_version: "0.1"
belong: calibers
---

该口径用于识别 [[tables/client_api_sync_error]] 中的失败记录集合：同步失败记录落库后均为停用态，因此按 `enable='N'` 取数即可覆盖全部失败留痕，无需额外状态过滤。

## 需求背景
同步失败不是业务对象生命周期中的「有效记录」，而是留痕记录。DB 实测 2227 行全部为 `'N'`，说明写入即停用，业务侧不会把失败记录当作有效数据参与后续查询。该口径是 [[concepts/sync-error-record]] 的判定标准，与 [[calibers/build-compensation-pending-records]]（补偿扫描口径）分属两条链路。

## 版本演进
- v0 契约：按 DB 实测沉淀；样本量 2227 行。

```ground:caliber
name: 客户端同步失败记录（全部停用态）
predicate: "client_api_sync_error.enable = 'N'"
scope: DB实测2227行全部为N
evidence: db
related_pages:
  - tables/client_api_sync_error
  - concepts/sync-error-record
```