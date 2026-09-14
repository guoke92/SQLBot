---
type: concept
title: 同步失败记录
page_key: sync-error-record
domain: 平台事件监听与同步
status: draft
aliases:
  - client_api_sync_error
  - ClientApiSyncErrorDO
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
  - code:CustSyncService.java:syncByRole
contract_version: "0.1"
maps_to: "客户端RPC同步调用失败落库记录（service_class_name + param + retry_num）"
field_targets:
  - client_api_sync_error.service_class_name
  - client_api_sync_error.param
  - client_api_sync_error.retry_num
  - client_api_sync_error.enable
adjudication:
  kind: boundary
  boundary: "client_api_sync_error 记录通用客户端同步失败（CustSyncService 用 error() 写入，重试上限以 retry_num 表达，DB实测恒为3）；cust_build_record 记录建档异步流程（pushFile/startProcess）补偿，用 retry_status 表达重试状态。二者表、状态字段均不同。"
also_confused_with:
  - cust_build_record 建档异步补偿记录
belong: concepts
---

「同步失败记录」特指客户端 RPC 同步调用失败的落库留痕，以服务类名 + 入参原文 + 重试次数刻画一次失败，落表 [[tables/client_api_sync_error]]。它常被与 [[concepts/compensation]] 混为一谈，但后者是建档异步流程的重放补偿，二者的表、状态字段、识别口径都不同。

## 需求背景
同步失败的诉求是「不吞异常、可追溯、可重试」：同步失败经 `custClientSyncService.error(e, rpcSync)` 落库后抛出（见 [[rules/sync-exception-retain-context]]），因此记录写入路径本身是异常处理链的一环。失败记录均为停用态（[[calibers/client-sync-error-all-disabled]]），重试上限以 `retry_num` 表达（[[calibers/client-sync-error-retry-num-3]]）。

## 版本演进
- v0 契约：区分口径以表与状态字段为准；重放任务相关文档主张未证实，见 [[tables/client_api_sync_error]] 的 ## 版本演进。