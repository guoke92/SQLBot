---
type: table
title: 租户产品配置
page_key: tenant_product
domain: 基线
status: draft
anchors: [tenant_product]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 租户产品配置

（基线页：39 字段，行数估计 384。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_product
database: lowcode_pplatform
desc: 租户产品配置
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: open_status
    type: string
    phys: varchar(16)
    desc: 产品开通状态
    dict: tenant_interworking_product__open_status
    topk: N|P|Y
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: credit_measures
    type: string
    phys: varchar(128)
    desc: 增信措施
    topk: 1|11|112|质押模式下需提供质押
  - name: customer_group
    type: string
    phys: varchar(128)
    desc: 客户群体
    topk: 客户群体3
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: is_migratory
    type: string
    phys: varchar(4)
    desc: 是否迁移标识,N代表未迁移,Y代表迁移
    topk: N|Y
  - name: logo_icon_url
    type: string
    phys: varchar(2048)
    desc: 产品logo
  - name: max_financing_amount
    type: string
    phys: varchar(128)
    desc: 融资金额上限
  - name: max_financing_amount_flag
    type: string
    phys: varchar(4)
    desc: 是否限额融资资金上线
    topk: 0|1|N|Y
  - name: max_financing_period
    type: string
    phys: varchar(128)
    desc: 融资期限上限
    topk: 0|12|12个月|36
  - name: multiple
    type: string
    phys: varchar(512)
    desc: 是否多个
    topk: 0
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    topk: 供票|供票QA|保理易融|国内信用证
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: 平台产品编号
    topk: ACFLOW|BEECREDIT|DRAFT|DRAFTQA
  - name: platform_product_id
    type: number
    phys: bigint(20)
    desc: 平台产品id
  - name: product_agreement
    type: string
    phys: varchar(1024)
    desc: 产品协议
  - name: product_cate
    type: string
    phys: varchar(16)
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
  - name: product_web_url
    type: string
    phys: varchar(512)
    desc: 站点url
  - name: ref_tenant_product_project_code
    type: string
    phys: varchar(128)
    desc: 租户产品-平台产品
    topk: 007142024a5c425bb3673f753060e534|b8468d68ba0a4762bda0f7b9164e4f6a
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
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: view_order
    type: number
    phys: int(10)
    desc: 展示顺序
    topk: 0|11|8|9
```

## 关联表

- [[cust_auth_application]]：tenant_product.code → cust_auth_application.ref_cust_auth_application_tenant_product（ref-convention:CustAuthApplicationDO.java，suggested）
- [[cust_project_rel]]：tenant_product.platform_product_id → cust_project_rel.product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[platform_product]]：tenant_product.ref_tenant_product_project_code → platform_product.code（write-flow:TenantProductDomainService.java，confirmed）
- [[tenant_project]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_project.ref_tenant_project_tenant_code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_setting_config]]：tenant_product.ref_tenant_product_tenant_setting_config → tenant_setting_config.code（ref-convention:TenantProductDO.java，suggested）
