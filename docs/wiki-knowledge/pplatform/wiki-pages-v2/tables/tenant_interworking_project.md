---
type: table
title: 租户互通产品项目
page_key: tenant_interworking_project
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_interworking_project]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 租户互通产品项目

（基线页：24 字段，行数估计 12。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_interworking_project
database: lowcode_pplatform
desc: 租户互通产品项目
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
    topk: "LN1|beehive-scf.qhhrly.cn"
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
    phys: varchar(32)
    desc: 平台产品编码
    topk: "AMS|HTCP1|HTCP13|HTCP14|HTCP5"
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
  - name: ref_tenant_interworking_project_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: 租户项目
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
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[tenant_interworking_product]]：tenant_interworking_project.platform_product_code → tenant_interworking_product.platform_product_code（copy:TenantInterworkingProjectApplicationService.java，suggested）
- [[tenant_interworking_product]]：tenant_interworking_project.product_id → tenant_interworking_product.id（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_interworking_product]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product → tenant_interworking_product.code（ref-convention:TenantInterworkingProjectDO.java，suggested）
- [[tenant_interworking_product]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product → tenant_interworking_product.id（db-index:ref_-naming，suggested）
- [[tenant_interworking_product]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config → tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_setting_config]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantInterworkingProjectDO.java，suggested）
- [[tenant_setting_config]]：tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config → tenant_setting_config.id（db-index:ref_-naming，suggested）
