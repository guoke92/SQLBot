---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
status: draft
anchors:
- cust_company_info
sources:
- database_schema:lowcode_pplatform.cust_company_info
- code_path:CustCompanyIfoEnchanceService.java:653
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- argeement_migratory_record
- authorization_agreement
- ca_certification_info
- ca_cfca_upgrade_report
- ca_fee_company
- ca_fee_order
- ca_fee_special_config
- cust_account_info
- cust_auth_application
- cust_auth_application_config
- cust_build_record
- cust_certification_info
- cust_change_record
- cust_company_lifecycle_info
- cust_company_survey_state
- cust_company_survey_whitelist
- cust_customized_product
- cust_group_rel
- cust_head_company_info
- cust_interworking_product
- cust_invite_info
- cust_oper_change_record
- cust_person_info
- cust_project_code_record
- cust_project_rel
- cust_role_info
- cust_shareholder_info
- cust_survey_answer
- cust_user_rel
- open_sso_channel
- cust_company_info__enable
- cust_company_info__legal_certification_type
- cust_company_info__need_register_bs
- cust_company_info__ca_register_status
- cust_company_info__bs_register_status
- cust_company_info__cust_build_type
- cust_company_info__cust_build_status
- cust_company_info__cust_status
- cust_company_info__apply_type
- cust_company_info__abroad_cust
- cust_company_info__group_company
- cust_company_info__head_company
- cust_company_info__legal_realname_status
- cust_company_info__test_data
- cust_company_info__need_charge
- cust_company_info__check_status
- cust_company_info__audit_back_flag
- cust_company_info__cert_no_flag
- cust_company_info__migarory_auth_aggrement_flag
- cust_company_info__auth_aggrement_supplement_flag
- cust_company_info__third_auth_status
- cust_company_info__cust_source
- cust_company_info__identify_style
---
# 客户信息主表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
inactive: false
primary_key:
- id
grain: 一企一行（code 唯一；列表有效集见 default_filter）
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
  dict:
  - Y
  - N
  label:
  - 启用
  - 停用
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
  dict:
  - CRET_ID
  - CERT_PASSPORT
  - CERT_RESIDENT_PERMIT
  - CERT_TAIWAN
  - CERT_MAINLAND_PASS
  - CERT_GREEN_CARD
  - 身份证
  - CRET_ID_HK
  - CREDENTIALS_ID
  - CERT_OTHER
  label:
    CRET_ID: 二代居民身份证
    CERT_PASSPORT: 护照
    CERT_RESIDENT_PERMIT: 港澳台居民居住证
    CERT_TAIWAN: 台胞证
    CERT_MAINLAND_PASS: 港澳居民来往内地通行证
    CERT_GREEN_CARD: 外国人永久居留证
    CRET_ID_HK: 香港身份证
    CERT_OTHER: 其他
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
  written_with:
  - ca_register_status
  - need_register_bs
  - bs_register_status
- name: need_register_bs
  type: string
  desc: 是否需要开通上上签电子签章
  dict:
  - N
  - Y
  - P
  label:
    N: 未开通/不需要
    Y: 需要开通
    P: 开通中
  written_with:
  - need_register_ca
  - ca_register_status
  - bs_register_status
- name: ca_register_status
  type: string
  desc: CA开通状态
  dict:
  - N
  - Y
  - P
  label:
  - 未开通
  - 已开通
  - 开通中
  written_with:
  - need_register_ca
  - need_register_bs
  - bs_register_status
- name: bs_register_status
  type: string
  desc: 上上签开通状态
  dict:
  - N
  - Y
  - P
  label:
  - 未开通
  - 已开通
  - 开通中
  written_with:
  - need_register_ca
  - ca_register_status
  - need_register_bs
- name: cust_build_type
  type: string
  desc: 录入方式
  dict:
  - AGW_BUILD
  - PC_BUILD
  - SIMPLE
  label:
    AGW_BUILD: 平台录入
    PC_BUILD: 客户录入
