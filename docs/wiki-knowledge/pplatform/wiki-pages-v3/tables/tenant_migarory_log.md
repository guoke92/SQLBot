---
type: table
title: 租户迁移日志
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
contract_version: "0.3"
belong: tables
scenes: [tenant_migration]
---

# 租户迁移日志

表名拼写以库为准。`direction`：IN 外部迁入、OUT 产融推数（代码分支名）。`status` 用 BooleanEnum，Y 成功 / N 未成功。出向重推看 `req_no`，且 type 不是 `*_SYNC_VALIDATE`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[tenant_migration]]

`id`, `enable`, `create_time`, `update_time`, `direction`, `name`, `platform_product_code`, `req_no`, `status`, `type`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `batch_no`, `data`, `db_tenant_code`, `falied_number`, `message`, `organization_id`, `remark`, `req_sn`, `request`, `response`, `success_number`, `total_number`, `trace_id`

```ground:table
table: tenant_migarory_log
database: lowcode_pplatform
desc: 租户项目迁移记录表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [tenant_migration]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    group: always
    scenes: [tenant_migration]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [tenant_migration]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [tenant_migration]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: direction
    type: string
    phys: varchar(16)
    desc: "方向"
    topk: "IN|OUT"
    roles: [query]
    scenes: [tenant_migration]
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
    scenes: [tenant_migration]
  - name: platform_product_code
    type: string
    phys: varchar(256)
    desc: "平台产品编码"
    scenes: [tenant_migration]
  - name: req_no
    type: string
    phys: varchar(64)
    desc: "请求号"
    roles: [query]
    scenes: [tenant_migration]
  - name: status
    type: string
    phys: varchar(128)
    desc: "状态"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    scenes: [tenant_migration]
  - name: type
    type: string
    phys: varchar(64)
    desc: "类型"
    topk: "CUST_PRODUCT_SYNC|PRODUCT_SYNC|PRODUCT_SYNC_VALIDATE|PROJECT_QUERY|PROJECT_SYNC|PROJECT_SYNC_VALIDATE|TENANT_SYNC|TENANT_SYNC_VALIDATE|migratoryCust|migratoryOnTheWayCust|migratoryProject|migratoryTenant|syncProduct|syncProject"
    roles: [query]
    scenes: [tenant_migration]
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "base|common"
  - name: batch_no
    type: string
    phys: varchar(32)
    desc: "批次号"
  - name: data
    type: string
    phys: text
    desc: "迁移数据"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: falied_number
    type: number
    phys: bigint(20)
    desc: "失败数量"
  - name: message
    type: string
    phys: text
    desc: "错误信息"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: text
    desc: "remark"
  - name: req_sn
    type: string
    phys: varchar(64)
    desc: "请求流水编码"
  - name: request
    type: string
    phys: longtext
    desc: "请求数据"
  - name: response
    type: string
    phys: text
    desc: "返回数据"
  - name: success_number
    type: number
    phys: bigint(20)
    desc: "成功数量"
  - name: total_number
    type: number
    phys: bigint(20)
    desc: "总数量"
  - name: trace_id
    type: string
    phys: varchar(128)
    desc: "trace_id"
```
