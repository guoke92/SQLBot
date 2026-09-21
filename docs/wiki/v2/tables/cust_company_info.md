---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
status: draft
anchors: [cust_company_info]
sources: ['database_schema:lowcode_pplatform.cust_company_info']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_account_info, cust_auth_application, cust_auth_application_config,
  cust_build_record, cust_certification_info, cust_change_record, cust_company_lifecycle_info,
  cust_company_survey_state, cust_company_survey_whitelist, cust_customized_product,
  cust_group_rel, cust_head_company_info, cust_interworking_product, cust_oper_change_record,
  cust_person_info, cust_project_code_record, cust_project_rel, cust_role_info, cust_setting_config,
  cust_shareholder_info, cust_survey_answer, cust_user_rel, cust_company_info__enable,
  cust_company_info__legal_certification_type, cust_company_info__need_register_ca,
  cust_company_info__need_register_bs, cust_company_info__ca_register_status, cust_company_info__bs_register_status,
  cust_company_info__cust_build_type, cust_company_info__cust_build_status, cust_company_info__identify_style,
  cust_company_info__cust_scale, cust_company_info__data_type, cust_company_info__contact_province_code,
  cust_company_info__contact_city_code, cust_company_info__contact_address, cust_company_info__signing_mode,
  cust_company_info__invoicing_bank_no, cust_company_info__sign_mode, cust_company_info__pc_task_id,
  cust_company_info__cust_status, cust_company_info__apply_type, cust_company_info__abroad_cust,
  cust_company_info__outside_org, cust_company_info__group_company, cust_company_info__head_company,
  cust_company_info__legal_realname_status, cust_company_info__test_data, cust_company_info__need_charge,
  cust_company_info__check_status, cust_company_info__audit_back_flag, cust_company_info__cert_no_flag,
  cust_company_info__cust_source, cust_company_info__migarory_auth_aggrement_flag,
  cust_company_info__auth_aggrement_supplement_flag, cust_company_info__third_auth_status,
  cust_company_info__channel_code]
---

# 客户信息主表

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_short_name, cust_english_name, cust_former_name, legal_name,
  business_province_code, business_city_code, regist_province_code, regist_city_code,
  contact_province_code, contact_city_code, contact_user_name, invoicing_name, invoicing_bank_name,
  invoicing_bank_code, cust_english_short_name, relate_company_name, finance_org_code,
  finance_org_type_name, channel_code]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 客户名称
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
- name: remark
  type: string
  desc: remark
- name: create_by
  type: string
  desc: 创建人id
- name: create_user
  type: string
  desc: 创建人名称
- name: create_time
  type: temporal
  desc: 创建时间
  nullable: false
- name: update_by
  type: string
  desc: 更新人id
- name: update_user
  type: string
  desc: 更新人名称
- name: update_time
  type: temporal
  desc: 更新时间
  nullable: false
- name: act_procinst_id
  type: string
  desc: 流程实例ID
- name: app_tenant_code
  type: string
  desc: 逻辑租户标识
- name: db_tenant_code
  type: string
  desc: 数据租户标识
- name: act_procinst_no
  type: string
  desc: 流程申请编号
- name: act_procinst_status
  type: string
  desc: 当前审批状态
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: cust_no
  type: string
  desc: 客户编号
- name: cust_short_name
  type: string
  desc: 企业简称
- name: cust_english_name
  type: string
  desc: 客户英文名称
- name: cust_company_type
  type: string
  desc: 企业角色
- name: biz_cust_type
  type: string
  desc: 工商类别
- name: cust_former_name
  type: string
  desc: 曾用名
- name: certification_no
  type: string
  desc: 统一信用代码
- name: establishment_time
  type: temporal
  desc: 成立日期
- name: register_capital
  type: number
  desc: 注册资本
- name: time_permanent
  type: string
  desc: 营业执照有效期
- name: business_license_start_time
  type: temporal
  desc: 企业营业执照开始时间
