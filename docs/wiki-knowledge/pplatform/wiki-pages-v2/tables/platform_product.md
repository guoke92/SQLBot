---
type: table
title: 平台产品基础配置
page_key: platform_product
domain: 平台产品配置
status: draft
anchors: [platform_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`platform_product` 是平台级产品定义表，被 [[tenant_product]]（`platform_product_code`、`ref_tenant_product_project_code`）与 [[tenant_project]]（`ref_tenant_project_platform_product`、`platform_product_code`）引用。产品类型 `product_type` 区分互通产品与通用产品，口径见 [[platform_product_interworking]]、[[platform_product_general]]。

## 需求背景
语义分析未附带需求文档锚点，仅依据 PlatformProductTypeEnum 的使用点归纳：产品查询需要按 `product_type` 分流（互通产品线 / 通用产品线），以支撑 [[interworking_product_term]] 与 [[tenant_product]] 的边界。

## 版本演进
语义分析未记录该表的版本演进；本页仅覆盖被证据引用的 `product_type` 字段。

```ground:table
table: platform_product
database: lowcode_pplatform
desc: 平台产品基础配置
fields:
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
    dict: act_procinst_status
    topk: "r"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: general_flag
    type: string
    phys: varchar(2)
    desc: 通用产品标识
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
    desc: 是否限额融资资金上线
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: menu_type
    type: string
    phys: varchar(32)
    desc: 菜单展示类型(topLeft/left)
    dict: menu_type
    topk: "left"
  - name: multiple_client_type
    type: string
    phys: varchar(128)
    desc: 多端口类型
    dict: multiple_client_type
    topk: "CompanyType|default"
  - name: multiple_cust_role_flag
    type: string
    phys: varchar(2)
    desc: 是否有多企业角色
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: multiple_project_flag
    type: string
    phys: varchar(2)
    desc: 是否有多项目
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: platform_flag
    type: string
    phys: varchar(2)
    desc: 是否平台标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: product_cate
    type: string
    phys: varchar(512)
    desc: 产品类型
    dict: product_cate
    topk: "CREDIT|STRONG|WEAKLY"
  - name: product_construction_status
    type: string
    phys: varchar(4)
    desc: 产品建设情况
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: product_status
    type: string
    phys: varchar(512)
    desc: 产品状态
    dict: product_status
    topk: "1"
    labels: "1:是"
  - name: product_type
    type: string
    phys: varchar(16)
    desc: 通用产品标识
    dict: product_type
    topk: "GENERAL|INTERWORKING"
  - name: wkfl_flag
    type: string
    phys: varchar(512)
    desc: 产品工作流启用开关
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
  - name: app_code
    type: string
    phys: varchar(64)
    desc: 蜂搭平台app编号
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "base"
  - name: basic_product
    type: string
    phys: varchar(12)
    desc: 是否是产融底座
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
    phys: varchar(512)
    desc: 增信措施
  - name: cust_role_combine
    type: string
    phys: text
    desc: 支持企业角色组合
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn|common"
  - name: default_menu_code
    type: string
    phys: varchar(128)
    desc: 默认菜单编号
  - name: default_menu_index
    type: number
    phys: int(10)
    desc: 默认菜单编号
    topk: "1"
    labels: "1:是"
  - name: logo_icon_url
    type: string
    phys: text
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
    topk: "0|10亿元|不限"
  - name: max_financing_period
    type: string
    phys: varchar(512)
    desc: 融资期限上限
    topk: "1-3年|12个月|36个月|6|6个月|HTCP15"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_code
    type: string
    phys: varchar(16)
    desc: 平台编码
    topk: "AMS|DRAFT|DRAFTQA|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7|PPLATFORM|STORAGE|VOUCHER|XYC"
  - name: product_code
    type: string
    phys: varchar(128)
    desc: 产品编码
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|DRAFT|DRAFTQA|HTCP1|HTCP13|HTCP14|HTCP15|HTCP18|HTCP19|HTCP2|HTCP5|HTCP6|HTCP7|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: product_description
    type: string
    phys: text
    desc: 产品详细描述
  - name: product_ref_num
    type: number
    phys: int(10)
    desc: 引用产品的平台数
  - name: product_summary
    type: string
    phys: text
    desc: 产品概述
  - name: project_code
    type: string
    phys: varchar(64)
    desc: 蜂搭平台项目编号
  - name: project_config
    type: string
    phys: varchar(256)
    desc: 项目配置
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: transaction_structure
    type: string
    phys: varchar(1024)
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

- [[cust_customized_product]]：platform_product.logo_icon_url → cust_customized_product.logo_icon_url（copy:CustGeneralProductApplication.java，suggested）
- [[cust_project_rel]]：platform_product.code → cust_project_rel.ref_cust_project_rel_platform_product（ref-convention:CustProjectRelDO.java，suggested）
- [[tenant_interworking_product]]：platform_product.code → tenant_interworking_product.ref_tenant_interworking_product_platform_product（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_interworking_product]]：platform_product.credit_measures → tenant_interworking_product.credit_measures（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.customer_group → tenant_interworking_product.customer_group（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.max_financing_amount_flag → tenant_interworking_product.max_financing_amount_flag（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.max_financing_amount → tenant_interworking_product.max_financing_amount（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.max_financing_period → tenant_interworking_product.max_financing_period（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.product_cate → tenant_interworking_product.product_cate（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.product_code → tenant_interworking_product.platform_product_code（write-flow:TenantInterworkingProductDomainService.java，confirmed）
- [[tenant_interworking_product]]：platform_product.product_description → tenant_interworking_product.product_description（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_interworking_product]]：platform_product.product_summary → tenant_interworking_product.product_summary（copy:TenantInterworkingProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.code → tenant_product.ref_tenant_product_project_code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_product]]：platform_product.credit_measures → tenant_product.credit_measures（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.customer_group → tenant_product.customer_group（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.max_financing_amount_flag → tenant_product.max_financing_amount_flag（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.max_financing_amount → tenant_product.max_financing_amount（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.max_financing_period → tenant_product.max_financing_period（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.product_cate → tenant_product.product_cate（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.product_code → tenant_product.platform_product_code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_product]]：platform_product.product_description → tenant_product.product_description（copy:TenantProductDomainService.java，suggested）
- [[tenant_product]]：platform_product.product_summary → tenant_product.product_summary（copy:TenantProductDomainService.java，suggested）
- [[tenant_project]]：platform_product.code → tenant_project.ref_tenant_project_platform_product（ref-convention:TenantProjectDO.java，suggested）
