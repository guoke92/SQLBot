---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
status: draft
aliases: []
anchors:
- cust_company_info
sources:
- database_schema:lowcode_pplatform.cust_company_info
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 客户信息主表

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant

`app_tenant_code`, `db_tenant_code`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`, `apply_data_id`, `pc_task_id`, `back_reason`, `apply_type`, `audit_back_flag`, `approval_date`

### identity

`name`, `cust_no`, `cust_short_name`, `cust_english_name`, `cust_former_name`, `certification_no`, `cust_english_short_name`

### classification

`cust_company_type`, `biz_cust_type`, `cust_build_type`, `cust_build_status`, `identify_style`, `cust_scale`, `industry_involved`, `cust_profile`, `data_type`, `main_data_id`, `cust_status`, `abroad_cust`, `check_status`, `company_size`, `cust_first_submit_auth`, `cust_from`, `cust_source`

### business

`establishment_time`, `register_capital`, `time_permanent`, `business_license_start_time`, `business_license_end_time`, `business_province`, `paid_in_capital`, `workers_no`, `business_province_code`, `business_city`, `business_city_code`, `business_address`, `business_scope`, `business_province_city`, `business_status`

### regist

`regist_province`, `regist_province_code`, `regist_city`, `regist_city_code`, `registered_address`, `regist_province_city`, `regist_province_city_english`, `regist_city_english`

### contact

`contact_province`, `contact_province_code`, `contact_city`, `contact_city_code`, `contact_address`, `contact_user_name`, `contact_tel`, `cust_email`, `contact_province_city`

### legal

`legal_name`, `legal_phone`, `legal_certification_no`, `legal_certification_type`, `legal_email`, `legal_certification_start_time`, `legal_certification_end_time`, `legal_time_permanent`, `legal_name_english`, `legal_birth_date`, `legal_name_english_end`, `legal_realname_status`, `nationality`, `nationality_en`

### esign

`need_register_ca`, `need_register_bs`, `ca_register_status`, `bs_register_status`, `signing_mode`, `sign_mode`, `need_charge`, `migarory_auth_aggrement_flag`, `auth_aggrement_supplement_flag`

### invoicing

`invoicing_taxpayer_no`, `invoicing_name`, `invoicing_accont_no`, `invoicing_phone`, `invoicing_email`, `invoicing_address`, `invoicing_bank_name`, `invoicing_bank_code`, `invoicing_bank_province_city`, `invoicing_bank_branch`, `invoicing_bank_no`, `billing_type`

### finance

`finance_org_flag`, `finance_org_type`, `finance_org_code`, `finance_org_type_name`, `bank_branch`, `third_auth_status`

### channel

`client_type`, `outside_org`, `tenant_flg_en`, `channel_code`

### group

`organization_id`, `relate_company_id`, `group_company`, `head_company`, `platform_cust_id`, `manager_id`, `relate_company_name`, `core_bosc_company_id`

### contract

`composite_field`, `cash_contract_no`, `xib_factor_contract_no`, `zybank_cash_contract_amt`, `lybank_cash_contract_no`

### misc

`remark`, `ext`, `test_data`, `company_ext_data`, `cert_no_flag`

## 字段

```ground:table
table: cust_company_info
database: lowcode_pplatform
description: 客户信息主表
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- cust_short_name
- cust_english_name
- cust_former_name
- legal_name
- business_province_code
- business_city_code
- regist_province_code
- regist_city_code
- contact_province_code
- contact_city_code
- contact_user_name
- invoicing_name
- invoicing_bank_name
- invoicing_bank_code
- cust_english_short_name
- relate_company_name
- finance_org_code
- finance_org_type_name
- channel_code
clusters:
- key: common
  title: 通用与审计
  include: always