- name: business_license_end_time
  type: temporal
  desc: 企业营业执照结束时间
- name: legal_name
  type: string
  desc: 法人姓名
- name: legal_phone
  type: string
  desc: 法人手机号码
- name: legal_certification_no
  type: string
  desc: 法人证件号
- name: legal_certification_type
  type: string
  desc: 法人证件类型
  dict: [CRET_ID, CERT_PASSPORT, CERT_RESIDENT_PERMIT, CERT_TAIWAN, CERT_MAINLAND_PASS,
    CERT_GREEN_CARD, 身份证, CRET_ID_HK, CREDENTIALS_ID, CERT_OTHER]
- name: legal_email
  type: string
  desc: 法人邮箱
- name: legal_certification_start_time
  type: temporal
  desc: 法人证件开始日期
- name: legal_certification_end_time
  type: temporal
  desc: 法人证件结束日期
- name: legal_time_permanent
  type: string
  desc: 身份证有效期标志
- name: need_register_ca
  type: string
  desc: 开通电子签章
  dict: [Y, N]
- name: need_register_bs
  type: string
  desc: 是否需要开通上上签电子签章
  dict: [N, Y]
- name: ca_register_status
  type: string
  desc: CA开通状态
  dict: [N, Y, P]
- name: bs_register_status
  type: string
  desc: 上上签开通状态
  dict: [N, Y]
- name: cust_build_type
  type: string
  desc: 录入方式
  dict: [AGW_BUILD, PC_BUILD, SIMPLE]
- name: cust_build_status
  type: string
  desc: 认证状态
  dict: [BUILD_SUCCESS, INIT, CUST_CONFIRM_AWAIT, BUILD_FAIL, CUST_BUILDING, CUST_CHANGE,
    AWAIT_CUST_CONFIRM, BUILD_ACTIVATE, BUILD_BACK, BUILDING, CUST_AUDIT_AWAIT, CUST_BUILD_SUCCESS]
- name: identify_style
  type: string
  desc: 认证方式
  dict: [INVITE_AGW, INVITE, SIMPLE, SELF]
- name: cust_scale
  type: string
  desc: 企业规模
  dict: [qw]
- name: industry_involved
  type: string
  desc: 所属行业
- name: cust_profile
  type: string
  desc: 企业简介
- name: data_type
  type: string
  desc: 数据类型：1,主数据，0记录数据
  dict: ['1', '0', '2']
  label: {'1': 主数据}
- name: main_data_id
  type: number
  desc: 主数据id
- name: business_province
  type: string
  desc: 经营省份
- name: paid_in_capital
  type: string
  desc: 实缴资本（元）
- name: workers_no
  type: string
  desc: 员工
- name: business_province_code
  type: string
  desc: 经营省份代码
- name: business_city
  type: string
  desc: 经营市
- name: business_city_code
  type: string
  desc: 经营城市代码
- name: business_address
  type: string
  desc: 经营地址
- name: regist_province
  type: string
  desc: 注册省份
- name: regist_province_code
  type: string
  desc: 注册省份代码
- name: regist_city
  type: string
  desc: 注册市
- name: regist_city_code
  type: string
  desc: 注册城市代码
- name: registered_address
  type: string
  desc: 注册地址
- name: contact_province
  type: string
  desc: 联系省份
- name: contact_province_code
  type: string
  desc: 联系省份代码
  dict: ['820000', '650000']
- name: contact_city
  type: string
  desc: 联系市
- name: contact_city_code
  type: string
  desc: 联系城市代码
  dict: ['820000', '650200']
- name: contact_address
  type: string
  desc: 联系地址
  dict: [qdqw]
- name: contact_user_name
  type: string
  desc: 联系人
- name: contact_tel
  type: string
  desc: 联系电话
- name: cust_email
  type: string
  desc: 公司联系邮箱
- name: business_scope
  type: string
  desc: 经营范围
