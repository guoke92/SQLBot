---
type: table
title: 租户配置
page_key: tenant_setting_config
belong: tables
status: draft
anchors: [tenant_setting_config]
sources: ['database_schema:lowcode_pplatform.tenant_setting_config', 'code_path:TenantDomainService.java:344']
created: '2026-09-18'
updated: '2026-09-18'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [ca_fee_company, ca_fee_order, ca_fee_project_config, tenant_interworking_product,
  tenant_interworking_project, tenant_product, tenant_project, tenant_setting_config_share,
  tenant_setting_config__source, tenant_setting_config__mp_sso_sys_channel, tenant_setting_config__enable,
  tenant_setting_config__act_procinst_status, tenant_setting_config__need_hfive, tenant_setting_config__need_mp_wx,
  tenant_setting_config__status, tenant_setting_config__self_registration_flag, tenant_setting_config__company_share_flag,
  tenant_setting_config__operator_ai_customer, tenant_setting_config__portal_flag,
  tenant_setting_config__share_flag, tenant_setting_config__recall_auth_doc_flag,
  tenant_setting_config__core_bosc_company_id_property_requried, tenant_setting_config__xib_factor_contract_no_property_requried,
  tenant_setting_config__company_size_property_requried, tenant_setting_config__cash_contract_no_property_requried,
  tenant_setting_config__zybank_cash_contract_amt_property_requried, tenant_setting_config__lybank_cash_contract_no_property_requried,
  tenant_setting_config__composite_field_property_requried, tenant_setting_config__pushing_status,
  tenant_setting_config__is_stack, tenant_setting_config__finance_org_type_property_requried,
  tenant_setting_config__sign_flag, tenant_setting_config__main_tenant_flg_en, tenant_setting_config__bank_branch_property_requried,
  tenant_setting_config__project_code_required, tenant_setting_config__customer_card_type,
  tenant_setting_config__generate_electronic_auth_flag, tenant_setting_config__access_mode,
  tenant_setting_config__use_theme_after_login]
---

# 租户配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_setting_config
database: lowcode_pplatform
desc: 租户配置
inactive: false
primary_key: [id]
grain: 一租户一行运营配置
name_anchors: [code, name, band_name, apaas_tenant_code, uni_social_credit_code, uat_mp_app_name,
  uat_mp_wx_login_name, prd_mp_app_name, prd_mp_wx_login_name, operator_name, operator_wechat_code,
  operator_qr_code, operator_applet_code]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: source_id
  type: string
  desc: 租户来源id
- name: source
  type: string
  desc: 租户来源
  dict: [ACFLOW, pplatform]
- name: name
  type: string
  desc: 租户名称
- name: band_name
  type: string
  desc: 贴牌平台名称
- name: cust_service_number
  type: string
  desc: 客服电话
- name: web_title
  type: string
  desc: 网站标题
- name: web_logo_url
  type: string
  desc: 网站logo
- name: dev_domain
  type: string
  desc: 开发环境域名
- name: sit_domain
  type: string
  desc: 测试环境域名
- name: uat_domain
  type: string
  desc: UAT环境域名
- name: prd_domain
  type: string
  desc: 生产环境域名
- name: privacy_policy_agreement
  type: string
  desc: 隐私协议
- name: user_protocol_agreement
  type: string
  desc: 用户协议
- name: auth_agreement
  type: string
  desc: 授权书协议
- name: apaas_tenant_code
  type: string
  desc: aPaaS租户编码
- name: dbass_app_id
  type: string
  desc: dbassAppId
- name: mp_dbass_app_id
  type: string
  desc: 小程序dbassAppId
- name: dbass_private_key
  type: string
  desc: dbassPrivateKey
- name: sso_sys_channel
  type: string
  desc: ssoSysChannel
- name: sso_tenant_chanel
  type: string
  desc: ssoTenantChanel
- name: mp_sso_tenant_chanel
  type: string
  desc: mpSsoTenantChanel
- name: pc_login_logo_path
  type: string
  desc: PC登录窗口横幅
- name: pc_icon_path
  type: string
  desc: PC浏览器页签Icon
