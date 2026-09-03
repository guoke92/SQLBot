---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
domain: 基线
status: draft
anchors: [tenant_interworking_product]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户互通产品

（基线页：38 字段，行数估计 37。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
desc: 租户互通产品
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: open_status
    type: string
    phys: varchar(4)
    desc: 产品开通状态
    dict: tenant_interworking_product__open_status
    topk: N|Y
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
    topk: GREENTOWNAT|JHYL|base|hylg
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1174240536503197698|1207485686830276611|1407266533295345665|1420232234333048834
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: liuning|ouyangpengfei|sjj|wangcong
  - name: credit_measures
    type: string
    phys: varchar(256)
    desc: 增信措施
    topk: HTCP15|ddd
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
    topk: HTCP15|sdsd|供应商|金融机构
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_CJTZ|ISOLATE_TAG_GREENTOWNAT|ISOLATE_TAG_JHYL|ISOLATE_TAG_QLT
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
    topk: 0|88888888|不限
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: 是否限额融资资金上限
    topk: N|Y
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: 融资期限上限
    topk: 1-3年|6|HTCP15
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
    phys: varchar(16)
    desc: 平台产品编号
    topk: AMS|HTCP1|HTCP13|HTCP14
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
  - name: product_cate
    type: string
    phys: varchar(64)
    desc: 产品类型
    topk: CREDIT|STRONG|WEAKLY
  - name: product_description
    type: string
    phys: text
    desc: 产品详细描述
  - name: product_summary
    type: string
    phys: text
    desc: 产品概述
  - name: ref_tenant_interworking_product_platform_product
    type: string
    phys: varchar(128)
    desc: 关联产品大类
    topk: 007142024a5c425bb3673f753060e533|956b7f49cc00471db99e552d778a12c2
  - name: ref_tenant_interworking_product_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: 关联租户
    topk: 0e3c8c4cbe2a4989b49dfed206ae7c77|53509862c98e42e8b174ceadf5ea0e7f
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: scope
    type: string
    phys: varchar(8)
    desc: 适应范围标识
    topk: ALL|SOME
  - name: scope_project
    type: string
    phys: longtext
    desc: 适用范围项目
  - name: scope_role
    type: string
    phys: varchar(200)
    desc: 适用角色
  - name: target_sys_channel
    type: string
    phys: varchar(64)
    desc: 目标系统ssochannel
    topk: ams_finance_pc|ams_proj_pc|ams_supplier_pc|smebee_pc
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 租户id
  - name: transaction_structure
    type: string
    phys: text
    desc: 交易结构
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
    topk: 1174240536503197698|1207485686830276611|1407266533295345665|1420232234333048834
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: liuning|ouyangpengfei|sjj|wangcong
```

## 关联表

- [[cust_interworking_product]]：tenant_interworking_product.code → cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product（ref-convention:CustInterworkingProductDO.java，suggested）
- [[platform_product]]：tenant_interworking_product.ref_tenant_interworking_product_platform_product → platform_product.code（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_interworking_project]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_setting_config]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantInterworkingProductDO.java，suggested）
