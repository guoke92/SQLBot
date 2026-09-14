---
type: table
title: 租户产品配置
page_key: tenant_product
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_product]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












tenant_product 保存租户与平台产品的开通关系：`db_tenant_code` 标识租户，`platform_product_code` 标识平台产品编码。产品编码是内部服务判定「某租户/某企业是否接入某产品」的关键值，同时出现在 [[tenant_project]]、[[cust_auth_application]] 以及 [[sys_cust_user_rel]] 的 `product_id` 语义域中。

## 需求背景
企业接入产品需要与租户已开通的产品范围对齐，因此产品编码必须在租户侧与客户侧使用同一取值；判断用户是否已关联指定产品的口径见 [[current_product_rel]]。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
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
  - name: is_migratory
    type: string
    phys: varchar(4)
    desc: 是否迁移标识,N代表未迁移,Y代表迁移
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: 是否限额融资资金上线
    dict: max_financing_amount_flag
    topk: "0|1|N|Y"
    labels: "0:否|1:是|N:否|Y:是"
  - name: multiple
    type: string
    phys: varchar(512)
    desc: 是否多个
    dict: multiple
    topk: "0"
    labels: "0:否"
  - name: product_cate
    type: string
    phys: varchar(16)
    desc: 产品类型
    dict: tenant_product__product_cate
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
    phys: varchar(128)
    desc: 增信措施
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: 融资期限上限
    topk: "0|12|12个月|36|36个月|6|6-12个月|6个月"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: open_status
    type: string
    phys: varchar(16)
    desc: 产品开通状态
    topk: "N|P|Y"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: 平台产品编号
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
  - name: product_agreement
    type: string
    phys: varchar(1024)
    desc: 产品协议
  - name: product_description
    type: string
    phys: text
    desc: 产品详细描述
  - name: product_summary
    type: string
    phys: text
    desc: 产品概述
  - name: product_web_url
    type: string
    phys: varchar(512)
    desc: 站点url
  - name: ref_tenant_product_project_code
    type: string
    phys: varchar(128)
    desc: 租户产品-平台产品
  - name: ref_tenant_product_tenant_setting_config
    type: string
    phys: varchar(128)
    desc: 租户-产品
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
  - name: view_order
    type: number
    phys: int(10)
    desc: 展示顺序
```

## 关联表

- [[cust_auth_application]]：tenant_product.code → cust_auth_application.ref_cust_auth_application_tenant_product（ref-convention:CustAuthApplicationDO.java，suggested）
- [[cust_auth_application]]：tenant_product.platform_product_code → cust_auth_application.platform_product_code（copy:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：tenant_product.id → cust_project_rel.product_id（java-eq:CustProjectController.java，suggested）
- [[cust_project_rel]]：tenant_product.platform_product_id → cust_project_rel.product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[platform_product]]：tenant_product.credit_measures → platform_product.credit_measures（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.customer_group → platform_product.customer_group（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.max_financing_amount_flag → platform_product.max_financing_amount_flag（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.max_financing_amount → platform_product.max_financing_amount（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.max_financing_period → platform_product.max_financing_period（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.platform_product_code → platform_product.product_code（write-flow:TenantProductDomainService.java，confirmed）
- [[platform_product]]：tenant_product.product_cate → platform_product.product_cate（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.product_description → platform_product.product_description（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.product_summary → platform_product.product_summary（copy:TenantProductDomainService.java，suggested）
- [[platform_product]]：tenant_product.ref_tenant_product_project_code → platform_product.code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.code → tenant_project.ref_tenant_project_product_code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.id → tenant_project.product_id（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.platform_product_code → tenant_project.platform_product_code（copy:TenantProjectDomainService.java，suggested）
- [[tenant_project]]：tenant_product.ref_tenant_product_project_code → tenant_project.ref_tenant_project_platform_product（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_project.ref_tenant_project_tenant_code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_setting_config]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantProductDO.java，suggested）
- [[tenant_setting_config]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_setting_config.id（db-index:ref_-naming，suggested）