- name: client_type
  type: string
  desc: 发起变更的客户端类型
- name: signing_mode
  type: string
  desc: 签署模式
  dict: ['01']
- name: contact_province_city
  type: string
  desc: 联系省市
- name: business_province_city
  type: string
  desc: 经营省市
- name: regist_province_city
  type: string
  desc: 注册省市
- name: invoicing_taxpayer_no
  type: string
  desc: 开票纳税人识别号
- name: invoicing_name
  type: string
  desc: 开票名称
- name: invoicing_accont_no
  type: string
  desc: 开票开户行账号
- name: invoicing_phone
  type: string
  desc: 开票电话
- name: invoicing_email
  type: string
  desc: 开票电子邮箱
- name: invoicing_address
  type: string
  desc: 开票地址
- name: invoicing_bank_name
  type: string
  desc: 开票银行名称
- name: invoicing_bank_code
  type: string
  desc: 开票银行代码
- name: invoicing_bank_province_city
  type: string
  desc: 开票银行省市
- name: invoicing_bank_branch
  type: string
  desc: 开票银行支行
- name: invoicing_bank_no
  type: string
  desc: 开票银行联行号
  dict: ['{}', '103304362223', '103224031227', '103304362024']
- name: apply_data_id
  type: number
  desc: 认证流程数据id
- name: sign_mode
  type: string
  desc: 产品协议签署方式
  dict: [ONLINE]
- name: pc_task_id
  type: string
  desc: 退回客户端补充资料taskId
  dict: ['230053', '135035', '130005', '305002', '305029', '210056', '225065', '110022',
    '230006', '280006', '140030', '225030', '245027', '285005']
- name: cust_status
  type: string
  desc: 客户状态
  dict: [EFFECT, ADD, CHANGE, WRITEOFF, FREEZE]
- name: back_reason
  type: string
  desc: 退回原因
- name: apply_type
  type: string
  desc: 流程类型
  dict: [add, update]
- name: cust_english_short_name
  type: string
  desc: 企业简称英文
- name: abroad_cust
  type: string
  desc: 是否境外
  dict: [Y, N]
- name: outside_org
  type: string
  desc: 外部机构
  dict: [N, Y, '0', '1']
- name: business_status
  type: string
  desc: 经营状态
- name: relate_company_id
  type: string
  desc: 归属企业id
- name: group_company
  type: string
  desc: 是否归属集团或核心企业
  dict: [N, Y, '1']
- name: regist_province_city_english
  type: string
  desc: 注册省市(英文)
- name: head_company
  type: string
  desc: 是否总公司
  dict: [Y, N]
- name: platform_cust_id
  type: number
  desc: 运营中台id
- name: legal_name_english
  type: string
  desc: 法人姓名(英文)
- name: manager_id
  type: string
  desc: 业务经理
- name: legal_birth_date
  type: temporal
  desc: 法人生日
- name: ext
  type: string
  desc: 扩展信息
- name: legal_name_english_end
  type: string
  desc: 法人名(英文)
- name: regist_city_english
  type: string
  desc: 市（英文）
- name: legal_realname_status
  type: string
  desc: 法人认证状态
  dict: [N, Y]
- name: test_data
  type: string
  desc: 是否测试数据
  dict: [N, Y]
- name: company_ext_data
  type: structured
- name: need_charge
  type: string
  desc: 运营方是否涉及收费
  dict: [N, Y]
- name: finance_org_flag
  type: string
  desc: 金融机构身份标识
- name: nationality
  type: string
- name: nationality_en
  type: string
- name: check_status
  type: string
  dict: [CUST_CHECK_PASS, CUST_CHECK_BACKTOCUSTOM, CUST_CHECK_REJECT, CUST_CHECK_CHECKING,
    CUST_CHECK_INIT, EFFECT]
- name: relate_company_name
  type: string
  desc: 归属集团或企业
- name: core_bosc_company_id
  type: string
  desc: 关联核心企业（补充字段）
