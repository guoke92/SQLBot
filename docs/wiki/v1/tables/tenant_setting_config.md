---
type: table
title: 租户配置
page_key: tenant_setting_config
belong: tables
status: draft
anchors: [tenant_setting_config]
sources: ['database_schema:lowcode_pplatform.tenant_setting_config']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_interworking_product, tenant_interworking_project, tenant_product,
  tenant_setting_config_share, tenant_setting_config__source, tenant_setting_config__privacy_policy_agreement,
  tenant_setting_config__user_protocol_agreement, tenant_setting_config__auth_agreement,
  tenant_setting_config__dbass_app_id, tenant_setting_config__mp_sso_sys_channel,
  tenant_setting_config__enable, tenant_setting_config__app_tenant_code, tenant_setting_config__act_procinst_status,
  tenant_setting_config__need_hfive, tenant_setting_config__need_mp_wx, tenant_setting_config__status,
  tenant_setting_config__person_auth_agreement, tenant_setting_config__self_registration_flag,
  tenant_setting_config__company_share_flag, tenant_setting_config__send_email, tenant_setting_config__operator_ai_customer,
  tenant_setting_config__ai_zc_sysnum, tenant_setting_config__ai_zc_channel, tenant_setting_config__portal_flag,
  tenant_setting_config__share_flag, tenant_setting_config__recall_auth_doc_flag,
  tenant_setting_config__core_bosc_company_id_property_requried, tenant_setting_config__xib_factor_contract_no_property_requried,
  tenant_setting_config__company_size_property_requried, tenant_setting_config__billing_type_property_requried,
  tenant_setting_config__cash_contract_no_property_requried, tenant_setting_config__zybank_cash_contract_amt_property_requried,
  tenant_setting_config__lybank_cash_contract_no_property_requried, tenant_setting_config__composite_field_property_requried,
  tenant_setting_config__pushing_status, tenant_setting_config__is_stack, tenant_setting_config__finance_org_type_property_requried,
  tenant_setting_config__sign_flag, tenant_setting_config__main_tenant_flg_en, tenant_setting_config__bank_branch_property_requried,
  tenant_setting_config__oper_auth_agreement, tenant_setting_config__project_code_required,
  tenant_setting_config__customer_card_type, tenant_setting_config__op_update_user,
  tenant_setting_config__generate_electronic_auth_flag, tenant_setting_config__access_mode,
  tenant_setting_config__use_theme_after_login]
---

# 租户配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### identity

