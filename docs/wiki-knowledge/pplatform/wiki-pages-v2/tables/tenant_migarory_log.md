---
type: table
title: 租户项目迁移记录表
page_key: tenant_migarory_log
domain: 租户迁移
status: draft
anchors: [tenant_migarory_log]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`tenant_migarory_log` 是 [[迁移]] 与 [[同步]]（推数）共用的一条流水线：业务系统把存量数据推进产融（入向）与产融反向把数据推给业务系统（出向）都落这张表，靠 [[迁移|type]] 与 [[同步|direction]] 两个维度区分，不能只按接口名或中文动作名判断归属。表的幂等与重推入口是 `req_no`（唯一键 `uk_req_no`）与 `pushByLog(reqNo)`，重推只覆盖 `direction=OUT` 的记录，见口径 [[outbound_push]] 与 [[failed_migratory_log]]。表名在库中拼写为 `migarory`（非 migratory），引用时须以物理名为准。

```ground:table
table: tenant_migarory_log
database: lowcode_pplatform
desc: 租户项目迁移记录表
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: status
    type: string
    phys: varchar(128)
    desc: 迁移状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: type
    type: string
    phys: varchar(64)
    desc: 类型
    dict: tenant_migarory_log__type
    topk: "CUST_PRODUCT_SYNC|PRODUCT_SYNC|PRODUCT_SYNC_VALIDATE|PROJECT_QUERY|PROJECT_SYNC|PROJECT_SYNC_VALIDATE|TENANT_SYNC|TENANT_SYNC_VALIDATE|migratoryCust|migratoryOnTheWayCust|migratoryProject|migratoryTenant|syncProduct|syncProject"
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
    topk: "base|common"
  - name: batch_no
    type: string
    phys: varchar(32)
    desc: 批次号
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
  - name: data
    type: string
    phys: text
    desc: 迁移数据
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: direction
    type: string
    phys: varchar(16)
    desc: 数据方向
    topk: "IN|OUT"
  - name: falied_number
    type: number
    phys: bigint(20)
    desc: 失败数量
  - name: message
    type: string
    phys: text
    desc: 错误信息
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(256)
    desc: 产品编码
  - name: remark
    type: string
    phys: text
    desc: remark
  - name: req_no
    type: string
    phys: varchar(64)
    desc: 请求编号
  - name: req_sn
    type: string
    phys: varchar(64)
    desc: 请求流水编码
  - name: request
    type: string
    phys: longtext
    desc: 请求数据
  - name: response
    type: string
    phys: text
    desc: 返回数据
  - name: success_number
    type: number
    phys: bigint(20)
    desc: 成功数量
  - name: total_number
    type: number
    phys: bigint(20)
    desc: 总数量
  - name: trace_id
    type: string
    phys: varchar(128)
    desc: trace_id
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

## 需求背景

迁移期业务系统与产融之间是双向流动：入向把存量企业、人员、项目推到产融，出向把产融侧变更推回业务系统。两侧都需要可追溯、可重推的流水，因此共用一张表；运营与排障时须先用 direction 判定方向、再用 type/name 定位具体动作，否则会把入向迁移量（123405）误读为出向推数量级。

## 版本演进

出向推数逐步引入 RpcPoint 枚举与 `*_SYNC_VALIDATE` 校验器记录；`platform_product_code` 从单产品扩展为一个事件横向铺开到多产品（productCodes 数组）。`status` 默认值 N 充当"待重试池"，是 [[failed_migratory_log]] 与重推链路的判定基础。

相关：[[sync]]、[[迁移]]、[[migratory_log_status]]、[[outbound_push]]、[[cust_company_info]]。