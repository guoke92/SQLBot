---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
status: draft
anchors: [cust_company_info]
sources: ['database_schema:lowcode_pplatform.cust_company_info']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_account_info, cust_auth_application, cust_auth_application_config,
  cust_build_record, cust_certification_info, cust_change_record, cust_company_lifecycle_info,
  cust_app_channel_config, cust_company_survey_state, cust_company_survey_whitelist,
  cust_customized_product, cust_group_rel, cust_head_company_info, cust_interworking_product,
  cust_oper_change_record, cust_person_info, cust_project_code_record, cust_project_rel,
  cust_role_info, cust_setting_config, cust_shareholder_info, cust_survey_answer,
  cust_user_rel, cust_company_info__enable, cust_company_info__act_procinst_status,
  cust_company_info__biz_cust_type, cust_company_info__legal_certification_type, cust_company_info__need_register_ca,
  cust_company_info__need_register_bs, cust_company_info__ca_register_status, cust_company_info__bs_register_status,
  cust_company_info__cust_build_type, cust_company_info__cust_build_status, cust_company_info__identify_style,
  cust_company_info__data_type, cust_company_info__contact_province, cust_company_info__contact_province_code,
  cust_company_info__contact_city_code, cust_company_info__signing_mode, cust_company_info__sign_mode,
  cust_company_info__cust_status, cust_company_info__apply_type, cust_company_info__abroad_cust,
  cust_company_info__outside_org, cust_company_info__group_company, cust_company_info__head_company,
  cust_company_info__legal_realname_status, cust_company_info__test_data, cust_company_info__need_charge,
  cust_company_info__check_status, cust_company_info__audit_back_flag, cust_company_info__cert_no_flag,
  cust_company_info__cust_source, cust_company_info__migarory_auth_aggrement_flag,
  cust_company_info__auth_aggrement_supplement_flag, cust_company_info__third_auth_status,
  cust_company_info__channel_code]
---

# 客户信息主表

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `name`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`, `app_tenant_code`, `db_tenant_code`, `data_type`, `main_data_id`, `ext`, `test_data`, `company_ext_data`, `tenant_flg_en`

### cust_base

`cust_no`, `cust_short_name`, `cust_english_name`, `cust_company_type`, `biz_cust_type`, `cust_former_name`, `certification_no`, `cust_build_type`, `cust_build_status`, `identify_style`, `cust_scale`, `industry_involved`, `cust_profile`, `cust_email`, `client_type`, `signing_mode`, `sign_mode`, `cust_status`, `cust_english_short_name`, `abroad_cust`, `outside_org`, `group_company`, `head_company`, `cust_first_submit_auth`, `cust_from`, `cust_source`

### legal

`legal_name`, `legal_phone`, `legal_certification_no`, `legal_certification_type`, `legal_email`, `legal_certification_start_time`, `legal_certification_end_time`, `legal_time_permanent`, `legal_name_english`, `legal_birth_date`, `legal_name_english_end`, `legal_realname_status`

### business

`establishment_time`, `register_capital`, `time_permanent`, `business_license_start_time`, `business_license_end_time`, `business_province`, `paid_in_capital`, `workers_no`, `business_province_code`, `business_city`, `business_city_code`, `business_address`, `business_scope`, `business_province_city`, `business_status`, `company_size`

### regist

`regist_province`, `regist_province_code`, `regist_city`, `regist_city_code`, `registered_address`, `regist_province_city`, `regist_province_city_english`, `regist_city_english`

### contact

`contact_province`, `contact_province_code`, `contact_city`, `contact_city_code`, `contact_address`, `contact_user_name`, `contact_tel`, `contact_province_city`

### invoicing

`invoicing_taxpayer_no`, `invoicing_name`, `invoicing_accont_no`, `invoicing_phone`, `invoicing_email`, `invoicing_address`, `invoicing_bank_name`, `invoicing_bank_code`, `invoicing_bank_province_city`, `invoicing_bank_branch`, `invoicing_bank_no`, `billing_type`, `bank_branch`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `apply_data_id`, `pc_task_id`, `back_reason`, `apply_type`, `check_status`, `audit_back_flag`, `third_auth_status`, `approval_date`

### signing

`need_register_ca`, `need_register_bs`, `ca_register_status`, `bs_register_status`, `need_charge`

### finance

`finance_org_flag`, `finance_org_type`, `finance_org_code`, `finance_org_type_name`

### relate

`organization_id`, `relate_company_id`, `platform_cust_id`, `manager_id`, `relate_company_name`, `core_bosc_company_id`

### channel_extension

`nationality`, `nationality_en`, `composite_field`, `cash_contract_no`, `xib_factor_contract_no`, `zybank_cash_contract_amt`, `lybank_cash_contract_no`, `cert_no_flag`, `migarory_auth_aggrement_flag`, `auth_aggrement_supplement_flag`, `channel_code`

## 字段

```ground:table
table: cust_company_info
database: lowcode_pplatform
description: 客户信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_short_name, cust_english_name, cust_former_name, legal_name,
  business_province_code, business_city_code, regist_province_code, regist_city_code,
  contact_province_code, contact_city_code, contact_user_name, invoicing_name, invoicing_bank_name,
  invoicing_bank_code, cust_english_short_name, relate_company_name, finance_org_code,
  finance_org_type_name]
