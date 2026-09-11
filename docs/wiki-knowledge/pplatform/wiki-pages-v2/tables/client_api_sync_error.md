---
type: table
title: client_api_sync_error 客户端同步失败记录表
page_key: tables/client_api_sync_error
domain: 平台事件监听与同步
status: draft
aliases:
  - ClientApiSyncErrorDO
  - 客户端同步失败记录
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
  - code:CustSyncService.java:syncByRole
  - "reqdoc:失败数据写入ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
contract_version: "0.1"
---


> 本页 ## 版本演进 收录了未在代码层证实的文档主张（document_claim，未证实）。

client_api_sync_error 是「平台事件监听与同步」主题下的失败留痕表：平台事件经监听回调进入业务系统后，业务系统向客户域发起的 RPC 同步一旦异常，即以入参原文 + 服务类名 + 重试次数落库，形成可排查、可重放的记录。它与 [[tables/cust_build_record]] 的建档异步补偿是两条独立的失败处理链路，口径见 [[concepts/sync-error-record]]。

## 需求背景
平台侧事件触发后构造 `FbpReq<T>` 并回调 `IPlatListener.onEvent`，业务系统消费该事件时需要把数据变动同步到客户/租户等下游系统。同步失败的诉求不是「静默丢弃」而是「留痕」：失败数据写入 ClientApiSyncErrorDO，调用异常 → `error(...)` → 落库（reqdoc 主张，代码层已证实于 `CustSyncService.java:syncByRole` 中的 `custClientSyncService.error`）。因此本表保存了 `service_class_name`（区分失败来源，DB 实测 12 种）、`param`（入参原文）等重放所必需的信息。

## 版本演进
- v0 契约：本表字段语义与失败态口径按 DB 实测沉淀（见 [[calibers/client-sync-error-all-disabled]]、[[calibers/client-sync-error-retry-num-3]]）。
- 启动时重试任务扫描失败记录 → 重放同步请求（StartupSyncRetry）（document_claim，未证实）。
- 服务停止时将队列数据落库，降低消息丢失风险（document_claim，未证实）；现有代码仅见 `CustSyncService.java:shutdownThreadPool` 的 `shutdown/awaitTermination`，未见队列落库实现。

```ground:table
table: client_api_sync_error
database: lowcode_pplatform
desc: 客户端接口同步失败记录
fields:
  - name: id
    type: number
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: enable
    type: string
    desc: enable
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: param
    type: string
    desc: 参数
  - name: remark
    type: string
    desc: remark
  - name: retry_num
    type: number
    desc: 重试次数
  - name: service_class_name
    type: string
    desc: 服务类名称
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

---REVIEW: table | client_api_sync_error---
1. `scope.databases` 在语义分析中未给出物理库名，本页（及本主题其他页）统一填 `unknown`，待确认。
2. `retry_num` 的语义在分析中同时表述为「已重试次数/重试上限」，二者不可同时成立；DB 实测恒为 3，暂按「默认重试上限」理解（见 [[calibers/client-sync-error-retry-num-3]]），需业务确认。
3. 启动重试（StartupSyncRetry）与服务停止队列落库两条文档主张无代码证据，已在 ## 版本演进 标注。
---END REVIEW---