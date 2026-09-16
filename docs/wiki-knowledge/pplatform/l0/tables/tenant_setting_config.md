---
type: table
title: 租户配置
page_key: tenant_setting_config
belong: tables
status: draft
aliases: []
anchors:
- tenant_setting_config
sources:
- database_schema:lowcode_pplatform.tenant_setting_config
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 租户配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant_identity

`source_id`, `source`, `name`, `apaas_tenant_code`, `uni_social_credit_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `tenant_flag_zh`, `tenant_flg_en`, `default_project_id`, `main_tenant_flg_en`

### brand_theme

`band_name`, `cust_service_number`, `web_title`, `web_logo_url`, `pc_login_logo_path`, `pc_icon_path`, `pc_logo_path`, `pc_home_background_path`, `mp_home_background_path`, `mp_logo_path`, `pcimg_loginpage_bg_logo_url`, `pcimg_indexpage_bg_logo_url`, `pcimg_browser_tab_icon_url`, `pcimg_loginpage_banner_url`, `mobile_indexpage_bg_logo_url`, `main_theme_color`, `mobile_indexpage_logo_url`, `bg_color`, `ai_resource_color`, `adapt_colour`, `use_theme_after_login`

### domain_env

`dev_domain`, `sit_domain`, `uat_domain`, `prd_domain`, `hfive_dev_domain`, `hfive_test_domain`, `hfive_uat_domain`, `hfive_prd_domain`

### agreement_auth

`privacy_policy_agreement`, `user_protocol_agreement`, `auth_agreement`, `person_auth_agreement`, `recall_auth_doc_flag`, `sign_flag`, `oper_auth_agreement`, `generate_electronic_auth_flag`

### platform_integration

`dbass_app_id`, `mp_dbass_app_id`, `dbass_private_key`, `sso_sys_channel`, `sso_tenant_chanel`, `mp_sso_tenant_chanel`, `mp_sso_sys_channel`, `platform_operator`, `platform_secret_key`, `platform_sms_signature`

### mp_wx_account

`uat_mp_app_id`, `uat_mp_app_name`, `uat_mp_wx_login_name`, `uat_mp_wx_login_pwd`, `prd_mp_app_id`, `prd_mp_app_name`, `prd_mp_wx_login_name`, `prd_mp_wx_login_pwd`

### tenant_switch

`need_hfive`, `need_mp_wx`, `status`, `self_registration_flag`, `company_share_flag`, `portal_flag`, `share_flag`, `pushing_status`, `is_stack`, `migratory_flag`, `project_code_required`, `access_mode`

### approval_flow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### ops_service

`operator_id`, `operator_name`, `operator_email`, `send_email`, `operator_ai_customer`, `operator_wechat_code`, `operator_qr_code`, `operator_applet_code`, `ai_zc_sysnum`, `ai_zc_channel`, `customer_card_type`, `op_update_user`, `op_update_time`

### ext_field_required

`core_bosc_company_id_property_requried`, `xib_factor_contract_no_property_requried`, `company_size_property_requried`, `billing_type_property_requried`, `cash_contract_no_property_requried`, `zybank_cash_contract_amt_property_requried`, `lybank_cash_contract_no_property_requried`, `composite_field_property_requried`, `finance_org_type_property_requried`, `bank_branch_property_requried`

### ext_field_company_role

`composite_field_property_requried_config_company_role`, `composite_field_property_requried_company_role`, `core_bosc_company_id_property_requried_config_cust_role`, `xib_factor_contract_no_property_requried_config_cust_role`, `company_size_property_requried_config_cust_role`, `billing_type_property_requried_config_cust_role`, `cash_contract_no_property_requried_config_cust_role`, `zybank_cash_contract_amt_property_requried_config_cust_role`, `lybank_cash_contract_no_property_requried_config_cust_role`, `composite_field_property_requried_config_cust_role`, `finance_org_type_property_requried_config_cust_role`, `bank_branch`, `bank_branch_property_requried_config_cust_role`

## 字段

```ground:table
table: tenant_setting_config
database: lowcode_pplatform
description: 租户配置
inactive: false
primary_key:
- id
grain: 一行一记录（id）
name_anchors:
- code
- name
- band_name
- apaas_tenant_code
- uni_social_credit_code
- uat_mp_app_name
- uat_mp_wx_login_name
- prd_mp_app_name
- prd_mp_wx_login_name
- operator_name
- operator_wechat_code
- operator_qr_code
- operator_applet_code
clusters:
- key: common
  title: 通用与审计
  include: always