clusters:
- key: common
  title: 通用
  include: always
- key: cust_base
  title: 客户主档
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: legal
  title: 法人信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: business
  title: 经营信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: regist
  title: 注册信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: contact
  title: 联系信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: invoicing
  title: 开票信息
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: signing
  title: 签约认证
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: finance
  title: 金融机构
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: relate
  title: 归属关系
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: channel_extension
  title: 渠道与扩展
  trust: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
fields:
- name: id
  data_type: number
  description: 表主键
  nullable: false
  cluster: common
- name: code
  data_type: string
  description: 编码
  cluster: common
- name: name
  data_type: string
  description: 客户名称
  cluster: common
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: cust_company_info__enable
- name: remark
  data_type: string
  description: remark
  cluster: common
- name: create_by
  data_type: string
  description: 创建人id
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  cluster: approval
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  cluster: common
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: common
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
  dictionary: cust_company_info__act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: relate
- name: cust_no
  data_type: string
  description: 客户编号
  cluster: cust_base
- name: cust_short_name
  data_type: string
  description: 企业简称
  cluster: cust_base
- name: cust_english_name
  data_type: string
  description: 客户英文名称
  cluster: cust_base
- name: cust_company_type
  data_type: string
  description: 企业角色
  cluster: cust_base
- name: biz_cust_type
  data_type: string
  description: 工商类别
  cluster: cust_base
  dictionary: cust_company_info__biz_cust_type
- name: cust_former_name
  data_type: string
  description: 曾用名
  cluster: cust_base
- name: certification_no
  data_type: string
  description: 统一信用代码
  cluster: cust_base
- name: establishment_time
  data_type: temporal
  description: 成立日期
  cluster: business
- name: register_capital
  data_type: number
  description: 注册资本
  cluster: business
- name: time_permanent
  data_type: string
  description: 营业执照有效期
  cluster: business
- name: business_license_start_time
  data_type: temporal
  description: 企业营业执照开始时间
  cluster: business
- name: business_license_end_time
  data_type: temporal
  description: 企业营业执照结束时间
  cluster: business
- name: legal_name
  data_type: string
  description: 法人姓名
  cluster: legal
- name: legal_phone
  data_type: string
  description: 法人手机号码
  cluster: legal
- name: legal_certification_no
  data_type: string
  description: 法人证件号
  cluster: legal
- name: legal_certification_type
  data_type: string
  description: 法人证件类型
  cluster: legal
  dictionary: cust_company_info__legal_certification_type
- name: legal_email
  data_type: string
  description: 法人邮箱
  cluster: legal
- name: legal_certification_start_time
  data_type: temporal
  description: 法人证件开始日期
  cluster: legal
- name: legal_certification_end_time
  data_type: temporal
  description: 法人证件结束日期
  cluster: legal
- name: legal_time_permanent
  data_type: string
  description: 身份证有效期标志
  cluster: legal
- name: need_register_ca
  data_type: string
  description: 开通电子签章
  cluster: signing
  dictionary: cust_company_info__need_register_ca
