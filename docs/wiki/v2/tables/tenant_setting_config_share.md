---
type: table
title: 共享租户配置
page_key: tenant_setting_config_share
belong: tables
status: draft
anchors: [tenant_setting_config_share]
sources: ['database_schema:lowcode_pplatform.tenant_setting_config_share']
created: '2026-09-17'
updated: '2026-09-17'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_setting_config, tenant_setting_config_share__source, tenant_setting_config_share__enable,
  tenant_setting_config_share__act_procinst_status, tenant_setting_config_share__tenant_flg_en,
  tenant_setting_config_share__need_hfive, tenant_setting_config_share__need_mp_wx,
  tenant_setting_config_share__status, tenant_setting_config_share__self_registration_flag,
  tenant_setting_config_share__company_share_flag, tenant_setting_config_share__portal_flag,
  tenant_setting_config_share__share_flag]
---

# 共享租户配置

L0 库侧合同（draft）。grain / 字段簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant_identity

`source_id`, `source`, `name`, `apaas_tenant_code`, `uni_social_credit_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `platform_operator`, `tenant_flag_zh`, `tenant_flg_en`

### brand_site

`band_name`, `web_title`, `web_logo_url`, `main_theme_color`

### domains

`dev_domain`, `sit_domain`, `uat_domain`, `prd_domain`, `hfive_dev_domain`, `hfive_test_domain`, `hfive_uat_domain`, `hfive_prd_domain`

### agreements

`privacy_policy_agreement`, `user_protocol_agreement`, `auth_agreement`, `person_auth_agreement`

### pc_assets

`pc_login_logo_path`, `pc_icon_path`, `pc_logo_path`, `pc_home_background_path`, `pcimg_loginpage_bg_logo_url`, `pcimg_indexpage_bg_logo_url`, `pcimg_browser_tab_icon_url`, `pcimg_loginpage_banner_url`

### mobile_assets

`mp_home_background_path`, `mp_logo_path`, `mobile_indexpage_bg_logo_url`, `mobile_indexpage_logo_url`

### mp_integration

`uat_mp_app_id`, `uat_mp_app_name`, `uat_mp_wx_login_name`, `uat_mp_wx_login_pwd`, `prd_mp_app_id`, `prd_mp_app_name`, `prd_mp_wx_login_name`, `prd_mp_wx_login_pwd`

### dbass

`dbass_app_id`, `mp_dbass_app_id`, `dbass_private_key`

### sso

`sso_sys_channel`, `sso_tenant_chanel`, `mp_sso_tenant_chanel`, `mp_sso_sys_channel`

### approval

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

### flags

`need_hfive`, `need_mp_wx`, `status`, `self_registration_flag`, `company_share_flag`, `portal_flag`, `share_flag`

### contact_service

`cust_service_number`, `operator_id`, `operator_name`, `operator_email`, `send_email`, `operator_ai_customer`, `operator_wechat_code`, `operator_qr_code`, `operator_applet_code`, `ai_zc_sysnum`, `ai_zc_channel`

## 字段

```ground:table
table: tenant_setting_config_share
database: lowcode_pplatform
description: 共享租户配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, band_name, uni_social_credit_code, uat_mp_app_name, uat_mp_wx_login_name,
  prd_mp_app_name, prd_mp_wx_login_name, operator_name, operator_wechat_code, operator_qr_code,
  operator_applet_code]
clusters:
- key: common
  title: 通用
  include: always
- key: tenant_identity
  title: 租户身份与来源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: brand_site
  title: 站点品牌
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: domains
  title: 环境域名
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: agreements
  title: 协议文档
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: pc_assets
  title: PC端页面资源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: mobile_assets
  title: 移动端页面资源
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: mp_integration
  title: 小程序与公众号接入
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: dbass
  title: dbass应用接入
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: sso
  title: SSO单点登录渠道
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: approval
  title: 审批流程
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: flags
  title: 状态与开关
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: contact_service
  title: 客服与运营联系
  trust: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
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
  cluster: tenant_identity
- name: source
  data_type: string
  description: 租户来源
  cluster: tenant_identity
  dictionary: tenant_setting_config_share__source
- name: name
  data_type: string
  description: 租户名称
  cluster: tenant_identity
- name: band_name
  data_type: string
  description: 贴牌平台名称
  cluster: brand_site
- name: cust_service_number
  data_type: string
  description: 客服电话
  cluster: contact_service
- name: web_title
  data_type: string
  description: 网站标题
  cluster: brand_site
- name: web_logo_url
  data_type: string
  description: 网站logo
  cluster: brand_site
- name: dev_domain
  data_type: string
  description: 开发环境域名
  cluster: domains