- key: tenant_identity
  title: 租户主档与标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: brand_theme
  title: 品牌展示与主题配色
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: domain_env
  title: 各环境域名
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: agreement_auth
  title: 协议与授权书
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: platform_integration
  title: 外部平台与单点登录集成
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: mp_wx_account
  title: 小程序与公众号账号
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: tenant_switch
  title: 功能开关与策略
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: approval_flow
  title: 审批流程
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: ops_service
  title: 运营与客服
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: ext_field_required
  title: 补充字段-是否必填
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: ext_field_company_role
  title: 补充字段-企业角色配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
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
- name: source_id
  data_type: string
  description: 租户来源id
  nullable: true
  cluster: tenant_identity
- name: source
  data_type: string
  description: 租户来源
  nullable: true
  cluster: tenant_identity
- name: name
  data_type: string
  description: 租户名称
  nullable: true
  cluster: tenant_identity
- name: band_name
  data_type: string
  description: 贴牌平台名称
  nullable: true
  cluster: brand_theme
- name: cust_service_number
  data_type: string
  description: 客服电话
  nullable: true
  cluster: brand_theme
- name: web_title
  data_type: string
  description: 网站标题
  nullable: true
  cluster: brand_theme
- name: web_logo_url
  data_type: string
  description: 网站logo
  nullable: true
  cluster: brand_theme
- name: dev_domain
  data_type: string
  description: 开发环境域名
  nullable: true
  cluster: domain_env
- name: sit_domain
  data_type: string
  description: 测试环境域名
  nullable: true
  cluster: domain_env
- name: uat_domain
  data_type: string
  description: UAT环境域名
  nullable: true
  cluster: domain_env
- name: prd_domain
  data_type: string
  description: 生产环境域名
  nullable: true
  cluster: domain_env
- name: privacy_policy_agreement
  data_type: string
  description: 隐私协议
  nullable: true
  cluster: agreement_auth
- name: user_protocol_agreement
  data_type: string
  description: 用户协议
  nullable: true
  cluster: agreement_auth
- name: auth_agreement
  data_type: string
  description: 授权书协议
  nullable: true
  cluster: agreement_auth
- name: apaas_tenant_code
  data_type: string
  description: aPaaS租户编码
  nullable: true
  cluster: tenant_identity
- name: dbass_app_id
  data_type: string
  description: dbassAppId
  nullable: true
  cluster: platform_integration
- name: mp_dbass_app_id
  data_type: string
  description: 小程序dbassAppId
  nullable: true
  cluster: platform_integration
- name: dbass_private_key
  data_type: string
  description: dbassPrivateKey
  nullable: true
  cluster: platform_integration
- name: sso_sys_channel
  data_type: string
  description: ssoSysChannel
  nullable: true
  cluster: platform_integration
- name: sso_tenant_chanel
  data_type: string
  description: ssoTenantChanel
  nullable: true
  cluster: platform_integration
- name: mp_sso_tenant_chanel
  data_type: string
  description: mpSsoTenantChanel
  nullable: true
  cluster: platform_integration
- name: pc_login_logo_path
  data_type: string
  description: PC登录窗口横幅
  nullable: true
  cluster: brand_theme
- name: pc_icon_path
  data_type: string
  description: PC浏览器页签Icon
  nullable: true
  cluster: brand_theme