`source_id`, `source`, `name`, `band_name`, `apaas_tenant_code`, `uni_social_credit_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `tenant_flag_zh`, `tenant_flg_en`, `main_tenant_flg_en`

### status_switch

`status`, `self_registration_flag`, `company_share_flag`, `portal_flag`, `share_flag`, `recall_auth_doc_flag`, `pushing_status`, `is_stack`, `sign_flag`, `project_code_required`

### agreement

`privacy_policy_agreement`, `user_protocol_agreement`, `auth_agreement`, `person_auth_agreement`, `oper_auth_agreement`, `generate_electronic_auth_flag`

### domain

`dev_domain`, `sit_domain`, `uat_domain`, `prd_domain`, `hfive_dev_domain`, `hfive_test_domain`, `hfive_uat_domain`, `hfive_prd_domain`

### brand_image

`web_title`, `web_logo_url`, `pc_login_logo_path`, `pc_icon_path`, `pc_logo_path`, `pc_home_background_path`, `mp_home_background_path`, `mp_logo_path`, `pcimg_loginpage_bg_logo_url`, `pcimg_indexpage_bg_logo_url`, `pcimg_browser_tab_icon_url`, `pcimg_loginpage_banner_url`, `mobile_indexpage_bg_logo_url`, `mobile_indexpage_logo_url`

### theme

`main_theme_color`, `bg_color`, `ai_resource_color`, `adapt_colour`, `use_theme_after_login`

### mini_program

`dbass_app_id`, `mp_dbass_app_id`, `dbass_private_key`, `sso_sys_channel`, `sso_tenant_chanel`, `mp_sso_tenant_chanel`, `mp_sso_sys_channel`, `uat_mp_app_id`, `uat_mp_app_name`, `uat_mp_wx_login_name`, `uat_mp_wx_login_pwd`, `prd_mp_app_id`, `prd_mp_app_name`, `prd_mp_wx_login_name`, `prd_mp_wx_login_pwd`, `need_hfive`, `need_mp_wx`

### customer_service

`cust_service_number`, `operator_id`, `operator_name`, `operator_email`, `send_email`, `operator_ai_customer`, `operator_wechat_code`, `operator_qr_code`, `operator_applet_code`, `ai_zc_sysnum`, `ai_zc_channel`, `customer_card_type`, `op_update_user`, `op_update_time`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### platform_config

`platform_operator`, `platform_secret_key`, `default_project_id`, `migratory_flag`, `platform_sms_signature`, `access_mode`

### property_required

`core_bosc_company_id_property_requried`, `xib_factor_contract_no_property_requried`, `company_size_property_requried`, `billing_type_property_requried`, `cash_contract_no_property_requried`, `zybank_cash_contract_amt_property_requried`, `lybank_cash_contract_no_property_requried`, `composite_field_property_requried`, `composite_field_property_requried_config_company_role`, `composite_field_property_requried_company_role`, `core_bosc_company_id_property_requried_config_cust_role`, `xib_factor_contract_no_property_requried_config_cust_role`, `company_size_property_requried_config_cust_role`, `billing_type_property_requried_config_cust_role`, `cash_contract_no_property_requried_config_cust_role`, `zybank_cash_contract_amt_property_requried_config_cust_role`, `lybank_cash_contract_no_property_requried_config_cust_role`, `composite_field_property_requried_config_cust_role`, `finance_org_type_property_requried`, `finance_org_type_property_requried_config_cust_role`, `bank_branch`, `bank_branch_property_requried`, `bank_branch_property_requried_config_cust_role`

## 字段

```ground:table
table: tenant_setting_config
database: lowcode_pplatform
description: 租户配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, band_name, apaas_tenant_code, uni_social_credit_code, uat_mp_app_name,
  uat_mp_wx_login_name, prd_mp_app_name, prd_mp_wx_login_name, operator_name, operator_wechat_code,
  operator_qr_code, operator_applet_code]
clusters:
- key: common
  title: 通用
  include: always
- key: identity
  title: 租户身份与标识
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: status_switch
  title: 租户状态与开关
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: agreement
  title: 协议与授权
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: domain
  title: 域名与环境
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: brand_image
  title: PC与移动端品牌图片
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: theme
  title: 主题与颜色
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: mini_program
  title: 小程序与公众号配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: customer_service
  title: 客服与运营
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: platform_config
  title: 平台配置
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config
- key: property_required
  title: 补充字段必填配置
  trust: proposed
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
  cluster: common
- name: source_id
  data_type: string
  description: 租户来源id
  cluster: identity
- name: source
  data_type: string
  description: 租户来源
  cluster: identity
  dictionary: tenant_setting_config__source
- name: name
  data_type: string
  description: 租户名称
  cluster: identity
- name: band_name
  data_type: string
  description: 贴牌平台名称
  cluster: identity
- name: cust_service_number
  data_type: string
  description: 客服电话
  cluster: customer_service
- name: web_title
  data_type: string
  description: 网站标题
  cluster: brand_image
- name: web_logo_url
  data_type: string
  description: 网站logo
  cluster: brand_image
- name: dev_domain
  data_type: string
  description: 开发环境域名
  cluster: domain
- name: sit_domain
  data_type: string
  description: 测试环境域名
  cluster: domain
- name: uat_domain
  data_type: string
  description: UAT环境域名
  cluster: domain
- name: prd_domain
  data_type: string
  description: 生产环境域名
  cluster: domain
- name: privacy_policy_agreement
  data_type: string
  description: 隐私协议
  cluster: agreement
  dictionary: tenant_setting_config__privacy_policy_agreement
- name: user_protocol_agreement
  data_type: string
  description: 用户协议
  cluster: agreement
  dictionary: tenant_setting_config__user_protocol_agreement
- name: auth_agreement
  data_type: string
  description: 授权书协议
  cluster: agreement
  dictionary: tenant_setting_config__auth_agreement
- name: apaas_tenant_code
  data_type: string
  description: aPaaS租户编码
  cluster: identity
- name: dbass_app_id
  data_type: string
  description: dbassAppId
  cluster: mini_program
  dictionary: tenant_setting_config__dbass_app_id
- name: mp_dbass_app_id
  data_type: string
  description: 小程序dbassAppId
  cluster: mini_program
- name: dbass_private_key
  data_type: string
  description: dbassPrivateKey
  cluster: mini_program