- key: tenant
  title: 租户标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: workflow
  title: 流程与审批
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: identity
  title: 客户主档标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: classification
  title: 客户分类与状态
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: business
  title: 工商与经营信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: regist
  title: 注册地址
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: contact
  title: 联系信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: legal
  title: 法人信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: esign
  title: 电子签章与授权
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: invoicing
  title: 开票信息
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: finance
  title: 金融机构
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: channel
  title: 客户端与渠道
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: group
  title: 归属与关联主体
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: contract
  title: 补充合同字段
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.cust_company_info
- key: misc
  title: 扩展与其他标记
  confidence: proposed
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
  nullable: true
  cluster: common
- name: name
  data_type: string
  description: 客户名称
  nullable: true
  cluster: identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: cust_company_info_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: misc
- name: create_by
  data_type: string
  description: 创建人id
  nullable: true
  cluster: common
- name: create_user
  data_type: string
  description: 创建人名称
  nullable: true
  cluster: common
- name: create_time
  data_type: temporal
  description: 创建时间
  nullable: false
  cluster: common
- name: update_by
  data_type: string
  description: 更新人id
  nullable: true
  cluster: common
- name: update_user
  data_type: string
  description: 更新人名称
  nullable: true
  cluster: common
- name: update_time
  data_type: temporal
  description: 更新时间
  nullable: false
  cluster: common
- name: act_procinst_id
  data_type: string
  description: 流程实例ID
  nullable: true
  cluster: workflow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: group
- name: cust_no
  data_type: string
  description: 客户编号
  nullable: true
  cluster: identity
- name: cust_short_name
  data_type: string
  description: 企业简称
  nullable: true
  cluster: identity
- name: cust_english_name
  data_type: string
  description: 客户英文名称
  nullable: true
  cluster: identity
- name: cust_company_type
  data_type: string
  description: 企业角色
  nullable: true
  cluster: classification
- name: biz_cust_type
  data_type: string
  description: 工商类别
  nullable: true
  cluster: classification
- name: cust_former_name
  data_type: string
  description: 曾用名
  nullable: true
  cluster: identity
- name: certification_no
  data_type: string
  description: 统一信用代码
  nullable: true
  cluster: identity
- name: establishment_time
  data_type: temporal
  description: 成立日期
  nullable: true
  cluster: business
- name: register_capital
  data_type: number
  description: 注册资本
  nullable: true
  cluster: business
- name: time_permanent
  data_type: string
  description: 营业执照有效期
  nullable: true
  cluster: business
- name: business_license_start_time
  data_type: temporal
  description: 企业营业执照开始时间
  nullable: true
  cluster: business
- name: business_license_end_time
  data_type: temporal
  description: 企业营业执照结束时间
  nullable: true
  cluster: business
- name: legal_name
  data_type: string
  description: 法人姓名
  nullable: true
  cluster: legal
- name: legal_phone
  data_type: string
  description: 法人手机号码
  nullable: true
  cluster: legal
- name: legal_certification_no
  data_type: string
  description: 法人证件号
  nullable: true
  cluster: legal
- name: legal_certification_type
  data_type: string
  description: 法人证件类型
  nullable: true
  cluster: legal
- name: legal_email
  data_type: string
  description: 法人邮箱
  nullable: true
  cluster: legal
- name: legal_certification_start_time
  data_type: temporal
  description: 法人证件开始日期
  nullable: true
  cluster: legal
- name: legal_certification_end_time
  data_type: temporal
  description: 法人证件结束日期
  nullable: true
  cluster: legal
- name: legal_time_permanent
  data_type: string
  description: 身份证有效期标志
  nullable: true
  cluster: legal
- name: need_register_ca
  data_type: string
  description: 开通电子签章
  nullable: true
  cluster: esign
  dictionary: cust_company_info_need_register_ca
- name: need_register_bs
  data_type: string
  description: 是否需要开通上上签电子签章
  nullable: true
  cluster: esign
  dictionary: cust_company_info_need_register_bs
- name: ca_register_status
  data_type: string
  description: CA开通状态
  nullable: true
  cluster: esign
  dictionary: cust_company_info_ca_register_status
