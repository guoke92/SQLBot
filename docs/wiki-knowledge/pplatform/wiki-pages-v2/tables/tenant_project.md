---
type: table
title: 租户项目配置
page_key: tenant_project
domain: 租户产品/互通产品/租户项目
status: draft
anchors: [tenant_project]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












tenant_project 保存平台项目主数据：`id` 为项目 ID，`name` 为项目名称，`project_status` 为项目状态，`platform_product_code` 关联产品维度。企业侧与项目的关系不在本表，而落在 [[cust_project_rel]]，后者以 `project_id`（字符串）引用项目。

## 需求背景
项目与产品共同构成企业接入的业务范围；企业在客户服务侧可见的项目由其与企业的关联记录决定，因此项目主数据与关联表需要成对读取。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_project
database: lowcode_pplatform
desc: 租户项目配置
fields:
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
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
    topk: "141|267|271|280|305|333|344|360|383|411|412|415|420|430|454|463|466|93|97"
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
    topk: "209|210|267|271|333|344|360|363|383|411|415|441|454|97"
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
    topk: "333|360|383|404|430|OP001"
    roles: [query, result]
  - name: verification_contact_group
    type: string
    phys: varchar(64)
    desc: 查验组别
    roles: [query, result]
  - name: cover_operator
    type: string
    phys: varchar(2)
    desc: 是否覆盖运营
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: cust_oper_show
    type: string
    phys: varchar(10)
    desc: 建档运营名片展示
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_add
    type: string
    phys: varchar(64)
    desc: 是否新增，Y：是，N：否，默认为N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_prd
    type: string
    phys: varchar(4)
    desc: 是否生产数据
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: operater_card_type
    type: string
    phys: varchar(12)
    desc: 运营名片类型
    dict: operater_card_type
    topk: "WX|WX_WORK"
  - name: project_status
    type: string
    phys: varchar(512)
    desc: 项目状态
    dict: project_status
    topk: "0|1|2"
  - name: send_email
    type: string
    phys: varchar(100)
    desc: 是否发送邮件
    dict: send_email
    topk: "0|1"
    labels: "0:否|1:是"
  - name: share_flag
    type: string
    phys: varchar(4)
    desc: 共享租户
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: test_data
    type: string
    phys: varchar(4)
    desc: 是否测试数据
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: top_flag
    type: string
    phys: varchar(4)
    desc: 置顶标识
    dict: tenant_project__top_flag
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
    topk: "GREENTOWNAT|JHYL|JYYL|Liugongscf|NAURA|QA2tiepai2|YINHEKEJI|base|boscxsbl|boscxyc|chenguang|hylg|reversefactoring|sdhsg|shanghaiyinhang"
  - name: business_group
    type: string
    phys: varchar(100)
    desc: 关联业务部门
    topk: "11|部门a"
  - name: business_manager
    type: string
    phys: varchar(64)
    desc: 业务经理
  - name: bussiness_project_relation
    type: string
    phys: varchar(100)
    desc: 运营项目归属
  - name: channel_code
    type: string
    phys: varchar(128)
    desc: 渠道码
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: config_json
    type: string
    phys: text
    desc: 配置详情
  - name: config_model
    type: string
    phys: varchar(8)
    desc: 项目配置模式(XYC)
    topk: "admin|normal"
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
  - name: custom_field_one
    type: string
    phys: varchar(500)
    desc: 自定义字段一
  - name: custom_field_three
    type: string
    phys: varchar(500)
    desc: 自定义字段三
  - name: custom_field_two
    type: string
    phys: varchar(500)
    desc: 自定义字段二
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: first_settlement_time
    type: temporal
    phys: datetime
    desc: 首笔落地时间
  - name: invite_customer_service_words
    type: string
    phys: varchar(500)
    desc: 客服话术
  - name: logo_path
    type: string
    phys: varchar(526)
    desc: logo路径
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
    roles: [result]
  - name: operator_email
    type: string
    phys: varchar(100)
    desc: 运营对接人邮箱
  - name: operator_id
    type: string
    phys: varchar(100)
    desc: 运营人员id
  - name: operator_name
    type: string
    phys: varchar(100)
    desc: 运营对接人名称
    topk: "112|12321321|4353|yinxiguang|乔|刘宁|唐唐|对先生A|王莲|计娜|阮班良|顾振清|香莲"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(32)
    desc: 平台产品编码
    topk: "ACFLOW|BEECREDIT|DRAFT|DRAFTQA|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [result]
  - name: product_id
    type: number
    phys: bigint(20)
    desc: 产品编码
  - name: project_agreement
    type: string
    phys: varchar(512)
    desc: 项目协议
  - name: project_approval_id
    type: number
    phys: bigint(20)
    desc: 项目线上审批ID
  - name: project_code
    type: string
    phys: varchar(128)
    desc: 项目编码
  - name: project_config_version
    type: string
    phys: varchar(64)
    desc: 项目配置版本
    topk: "config|configPro"
  - name: project_create_time
    type: temporal
    phys: datetime
    desc: 项目创建时间
  - name: project_effective_time
    type: temporal
    phys: datetime
    desc: 项目生效时间
  - name: project_relation
    type: string
    phys: varchar(100)
    desc: 项目归属
    topk: "111|1111"
  - name: project_tag
    type: string
    phys: varchar(150)
    desc: 项目标签
    topk: "PRD|TEST"
  - name: ref_tenant_project_platform_product
    type: string
    phys: varchar(128)
    desc: 平台产品-项目关联
  - name: ref_tenant_project_product_code
    type: string
    phys: varchar(128)
    desc: 租户产品-项目
  - name: ref_tenant_project_tenant_code
    type: string
    phys: varchar(128)
    desc: 租户-项目
  - name: refer_tenant_project_id
    type: number
    phys: bigint(20)
    desc: 复制的租户项目
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: risk_control_contact_b
    type: string
    phys: varchar(64)
    desc: 风控对接人B
    roles: [result]
  - name: solution_manager
    type: string
    phys: varchar(64)
    desc: 方案经理
  - name: source
    type: string
    phys: varchar(32)
    desc: 项目来源
    topk: "ACFLOW|ORDER|RVSFACTOR_PC|STORAGE|pplatform"
  - name: source_id
    type: string
    phys: varchar(32)
    desc: 项目来源id
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: tenant_id
    type: number
    phys: bigint(20)
    desc: 租户编码
  - name: text
    type: string
    phys: varchar(1000)
    desc: 备注
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
  - name: wechat_audit_no
    type: string
    phys: varchar(40)
    desc: 企微审批编号
  - name: wechat_audit_pass_time
    type: temporal
    phys: datetime
    desc: 项目立项审批通过时间
