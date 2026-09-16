---
type: table
title: CA 服务费企业主档
page_key: ca_fee_company
domain: CA证书收费
status: draft
anchors: [ca_fee_company]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [ca_fee]
---

# CA 服务费企业主档

本表是场景 [[scenarios/ca_fee]] 的**主档**：`certification_no` 唯一标识一个企业在收费语境下的当前结论（缴费快照 + 服务期）。订单行见 [[tables/ca_fee_order]]，项目开关见 [[tables/ca_fee_project_config]]。

问数默认 FROM 本表。不要用订单 `order_status=PAID` 去数「已缴费企业」。本页列出收费场景常用列。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[ca_fee]]

`id`, `enable`, `create_time`, `update_time`, `ca_status`, `certification_no`, `company_name`, `fee_locked`, `locked_annual_fee`, `pay_status`, `renew_remind_sent`, `service_end`, `service_start`, `source_company_type`, `source_project_id`, `special_annual_fee`, `special_config_flag`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `db_tenant_code`, `ext_json`, `name`, `organization_id`, `remark`, `tenant_id`

```ground:table
table: ca_fee_company
database: lowcode_pplatform
desc: CA服务费企业主数据
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [ca_fee]
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
    scenes: [ca_fee]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [ca_fee]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [ca_fee]
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
  - name: ca_status
    type: string
    phys: varchar(64)
    desc: "CA签章状态"
    topk: "CANCELLED|NORMAL|UNKNOWN"
    scenes: [ca_fee]
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: "统一社会信用代码"
    scenes: [ca_fee]
  - name: company_name
    type: string
    phys: varchar(512)
    desc: "企业名称"
    scenes: [ca_fee]
  - name: fee_locked
    type: string
    phys: varchar(2)
    desc: "是否已锁定年费标准"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [ca_fee]
  - name: locked_annual_fee
    type: number
    phys: int(10)
    desc: "首次缴费成功后锁定的年费标准（元）"
    scenes: [ca_fee]
  - name: pay_status
    type: string
    phys: varchar(64)
    desc: "缴费状态：PAID 已缴费 / UNPAID 未缴费"
    dict: pay_status
    topk: "PAID|UNPAID"
    labels: "PAID:已缴费|UNPAID:未缴费"
    scenes: [ca_fee]
  - name: renew_remind_sent
    type: string
    phys: varchar(2)
    desc: "本期续费待办是否已生成：Y 已生成 / N 未生成"
    dict: enable
    topk: "N|Y"
    labels: "N:未生成|Y:已生成"
    scenes: [ca_fee]
  - name: service_end
    type: temporal
    phys: date
    desc: "当前 CA 服务费服务周期截止日（含）"
    scenes: [ca_fee]
  - name: service_start
    type: temporal
    phys: date
    desc: "当前 CA 服务费服务周期起始日（含）"
    scenes: [ca_fee]
  - name: source_company_type
    type: string
    phys: varchar(128)
    desc: "首次锁定来源企业角色，如 SUPPLIER/CORE"
    topk: "CORE|PROJECT_COMPANY|SUPPLIER"
    scenes: [ca_fee]
  - name: source_project_id
    type: number
    phys: bigint(20)
    desc: "首次锁定来源项目 ID"
    scenes: [ca_fee]
  - name: special_annual_fee
    type: number
    phys: int(10)
    desc: "特殊配置后应缴年费（元）"
    scenes: [ca_fee]
  - name: special_config_flag
    type: string
    phys: varchar(2)
    desc: "是否存在生效中的特殊配置快照"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [ca_fee]
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
    topk: "ISOLATE_TAG_boscebl|ISOLATE_TAG_yccsfzjt|LN1|beehive-scf.qhhrly.cn|xylxchf"
  - name: ext_json
    type: string
    phys: text
    desc: "扩展字段 JSON预留"
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
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: "首次锁定来源租户"
```

```ground:relation
type: EQUI_JOIN
left: ca_fee_company.certification_no
right: ca_fee_order.certification_no
cardinality: one_to_many
status: proposed
evidence: code_path:CaFeeLedgerQueryService.java
```

```ground:relation
type: DERIVED
left: ca_fee_company.service_end
right: ca_fee_order.service_end
cardinality: many_to_one
status: proposed
evidence: code_path:CaFeeOrderService.java
derived_from: ca_fee_order.service_end
```