- name: bs_register_status
  data_type: string
  description: 上上签开通状态
  nullable: true
  cluster: esign
  dictionary: cust_company_info_bs_register_status
- name: cust_build_type
  data_type: string
  description: 录入方式
  nullable: true
  cluster: classification
  dictionary: cust_company_info_cust_build_type
- name: cust_build_status
  data_type: string
  description: 认证状态
  nullable: true
  cluster: classification
  dictionary: cust_company_info_cust_build_status
- name: identify_style
  data_type: string
  description: 认证方式
  nullable: true
  cluster: classification
  dictionary: cust_company_info_identify_style
- name: cust_scale
  data_type: string
  description: 企业规模
  nullable: true
  cluster: classification
- name: industry_involved
  data_type: string
  description: 所属行业
  nullable: true
  cluster: classification
- name: cust_profile
  data_type: string
  description: 企业简介
  nullable: true
  cluster: classification
- name: data_type
  data_type: string
  description: 数据类型：1,主数据，0记录数据
  nullable: true
  cluster: classification
  dictionary: cust_company_info_data_type
- name: main_data_id
  data_type: number
  description: 主数据id
  nullable: true
  cluster: classification
- name: business_province
  data_type: string
  description: 经营省份
  nullable: true
  cluster: business
- name: paid_in_capital
  data_type: string
  description: 实缴资本（元）
  nullable: true
  cluster: business
- name: workers_no
  data_type: string
  description: 员工
  nullable: true
  cluster: business
- name: business_province_code
  data_type: string
  description: 经营省份代码
  nullable: true
  cluster: business
- name: business_city
  data_type: string
  description: 经营市
  nullable: true
  cluster: business
- name: business_city_code
  data_type: string
  description: 经营城市代码
  nullable: true
  cluster: business
- name: business_address
  data_type: string
  description: 经营地址
  nullable: true
  cluster: business
- name: regist_province
  data_type: string
  description: 注册省份
  nullable: true
  cluster: regist
- name: regist_province_code
  data_type: string
  description: 注册省份代码
  nullable: true
  cluster: regist
- name: regist_city
  data_type: string
  description: 注册市
  nullable: true
  cluster: regist
- name: regist_city_code
  data_type: string
  description: 注册城市代码
  nullable: true
  cluster: regist
- name: registered_address
  data_type: string
  description: 注册地址
  nullable: true
  cluster: regist
- name: contact_province
  data_type: string
  description: 联系省份
  nullable: true
  cluster: contact
- name: contact_province_code
  data_type: string
  description: 联系省份代码
  nullable: true
  cluster: contact
- name: contact_city
  data_type: string
  description: 联系市
  nullable: true
  cluster: contact
- name: contact_city_code
  data_type: string
  description: 联系城市代码
  nullable: true
  cluster: contact
- name: contact_address
  data_type: string
  description: 联系地址
  nullable: true
  cluster: contact
- name: contact_user_name
  data_type: string
  description: 联系人
  nullable: true
  cluster: contact
- name: contact_tel
  data_type: string
  description: 联系电话
  nullable: true
  cluster: contact
- name: cust_email
  data_type: string
  description: 公司联系邮箱
  nullable: true
  cluster: contact
- name: business_scope
  data_type: string
  description: 经营范围
  nullable: true
  cluster: business
- name: client_type
  data_type: string
  description: 发起变更的客户端类型
  nullable: true
  cluster: channel
- name: signing_mode
  data_type: string
  description: 签署模式
  nullable: true
  cluster: esign
- name: contact_province_city
  data_type: string
  description: 联系省市
  nullable: true
  cluster: contact
- name: business_province_city
  data_type: string
  description: 经营省市
  nullable: true
  cluster: business
- name: regist_province_city
  data_type: string
  description: 注册省市
  nullable: true
  cluster: regist
- name: invoicing_taxpayer_no
  data_type: string
  description: 开票纳税人识别号
  nullable: true
  cluster: invoicing