- name: sso_sys_channel
  data_type: string
  description: ssoSysChannel
  cluster: mini_program
- name: sso_tenant_chanel
  data_type: string
  description: ssoTenantChanel
  cluster: mini_program
- name: mp_sso_tenant_chanel
  data_type: string
  description: mpSsoTenantChanel
  cluster: mini_program
- name: pc_login_logo_path
  data_type: string
  description: PC登录窗口横幅
  cluster: brand_image
- name: pc_icon_path
  data_type: string
  description: PC浏览器页签Icon
  cluster: brand_image
- name: pc_logo_path
  data_type: string
  description: PC内页logo
  cluster: brand_image
- name: pc_home_background_path
  data_type: string
  description: PC首页背景图
  cluster: brand_image
- name: mp_home_background_path
  data_type: string
  description: 小程序首页背景图
  cluster: brand_image
- name: mp_logo_path
  data_type: string
  description: 移动端首页logo
  cluster: brand_image
- name: mp_sso_sys_channel
  data_type: string
  description: mpSsoSysChannel
  cluster: mini_program
  dictionary: tenant_setting_config__mp_sso_sys_channel
- name: uni_social_credit_code
  data_type: string
  description: 统一社会信用证
  cluster: identity
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_setting_config__enable
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
  cluster: identity
  dictionary: tenant_setting_config__app_tenant_code
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: identity
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
  dictionary: tenant_setting_config__act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: identity
- name: platform_operator
  data_type: string
  description: 平台运营方
  cluster: platform_config
- name: pcimg_loginpage_bg_logo_url
  data_type: string
  description: PC首页背景图
  cluster: brand_image
- name: pcimg_indexpage_bg_logo_url
  data_type: string
  description: PC内页logo
  cluster: brand_image
- name: pcimg_browser_tab_icon_url
  data_type: string
  description: PC浏览器页签Icon
  cluster: brand_image
- name: pcimg_loginpage_banner_url
  data_type: string
  description: PC登录窗口横幅
  cluster: brand_image
- name: tenant_flag_zh
  data_type: string
  description: 项目标识（中文）
  cluster: identity
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  cluster: identity
- name: uat_mp_app_id
  data_type: string
  description: UAT小程序appID
  cluster: mini_program
- name: uat_mp_app_name
  data_type: string
  description: UAT小程序名称
  cluster: mini_program
- name: uat_mp_wx_login_name
  data_type: string
  description: UAT公众登陆账号
  cluster: mini_program
- name: uat_mp_wx_login_pwd
  data_type: string
  description: UAT公众号登录密码
  cluster: mini_program
- name: prd_mp_app_id
  data_type: string
  description: 生产小程序appID
  cluster: mini_program
- name: prd_mp_app_name
  data_type: string
  description: 生产小程序名称
  cluster: mini_program
- name: prd_mp_wx_login_name
  data_type: string
  description: 生产公众号登录账号
  cluster: mini_program
- name: prd_mp_wx_login_pwd
  data_type: string
  description: 生产公众号登录密码
  cluster: mini_program
- name: need_hfive
  data_type: string
  description: 是否定制H5
  cluster: mini_program
  dictionary: tenant_setting_config__need_hfive
- name: mobile_indexpage_bg_logo_url
  data_type: string
  description: 移动端首页背景图
  cluster: brand_image
- name: need_mp_wx
  data_type: string
  description: 是否定制小程序
  cluster: mini_program
  dictionary: tenant_setting_config__need_mp_wx
- name: main_theme_color
  data_type: string
  description: 主题色
  cluster: theme
- name: status
  data_type: string
  description: 生效状态
  cluster: status_switch
  dictionary: tenant_setting_config__status
- name: person_auth_agreement
  data_type: string
  description: 变更联系人授权书
  cluster: agreement
  dictionary: tenant_setting_config__person_auth_agreement
- name: self_registration_flag
  data_type: string
  description: 是否放开自主注册
  cluster: status_switch
  dictionary: tenant_setting_config__self_registration_flag
- name: company_share_flag
  data_type: string
  description: 客户认证数据是否可用于其他贴牌平台
  cluster: status_switch
  dictionary: tenant_setting_config__company_share_flag
- name: mobile_indexpage_logo_url
  data_type: string
  description: 移动端首页logo
  cluster: brand_image