- name: cust_build_status
  type: string
  desc: 认证状态
  dict:
  - BUILD_SUCCESS
  - INIT
  - CUST_CONFIRM_AWAIT
  - BUILD_FAIL
  - CUST_BUILDING
  - CUST_CHANGE
  - AWAIT_CUST_CONFIRM
  - BUILD_ACTIVATE
  - BUILD_BACK
  - BUILDING
  - CUST_AUDIT_AWAIT
  - CUST_BUILD_SUCCESS
  - TO_BE_BUILD
  - CUST_BUILD_FAIL
  label:
  - 认证成功
  - 初始化
  - 待客户认证
  - 认证失败
  - 审核中
  - 变更
  - 待客户确认
  - 待激活
  - 退回
  - 建档中
  - 待审核
  - 审核通过
  - 未建档
  - 审核拒绝
  written_with:
  - cust_status
  - check_status
- name: identify_style
  type: string
  desc: 认证方式
  dict:
  - INVITE_AGW
  - INVITE
  - SIMPLE
  - SELF
  label:
  - 邀请认证-内管录入
  - 邀请认证-客户录入
  - 简易认证
  - 自主认证
- name: cust_scale
  type: string
  desc: 企业规模
- name: industry_involved
  type: string
  desc: 所属行业
- name: cust_profile
  type: string
  desc: 企业简介
- name: data_type
  type: string
  desc: 数据类型：1,主数据，0记录数据
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
- name: contact_city
  type: string
  desc: 联系市
- name: contact_city_code
  type: string
  desc: 联系城市代码
- name: contact_address
  type: string
  desc: 联系地址
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
- name: apply_data_id
  type: number
  desc: 认证流程数据id
- name: sign_mode
  type: string
  desc: 产品协议签署方式
  dict:
  - ONLINE
- name: pc_task_id
  type: string
  desc: 退回客户端补充资料taskId
- name: cust_status
  type: string
  desc: 客户状态
  dict:
  - EFFECT
  - ADD
  - CHANGE
  - WRITEOFF
  - FREEZE
  - FAILURE
  label:
  - 生效
  - 新增
  - 变更
  - 注销
  - 冻结
  - 失效
  written_with:
  - cust_build_status
  - check_status
- name: back_reason
  type: string
  desc: 退回原因
- name: apply_type
  type: string
  desc: 流程类型
  dict:
  - add
  - update
- name: cust_english_short_name
  type: string
  desc: 企业简称英文
- name: abroad_cust
  type: string
  desc: 是否境外
  dict:
  - Y
  - N
  label:
    Y: 是
    N: 否
- name: outside_org
  type: string
  desc: 外部机构
- name: business_status
  type: string
  desc: 经营状态
- name: relate_company_id
  type: string
  desc: 归属企业id
- name: group_company
  type: string
  desc: 是否归属集团或核心企业
  dict:
  - N
  - Y
  - '1'
  label:
    N: 否
    Y: 是
    '1': 否（脏数据）
- name: regist_province_city_english
  type: string
  desc: 注册省市(英文)
- name: head_company
  type: string
  desc: 是否总公司
  dict:
  - Y
  - N
  label:
    Y: 是
    N: 否
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
  dict:
  - N
  - Y
- name: test_data
  type: string
  desc: 是否测试数据
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
- name: company_ext_data
  type: structured
- name: need_charge
  type: string
  desc: 运营方是否涉及收费
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
- name: finance_org_flag
  type: string
  desc: 金融机构身份标识
- name: nationality
  type: string
- name: nationality_en
  type: string
- name: check_status
  type: string
  dict:
  - CUST_CHECK_PASS
  - CUST_CHECK_BACKTOCUSTOM
  - CUST_CHECK_REJECT
  - CUST_CHECK_CHECKING
  - CUST_CHECK_INIT
  - EFFECT
  - CUST_BACK
  label:
    CUST_CHECK_PASS: 审核通过
    CUST_CHECK_BACKTOCUSTOM: 待客户确认
    CUST_CHECK_REJECT: 审核不通过
    CUST_CHECK_CHECKING: 审核中
    CUST_CHECK_INIT: 待审核
    CUST_BACK: 退回
  written_with:
  - cust_build_status
  - cust_status
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
  dict:
  - N
  - Y
  label:
  - 否
  - 是