- name: invoicing_name
  data_type: string
  description: 开票名称
  nullable: true
  cluster: invoicing
- name: invoicing_accont_no
  data_type: string
  description: 开票开户行账号
  nullable: true
  cluster: invoicing
- name: invoicing_phone
  data_type: string
  description: 开票电话
  nullable: true
  cluster: invoicing
- name: invoicing_email
  data_type: string
  description: 开票电子邮箱
  nullable: true
  cluster: invoicing
- name: invoicing_address
  data_type: string
  description: 开票地址
  nullable: true
  cluster: invoicing
- name: invoicing_bank_name
  data_type: string
  description: 开票银行名称
  nullable: true
  cluster: invoicing
- name: invoicing_bank_code
  data_type: string
  description: 开票银行代码
  nullable: true
  cluster: invoicing
- name: invoicing_bank_province_city
  data_type: string
  description: 开票银行省市
  nullable: true
  cluster: invoicing
- name: invoicing_bank_branch
  data_type: string
  description: 开票银行支行
  nullable: true
  cluster: invoicing
- name: invoicing_bank_no
  data_type: string
  description: 开票银行联行号
  nullable: true
  cluster: invoicing
- name: apply_data_id
  data_type: number
  description: 认证流程数据id
  nullable: true
  cluster: workflow
- name: sign_mode
  data_type: string
  description: 产品协议签署方式
  nullable: true
  cluster: esign
- name: pc_task_id
  data_type: string
  description: 退回客户端补充资料taskId
  nullable: true
  cluster: workflow
- name: cust_status
  data_type: string
  description: 客户状态
  nullable: true
  cluster: classification
  dictionary: cust_company_info_cust_status
- name: back_reason
  data_type: string
  description: 退回原因
  nullable: true
  cluster: workflow
- name: apply_type
  data_type: string
  description: 流程类型
  nullable: true
  cluster: workflow
  dictionary: cust_company_info_apply_type
- name: cust_english_short_name
  data_type: string
  description: 企业简称英文
  nullable: true
  cluster: identity
- name: abroad_cust
  data_type: string
  description: 是否境外
  nullable: true
  cluster: classification
  dictionary: cust_company_info_abroad_cust
- name: outside_org
  data_type: string
  description: 外部机构
  nullable: true
  cluster: channel
  dictionary: cust_company_info_outside_org
- name: business_status
  data_type: string
  description: 经营状态
  nullable: true
  cluster: business
- name: relate_company_id
  data_type: string
  description: 归属企业id
  nullable: true
  cluster: group
- name: group_company
  data_type: string
  description: 是否归属集团或核心企业
  nullable: true
  cluster: group
  dictionary: cust_company_info_group_company
- name: regist_province_city_english
  data_type: string
  description: 注册省市(英文)
  nullable: true
  cluster: regist
- name: head_company
  data_type: string
  description: 是否总公司
  nullable: true
  cluster: group
  dictionary: cust_company_info_head_company
- name: platform_cust_id
  data_type: number
  description: 运营中台id
  nullable: true
  cluster: group
- name: legal_name_english
  data_type: string
  description: 法人姓名(英文)
  nullable: true
  cluster: legal
- name: manager_id
  data_type: string
  description: 业务经理
  nullable: true
  cluster: group
- name: legal_birth_date
  data_type: temporal
  description: 法人生日
  nullable: true
  cluster: legal
- name: ext
  data_type: string
  description: 扩展信息
  nullable: true
  cluster: misc
- name: legal_name_english_end
  data_type: string
  description: 法人名(英文)
  nullable: true
  cluster: legal
- name: regist_city_english
  data_type: string
  description: 市（英文）
  nullable: true
  cluster: regist
- name: legal_realname_status
  data_type: string
  description: 法人认证状态
  nullable: true
  cluster: legal
  dictionary: cust_company_info_legal_realname_status
