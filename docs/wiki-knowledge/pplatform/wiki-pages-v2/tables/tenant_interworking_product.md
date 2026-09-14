---
type: table
title: 租户互通产品
page_key: tenant_interworking_product
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_interworking_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`tenant_interworking_product` 记录租户维度的互通产品开通情况，是 [[interworking_product_term]] 在租户侧的落库表。开通状态 `open_status` 由 ProductOpenStatusEnum 写值，口径见 [[tenant_interworking_product_opened]]。与 [[tenant_product]] 的区别在于产品线：互通产品独立于租户通用产品配置。

## 需求背景
语义分析未附带需求文档锚点，依据字段语义归纳：互通产品线需要独立于通用产品记录开通过程，因此复用 ProductOpenStatusEnum 的状态语义，但独立建表。

## 版本演进
语义分析未记录该表的版本演进。

```ground:table
table: tenant_interworking_product
database: lowcode_pplatform
desc: 租户互通产品
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
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: 是否限额融资资金上限
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: open_status
    type: string
    phys: varchar(4)
    desc: 产品开通状态
    dict: tenant_interworking_product__open_status
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: product_cate
    type: string
    phys: varchar(64)
    desc: 产品类型
    dict: tenant_interworking_product__product_cate
    topk: "CREDIT|STRONG|WEAKLY"
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
    topk: "GREENTOWNAT|JHYL|base|hylg"
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
  - name: credit_measures
    type: string
    phys: varchar(256)
    desc: 增信措施
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "ISOLATE_TAG_CJTZ|ISOLATE_TAG_GREENTOWNAT|ISOLATE_TAG_JHYL|ISOLATE_TAG_QLT|ISOLATE_TAG_hylg|ISOLATE_TAG_lygs|ISOLATE_TAG_xjt|ISOLATE_TAG_yccsfzjt|LN1|LNceshizuhu0113|beehive-scf.qhhrly.cn|mengniu|yunyingzhongtai"
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
    topk: "0|88888888|不限"
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: 融资期限上限
    topk: "1-3年|6|HTCP15"
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
    topk: "AMS|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7"
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
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
  - name: ref_tenant_interworking_product_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: 关联租户
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: scope
    type: string
    phys: varchar(8)
    desc: 适应范围标识
    topk: "ALL|SOME"
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

- [[cust_interworking_product]]：tenant_interworking_product.code → cust_interworking_product.ref_cust_interworking_product_tenant_interworking_product（ref-convention:CustInterworkingProductDO.java，suggested）
- [[platform_product]]：tenant_interworking_product.credit_measures → platform_product.credit_measures（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.customer_group → platform_product.customer_group（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.max_financing_amount_flag → platform_product.max_financing_amount_flag（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.max_financing_amount → platform_product.max_financing_amount（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.max_financing_period → platform_product.max_financing_period（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.platform_product_code → platform_product.product_code（write-flow:TenantInterworkingProductDomainService.java，confirmed）
- [[platform_product]]：tenant_interworking_product.product_cate → platform_product.product_cate（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.product_description → platform_product.product_description（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.product_summary → platform_product.product_summary（copy:TenantInterworkingProductDomainService.java，suggested）
- [[platform_product]]：tenant_interworking_product.ref_tenant_interworking_product_platform_product → platform_product.code（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[platform_product]]：tenant_interworking_product.ref_tenant_interworking_product_platform_product → platform_product.id（db-index:ref_-naming，suggested）
- [[tenant_interworking_project]]：tenant_interworking_product.code → tenant_interworking_project.ref_tenant_interworking_project_tenant_interworking_product（ref-convention:TenantInterworkingProjectDO.java，suggested）
- [[tenant_interworking_project]]：tenant_interworking_product.id → tenant_interworking_project.product_id（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_interworking_project]]：tenant_interworking_product.platform_product_code → tenant_interworking_project.platform_product_code（copy:TenantInterworkingProjectApplicationService.java，suggested）
- [[tenant_interworking_project]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config（write-flow:TenantInterworkingProjectApplicationService.java，confirmed）
- [[tenant_setting_config]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_setting_config]]：tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config → tenant_setting_config.id（db-index:ref_-naming，suggested）