- name: cert_no_flag
  type: string
  desc: 执行查询统一信用证编码
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: cust_source
  type: string
  desc: 建档数据来源
  dict:
  - PPLATFORM
  - MIGRATORY
  - PLATFORM_PUSH
  - PLATFORM
- name: migarory_auth_aggrement_flag
  type: string
  desc: 新旧渠道授权书补签标识，Y 新渠道:N 旧渠道
  dict:
  - Y
  - N
  label:
  - 新渠道
  - 新渠道
- name: auth_aggrement_supplement_flag
  type: string
  desc: 是否授权书补签标识
  dict:
  - N
  - Y
  label:
  - 否
  - 是
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
  dict:
  - '1'
- name: approval_date
  type: temporal
  desc: 核准日期
- name: channel_code
  type: string
  desc: 开放平台channelcode
default_filter:
  predicate: cust_company_info.enable = 'Y' AND cust_company_info.data_type = '1'
  trust: confirmed
  evidence: code_path:CustCompanyIfoEnchanceService.java:653
```

## 关联关系

_（本页暂无保留的 EQUI_JOIN 边；已移除边见 `_raw/join_validation/removed_relations.md`。）_

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: argeement_migratory_record.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:PlatFormMigratoryApplication.java:629
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: authorization_agreement.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:AuthorizationAgreementDaoImpl.java:43
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: ca_certification_info.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CaCertificationInfoAppServiceImpl.java:151
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: ca_cfca_upgrade_report.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:CFCA 升级上报企业
source: reextract_joins
join_role: identity
priority: primary
authenticity_note: CFCA 升级上报企业
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_cfca_upgrade_report.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: 'live_validate:fk_like;collide_refine:promoted: ca_cfca_upgrade_report.certification_no
  ⊆ cust_company_info.certification_no'
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 'promoted: ca_cfca_upgrade_report.certification_no ⊆ cust_company_info.certification_no'
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_company.certification_no
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CaFeeCompanyCaStatusSupport.java:85
source: l1_code
join_role: identity
priority: primary
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: ca_fee_order.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CaFeeBocomGateway.java:118
source: l1_code
join_role: identity
priority: primary
authenticity_note: company_id 是企业主键，不是 ca_fee_company.id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_order.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: 'live_validate:fk_like;collide_refine:promoted: ca_fee_order.certification_no
  ⊆ cust_company_info.certification_no'
source: collide_refine
join_role: business_code
priority: primary
authenticity_note: 'promoted: ca_fee_order.certification_no ⊆ cust_company_info.certification_no'
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_account_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperCustFacade.java:3062
source: l1_code
join_role: identity
priority: primary
authenticity_note: 银行账户按企业 code 关联，不是 id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_auth_application.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustAuthApplicationDaoImpl.java:73
source: l1_code
join_role: identity
priority: primary
authenticity_note: 产品开通按企业 code 关联，不是 id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_build_record.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperCustFacade.java:4288
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业ID
overlap:
  probed: true
  ratio: 0.9699
  ratio_reverse: 0.58
  sample_size: 598
  miss: 18
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: 建档推送记录的 cust_id 是企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_certification_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCertificationInfoDao.java:16
source: l1_code
join_role: identity
priority: primary
authenticity_note: 证照按企业 code 关联。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_change_record.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperCustFacade.java:1417
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 客户记录id
overlap:
  probed: true
  ratio: 0.9683
  ratio_reverse: 0.315
  sample_size: 284
  miss: 9
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: 变更记录 cust_id 是企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_lifecycle_info.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyInfoApplication.java:7082
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9143
  ratio_reverse: 0.0
  sample_size: 35
  miss: 3
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: 冻结/解冻留痕按企业主键。预生成行 enable=N，确认后改 Y。ref_cust_company_info 本路径未使用。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_survey_state.company_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanySurveyStateDao.java:18
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业ID
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 问卷星活动状态按企业主键，一企一行。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_company_survey_whitelist.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanySurveyWhitelistDao.java:19
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 11
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 问卷星白名单按企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_customized_product.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCustomizedProductDaoImpl.java:25
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 15
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 定制产品按企业主键 cust_id，不是 ref_cust_customized_product_cust_company_info。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_group_rel.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:109
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 200
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 集团关系 cust_id 是企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_head_company_info.ref_cust_head_company_info_cust_company_info
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CustDocFacade.java:952
source: l1_code
join_role: identity
priority: primary
authenticity_note: 总公司资料按企业 code 关联，不是 id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_interworking_product.cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustInterworkingProductDaoImpl.java:74
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_hub
  stem: cust
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9948
  sample_size: 194
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 企业互通产品按 cust_id=企业主键查询（与 ref_* 存 code 的双轨并存）。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_interworking_product.ref_cust_interworking_product_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustInterworkingProductDaoImpl.java:47
source: l1_code
join_role: identity
priority: primary
authenticity_note: 互通产品按企业 code 关联。listCustAllProduct 先 getById 再取 code；不要把 cust_id
  当成这条查询的 JOIN。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_invite_info.invite_cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyIfoEnchanceService.java:1587
source: l1_code
join_role: identity
priority: primary
authenticity_note: 邀请方企业主键。progress 回写按被邀请企业 name+db_tenant_code 匹配，不是这条 JOIN。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_oper_change_record.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperChangeRecordHelper.java:87
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业ID
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 运营人员变更留痕写入企业主键。列表查询按 person_id，company_code 只是冗余拷贝。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_oper_change_record.company_code
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:OperChangeRecordHelper.java:83
source: l1_code
join_role: business_code
priority: secondary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业编号
overlap:
  probed: true
  ratio: 1.0
  sample_size: 97
  miss: 0
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 写变更记录时同时落 companyId 与 companyCode（双轨）。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_person_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyInfoApplication.java:1553
source: l1_code
join_role: identity
priority: primary
authenticity_note: 人员主引用是企业 code。L0 把 id 接到 ref 列是假边。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.cust_company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustPersonApplication.java:740
source: l1_code
join_role: identity
priority: secondary
name_evidence:
  match: stem_info
  stem: cust_company
  comment: 冗余企业id
overlap:
  probed: true
  ratio: 0.9939
  sample_size: 165
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 冗余企业 id，查询里与 code 引用并存，不是 ref_cust_company_info。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_project_code_record.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustProjectRelEnhanceService.java:407
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 0.9278
  ratio_reverse: 0.0
  sample_size: 263
  miss: 19
  deepened: true
  query_ok: true
  authenticity: unknown
authenticity_note: 项目码输入记录按企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_project_rel.ref_cust_project_rel_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:97
source: l1_code
join_role: identity
priority: primary
authenticity_note: 代码按企业 code 关联项目，不是 cust_company_info.id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_role_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyQueryMapper.xml:80
source: l1_code
join_role: identity
priority: primary
authenticity_note: listEffectCompanyByCustType 以 code 连接角色表。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_shareholder_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:ApplyCompanyInfoApplication.java:190
source: l1_code
join_role: identity
priority: primary
authenticity_note: 股东按企业 code 复制/查询，不是 id。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_survey_answer.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustSurveyAnswerDao.java:18
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 当前登录企业ID
overlap:
  probed: true
  ratio: 0.95
  ratio_reverse: 0.0
  sample_size: 60
  miss: 3
  deepened: true
  query_ok: true
  authenticity: likely
authenticity_note: 调研答案按登录企业主键。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_user_rel.company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyIfoEnchanceService.java:566
source: l1_code
join_role: identity
priority: primary
name_evidence:
  match: family_suffix
  stem: company
  comment: 企业id
overlap:
  probed: true
  ratio: 1.0
  sample_size: 1
  miss: 0
  deepened: false
  query_ok: true
  authenticity: unknown
authenticity_note: 用户企业角色按企业主键。现网几乎无行；不要当成 sys 侧用户关系。
```
```ground:relation
type: EQUI_JOIN
left: open_sso_channel.channel_code
right: cust_company_info.channel_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: full_sweep:same_semantic UAT company.channel_code empty
source: full_sweep
join_role: business_code
priority: secondary
authenticity_note: same_semantic:sso
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application.main_data_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: identity
priority: primary
authenticity_note: code+live
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_auth_application.ref_parent_company
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: business_code
priority: primary
authenticity_note: code:write-flow parent company
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_customized_product.ref_cust_customized_product_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: full_sweep:code_ref UAT empty child
source: full_sweep
join_role: business_code
priority: secondary
authenticity_note: code:ref-convention
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_group_rel.parent_cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: identity
priority: primary
authenticity_note: code+live
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_group_rel.root_cust_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: full_sweep:live_fk_like
source: full_sweep
join_role: identity
priority: primary
authenticity_note: code+live
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.certification_no
right: ca_fee_special_config.certification_no
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: orphan_repair:live R→L=0.93 certification hub
source: orphan_repair
join_role: business_code
priority: primary
authenticity_note: 统码 hub
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_auth_application_config.cust_id
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: orphan_repair:affiliate UAT empty
source: orphan_repair
join_role: identity
priority: secondary
authenticity_note: config.cust_id
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_company_lifecycle_info.ref_cust_company_info
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: orphan_repair:ref_convention UAT ref empty; company_id already linked
source: orphan_repair
join_role: business_code
priority: secondary
authenticity_note: ref_* 并行 company_id
```