- name: need_register_bs
  data_type: string
  description: 是否需要开通上上签电子签章
  cluster: signing
  dictionary: cust_company_info__need_register_bs
- name: ca_register_status
  data_type: string
  description: CA开通状态
  cluster: signing
  dictionary: cust_company_info__ca_register_status
- name: bs_register_status
  data_type: string
  description: 上上签开通状态
  cluster: signing
  dictionary: cust_company_info__bs_register_status
- name: cust_build_type
  data_type: string
  description: 录入方式
  cluster: cust_base
  dictionary: cust_company_info__cust_build_type
- name: cust_build_status
  data_type: string
  description: 认证状态
  cluster: cust_base
  dictionary: cust_company_info__cust_build_status
- name: identify_style
  data_type: string
  description: 认证方式
  cluster: cust_base
  dictionary: cust_company_info__identify_style
- name: cust_scale
  data_type: string
  description: 企业规模
  cluster: cust_base
- name: industry_involved
  data_type: string
  description: 所属行业
  cluster: cust_base
- name: cust_profile
  data_type: string
  description: 企业简介
  cluster: cust_base
- name: data_type
  data_type: string
  description: 数据类型：1,主数据，0记录数据
  cluster: common
  dictionary: cust_company_info__data_type
- name: main_data_id
  data_type: number
  description: 主数据id
  cluster: common
- name: business_province
  data_type: string
  description: 经营省份
  cluster: business
- name: paid_in_capital
  data_type: string
  description: 实缴资本（元）
  cluster: business
- name: workers_no
  data_type: string
  description: 员工
  cluster: business
- name: business_province_code
  data_type: string
  description: 经营省份代码
  cluster: business
- name: business_city
  data_type: string
  description: 经营市
  cluster: business
- name: business_city_code
  data_type: string
  description: 经营城市代码
  cluster: business
- name: business_address
  data_type: string
  description: 经营地址
  cluster: business
- name: regist_province
  data_type: string
  description: 注册省份
  cluster: regist
- name: regist_province_code
  data_type: string
  description: 注册省份代码
  cluster: regist
- name: regist_city
  data_type: string
  description: 注册市
  cluster: regist
- name: regist_city_code
  data_type: string
  description: 注册城市代码
  cluster: regist
- name: registered_address
  data_type: string
  description: 注册地址
  cluster: regist
- name: contact_province
  data_type: string
  description: 联系省份
  cluster: contact
  dictionary: cust_company_info__contact_province
- name: contact_province_code
  data_type: string
  description: 联系省份代码
  cluster: contact
  dictionary: cust_company_info__contact_province_code
- name: contact_city
  data_type: string
  description: 联系市
  cluster: contact
- name: contact_city_code
  data_type: string
  description: 联系城市代码
  cluster: contact
  dictionary: cust_company_info__contact_city_code
- name: contact_address
  data_type: string
  description: 联系地址
  cluster: contact
- name: contact_user_name
  data_type: string
  description: 联系人
  cluster: contact
- name: contact_tel
  data_type: string
  description: 联系电话
  cluster: contact
- name: cust_email
  data_type: string
  description: 公司联系邮箱
  cluster: cust_base
- name: business_scope
  data_type: string
  description: 经营范围
  cluster: business
- name: client_type
  data_type: string
  description: 发起变更的客户端类型
  cluster: cust_base
- name: signing_mode
  data_type: string
  description: 签署模式
  cluster: cust_base
  dictionary: cust_company_info__signing_mode
- name: contact_province_city
  data_type: string
  description: 联系省市
  cluster: contact
- name: business_province_city
  data_type: string
  description: 经营省市
  cluster: business
- name: regist_province_city
  data_type: string
  description: 注册省市
  cluster: regist
- name: invoicing_taxpayer_no
  data_type: string
  description: 开票纳税人识别号
  cluster: invoicing
- name: invoicing_name
  data_type: string
  description: 开票名称
  cluster: invoicing
- name: invoicing_accont_no
  data_type: string
  description: 开票开户行账号
  cluster: invoicing
- name: invoicing_phone
  data_type: string
  description: 开票电话
  cluster: invoicing