- name: hfive_dev_domain
  data_type: string
  description: H5开发环境域名
  cluster: domain
- name: hfive_test_domain
  data_type: string
  description: H5测试环境域名
  cluster: domain
- name: hfive_uat_domain
  data_type: string
  description: H5UAT环境域名
  cluster: domain
- name: hfive_prd_domain
  data_type: string
  description: H5生产环境域名
  cluster: domain
- name: operator_id
  data_type: string
  cluster: customer_service
- name: operator_name
  data_type: string
  cluster: customer_service
- name: operator_email
  data_type: string
  cluster: customer_service
- name: send_email
  data_type: string
  cluster: customer_service
  dictionary: tenant_setting_config__send_email
- name: operator_ai_customer
  data_type: string
  cluster: customer_service
  dictionary: tenant_setting_config__operator_ai_customer
- name: operator_wechat_code
  data_type: string
  description: 公众号码
  cluster: customer_service
- name: operator_qr_code
  data_type: string
  description: 客服二维码
  cluster: customer_service
- name: operator_applet_code
  data_type: string
  description: 客服小程序码
  cluster: customer_service
- name: ai_zc_sysnum
  data_type: string
  description: 智能客服系统号
  cluster: customer_service
  dictionary: tenant_setting_config__ai_zc_sysnum
- name: ai_zc_channel
  data_type: string
  description: 智能客服渠道号
  cluster: customer_service
  dictionary: tenant_setting_config__ai_zc_channel
- name: portal_flag
  data_type: string
  description: 是否启用门户
  cluster: status_switch
  dictionary: tenant_setting_config__portal_flag
- name: share_flag
  data_type: string
  description: 租户共享标识
  cluster: status_switch
  dictionary: tenant_setting_config__share_flag
- name: recall_auth_doc_flag
  data_type: string
  description: 是否需回收授权书标识
  cluster: status_switch
  dictionary: tenant_setting_config__recall_auth_doc_flag
- name: core_bosc_company_id_property_requried
  data_type: string
  description: 关联核心企业（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__core_bosc_company_id_property_requried
- name: xib_factor_contract_no_property_requried
  data_type: string
  description: 厦银保理合同编号（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__xib_factor_contract_no_property_requried
- name: company_size_property_requried
  data_type: string
  description: 增值税纳税人类别（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__company_size_property_requried
- name: billing_type_property_requried
  data_type: string
  description: 开票类型（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__billing_type_property_requried
- name: cash_contract_no_property_requried
  data_type: string
  description: 中原融资合同编号（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__cash_contract_no_property_requried
- name: zybank_cash_contract_amt_property_requried
  data_type: string
  description: 中原融资合同金额（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__zybank_cash_contract_amt_property_requried
- name: lybank_cash_contract_no_property_requried
  data_type: string
  description: 洛阳融资合同编号（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__lybank_cash_contract_no_property_requried
- name: composite_field_property_requried
  data_type: string
  description: 工行供应链编号（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__composite_field_property_requried
- name: composite_field_property_requried_config_company_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  cluster: property_required
- name: composite_field_property_requried_company_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  cluster: property_required
- name: core_bosc_company_id_property_requried_config_cust_role
  data_type: string
  description: 关联核心企业（补充字段-是否必填，企业角色）
  cluster: property_required
- name: xib_factor_contract_no_property_requried_config_cust_role
  data_type: string
  description: 厦银保理合同编号（补充字段-是否必填，企业角色
  cluster: property_required
- name: company_size_property_requried_config_cust_role
  data_type: string
  description: 增值税纳税人类别（补充字段-是否必填，企业角色）
  cluster: property_required
- name: billing_type_property_requried_config_cust_role
  data_type: string
  description: 开票类型（补充字段-是否必填，企业角色）
  cluster: property_required
- name: cash_contract_no_property_requried_config_cust_role
  data_type: string
  description: 中原融资合同编号（补充字段-是否必填，企业角色）
  cluster: property_required
- name: zybank_cash_contract_amt_property_requried_config_cust_role
  data_type: string
  description: 中原融资合同金额（补充字段-是否必填，企业角色）
  cluster: property_required
- name: lybank_cash_contract_no_property_requried_config_cust_role
  data_type: string
  description: 洛阳融资合同编号（补充字段-是否必填，企业角色）
  cluster: property_required
- name: composite_field_property_requried_config_cust_role
  data_type: string
  description: 工行供应链编号（补充字段-企业角色）
  cluster: property_required