- name: pc_logo_path
  type: string
  desc: PC内页logo
- name: pc_home_background_path
  type: string
  desc: PC首页背景图
- name: mp_home_background_path
  type: string
  desc: 小程序首页背景图
- name: mp_logo_path
  type: string
  desc: 移动端首页logo
- name: mp_sso_sys_channel
  type: string
  desc: mpSsoSysChannel
  dict: [scpr-pplatform-mp]
- name: uni_social_credit_code
  type: string
  desc: 统一社会信用证
- name: enable
  type: string
  desc: enable
  dict: [Y]
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
  dict: [N]
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: platform_operator
  type: string
  desc: 平台运营方
- name: pcimg_loginpage_bg_logo_url
  type: string
  desc: PC首页背景图
- name: pcimg_indexpage_bg_logo_url
  type: string
  desc: PC内页logo
- name: pcimg_browser_tab_icon_url
  type: string
  desc: PC浏览器页签Icon
- name: pcimg_loginpage_banner_url
  type: string
  desc: PC登录窗口横幅
- name: tenant_flag_zh
  type: string
  desc: 项目标识（中文）
- name: tenant_flg_en
  type: string
  desc: 项目标识（英文）
- name: uat_mp_app_id
  type: string
  desc: UAT小程序appID
- name: uat_mp_app_name
  type: string
  desc: UAT小程序名称
- name: uat_mp_wx_login_name
  type: string
  desc: UAT公众登陆账号
- name: uat_mp_wx_login_pwd
  type: string
  desc: UAT公众号登录密码
- name: prd_mp_app_id
  type: string
  desc: 生产小程序appID
- name: prd_mp_app_name
  type: string
  desc: 生产小程序名称
- name: prd_mp_wx_login_name
  type: string
  desc: 生产公众号登录账号
- name: prd_mp_wx_login_pwd
  type: string
  desc: 生产公众号登录密码
- name: need_hfive
  type: string
  desc: 是否定制H5
  dict: [N, Y]
- name: mobile_indexpage_bg_logo_url
  type: string
  desc: 移动端首页背景图
- name: need_mp_wx
  type: string
  desc: 是否定制小程序
  dict: [Y, N]
- name: main_theme_color
  type: string
  desc: 主题色
- name: status
  type: string
  desc: 生效状态
  dict: [N, Y]
- name: person_auth_agreement
  type: string
  desc: 变更联系人授权书
- name: self_registration_flag
  type: string
  desc: 是否放开自主注册
  dict: [Y, N]
- name: company_share_flag
  type: string
  desc: 客户认证数据是否可用于其他贴牌平台
  dict: [Y, N]
- name: mobile_indexpage_logo_url
  type: string
  desc: 移动端首页logo
- name: hfive_dev_domain
  type: string
  desc: H5开发环境域名
- name: hfive_test_domain
  type: string
  desc: H5测试环境域名
- name: hfive_uat_domain
  type: string
  desc: H5UAT环境域名
- name: hfive_prd_domain
  type: string
  desc: H5生产环境域名
- name: operator_id
  type: string
- name: operator_name
  type: string
- name: operator_email
  type: string
- name: send_email
  type: string
- name: operator_ai_customer
  type: string
  dict: ['0', '1']
- name: operator_wechat_code
  type: string
  desc: 公众号码
- name: operator_qr_code
  type: string
  desc: 客服二维码
- name: operator_applet_code
  type: string
  desc: 客服小程序码
- name: ai_zc_sysnum
  type: string
  desc: 智能客服系统号
- name: ai_zc_channel
  type: string
  desc: 智能客服渠道号
- name: portal_flag
  type: string
  desc: 是否启用门户
  dict: [N, Y]
- name: share_flag
  type: string
  desc: 租户共享标识
  dict: [N, Y]
- name: recall_auth_doc_flag
  type: string
  desc: 是否需回收授权书标识
  dict: [Y, N]
- name: core_bosc_company_id_property_requried
  type: string
  desc: 关联核心企业（补充字段-是否必填）
  dict: [N]
