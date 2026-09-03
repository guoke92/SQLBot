---
type: table
title: 租户产品菜单按钮表
page_key: tenant_product_menu_res
domain: 基线
status: draft
anchors: [tenant_product_menu_res]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户产品菜单按钮表

（基线页：22 字段，行数估计 110。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_product_menu_res
database: lowcode_pplatform
desc: 租户产品菜单按钮表
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
  - name: company_type
    type: string
    phys: varchar(32)
    desc: 企业类型
    topk: CORE|CORPORATION_COMPANY|PLATFORM_OPERATOR_COMPANY|SUPPLIER
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 刘宁|肖龙豪|黄丽玉
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: huangliyu|liuning|xiaolonghao
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: LN1|beehive-scf.qhhrly.cn|ning
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: menu_id
    type: number
    phys: bigint(20)
    desc: 菜单ID
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: product_code
    type: string
    phys: varchar(64)
    desc: 产品code
    topk: ACCOUNT_PRODUCT|RVSFACTOR_PC
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: resource_id
    type: number
    phys: bigint(20)
    desc: 按钮ID
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 刘宁|肖龙豪|黄丽玉
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: huangliyu|liuning|xiaolonghao
```
