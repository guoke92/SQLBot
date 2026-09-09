---
type: table
title: 租户互通产品项目
page_key: tenant_interworking_project
belong: tables
domain: 基线
status: draft
anchors: [tenant_interworking_project]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户互通产品项目

（基线页：24 字段，行数估计 13。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_interworking_project
database: lowcode_pplatform
desc: 租户互通产品项目
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
    topk: 082d4b100c6e46fca373b77d90f48315|26c78215b94a49b7b26059e04b415f8d
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1420232234333048834|1801438863791919106
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: liuning|wangcong
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|beehive-scf.qhhrly.cn
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: 互通产品1-0905项目|互通产品1-LN1保理易融项目|互通产品1-LN1应收易融项目|互通产品1-LN1项目1
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: AMS|HTCP1|HTCP13|HTCP14
  - name: product_id
    type: number
    phys: bigint(20)
    desc: 产品id
  - name: project_id
    type: number
    phys: bigint(20)
    desc: 项目id
  - name: ref_tenant_interworking_project_tenant_interworking_product
    type: string
    phys: varchar(128)
    desc: 租户产品项目
    topk: 2dbc124f73dd4e9eb96cc74685b17645|4932eca2392d45f8821aba513f379c7f
  - name: ref_tenant_interworking_project_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: 租户项目
    topk: a285d4cf94ec4384bb7b6cf5ba994b4a|d77dc6bffbcc46fba7a864a07ef63c24
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 租户id
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1420232234333048834|1801438863791919106
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: liuning|wangcong
```

## 关联表

- [[tenant_interworking_product]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config → tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_setting_config]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantInterworkingProjectDO.java，suggested）