- name: composite_field
  type: string
  desc: 工行供应链编号（补充字段）
- name: cash_contract_no
  type: string
  desc: 中原融资合同编号（补充字段）
- name: xib_factor_contract_no
  type: string
  desc: 厦银保理合同编号（补充字段）
- name: zybank_cash_contract_amt
  type: string
  desc: 中原融资合同金额（补充字段）
- name: billing_type
  type: string
  desc: 开票类型（补充字段）
- name: lybank_cash_contract_no
  type: string
  desc: 洛阳融资合同编号（补充字段）
- name: company_size
  type: string
  desc: 增值税纳税人类别（补充字段）
- name: cust_first_submit_auth
  type: temporal
  desc: 客户首次提交认证时间
- name: tenant_flg_en
  type: string
  desc: 项目标识（英文）
- name: cust_from
  type: string
  desc: 客户来源
- name: audit_back_flag
  type: string
  desc: 审核退回标记
  dict: [N, Y]
- name: cert_no_flag
  type: string
  desc: 执行查询统一信用证编码
  dict: [Y]
- name: cust_source
  type: string
  desc: 建档数据来源
  dict: [PPLATFORM, MIGRATORY, PLATFORM_PUSH, PLATFORM]
- name: migarory_auth_aggrement_flag
  type: string
  desc: 新旧渠道授权书补签标识，Y 新渠道:N 旧渠道
  dict: [Y, N]
  label: [新渠道, 新渠道]
- name: auth_aggrement_supplement_flag
  type: string
  desc: 是否授权书补签标识
  dict: [N, Y]
- name: finance_org_type
  type: string
  desc: 金融机构类型(补充字段)
- name: finance_org_code
  type: string
  desc: 金融机构编码(补充字段)
- name: finance_org_type_name
  type: string
- name: bank_branch
  type: string
  desc: 银行分行名称（通用）(补充字段)
- name: third_auth_status
  type: string
  desc: 第三方认证状态
  dict: ['1']
- name: approval_date
  type: temporal
  desc: 核准日期
- name: channel_code
  type: string
  desc: 开放平台channelcode
  dict: [longteng, jingke]
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
preview_block: overlap_unsemantic
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
- [[dicts/cust_company_info__legal_certification_type]]（`cust_company_info.legal_certification_type`）
- [[dicts/cust_company_info__need_register_ca]]（`cust_company_info.need_register_ca`）
- [[dicts/cust_company_info__need_register_bs]]（`cust_company_info.need_register_bs`）
- [[dicts/cust_company_info__ca_register_status]]（`cust_company_info.ca_register_status`）
- [[dicts/cust_company_info__bs_register_status]]（`cust_company_info.bs_register_status`）
- [[dicts/cust_company_info__cust_build_type]]（`cust_company_info.cust_build_type`）
- [[dicts/cust_company_info__cust_build_status]]（`cust_company_info.cust_build_status`）
- [[dicts/cust_company_info__identify_style]]（`cust_company_info.identify_style`）
- [[dicts/cust_company_info__cust_scale]]（`cust_company_info.cust_scale`）
- [[dicts/cust_company_info__data_type]]（`cust_company_info.data_type`）
- [[dicts/cust_company_info__contact_province_code]]（`cust_company_info.contact_province_code`）
- [[dicts/cust_company_info__contact_city_code]]（`cust_company_info.contact_city_code`）
- [[dicts/cust_company_info__contact_address]]（`cust_company_info.contact_address`）
- [[dicts/cust_company_info__signing_mode]]（`cust_company_info.signing_mode`）
- [[dicts/cust_company_info__invoicing_bank_no]]（`cust_company_info.invoicing_bank_no`）
- [[dicts/cust_company_info__sign_mode]]（`cust_company_info.sign_mode`）
- [[dicts/cust_company_info__pc_task_id]]（`cust_company_info.pc_task_id`）
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