- name: invoicing_email
  data_type: string
  description: 开票电子邮箱
  cluster: invoicing
- name: invoicing_address
  data_type: string
  description: 开票地址
  cluster: invoicing
- name: invoicing_bank_name
  data_type: string
  description: 开票银行名称
  cluster: invoicing
- name: invoicing_bank_code
  data_type: string
  description: 开票银行代码
  cluster: invoicing
- name: invoicing_bank_province_city
  data_type: string
  description: 开票银行省市
  cluster: invoicing
- name: invoicing_bank_branch
  data_type: string
  description: 开票银行支行
  cluster: invoicing
- name: invoicing_bank_no
  data_type: string
  description: 开票银行联行号
  cluster: invoicing
- name: apply_data_id
  data_type: number
  description: 认证流程数据id
  cluster: approval
- name: sign_mode
  data_type: string
  description: 产品协议签署方式
  cluster: cust_base
  dictionary: cust_company_info__sign_mode
- name: pc_task_id
  data_type: string
  description: 退回客户端补充资料taskId
  cluster: approval
- name: cust_status
  data_type: string
  description: 客户状态
  cluster: cust_base
  dictionary: cust_company_info__cust_status
- name: back_reason
  data_type: string
  description: 退回原因
  cluster: approval
- name: apply_type
  data_type: string
  description: 流程类型
  cluster: approval
  dictionary: cust_company_info__apply_type
- name: cust_english_short_name
  data_type: string
  description: 企业简称英文
  cluster: cust_base
- name: abroad_cust
  data_type: string
  description: 是否境外
  cluster: cust_base
  dictionary: cust_company_info__abroad_cust
- name: outside_org
  data_type: string
  description: 外部机构
  cluster: cust_base
  dictionary: cust_company_info__outside_org
- name: business_status
  data_type: string
  description: 经营状态
  cluster: business
- name: relate_company_id
  data_type: string
  description: 归属企业id
  cluster: relate
- name: group_company
  data_type: string
  description: 是否归属集团或核心企业
  cluster: cust_base
  dictionary: cust_company_info__group_company
- name: regist_province_city_english
  data_type: string
  description: 注册省市(英文)
  cluster: regist
- name: head_company
  data_type: string
  description: 是否总公司
  cluster: cust_base
  dictionary: cust_company_info__head_company
- name: platform_cust_id
  data_type: number
  description: 运营中台id
  cluster: relate
- name: legal_name_english
  data_type: string
  description: 法人姓名(英文)
  cluster: legal
- name: manager_id
  data_type: string
  description: 业务经理
  cluster: relate
- name: legal_birth_date
  data_type: temporal
  description: 法人生日
  cluster: legal
- name: ext
  data_type: string
  description: 扩展信息
  cluster: common
- name: legal_name_english_end
  data_type: string
  description: 法人名(英文)
  cluster: legal
- name: regist_city_english
  data_type: string
  description: 市（英文）
  cluster: regist
- name: legal_realname_status
  data_type: string
  description: 法人认证状态
  cluster: legal
  dictionary: cust_company_info__legal_realname_status
- name: test_data
  data_type: string
  description: 是否测试数据
  cluster: common
  dictionary: cust_company_info__test_data
- name: company_ext_data
  data_type: structured
  cluster: common
- name: need_charge
  data_type: string
  description: 运营方是否涉及收费
  cluster: signing
  dictionary: cust_company_info__need_charge
- name: finance_org_flag
  data_type: string
  description: 金融机构身份标识
  cluster: finance
- name: nationality
  data_type: string
  cluster: channel_extension
- name: nationality_en
  data_type: string
  cluster: channel_extension
- name: check_status
  data_type: string
  cluster: approval
  dictionary: cust_company_info__check_status
- name: relate_company_name
  data_type: string
  description: 归属集团或企业
  cluster: relate
- name: core_bosc_company_id
  data_type: string
  description: 关联核心企业（补充字段）
  cluster: relate
- name: composite_field
  data_type: string
  description: 工行供应链编号（补充字段）
  cluster: channel_extension
- name: cash_contract_no
  data_type: string
  description: 中原融资合同编号（补充字段）
  cluster: channel_extension
