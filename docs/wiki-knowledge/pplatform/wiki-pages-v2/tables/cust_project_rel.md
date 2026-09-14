---
type: table
title: 客户项目关联表
page_key: cust_project_rel
domain: 项目报表/统计/上报
status: draft
anchors: [cust_project_rel]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












cust_project_rel 记录客户与项目的关系，其中 company_type 承载该客户在项目中的企业角色。该字段与 [[cust_role_info]].role_type 为业务同步关系（derived，无外键约束）。

## 需求背景

为客户添加角色后，需要把该企业所有项目关系记录的 companyType 统一更新为第一个角色值，使项目维度也能识别客户身份，规则见 [[project_rel_role_sync]]。

## 版本演进

- v0（draft）：本页仅依据 addRoleInfo 代码路径成页，字段清单不完整，待补 DDL 后扩充。

```ground:table
table: cust_project_rel
database: lowcode_pplatform
desc: 客户项目关联表
fields:
  - name: company_type
    type: string
    phys: varchar(128)
    desc: 客户角色(只取一个)
    dict: cust_project_rel__company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PLATFORM_OPREATOR_COMPANY|PROJECT_COMPANY|SUPPLIER"
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
    topk: "141|145|257|267|333|344|360|383|411|415|420|454|466|93|OP001|OP002|OP003|OP010"
    roles: [query, result]
  - name: op_contact_a_group
    type: string
    phys: varchar(100)
    desc: 运营组别
    roles: [query, result]
  - name: risk_control_contact_a
    type: string
    phys: varchar(64)
    desc: 风控对接人A
    topk: "257|267|333|344|360|383|420|441|466|97|OP001|OP002|OP005|OP006|OP007"
    roles: [query, result]
  - name: risk_control_contact_a_group
    type: string
    phys: varchar(64)
    desc: 风控组别
    roles: [query, result]
  - name: verification_contact
    type: string
    phys: varchar(64)
    desc: 查验对接人
    topk: "257|289|333|344|360|383|404|430|454|97|OP001|OP002|OP003|OP004"
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    roles: [query, result]
  - name: project_open_status
    type: string
    phys: varchar(64)
    desc: 项目开通状态
    dict: project_open_status
    topk: "NOT_OPEN|OPENED"
  - name: show_flag
    type: string
    phys: varchar(20)
    desc: 展示标记
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: status
    type: string
    phys: varchar(64)
    desc: 关联状态
    dict: cust_project_rel__status
    topk: " 1 |0|1"
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    dict: top_flag
    topk: "0|1"
    labels: "0:否|1:是"
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
    topk: "base|common|xyc.llschain.com"
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
    topk: "admin"
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
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
    topk: "刘倍材|刘宁"
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
  - name: ref_cust_project_rel_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户和项目关系
  - name: ref_cust_project_rel_platform_product
    type: string
    phys: varchar(128)
    desc: 平台产品
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: "ACFLOW|AMS|BEECREDIT|DEALER|DRAFT|DRAFTQA|ORDER|RVSFACTOR|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: risk_control_contact_b
    type: string
    phys: varchar(200)
    desc: 风控对接人B
    roles: [result]
  - name: tenant_code
    type: string
    phys: varchar(512)
    desc: 租户
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
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

- [[ca_fee_company]]：cust_project_rel.ref_cust_project_rel_cust_company_info → ca_fee_company.code（java-eq:CaFeeRuleEngineService.java，suggested）
- [[cust_change_cfg]]：cust_project_rel.product_id → cust_change_cfg.id（write-flow:PlatFormMigratoryApplication.java，confirmed）
- [[cust_change_record]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_company_info.code（ref-convention:CustProjectRelDO.java，suggested）
- [[cust_company_info]]：cust_project_rel.ref_cust_project_rel_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[cust_person_info]]：cust_project_rel.company_type → cust_person_info.company_type（copy:PlatFormMigratoryApplication.java，suggested）
- [[platform_product]]：cust_project_rel.ref_cust_project_rel_platform_product → platform_product.code（ref-convention:CustProjectRelDO.java，suggested）
- [[platform_product]]：cust_project_rel.ref_cust_project_rel_platform_product → platform_product.id（db-index:ref_-naming，suggested）
- [[tenant_product]]：cust_project_rel.product_id → tenant_product.id（java-eq:CustProjectController.java，suggested）
- [[tenant_product]]：cust_project_rel.product_id → tenant_product.platform_product_id（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[tenant_project]]：cust_project_rel.channel_code → tenant_project.channel_code（copy:CustCompanyInfoApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.op_contact_a_group → tenant_project.op_contact_a_group（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.op_contact_a → tenant_project.op_contact_a（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.op_contact_b → tenant_project.op_contact_b（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.project_id → tenant_project.id（mapper:CustCompanyQueryMapper.xml，confirmed）
- [[tenant_project]]：cust_project_rel.ref_cust_project_rel_platform_product → tenant_project.platform_product_code（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[tenant_project]]：cust_project_rel.ref_cust_project_rel_platform_product → tenant_project.ref_tenant_project_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[tenant_project]]：cust_project_rel.risk_control_contact_a_group → tenant_project.risk_control_contact_a_group（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.risk_control_contact_a → tenant_project.risk_control_contact_a（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.risk_control_contact_b → tenant_project.risk_control_contact_b（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.tenant_flg_en → tenant_project.tenant_flg_en（copy:CustCompanyInfoApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.verification_contact_group → tenant_project.verification_contact_group（copy:TenantProjectApplication.java，suggested）
- [[tenant_project]]：cust_project_rel.verification_contact → tenant_project.verification_contact（copy:TenantProjectApplication.java，suggested）
