---
type: table
title: 客户项目关联表
page_key: cust_project_rel
domain: 基线
status: draft
anchors: [cust_project_rel]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户项目关联表

（基线页：41 字段，行数估计 57359。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_project_rel
database: lowcode_pplatform
desc: 客户项目关联表
inactive: false
fields:
  - name: company_type
    type: string
    phys: varchar(128)
    desc: 客户角色(只取一个)
    topk: CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
    roles: [query, result]
  - name: op_contact_a
    type: string
    phys: varchar(64)
    desc: 运营对接人A
    topk: 141|145|257|267
    roles: [query, result]
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    topk: 1|2|3|ams
    roles: [query, result]
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: 风控对接人A
    topk: 257|267|333|344
    roles: [query, result]
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: 风控组别
    topk: 1|ams|zu1|审核组2
    roles: [query, result]
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: 查验对接人
    topk: 257|289|333|344
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    topk: 1|11|ams|zu1
    roles: [query, result]
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
    topk: base|common|xyc.llschain.com
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: config_model
    type: string
    phys: varchar(8)
    desc: 项目配置模式
    topk: admin
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: op_contact_b
    type: string
    phys: varchar(400)
    desc: 运营对接人B
    roles: [result]
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: 运营信息更新时间
    roles: [result]
  - name: op_update_user
    type: string
    phys: varchar(64)
    desc: 运营信息更新人
    topk: 刘倍材|刘宁
    roles: [result]
  - name: organization_id
    type: string
    phys: varchar(30)
  - name: product_id
    type: string
    phys: varchar(512)
    desc: 产品
  - name: project_id
    type: string
    phys: varchar(512)
    desc: 项目id
  - name: project_open_status
    type: string
    phys: varchar(64)
    desc: 项目开通状态
    topk: NOT_OPEN|OPENED
  - name: ref_cust_project_rel_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户和项目关系
  - name: ref_cust_project_rel_platform_product
    type: string
    phys: varchar(128)
    desc: 平台产品
    topk: 007142024a5c425bb3673f753060e533|007142024a5c425bb3673f753060e534|ACFLOW|DRAFTQA
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: ACFLOW|AMS|BEECREDIT|DEALER
  - name: risk_control_contact_b
    type: string
    phys: varchar(200)
    desc: 风控对接人B
    roles: [result]
  - name: show_flag
    type: string
    phys: varchar(20)
    desc: 展示标记
    topk: N|Y
  - name: status
    type: string
    phys: varchar(64)
    desc: 关联状态
    topk: 0|1
  - name: tenant_code
    type: string
    phys: varchar(512)
    desc: 租户
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    topk: 0|1
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

- [[ca_fee_company]]：cust_project_rel.ref_cust_project_rel_cust_company_info → ca_fee_company.code（java-eq:CaFeeRuleEngineService.java，suggested）
- [[cust_change_cfg]]：cust_project_rel.product_id → cust_change_cfg.id（write-flow:PlatFormMigratoryApplication.java，confirmed）
- [[cust_change_record]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_company_info.code（ref-convention:CustProjectRelDO.java，suggested）
- [[platform_product]]：cust_project_rel.ref_cust_project_rel_platform_product → platform_product.code（ref-convention:CustProjectRelDO.java，suggested）
- [[tenant_product]]：cust_project_rel.product_id → tenant_product.platform_product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[tenant_project]]：cust_project_rel.ref_cust_project_rel_platform_product → tenant_project.ref_tenant_project_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