- name: test_data
  data_type: string
  description: 是否测试数据
  nullable: true
  cluster: misc
  dictionary: cust_company_info_test_data
- name: company_ext_data
  data_type: structured
  description: ''
  nullable: true
  cluster: misc
- name: need_charge
  data_type: string
  description: 运营方是否涉及收费
  nullable: true
  cluster: esign
  dictionary: cust_company_info_need_charge
- name: finance_org_flag
  data_type: string
  description: 金融机构身份标识
  nullable: true
  cluster: finance
- name: nationality
  data_type: string
  description: ''
  nullable: true
  cluster: legal
- name: nationality_en
  data_type: string
  description: ''
  nullable: true
  cluster: legal
- name: check_status
  data_type: string
  description: ''
  nullable: true
  cluster: classification
  dictionary: cust_company_info_check_status
- name: relate_company_name
  data_type: string
  description: 归属集团或企业
  nullable: true
  cluster: group
- name: core_bosc_company_id
  data_type: string
  description: 关联核心企业（补充字段）
  nullable: true
  cluster: group
- name: composite_field
  data_type: string
  description: 工行供应链编号（补充字段）
  nullable: true
  cluster: contract
- name: cash_contract_no
  data_type: string
  description: 中原融资合同编号（补充字段）
  nullable: true
  cluster: contract
- name: xib_factor_contract_no
  data_type: string
  description: 厦银保理合同编号（补充字段）
  nullable: true
  cluster: contract
- name: zybank_cash_contract_amt
  data_type: string
  description: 中原融资合同金额（补充字段）
  nullable: true
  cluster: contract
- name: billing_type
  data_type: string
  description: 开票类型（补充字段）
  nullable: true
  cluster: invoicing
- name: lybank_cash_contract_no
  data_type: string
  description: 洛阳融资合同编号（补充字段）
  nullable: true
  cluster: contract
- name: company_size
  data_type: string
  description: 增值税纳税人类别（补充字段）
  nullable: true
  cluster: classification
- name: cust_first_submit_auth
  data_type: temporal
  description: 客户首次提交认证时间
  nullable: true
  cluster: classification
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  nullable: true
  cluster: channel
- name: cust_from
  data_type: string
  description: 客户来源
  nullable: true
  cluster: classification
- name: audit_back_flag
  data_type: string
  description: 审核退回标记
  nullable: true
  cluster: workflow
  dictionary: cust_company_info_audit_back_flag
- name: cert_no_flag
  data_type: string
  description: 执行查询统一信用证编码
  nullable: true
  cluster: misc
- name: cust_source
  data_type: string
  description: 建档数据来源
  nullable: true
  cluster: classification
  dictionary: cust_company_info_cust_source
- name: migarory_auth_aggrement_flag
  data_type: string
  description: 新旧渠道授权书补签标识，Y 新渠道:N 旧渠道
  nullable: true
  cluster: esign
  dictionary: cust_company_info_migarory_auth_aggrement_flag
- name: auth_aggrement_supplement_flag
  data_type: string
  description: 是否授权书补签标识
  nullable: true
  cluster: esign
  dictionary: cust_company_info_auth_aggrement_supplement_flag
- name: finance_org_type
  data_type: string
  description: 金融机构类型(补充字段)
  nullable: true
  cluster: finance
- name: finance_org_code
  data_type: string
  description: 金融机构编码(补充字段)
  nullable: true
  cluster: finance
- name: finance_org_type_name
  data_type: string
  description: ''
  nullable: true
  cluster: finance
- name: bank_branch
  data_type: string
  description: 银行分行名称（通用）(补充字段)
  nullable: true
  cluster: finance
- name: third_auth_status
  data_type: string
  description: 第三方认证状态
  nullable: true
  cluster: finance
- name: approval_date
  data_type: temporal
  description: 核准日期
  nullable: true
  cluster: workflow
- name: channel_code
  data_type: string
  description: 开放平台channelcode
  nullable: true
  cluster: channel
```