- name: xib_factor_contract_no_property_requried
  type: string
  desc: 厦银保理合同编号（补充字段-是否必填）
  dict: [N]
- name: company_size_property_requried
  type: string
  desc: 增值税纳税人类别（补充字段-是否必填）
  dict: [N]
- name: billing_type_property_requried
  type: string
  desc: 开票类型（补充字段-是否必填）
- name: cash_contract_no_property_requried
  type: string
  desc: 中原融资合同编号（补充字段-是否必填）
  dict: [N]
- name: zybank_cash_contract_amt_property_requried
  type: string
  desc: 中原融资合同金额（补充字段-是否必填）
  dict: [N]
- name: lybank_cash_contract_no_property_requried
  type: string
  desc: 洛阳融资合同编号（补充字段-是否必填）
  dict: [N]
- name: composite_field_property_requried
  type: string
  desc: 工行供应链编号（补充字段-是否必填）
  dict: [N, Y]
- name: composite_field_property_requried_config_company_role
  type: string
  desc: 工行供应链编号（补充字段-企业角色）
- name: composite_field_property_requried_company_role
  type: string
  desc: 工行供应链编号（补充字段-企业角色）
- name: core_bosc_company_id_property_requried_config_cust_role
  type: string
  desc: 关联核心企业（补充字段-是否必填，企业角色）
- name: xib_factor_contract_no_property_requried_config_cust_role
  type: string
  desc: 厦银保理合同编号（补充字段-是否必填，企业角色
- name: company_size_property_requried_config_cust_role
  type: string
  desc: 增值税纳税人类别（补充字段-是否必填，企业角色）
- name: billing_type_property_requried_config_cust_role
  type: string
  desc: 开票类型（补充字段-是否必填，企业角色）
- name: cash_contract_no_property_requried_config_cust_role
  type: string
  desc: 中原融资合同编号（补充字段-是否必填，企业角色）
- name: zybank_cash_contract_amt_property_requried_config_cust_role
  type: string
  desc: 中原融资合同金额（补充字段-是否必填，企业角色）
- name: lybank_cash_contract_no_property_requried_config_cust_role
  type: string
  desc: 洛阳融资合同编号（补充字段-是否必填，企业角色）
- name: composite_field_property_requried_config_cust_role
  type: string
  desc: 工行供应链编号（补充字段-企业角色）
- name: bg_color
  type: string
  desc: 背景颜色(L:彩色 G：灰色)
- name: pushing_status
  type: string
  desc: 租户推送状态
  dict: [Y, N]
- name: platform_secret_key
  type: string
  desc: 中台互通配置秘钥
- name: default_project_id
  type: number
  desc: 默认项目
- name: is_stack
  type: string
  desc: 是否存量数据
  dict: [Y, N]
- name: finance_org_type_property_requried
  type: string
  desc: 金融机构类型（补充字段-是否必填）
  dict: [N, Y]
- name: finance_org_type_property_requried_config_cust_role
  type: string
  desc: 金融机构类型（补充字段-是否必填 企业角色）
- name: sign_flag
  type: string
  desc: 接收跨贴牌数据是否强制重签授权书
  dict: [N, Y]
- name: main_tenant_flg_en
  type: string
  desc: 主定制项目标识
  dict: [HBLT, shendu]
- name: bank_branch
  type: string
  desc: 分行适用角色
- name: bank_branch_property_requried
  type: string
  desc: 银行分行名称（通用）（补充字段-是否必填）
  dict: [N, Y]
- name: bank_branch_property_requried_config_cust_role
  type: string
  desc: 银行分行名称（通用）（补充字段-是否必填 企业角色）
- name: oper_auth_agreement
  type: string
  desc: 子账户授权书
- name: migratory_flag
  type: string
  desc: 迁移标志
- name: project_code_required
  type: string
  desc: 项目码是否必填：Y/N
  dict: [N, Y]
- name: customer_card_type
  type: string
  desc: 客服名片类型：WX_WORK=发送企微名片，WX=发送微信名片，与operCardType枚举一致
  dict: [WX_WORK, WX]
  label: [发送企微名片, 发送微信名片]