- name: pc_logo_path
  data_type: string
  description: PC内页logo
  nullable: true
  cluster: brand_theme
- name: pc_home_background_path
  data_type: string
  description: PC首页背景图
  nullable: true
  cluster: brand_theme
- name: mp_home_background_path
  data_type: string
  description: 小程序首页背景图
  nullable: true
  cluster: brand_theme
- name: mp_logo_path
  data_type: string
  description: 移动端首页logo
  nullable: true
  cluster: brand_theme
- name: mp_sso_sys_channel
  data_type: string
  description: mpSsoSysChannel
  nullable: true
  cluster: platform_integration
- name: uni_social_credit_code
  data_type: string
  description: 统一社会信用证
  nullable: true
  cluster: tenant_identity
- name: enable
  data_type: string
  description: enable
  nullable: true
  cluster: common
  dictionary: tenant_setting_config_enable
- name: remark
  data_type: string
  description: remark
  nullable: true
  cluster: common
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
  cluster: approval_flow
- name: app_tenant_code
  data_type: string
  description: 逻辑租户标识
  nullable: true
  cluster: tenant_identity
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  nullable: true
  cluster: tenant_identity
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  nullable: true
  cluster: approval_flow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: approval_flow
  dictionary: tenant_setting_config_act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: approval_flow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_identity
- name: platform_operator
  data_type: string
  description: 平台运营方
  nullable: true
  cluster: platform_integration
- name: pcimg_loginpage_bg_logo_url
  data_type: string
  description: PC首页背景图
  nullable: true
  cluster: brand_theme
- name: pcimg_indexpage_bg_logo_url
  data_type: string
  description: PC内页logo
  nullable: true
  cluster: brand_theme
- name: pcimg_browser_tab_icon_url
  data_type: string
  description: PC浏览器页签Icon
  nullable: true
  cluster: brand_theme
- name: pcimg_loginpage_banner_url
  data_type: string
  description: PC登录窗口横幅
  nullable: true
  cluster: brand_theme
- name: tenant_flag_zh
  data_type: string
  description: 项目标识（中文）
  nullable: true
  cluster: tenant_identity
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  nullable: true
  cluster: tenant_identity
- name: uat_mp_app_id
  data_type: string
  description: UAT小程序appID
  nullable: true
  cluster: mp_wx_account
- name: uat_mp_app_name
  data_type: string
  description: UAT小程序名称
  nullable: true
  cluster: mp_wx_account
- name: uat_mp_wx_login_name
  data_type: string
  description: UAT公众登陆账号
  nullable: true
  cluster: mp_wx_account
- name: uat_mp_wx_login_pwd
  data_type: string
  description: UAT公众号登录密码
  nullable: true
  cluster: mp_wx_account
- name: prd_mp_app_id
  data_type: string
  description: 生产小程序appID
  nullable: true
  cluster: mp_wx_account
- name: prd_mp_app_name
  data_type: string
  description: 生产小程序名称
  nullable: true
  cluster: mp_wx_account
- name: prd_mp_wx_login_name
  data_type: string
  description: 生产公众号登录账号
  nullable: true
  cluster: mp_wx_account
- name: prd_mp_wx_login_pwd
  data_type: string
  description: 生产公众号登录密码
  nullable: true
  cluster: mp_wx_account
- name: need_hfive
  data_type: string
  description: 是否定制H5
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_need_hfive
- name: mobile_indexpage_bg_logo_url
  data_type: string
  description: 移动端首页背景图
  nullable: true
  cluster: brand_theme
- name: need_mp_wx
  data_type: string
  description: 是否定制小程序
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_need_mp_wx
- name: main_theme_color
  data_type: string
  description: 主题色
  nullable: true
  cluster: brand_theme
- name: status
  data_type: string
  description: 生效状态
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_status
- name: person_auth_agreement
  data_type: string
  description: 变更联系人授权书
  nullable: true
  cluster: agreement_auth