- name: bg_color
  data_type: string
  description: 背景颜色(L:彩色 G：灰色)
  cluster: theme
- name: pushing_status
  data_type: string
  description: 租户推送状态
  cluster: status_switch
  dictionary: tenant_setting_config__pushing_status
- name: platform_secret_key
  data_type: string
  description: 中台互通配置秘钥
  cluster: platform_config
- name: default_project_id
  data_type: number
  description: 默认项目
  cluster: platform_config
- name: is_stack
  data_type: string
  description: 是否存量数据
  cluster: status_switch
  dictionary: tenant_setting_config__is_stack
- name: finance_org_type_property_requried
  data_type: string
  description: 金融机构类型（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__finance_org_type_property_requried
- name: finance_org_type_property_requried_config_cust_role
  data_type: string
  description: 金融机构类型（补充字段-是否必填 企业角色）
  cluster: property_required
- name: sign_flag
  data_type: string
  description: 接收跨贴牌数据是否强制重签授权书
  cluster: status_switch
  dictionary: tenant_setting_config__sign_flag
- name: main_tenant_flg_en
  data_type: string
  description: 主定制项目标识
  cluster: identity
  dictionary: tenant_setting_config__main_tenant_flg_en
- name: bank_branch
  data_type: string
  description: 分行适用角色
  cluster: property_required
- name: bank_branch_property_requried
  data_type: string
  description: 银行分行名称（通用）（补充字段-是否必填）
  cluster: property_required
  dictionary: tenant_setting_config__bank_branch_property_requried
- name: bank_branch_property_requried_config_cust_role
  data_type: string
  description: 银行分行名称（通用）（补充字段-是否必填 企业角色）
  cluster: property_required
- name: oper_auth_agreement
  data_type: string
  description: 子账户授权书
  cluster: agreement
  dictionary: tenant_setting_config__oper_auth_agreement
- name: migratory_flag
  data_type: string
  description: 迁移标志
  cluster: platform_config
- name: project_code_required
  data_type: string
  description: 项目码是否必填：Y/N
  cluster: status_switch
  dictionary: tenant_setting_config__project_code_required
- name: customer_card_type
  data_type: string
  description: 客服名片类型：WX_WORK=发送企微名片，WX=发送微信名片，与operCardType枚举一致
  cluster: customer_service
  dictionary: tenant_setting_config__customer_card_type
- name: op_update_user
  data_type: string
  description: 租户运营更新人
  cluster: customer_service
  dictionary: tenant_setting_config__op_update_user
- name: op_update_time
  data_type: temporal
  description: 租户运营更新时间
  cluster: customer_service
- name: ai_resource_color
  data_type: string
  description: 智能客服按钮颜色
  cluster: theme
- name: generate_electronic_auth_flag
  data_type: string
  description: 是否生成电子版授权书：Y-是，N-否
  cluster: agreement
  dictionary: tenant_setting_config__generate_electronic_auth_flag
- name: platform_sms_signature
  data_type: string
  description: 产融平台短信签名(无方括号)
  cluster: platform_config
- name: adapt_colour
  data_type: string
  description: 适配背景颜色
  cluster: theme
- name: access_mode
  data_type: string
  description: 接入模式
  cluster: platform_config
  dictionary: tenant_setting_config__access_mode
- name: use_theme_after_login
  data_type: string
  description: 登录后是否使用该色调：Y-是，N-否
  cluster: theme
  dictionary: tenant_setting_config__use_theme_after_login