- name: op_update_user
  type: string
  desc: 租户运营更新人
- name: op_update_time
  type: temporal
  desc: 租户运营更新时间
- name: ai_resource_color
  type: string
  desc: 智能客服按钮颜色
- name: generate_electronic_auth_flag
  type: string
  desc: 是否生成电子版授权书：Y-是，N-否
  dict: [N, Y]
  label: [否, 是]
- name: platform_sms_signature
  type: string
  desc: 产融平台短信签名(无方括号)
- name: adapt_colour
  type: string
  desc: 适配背景颜色
- name: access_mode
  type: string
  desc: 接入模式
  dict: [DIRECT_INIT]
- name: use_theme_after_login
  type: string
  desc: 登录后是否使用该色调：Y-是，N-否
  dict: [N, Y]
  label: [否, 是]
default_filter:
  predicate: tenant_setting_config.enable = 'Y'
  trust: confirmed
  evidence: code_path:TenantDomainService.java:344
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_project.id
right: tenant_setting_config.default_project_id
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:TenantAppliactionService.java:449
source: l1_code
join_role: identity
priority: primary
authenticity_note: 默认关联项目是租户配置上的项目主键。
```

## 页面链接

### 关联表

- [[tables/ca_fee_company]]
- [[tables/ca_fee_order]]
- [[tables/ca_fee_project_config]]
- [[tables/tenant_interworking_product]]
- [[tables/tenant_interworking_project]]
- [[tables/tenant_product]]
- [[tables/tenant_project]]
- [[tables/tenant_setting_config_share]]

### 字典

- [[dicts/tenant_setting_config__source]]（`tenant_setting_config.source`）
- [[dicts/tenant_setting_config__mp_sso_sys_channel]]（`tenant_setting_config.mp_sso_sys_channel`）
- [[dicts/tenant_setting_config__enable]]（`tenant_setting_config.enable`）
- [[dicts/tenant_setting_config__act_procinst_status]]（`tenant_setting_config.act_procinst_status`）
- [[dicts/tenant_setting_config__need_hfive]]（`tenant_setting_config.need_hfive`）
- [[dicts/tenant_setting_config__need_mp_wx]]（`tenant_setting_config.need_mp_wx`）
- [[dicts/tenant_setting_config__status]]（`tenant_setting_config.status`）
- [[dicts/tenant_setting_config__self_registration_flag]]（`tenant_setting_config.self_registration_flag`）
- [[dicts/tenant_setting_config__company_share_flag]]（`tenant_setting_config.company_share_flag`）
- [[dicts/tenant_setting_config__operator_ai_customer]]（`tenant_setting_config.operator_ai_customer`）
- [[dicts/tenant_setting_config__portal_flag]]（`tenant_setting_config.portal_flag`）
- [[dicts/tenant_setting_config__share_flag]]（`tenant_setting_config.share_flag`）
- [[dicts/tenant_setting_config__recall_auth_doc_flag]]（`tenant_setting_config.recall_auth_doc_flag`）
- [[dicts/tenant_setting_config__core_bosc_company_id_property_requried]]（`tenant_setting_config.core_bosc_company_id_property_requried`）
- [[dicts/tenant_setting_config__xib_factor_contract_no_property_requried]]（`tenant_setting_config.xib_factor_contract_no_property_requried`）
- [[dicts/tenant_setting_config__company_size_property_requried]]（`tenant_setting_config.company_size_property_requried`）
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
- [[dicts/tenant_setting_config__project_code_required]]（`tenant_setting_config.project_code_required`）
- [[dicts/tenant_setting_config__customer_card_type]]（`tenant_setting_config.customer_card_type`）
- [[dicts/tenant_setting_config__generate_electronic_auth_flag]]（`tenant_setting_config.generate_electronic_auth_flag`）
- [[dicts/tenant_setting_config__access_mode]]（`tenant_setting_config.access_mode`）
- [[dicts/tenant_setting_config__use_theme_after_login]]（`tenant_setting_config.use_theme_after_login`）