- name: sit_domain
  data_type: string
  description: 测试环境域名
  cluster: domains
- name: uat_domain
  data_type: string
  description: UAT环境域名
  cluster: domains
- name: prd_domain
  data_type: string
  description: 生产环境域名
  cluster: domains
- name: privacy_policy_agreement
  data_type: string
  description: 隐私协议
  cluster: agreements
- name: user_protocol_agreement
  data_type: string
  description: 用户协议
  cluster: agreements
- name: auth_agreement
  data_type: string
  description: 授权书协议
  cluster: agreements
- name: apaas_tenant_code
  data_type: string
  description: aPaaS租户编码
  cluster: tenant_identity
- name: dbass_app_id
  data_type: string
  description: dbassAppId
  cluster: dbass
- name: mp_dbass_app_id
  data_type: string
  description: 小程序dbassAppId
  cluster: dbass
- name: dbass_private_key
  data_type: string
  description: dbassPrivateKey
  cluster: dbass
- name: sso_sys_channel
  data_type: string
  description: ssoSysChannel
  cluster: sso
- name: sso_tenant_chanel
  data_type: string
  description: ssoTenantChanel
  cluster: sso
- name: mp_sso_tenant_chanel
  data_type: string
  description: mpSsoTenantChanel
  cluster: sso
- name: pc_login_logo_path
  data_type: string
  description: PC登录窗口横幅
  cluster: pc_assets
- name: pc_icon_path
  data_type: string
  description: PC浏览器页签Icon
  cluster: pc_assets
- name: pc_logo_path
  data_type: string
  description: PC内页logo
  cluster: pc_assets
- name: pc_home_background_path
  data_type: string
  description: PC首页背景图
  cluster: pc_assets
- name: mp_home_background_path
  data_type: string
  description: 小程序首页背景图
  cluster: mobile_assets
- name: mp_logo_path
  data_type: string
  description: 移动端首页logo
  cluster: mobile_assets
- name: mp_sso_sys_channel
  data_type: string
  description: mpSsoSysChannel
  cluster: sso
- name: uni_social_credit_code
  data_type: string
  description: 统一社会信用证
  cluster: tenant_identity
- name: enable
  data_type: string
  description: enable
  cluster: common
  dictionary: tenant_setting_config_share__enable
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
  cluster: tenant_identity
- name: db_tenant_code
  data_type: string
  description: 数据租户标识
  cluster: tenant_identity
- name: act_procinst_no
  data_type: string
  description: 流程申请编号
  cluster: approval
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  cluster: approval
  dictionary: tenant_setting_config_share__act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  cluster: approval
- name: organization_id
  data_type: string
  description: 机构编号
  cluster: tenant_identity
- name: platform_operator
  data_type: string
  description: 平台运营方
  cluster: tenant_identity
- name: pcimg_loginpage_bg_logo_url
  data_type: string
  description: PC首页背景图
  cluster: pc_assets
- name: pcimg_indexpage_bg_logo_url
  data_type: string
  description: PC内页logo
  cluster: pc_assets
- name: pcimg_browser_tab_icon_url
  data_type: string
  description: PC浏览器页签Icon
  cluster: pc_assets
- name: pcimg_loginpage_banner_url
  data_type: string
  description: PC登录窗口横幅
  cluster: pc_assets
- name: tenant_flag_zh
  data_type: string
  description: 项目标识（中文）
  cluster: tenant_identity
- name: tenant_flg_en
  data_type: string
  description: 项目标识（英文）
  cluster: tenant_identity
  dictionary: tenant_setting_config_share__tenant_flg_en
- name: uat_mp_app_id
  data_type: string
  description: UAT小程序appID
  cluster: mp_integration
- name: uat_mp_app_name
  data_type: string
  description: UAT小程序名称
  cluster: mp_integration
- name: uat_mp_wx_login_name
  data_type: string
  description: UAT公众登陆账号
  cluster: mp_integration
- name: uat_mp_wx_login_pwd
  data_type: string
  description: UAT公众号登录密码
  cluster: mp_integration
- name: prd_mp_app_id
  data_type: string
  description: 生产小程序appID
  cluster: mp_integration
- name: prd_mp_app_name
  data_type: string
  description: 生产小程序名称
  cluster: mp_integration
- name: prd_mp_wx_login_name
  data_type: string
  description: 生产公众号登录账号
  cluster: mp_integration
- name: prd_mp_wx_login_pwd
  data_type: string
  description: 生产公众号登录密码
  cluster: mp_integration
- name: need_hfive
  data_type: string
  description: 是否定制H5
  cluster: flags
  dictionary: tenant_setting_config_share__need_hfive
