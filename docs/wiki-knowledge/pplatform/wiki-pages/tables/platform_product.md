---
type: table
title: 平台产品基础配置
page_key: platform_product
belong: tables
domain: 基线
status: draft
anchors: [platform_product]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 平台产品基础配置

（基线页：48 字段，行数估计 19。行语义/常用过滤待语义摄取增强。）

```ground:table
table: platform_product
database: lowcode_pplatform
desc: 平台产品基础配置
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: product_status
    type: string
    phys: varchar(512)
    desc: 产品状态
    dict: product_status
    topk: 1
  - name: product_type
    type: string
    phys: varchar(16)
    desc: 通用产品标识
    dict: product_type
    topk: GENERAL|INTERWORKING
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
    topk: r
  - name: app_code
    type: string
    phys: varchar(64)
    desc: 蜂搭平台app编号
    topk: 8b6020c4034a47ad9a9a216e29a23616|be1b5de568064ef1bc2f01c8105df7b2
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: base
  - name: basic_product
    type: string
    phys: varchar(12)
    desc: 是否是产融底座
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
    topk: 007142024a5c425bb3673f753060e533|007142024a5c425bb3673f753060e534
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
    topk: 1420232234333048834
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
    topk: wangcong
  - name: credit_measures
    type: string
    phys: varchar(512)
    desc: 增信措施
    topk: 11|112|HTCP15|ddd
  - name: cust_role_combine
    type: string
    phys: text
    desc: 支持企业角色组合
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
    topk: HTCP15|sdsd
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn|common
  - name: default_menu_code
    type: string
    phys: varchar(128)
    desc: 默认菜单编号
  - name: default_menu_index
    type: number
    phys: int(10)
    desc: 默认菜单编号
    topk: 1
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
  - name: general_flag
    type: string
    phys: varchar(2)
    desc: 通用产品标识
    topk: Y
  - name: logo_icon_url
    type: string
    phys: text
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
    topk: 0|10亿元|不限
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: 是否限额融资资金上线
    topk: N|Y
  - name: max_financing_period
    type: string
    phys: varchar(512)
    desc: 融资期限上限
    topk: 1-3年|12个月|36个月|6
  - name: menu_type
    type: string
    phys: varchar(32)
    desc: 菜单展示类型(topLeft/left)
    topk: left
  - name: multiple_client_type
    type: string
    phys: varchar(128)
    desc: 多端口类型
    topk: CompanyType|default
  - name: multiple_cust_role_flag
    type: string
    phys: varchar(2)
    desc: 是否有多企业角色
    topk: N|Y
  - name: multiple_project_flag
    type: string
    phys: varchar(2)
    desc: 是否有多项目
    topk: N|Y
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: AMS供应商|AMS金融机构|AMS项目公司|HTCP15
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_code
    type: string
    phys: varchar(16)
    desc: 平台编码
    topk: AMS|DRAFT|DRAFTQA|HTCP1
  - name: platform_flag
    type: string
    phys: varchar(2)
    desc: 是否平台标识
    topk: N|Y
  - name: product_cate
    type: string
    phys: varchar(512)
    desc: 产品类型
    topk: CREDIT|STRONG|WEAKLY
  - name: product_code
    type: string
    phys: varchar(128)
    desc: 产品编码
    topk: ACFLOW|AMS|BEECREDIT|DEALER
  - name: product_construction_status
    type: string
    phys: varchar(4)
    desc: 产品建设情况
    topk: Y
  - name: product_description
    type: string
    phys: text
    desc: 产品详细描述
  - name: product_ref_num
    type: number
    phys: int(10)
    desc: 引用产品的平台数
    topk: 0|1|11|199
  - name: product_summary
    type: string
    phys: text
    desc: 产品概述
  - name: project_code
    type: string
    phys: varchar(64)
    desc: 蜂搭平台项目编号
    topk: 0cb8c9bc0c2f4053986a9cb63060f951
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
    topk: 1209355979188113409|1420232234333048834|1801438863791919106|1861965537092087809
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
    topk: liuning|lwj|pengkang|wangcong
  - name: wkfl_flag
    type: string
    phys: varchar(512)
    desc: 产品工作流启用开关
    topk: Y
```

## 关联表

- [[cust_project_rel]]：platform_product.code → cust_project_rel.ref_cust_project_rel_platform_product（ref-convention:CustProjectRelDO.java，suggested）
- [[tenant_interworking_product]]：platform_product.code → tenant_interworking_product.ref_tenant_interworking_product_platform_product（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_product]]：platform_product.code → tenant_product.ref_tenant_product_project_code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_project]]：platform_product.code → tenant_project.ref_tenant_project_platform_product（ref-convention:TenantProjectDO.java，suggested）