- name: xib_factor_contract_no
  data_type: string
  description: 厦银保理合同编号（补充字段）
  cluster: channel_extension
- name: zybank_cash_contract_amt
  data_type: string
  description: 中原融资合同金额（补充字段）
  cluster: channel_extension
- name: billing_type
  data_type: string
  description: 开票类型（补充字段）
  cluster: invoicing
- name: lybank_cash_contract_no
  data_type: string
  description: 洛阳融资合同编号（补充字段）
  cluster: channel_extension
- name: company_size
  data_type: string
  description: 增值税纳税人类别（补充字段）
  cluster: business
- name: cust_first_submit_auth
  data_type: temporal
  description: 客户首次提交认证时间
  cluster: cust_base
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  cluster: common
- name: cust_from
  data_type: string
  description: 客户来源
  cluster: cust_base
- name: audit_back_flag
  data_type: string
  description: 审核退回标记
  cluster: approval
  dictionary: cust_company_info__audit_back_flag
- name: cert_no_flag
  data_type: string
  description: 执行查询统一信用证编码
  cluster: channel_extension
  dictionary: cust_company_info__cert_no_flag
- name: cust_source
  data_type: string
  description: 建档数据来源
  cluster: cust_base
  dictionary: cust_company_info__cust_source
- name: migarory_auth_aggrement_flag
  data_type: string
  description: 新旧渠道授权书补签标识，Y 新渠道:N 旧渠道
  cluster: channel_extension
  dictionary: cust_company_info__migarory_auth_aggrement_flag
- name: auth_aggrement_supplement_flag
  data_type: string
  description: 是否授权书补签标识
  cluster: channel_extension
  dictionary: cust_company_info__auth_aggrement_supplement_flag
- name: finance_org_type
  data_type: string
  description: 金融机构类型(补充字段)
  cluster: finance
- name: finance_org_code
  data_type: string
  description: 金融机构编码(补充字段)
  cluster: finance
- name: finance_org_type_name
  data_type: string
  cluster: finance
- name: bank_branch
  data_type: string
  description: 银行分行名称（通用）(补充字段)
  cluster: invoicing
- name: third_auth_status
  data_type: string
  description: 第三方认证状态
  cluster: approval
  dictionary: cust_company_info__third_auth_status
- name: approval_date
  data_type: temporal
  description: 核准日期
  cluster: approval
- name: channel_code
  data_type: string
  description: 开放平台channelcode
  cluster: channel_extension
  dictionary: cust_company_info__channel_code
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: cust_company_lifecycle_info.code
right: cust_company_info.apply_data_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_profile:lowcode_pplatform.cust_company_info.apply_data_id
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: apply_data_id
  comment: 认证流程数据id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 15
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 值域重合 1.0，但列名/注释无关联语义（code vs 认证流程数据id），仅值域契合，待人工确认。
preview_block: overlap_unsemantic
```

```ground:relation
type: EQUI_JOIN
left: cust_account_info.code
right: cust_company_info.apply_data_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_profile:lowcode_pplatform.cust_company_info.apply_data_id
source: overlap
join_role: business_code
priority: primary
name_evidence:
  match: none
  stem: apply_data_id
  comment: 认证流程数据id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 15
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 值域重合 1.0，但列名/注释无关联语义（code vs 认证流程数据id），仅值域契合，待人工确认。
preview_block: overlap_unsemantic
```

```ground:relation
type: EQUI_JOIN
left: cust_app_channel_config.code
right: cust_company_info.channel_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.cust_company_info.channel_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: channel_code
  comment: 码对码且值域重合 1.0，客户应用渠道关系表 code 可对应开放平台 channel_code；样本仅 2，建议人工确认。
overlap:
  probed: true
  ratio: 1.0
  sample_size: 2
  authenticity: unknown
