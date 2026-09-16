---
type: table
title: 短链接
page_key: short_link
domain: 通知/验证码/短链
status: draft
anchors: [short_link]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [tenant_config]
---

# 短链接

`type`：FILE 文件类型 / NORMAL 一般类型。`is_forever` 绑定 BooleanEnum。非永久链默认 24h 过期。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[tenant_config]]

`id`, `enable`, `create_time`, `update_time`, `expire_time`, `is_forever`, `number`, `type`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `name`, `organization_id`, `remark`, `source_url`

```ground:table
table: short_link
database: lowcode_pplatform
desc: 短链接
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [tenant_config]
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
    roles: [query]
    group: always
    scenes: [tenant_config]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [tenant_config]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [tenant_config]
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
  - name: expire_time
    type: temporal
    phys: datetime
    desc: "到期时间"
    scenes: [tenant_config]
  - name: is_forever
    type: string
    phys: varchar(64)
    desc: "到期类型"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    scenes: [tenant_config]
  - name: number
    type: string
    phys: varchar(64)
    desc: "编码"
    roles: [query]
    scenes: [tenant_config]
  - name: type
    type: string
    phys: varchar(64)
    desc: "类型"
    dict: short_link_type
    topk: "FILE|NORMAL"
    roles: [query]
    scenes: [tenant_config]
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
    topk: "base"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: source_url
    type: string
    phys: varchar(2048)
    desc: "源链接"
```