```

## 页面链接

### 关联表

- [[tables/tenant_interworking_product]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_product]]
- [[tables/tenant_setting_config_share]]

### 字典

- [[dicts/tenant_setting_config__source]]（`tenant_setting_config.source`）
- [[dicts/tenant_setting_config__privacy_policy_agreement]]（`tenant_setting_config.privacy_policy_agreement`）
- [[dicts/tenant_setting_config__user_protocol_agreement]]（`tenant_setting_config.user_protocol_agreement`）
- [[dicts/tenant_setting_config__auth_agreement]]（`tenant_setting_config.auth_agreement`）
- [[dicts/tenant_setting_config__dbass_app_id]]（`tenant_setting_config.dbass_app_id`）
- [[dicts/tenant_setting_config__mp_sso_sys_channel]]（`tenant_setting_config.mp_sso_sys_channel`）
- [[dicts/tenant_setting_config__enable]]（`tenant_setting_config.enable`）
- [[dicts/tenant_setting_config__app_tenant_code]]（`tenant_setting_config.app_tenant_code`）
- [[dicts/tenant_setting_config__act_procinst_status]]（`tenant_setting_config.act_procinst_status`）
- [[dicts/tenant_setting_config__need_hfive]]（`tenant_setting_config.need_hfive`）
- [[dicts/tenant_setting_config__need_mp_wx]]（`tenant_setting_config.need_mp_wx`）
- [[dicts/tenant_setting_config__status]]（`tenant_setting_config.status`）
- [[dicts/tenant_setting_config__person_auth_agreement]]（`tenant_setting_config.person_auth_agreement`）
- [[dicts/tenant_setting_config__self_registration_flag]]（`tenant_setting_config.self_registration_flag`）
- [[dicts/tenant_setting_config__company_share_flag]]（`tenant_setting_config.company_share_flag`）
- [[dicts/tenant_setting_config__send_email]]（`tenant_setting_config.send_email`）
- [[dicts/tenant_setting_config__operator_ai_customer]]（`tenant_setting_config.operator_ai_customer`）
- [[dicts/tenant_setting_config__ai_zc_sysnum]]（`tenant_setting_config.ai_zc_sysnum`）
- [[dicts/tenant_setting_config__ai_zc_channel]]（`tenant_setting_config.ai_zc_channel`）
- [[dicts/tenant_setting_config__portal_flag]]（`tenant_setting_config.portal_flag`）
- [[dicts/tenant_setting_config__share_flag]]（`tenant_setting_config.share_flag`）
- [[dicts/tenant_setting_config__recall_auth_doc_flag]]（`tenant_setting_config.recall_auth_doc_flag`）
- [[dicts/tenant_setting_config__core_bosc_company_id_property_requried]]（`tenant_setting_config.core_bosc_company_id_property_requried`）
- [[dicts/tenant_setting_config__xib_factor_contract_no_property_requried]]（`tenant_setting_config.xib_factor_contract_no_property_requried`）
- [[dicts/tenant_setting_config__company_size_property_requried]]（`tenant_setting_config.company_size_property_requried`）
- [[dicts/tenant_setting_config__billing_type_property_requried]]（`tenant_setting_config.billing_type_property_requried`）
- [[dicts/tenant_setting_config__cash_contract_no_property_requried]]（`tenant_setting_config.cash_contract_no_property_requried`）
- [[dicts/tenant_setting_config__zybank_cash_contract_amt_property_requried]]（`tenant_setting_config.zybank_cash_contract_amt_property_requried`）
- [[dicts/tenant_setting_config__lybank_cash_contract_no_property_requried]]（`tenant_setting_config.lybank_cash_contract_no_property_requried`）
- [[dicts/tenant_setting_config__composite_field_property_requried]]（`tenant_setting_config.composite_field_property_requried`）
- [[dicts/tenant_setting_config__pushing_status]]（`tenant_setting_config.pushing_status`）
- [[dicts/tenant_setting_config__is_stack]]（`tenant_setting_config.is_stack`）
- [[dicts/tenant_setting_config__finance_org_type_property_requried]]（`tenant_setting_config.finance_org_type_property_requried`）
- [[dicts/tenant_setting_config__sign_flag]]（`tenant_setting_config.sign_flag`）
- [[dicts/tenant_setting_config__main_tenant_flg_en]]（`tenant_setting_config.main_tenant_flg_en`）
- [[dicts/tenant_setting_config__bank_branch_property_requried]]（`tenant_setting_config.bank_branch_property_requried`）
- [[dicts/tenant_setting_config__oper_auth_agreement]]（`tenant_setting_config.oper_auth_agreement`）
- [[dicts/tenant_setting_config__project_code_required]]（`tenant_setting_config.project_code_required`）
- [[dicts/tenant_setting_config__customer_card_type]]（`tenant_setting_config.customer_card_type`）
- [[dicts/tenant_setting_config__op_update_user]]（`tenant_setting_config.op_update_user`）
- [[dicts/tenant_setting_config__generate_electronic_auth_flag]]（`tenant_setting_config.generate_electronic_auth_flag`）
- [[dicts/tenant_setting_config__access_mode]]（`tenant_setting_config.access_mode`）
- [[dicts/tenant_setting_config__use_theme_after_login]]（`tenant_setting_config.use_theme_after_login`）