- name: self_registration_flag
  data_type: string
  description: 是否放开自主注册
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_self_registration_flag
- name: company_share_flag
  data_type: string
  description: 客户认证数据是否可用于其他贴牌平台
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_company_share_flag
- name: mobile_indexpage_logo_url
  data_type: string
  description: 移动端首页logo
  nullable: true
  cluster: brand_theme
- name: hfive_dev_domain
  data_type: string
  description: H5开发环境域名
  nullable: true
  cluster: domain_env
- name: hfive_test_domain
  data_type: string
  description: H5测试环境域名
  nullable: true
  cluster: domain_env
- name: hfive_uat_domain
  data_type: string
  description: H5UAT环境域名
  nullable: true
  cluster: domain_env
- name: hfive_prd_domain
  data_type: string
  description: H5生产环境域名
  nullable: true
  cluster: domain_env
- name: operator_id
  data_type: string
  description: ''
  nullable: true
  cluster: ops_service
- name: operator_name
  data_type: string
  description: ''
  nullable: true
  cluster: ops_service
- name: operator_email
  data_type: string
  description: ''
  nullable: true
  cluster: ops_service
- name: send_email
  data_type: string
  description: ''
  nullable: true
  cluster: ops_service
  dictionary: tenant_setting_config_send_email
- name: operator_ai_customer
  data_type: string
  description: ''
  nullable: true
  cluster: ops_service
  dictionary: tenant_setting_config_operator_ai_customer
- name: operator_wechat_code
  data_type: string
  description: 公众号码
  nullable: true
  cluster: ops_service
- name: operator_qr_code
  data_type: string
  description: 客服二维码
  nullable: true
  cluster: ops_service
- name: operator_applet_code
  data_type: string
  description: 客服小程序码
  nullable: true
  cluster: ops_service
- name: ai_zc_sysnum
  data_type: string
  description: 智能客服系统号
  nullable: true
  cluster: ops_service
- name: ai_zc_channel
  data_type: string
  description: 智能客服渠道号
  nullable: true
  cluster: ops_service
- name: portal_flag
  data_type: string
  description: 是否启用门户
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_portal_flag
- name: share_flag
  data_type: string
  description: 租户共享标识
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_share_flag
- name: recall_auth_doc_flag
  data_type: string
  description: 是否需回收授权书标识
  nullable: true
  cluster: agreement_auth
  dictionary: tenant_setting_config_recall_auth_doc_flag
- name: core_bosc_company_id_property_requried
  data_type: string
  description: 关联核心企业（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_core_bosc_company_id_property_requried
- name: xib_factor_contract_no_property_requried
  data_type: string
  description: 厦银保理合同编号（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_xib_factor_contract_no_property_requried
- name: company_size_property_requried
  data_type: string
  description: 增值税纳税人类别（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_company_size_property_requried
- name: billing_type_property_requried
  data_type: string
  description: 开票类型（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_billing_type_property_requried
- name: cash_contract_no_property_requried
  data_type: string
  description: 中原融资合同编号（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_cash_contract_no_property_requried
- name: zybank_cash_contract_amt_property_requried
  data_type: string
  description: 中原融资合同金额（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_zybank_cash_contract_amt_property_requried
- name: lybank_cash_contract_no_property_requried
  data_type: string
  description: 洛阳融资合同编号（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_lybank_cash_contract_no_property_requried
- name: composite_field_property_requried
  data_type: string
  description: 工行供应链编号（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_composite_field_property_requried
- name: composite_field_property_requried_config_company_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: composite_field_property_requried_company_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: core_bosc_company_id_property_requried_config_cust_role
  data_type: string
  description: 关联核心企业（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: xib_factor_contract_no_property_requried_config_cust_role
  data_type: string
  description: 厦银保理合同编号（补充字段-是否必填，企业角色
  nullable: true
  cluster: ext_field_company_role