```

## 关联表

- [[ca_fee_project_config]]：tenant_project.id → ca_fee_project_config.project_id（write-flow:CaFeeProjectConfigService.java，confirmed）
- [[cust_project_rel]]：tenant_project.channel_code → cust_project_rel.channel_code（copy:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.id → cust_project_rel.project_id（mapper:CustCompanyQueryMapper.xml，confirmed）
- [[cust_project_rel]]：tenant_project.op_contact_a_group → cust_project_rel.op_contact_a_group（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.op_contact_a → cust_project_rel.op_contact_a（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.op_contact_b → cust_project_rel.op_contact_b（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.platform_product_code → cust_project_rel.ref_cust_project_rel_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[cust_project_rel]]：tenant_project.ref_tenant_project_platform_product → cust_project_rel.ref_cust_project_rel_platform_product（write-flow:CustCompanyInfoApplication.java，confirmed）
- [[cust_project_rel]]：tenant_project.risk_control_contact_a_group → cust_project_rel.risk_control_contact_a_group（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.risk_control_contact_a → cust_project_rel.risk_control_contact_a（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.risk_control_contact_b → cust_project_rel.risk_control_contact_b（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.tenant_flg_en → cust_project_rel.tenant_flg_en（copy:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.verification_contact_group → cust_project_rel.verification_contact_group（copy:TenantProjectApplication.java，suggested）
- [[cust_project_rel]]：tenant_project.verification_contact → cust_project_rel.verification_contact（copy:TenantProjectApplication.java，suggested）
- [[platform_product]]：tenant_project.ref_tenant_project_platform_product → platform_product.code（ref-convention:TenantProjectDO.java，suggested）
- [[platform_product]]：tenant_project.ref_tenant_project_platform_product → platform_product.id（db-index:ref_-naming，suggested）
- [[tenant_product]]：tenant_project.platform_product_code → tenant_product.platform_product_code（copy:TenantProjectDomainService.java，suggested）
- [[tenant_product]]：tenant_project.product_id → tenant_product.id（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_product]]：tenant_project.ref_tenant_project_platform_product → tenant_product.ref_tenant_product_project_code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_product]]：tenant_project.ref_tenant_project_product_code → tenant_product.code（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_product]]：tenant_project.ref_tenant_project_tenant_code → tenant_product.ref_tenant_product_tenant_setting_config（write-flow:TenantProjectDomainService.java，confirmed）
- [[tenant_project_approval_business_info]]：tenant_project.project_config_version → tenant_project_approval_business_info.project_config_version（copy:ProjectBusinessConfigApplication.java，suggested）
- [[tenant_project_approval]]：tenant_project.code → tenant_project_approval.ref_tenant_project_approval_tenant_project（ref-convention:TenantProjectApprovalDO.java，suggested）
- [[tenant_project_approval]]：tenant_project.project_approval_id → tenant_project_approval.id（write-flow:ProjectApprovalApplication.java，confirmed）