- name: mobile_indexpage_bg_logo_url
  data_type: string
  description: 移动端首页背景图
  cluster: mobile_assets
- name: need_mp_wx
  data_type: string
  description: 是否定制小程序
  cluster: flags
  dictionary: tenant_setting_config_share__need_mp_wx
- name: main_theme_color
  data_type: string
  description: 主题色
  cluster: brand_site
- name: status
  data_type: string
  description: 生效状态
  cluster: flags
  dictionary: tenant_setting_config_share__status
- name: person_auth_agreement
  data_type: string
  description: 变更联系人授权书
  cluster: agreements
- name: self_registration_flag
  data_type: string
  description: 是否放开自主注册
  cluster: flags
  dictionary: tenant_setting_config_share__self_registration_flag
- name: company_share_flag
  data_type: string
  description: 客户认证数据是否可用于其他贴牌平台
  cluster: flags
  dictionary: tenant_setting_config_share__company_share_flag
- name: mobile_indexpage_logo_url
  data_type: string
  description: 移动端首页logo
  cluster: mobile_assets
- name: hfive_dev_domain
  data_type: string
  description: H5开发环境域名
  cluster: domains
- name: hfive_test_domain
  data_type: string
  description: H5测试环境域名
  cluster: domains
- name: hfive_uat_domain
  data_type: string
  description: H5UAT环境域名
  cluster: domains
- name: hfive_prd_domain
  data_type: string
  description: H5生产环境域名
  cluster: domains
- name: operator_id
  data_type: string
  cluster: contact_service
- name: operator_name
  data_type: string
  cluster: contact_service
- name: operator_email
  data_type: string
  cluster: contact_service
- name: send_email
  data_type: string
  cluster: contact_service
- name: operator_ai_customer
  data_type: string
  cluster: contact_service
- name: operator_wechat_code
  data_type: string
  description: 公众号码
  cluster: contact_service
- name: operator_qr_code
  data_type: string
  description: 客服二维码
  cluster: contact_service
- name: operator_applet_code
  data_type: string
  description: 客服小程序码
  cluster: contact_service
- name: ai_zc_sysnum
  data_type: string
  description: 智能客服系统号
  cluster: contact_service
- name: ai_zc_channel
  data_type: string
  description: 智能客服渠道号
  cluster: contact_service
- name: portal_flag
  data_type: string
  description: 是否启用门户
  cluster: flags
  dictionary: tenant_setting_config_share__portal_flag
- name: share_flag
  data_type: string
  description: 共享租户
  cluster: flags
  dictionary: tenant_setting_config_share__share_flag
```

## 关联关系

### unknown — 待复核

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.code
right: tenant_setting_config_share.apaas_tenant_code
cardinality: one_to_many
trust: proposed
authenticity: unknown
evidence: database_schema:lowcode_pplatform.tenant_setting_config_share.apaas_tenant_code
source: llm
join_role: business_code
priority: primary
name_evidence:
  match: llm_propose
  stem: apaas_tenant_code
  comment: 码对码：aPaaS租户编码 ↔ 租户配置编码，注释同涉租户；overlap 未探明(sample 0)，仅作候选边不升格
overlap:
  probed: true
  sample_size: 0
  authenticity: unknown
authenticity_note: 码对码：aPaaS租户编码 ↔ 租户配置编码，注释同涉租户；overlap 未探明(sample 0)，仅作候选边不升格
```

## 页面链接

### 关联表

- [[tables/tenant_setting_config]]

### 字典

- [[dicts/tenant_setting_config_share__source]]（`tenant_setting_config_share.source`）
- [[dicts/tenant_setting_config_share__enable]]（`tenant_setting_config_share.enable`）
- [[dicts/tenant_setting_config_share__act_procinst_status]]（`tenant_setting_config_share.act_procinst_status`）
- [[dicts/tenant_setting_config_share__tenant_flg_en]]（`tenant_setting_config_share.tenant_flg_en`）
- [[dicts/tenant_setting_config_share__need_hfive]]（`tenant_setting_config_share.need_hfive`）
- [[dicts/tenant_setting_config_share__need_mp_wx]]（`tenant_setting_config_share.need_mp_wx`）
- [[dicts/tenant_setting_config_share__status]]（`tenant_setting_config_share.status`）
- [[dicts/tenant_setting_config_share__self_registration_flag]]（`tenant_setting_config_share.self_registration_flag`）
- [[dicts/tenant_setting_config_share__company_share_flag]]（`tenant_setting_config_share.company_share_flag`）
- [[dicts/tenant_setting_config_share__portal_flag]]（`tenant_setting_config_share.portal_flag`）
- [[dicts/tenant_setting_config_share__share_flag]]（`tenant_setting_config_share.share_flag`）