- name: company_size_property_requried_config_cust_role
  data_type: string
  description: 增值税纳税人类别（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: billing_type_property_requried_config_cust_role
  data_type: string
  description: 开票类型（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: cash_contract_no_property_requried_config_cust_role
  data_type: string
  description: 中原融资合同编号（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: zybank_cash_contract_amt_property_requried_config_cust_role
  data_type: string
  description: 中原融资合同金额（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: lybank_cash_contract_no_property_requried_config_cust_role
  data_type: string
  description: 洛阳融资合同编号（补充字段-是否必填，企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: composite_field_property_requried_config_cust_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: bg_color
  data_type: string
  description: 背景颜色(L:彩色 G：灰色)
  nullable: true
  cluster: brand_theme
- name: pushing_status
  data_type: string
  description: 租户推送状态
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_pushing_status
- name: platform_secret_key
  data_type: string
  description: 中台互通配置秘钥
  nullable: true
  cluster: platform_integration
- name: default_project_id
  data_type: number
  description: 默认项目
  nullable: true
  cluster: tenant_identity
- name: is_stack
  data_type: string
  description: 是否存量数据
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_is_stack
- name: finance_org_type_property_requried
  data_type: string
  description: 金融机构类型（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_finance_org_type_property_requried
- name: finance_org_type_property_requried_config_cust_role
  data_type: string
  description: 金融机构类型（补充字段-是否必填 企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: sign_flag
  data_type: string
  description: 接收跨贴牌数据是否强制重签授权书
  nullable: true
  cluster: agreement_auth
  dictionary: tenant_setting_config_sign_flag
- name: main_tenant_flg_en
  data_type: string
  description: 主定制项目标识
  nullable: true
  cluster: tenant_identity
- name: bank_branch
  data_type: string
  description: 分行适用角色
  nullable: true
  cluster: ext_field_company_role
- name: bank_branch_property_requried
  data_type: string
  description: 银行分行名称（通用）（补充字段-是否必填）
  nullable: true
  cluster: ext_field_required
  dictionary: tenant_setting_config_bank_branch_property_requried
- name: bank_branch_property_requried_config_cust_role
  data_type: string
  description: 银行分行名称（通用）（补充字段-是否必填 企业角色）
  nullable: true
  cluster: ext_field_company_role
- name: oper_auth_agreement
  data_type: string
  description: 子账户授权书
  nullable: true
  cluster: agreement_auth
- name: migratory_flag
  data_type: string
  description: 迁移标志
  nullable: true
  cluster: tenant_switch
- name: project_code_required
  data_type: string
  description: 项目码是否必填：Y/N
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_project_code_required
- name: customer_card_type
  data_type: string
  description: 客服名片类型：WX_WORK=发送企微名片，WX=发送微信名片，与operCardType枚举一致
  nullable: true
  cluster: ops_service
  dictionary: tenant_setting_config_customer_card_type
- name: op_update_user
  data_type: string
  description: 租户运营更新人
  nullable: true
  cluster: ops_service
- name: op_update_time
  data_type: temporal
  description: 租户运营更新时间
  nullable: true
  cluster: ops_service
- name: ai_resource_color
  data_type: string
  description: 智能客服按钮颜色
  nullable: true
  cluster: brand_theme
- name: generate_electronic_auth_flag
  data_type: string
  description: 是否生成电子版授权书：Y-是，N-否
  nullable: true
  cluster: agreement_auth
  dictionary: tenant_setting_config_generate_electronic_auth_flag
- name: platform_sms_signature
  data_type: string
  description: 产融平台短信签名(无方括号)
  nullable: true
  cluster: platform_integration
- name: adapt_colour
  data_type: string
  description: 适配背景颜色
  nullable: true
  cluster: brand_theme
- name: access_mode
  data_type: string
  description: 接入模式
  nullable: true
  cluster: tenant_switch
  dictionary: tenant_setting_config_access_mode
- name: use_theme_after_login
  data_type: string
  description: 登录后是否使用该色调：Y-是，N-否
  nullable: true
  cluster: brand_theme
  dictionary: tenant_setting_config_use_theme_after_login
```