authenticity_note: 码对码且值域重合 1.0，客户应用渠道关系表 code 可对应开放平台 channel_code；样本仅 2，建议人工确认。
```

## 页面链接

### 关联表

- [[tables/cust_account_info]]
- [[tables/cust_auth_application]]
- [[tables/cust_auth_application_config]]
- [[tables/cust_build_record]]
- [[tables/cust_certification_info]]
- [[tables/cust_change_record]]
- [[tables/cust_company_lifecycle_info]]
- [[tables/cust_app_channel_config]]
- [[tables/cust_company_survey_state]]
- [[tables/cust_company_survey_whitelist]]
- [[tables/cust_customized_product]]
- [[tables/cust_group_rel]]
- [[tables/cust_head_company_info]]
- [[tables/cust_interworking_product]]
- [[tables/cust_oper_change_record]]
- [[tables/cust_person_info]]
- [[tables/cust_project_code_record]]
- [[tables/cust_project_rel]]
- [[tables/cust_role_info]]
- [[tables/cust_setting_config]]
- [[tables/cust_shareholder_info]]
- [[tables/cust_survey_answer]]
- [[tables/cust_user_rel]]

### 字典

- [[dicts/cust_company_info__enable]]（`cust_company_info.enable`）
- [[dicts/cust_company_info__act_procinst_status]]（`cust_company_info.act_procinst_status`）
- [[dicts/cust_company_info__biz_cust_type]]（`cust_company_info.biz_cust_type`）
- [[dicts/cust_company_info__legal_certification_type]]（`cust_company_info.legal_certification_type`）
- [[dicts/cust_company_info__need_register_ca]]（`cust_company_info.need_register_ca`）
- [[dicts/cust_company_info__need_register_bs]]（`cust_company_info.need_register_bs`）
- [[dicts/cust_company_info__ca_register_status]]（`cust_company_info.ca_register_status`）
- [[dicts/cust_company_info__bs_register_status]]（`cust_company_info.bs_register_status`）
- [[dicts/cust_company_info__cust_build_type]]（`cust_company_info.cust_build_type`）
- [[dicts/cust_company_info__cust_build_status]]（`cust_company_info.cust_build_status`）
- [[dicts/cust_company_info__identify_style]]（`cust_company_info.identify_style`）
- [[dicts/cust_company_info__data_type]]（`cust_company_info.data_type`）
- [[dicts/cust_company_info__contact_province]]（`cust_company_info.contact_province`）
- [[dicts/cust_company_info__contact_province_code]]（`cust_company_info.contact_province_code`）
- [[dicts/cust_company_info__contact_city_code]]（`cust_company_info.contact_city_code`）
- [[dicts/cust_company_info__signing_mode]]（`cust_company_info.signing_mode`）
- [[dicts/cust_company_info__sign_mode]]（`cust_company_info.sign_mode`）
- [[dicts/cust_company_info__cust_status]]（`cust_company_info.cust_status`）
- [[dicts/cust_company_info__apply_type]]（`cust_company_info.apply_type`）
- [[dicts/cust_company_info__abroad_cust]]（`cust_company_info.abroad_cust`）
- [[dicts/cust_company_info__outside_org]]（`cust_company_info.outside_org`）
- [[dicts/cust_company_info__group_company]]（`cust_company_info.group_company`）
- [[dicts/cust_company_info__head_company]]（`cust_company_info.head_company`）
- [[dicts/cust_company_info__legal_realname_status]]（`cust_company_info.legal_realname_status`）
- [[dicts/cust_company_info__test_data]]（`cust_company_info.test_data`）
- [[dicts/cust_company_info__need_charge]]（`cust_company_info.need_charge`）
- [[dicts/cust_company_info__check_status]]（`cust_company_info.check_status`）
- [[dicts/cust_company_info__audit_back_flag]]（`cust_company_info.audit_back_flag`）
- [[dicts/cust_company_info__cert_no_flag]]（`cust_company_info.cert_no_flag`）
- [[dicts/cust_company_info__cust_source]]（`cust_company_info.cust_source`）
- [[dicts/cust_company_info__migarory_auth_aggrement_flag]]（`cust_company_info.migarory_auth_aggrement_flag`）
- [[dicts/cust_company_info__auth_aggrement_supplement_flag]]（`cust_company_info.auth_aggrement_supplement_flag`）
- [[dicts/cust_company_info__third_auth_status]]（`cust_company_info.third_auth_status`）
- [[dicts/cust_company_info__channel_code]]（`cust_company_info.channel_code`）
