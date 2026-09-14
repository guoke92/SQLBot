---
type: table
title: 客户端接口同步失败记录
page_key: client_api_sync_error
domain: 平台事件监听与同步
status: draft
anchors: [client_api_sync_error]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












本表是平台向客户端（客户、经办人、影像、产品、租户、项目、KA 等）发起同步调用失败时的登记表。每条记录对应一次失败的 RPC 调用，`service_class_name` 标识具体同步链路，`param` 保留请求参数原文，供重试/排查使用。与 [[cust_build_record]] 的差别在于：本表以「调用失败即登记」为粒度，重试次数有独立列 [[retry_count]]；而建档补偿把重试计数塞进 JSON。

## 需求背景

外部同步链路（用户/企业/经办人/影像/产品/租户/项目/KA）在异常时不能让主流程失败，因此统一落到本表，由后台线程池侧（`AbstractQueueThread`）写入并在启用标识为 Y 时继续被重试消费。实测 `name` 与 `remark` 中出现的「直推变更回调连通性」「self-test retry」说明本表同时被用做链路自检的落点。

## 版本演进

- 存量 2227 行 `enable` 全部为 N、`retry_num` 常驻 3，对应「已登记失败/已终止重试」的保留口径，见 [[sync_error_retained_scope]]。
- `service_class_name` 的实测 TopK 以 `ClientCustSyncService`(1453) 与 `ClientOperatorSyncService`(555) 为最多，说明本表当前主要承担客户与经办人同步的失败登记。

```ground:table
table: client_api_sync_error
database: lowcode_pplatform
desc: 客户端接口同步失败记录
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: param
    type: string
    phys: text
    desc: 参数
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: retry_num
    type: number
    phys: int(11)
    desc: 重试次数
  - name: service_class_name
    type: string
    phys: varchar(256)
    desc: 服务类名称
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```