## 页面链接

### 关联表

- [[tables/argeement_migratory_record]]
- [[tables/authorization_agreement]]
- [[tables/ca_certification_info]]
- [[tables/ca_cfca_upgrade_report]]
- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/ca_fee_special_config]]
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
- [[tables/cust_invite_info]]
- [[tables/cust_oper_change_record]]
- [[tables/cust_person_info]]
- [[tables/cust_project_code_record]]
- [[tables/cust_project_rel]]
- [[tables/cust_role_info]]
- [[tables/cust_shareholder_info]]
- [[tables/cust_survey_answer]]
- [[tables/cust_user_rel]]
- [[tables/open_sso_channel]]

### 概念

- [[concepts/agw_build]]
- [[concepts/auth_channel_flag]]
- [[concepts/auth_supplement_flag]]
- [[concepts/bank_branch_name]]
- [[concepts/build_success_not_effect]]
- [[concepts/certification_no_term]]
- [[concepts/change_identify_style]]
- [[concepts/channel_archive_longteng]]
- [[concepts/channel_code_homonym_bundle]]
- [[concepts/company_id_vs_code]]
- [[concepts/core_company]]
- [[concepts/effective_company_term]]
- [[concepts/finance_org_type_term]]
- [[concepts/invite_customer_entry]]
- [[concepts/invite_platform_entry]]
- [[concepts/invite_progress_copy]]
- [[concepts/pc_build]]
- [[concepts/reauth_reset]]
- [[concepts/self_auth]]
- [[concepts/simple_auth]]
- [[concepts/simple_auth_ca_history]]
- [[concepts/visitor_flow_data]]

### 字典

- [[dicts/cust_company_info__enable]]（`cust_company_info.enable`）
- [[dicts/cust_company_info__legal_certification_type]]（`cust_company_info.legal_certification_type`）
- [[dicts/cust_company_info__need_register_bs]]（`cust_company_info.need_register_bs`）
- [[dicts/cust_company_info__ca_register_status]]（`cust_company_info.ca_register_status`）
- [[dicts/cust_company_info__bs_register_status]]（`cust_company_info.bs_register_status`）
- [[dicts/cust_company_info__cust_build_type]]（`cust_company_info.cust_build_type`）
- [[dicts/cust_company_info__cust_build_status]]（`cust_company_info.cust_build_status`）
- [[dicts/cust_company_info__identify_style]]（`cust_company_info.identify_style`）
- [[dicts/cust_company_info__sign_mode]]（`cust_company_info.sign_mode`）
- [[dicts/cust_company_info__cust_status]]（`cust_company_info.cust_status`）
- [[dicts/cust_company_info__apply_type]]（`cust_company_info.apply_type`）
- [[dicts/cust_company_info__abroad_cust]]（`cust_company_info.abroad_cust`）
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
