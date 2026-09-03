---
type: table
title: CA服务费项目配置
page_key: ca_fee_project_config
domain: 基线
status: draft
anchors: [ca_fee_project_config]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CA服务费项目配置

（基线页：28 字段，行数估计 303。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_fee_project_config
database: lowcode_pplatform
desc: CA服务费项目配置
inactive: false
fields:
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
  - name: agreement_version
    type: string
    phys: varchar(64)
    desc: 当前绑定收费协议版本号
    topk: V1.0
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: GREENTOWNAT|JYYL|base|boscxsbl
  - name: block_scene_list
    type: string
    phys: text
    desc: 拦截场景编码 JSON 数组，元素见 CaFeeInterceptSceneEnum
  - name: charge_enabled
    type: string
    phys: varchar(2)
    desc: 是否开启CA收费
    topk: N|Y
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: core_annual_fee
    type: number
    phys: int(10)
    desc: 核心企业角色年费（元）
    topk: 0|1|100|12
    group: supplier_annual_fee_group
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: last_toggle_time
    type: temporal
    phys: datetime
    desc: 最近一次收费开关切换时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pay_channel
    type: string
    phys: text
    desc: 缴费渠道JSON数组
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 项目ID
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: special_company_list
    type: string
    phys: text
    desc: 特殊企业配置JSON数组
  - name: supplier_annual_fee
    type: number
    phys: int(10)
    desc: 供应商角色年费（元）
    topk: 0|100|101|120
    group: supplier_annual_fee_group
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 所属租户
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[tenant_project]]：ca_fee_project_config.project_id → tenant_project.id（write-flow:CaFeeProjectConfigService.java，confirmed）
