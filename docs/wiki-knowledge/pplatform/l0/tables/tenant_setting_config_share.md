---
type: table
title: 共享租户配置
page_key: tenant_setting_config_share
belong: tables
status: draft
aliases: []
anchors:
- tenant_setting_config_share
sources:
- database_schema:lowcode_pplatform.tenant_setting_config_share
created: '2026-09-15'
updated: '2026-09-15'
contract_version: '0.1'
databases:
- lowcode_pplatform
recall: true
---

# 共享租户配置

L0 库侧合同（draft）。grain / 前缀簇 / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段簇

### common

`id`, `code`, `enable`, `remark`, `create_by`, `create_user`, `create_time`, `update_by`, `update_user`, `update_time`

### tenant_identity

`source_id`, `source`, `name`, `apaas_tenant_code`, `uni_social_credit_code`, `app_tenant_code`, `db_tenant_code`, `organization_id`, `tenant_flag_zh`, `tenant_flg_en`

### domain_env

`dev_domain`, `sit_domain`, `uat_domain`, `prd_domain`, `hfive_dev_domain`, `hfive_test_domain`, `hfive_uat_domain`, `hfive_prd_domain`

### brand_visual

`band_name`, `web_title`, `web_logo_url`, `pc_login_logo_path`, `pc_icon_path`, `pc_logo_path`, `pc_home_background_path`, `mp_home_background_path`, `mp_logo_path`, `pcimg_loginpage_bg_logo_url`, `pcimg_indexpage_bg_logo_url`, `pcimg_browser_tab_icon_url`, `pcimg_loginpage_banner_url`, `mobile_indexpage_bg_logo_url`, `main_theme_color`, `mobile_indexpage_logo_url`

### agreement

`privacy_policy_agreement`, `user_protocol_agreement`, `auth_agreement`, `person_auth_agreement`

### dbass

`dbass_app_id`, `mp_dbass_app_id`, `dbass_private_key`

### sso

`sso_sys_channel`, `sso_tenant_chanel`, `mp_sso_tenant_chanel`, `mp_sso_sys_channel`

### mp_account

`uat_mp_app_id`, `uat_mp_app_name`, `uat_mp_wx_login_name`, `uat_mp_wx_login_pwd`, `prd_mp_app_id`, `prd_mp_app_name`, `prd_mp_wx_login_name`, `prd_mp_wx_login_pwd`

### service_ops

`cust_service_number`, `platform_operator`, `operator_id`, `operator_name`, `operator_email`, `send_email`, `operator_ai_customer`, `operator_wechat_code`, `operator_qr_code`, `operator_applet_code`, `ai_zc_sysnum`, `ai_zc_channel`

### flag_status

`need_hfive`, `need_mp_wx`, `status`, `self_registration_flag`, `company_share_flag`, `portal_flag`, `share_flag`

### workflow

`act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `act_procinst_date`

## 字段

```ground:table
table: tenant_setting_config_share
database: lowcode_pplatform
description: 共享租户配置
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
  title: 通用/审计字段
  include: always
- key: tenant_identity
  title: 租户身份与标识
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: domain_env
  title: 环境域名
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: brand_visual
  title: 品牌外观与图片
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: agreement
  title: 协议与合规文本
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: dbass
  title: dbass 集成配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: sso
  title: SSO 渠道配置
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: mp_account
  title: 小程序与公众号账号
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: service_ops
  title: 客服与运营联系
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: flag_status
  title: 开关与生效状态
  confidence: proposed
  evidence: database_schema:lowcode_pplatform.tenant_setting_config_share
- key: workflow
  title: 审批流程
  confidence: proposed
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
  dictionary: tenant_setting_config_share_source
- name: name
  data_type: string
  description: 租户名称
  nullable: true
  cluster: tenant_identity
- name: band_name
  data_type: string
  description: 贴牌平台名称
  nullable: true
  cluster: brand_visual
- name: cust_service_number
  data_type: string
  description: 客服电话
  nullable: true
  cluster: service_ops
- name: web_title
  data_type: string
  description: 网站标题
  nullable: true
  cluster: brand_visual
- name: web_logo_url
  data_type: string
  description: 网站logo
  nullable: true
  cluster: brand_visual
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
  cluster: agreement
- name: user_protocol_agreement
  data_type: string
  description: 用户协议
  nullable: true
  cluster: agreement
- name: auth_agreement
  data_type: string
  description: 授权书协议
  nullable: true
  cluster: agreement
- name: apaas_tenant_code
  data_type: string
  description: aPaaS租户编码
  nullable: true
  cluster: tenant_identity
- name: dbass_app_id
  data_type: string
  description: dbassAppId
  nullable: true
  cluster: dbass
- name: mp_dbass_app_id
  data_type: string
  description: 小程序dbassAppId
  nullable: true
  cluster: dbass
- name: dbass_private_key
  data_type: string
  description: dbassPrivateKey
  nullable: true
  cluster: dbass
- name: sso_sys_channel
  data_type: string
  description: ssoSysChannel
  nullable: true
  cluster: sso
- name: sso_tenant_chanel
  data_type: string
  description: ssoTenantChanel
  nullable: true
  cluster: sso
- name: mp_sso_tenant_chanel
  data_type: string
  description: mpSsoTenantChanel
  nullable: true
  cluster: sso
- name: pc_login_logo_path
  data_type: string
  description: PC登录窗口横幅
  nullable: true
  cluster: brand_visual
- name: pc_icon_path
  data_type: string
  description: PC浏览器页签Icon
  nullable: true
  cluster: brand_visual
- name: pc_logo_path
  data_type: string
  description: PC内页logo
  nullable: true
  cluster: brand_visual
- name: pc_home_background_path
  data_type: string
  description: PC首页背景图
  nullable: true
  cluster: brand_visual
- name: mp_home_background_path
  data_type: string
  description: 小程序首页背景图
  nullable: true
  cluster: brand_visual
- name: mp_logo_path
  data_type: string
  description: 移动端首页logo
  nullable: true
  cluster: brand_visual
- name: mp_sso_sys_channel
  data_type: string
  description: mpSsoSysChannel
  nullable: true
  cluster: sso
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
  dictionary: tenant_setting_config_share_enable
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
  cluster: workflow
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
  cluster: workflow
- name: act_procinst_status
  data_type: string
  description: 当前审批状态
  nullable: true
  cluster: workflow
  dictionary: tenant_setting_config_share_act_procinst_status
- name: act_procinst_date
  data_type: temporal
  description: 审批结束时间
  nullable: true
  cluster: workflow
- name: organization_id
  data_type: string
  description: 机构编号
  nullable: true
  cluster: tenant_identity
- name: platform_operator
  data_type: string
  description: 平台运营方
  nullable: true
  cluster: service_ops
- name: pcimg_loginpage_bg_logo_url
  data_type: string
  description: PC首页背景图
  nullable: true
  cluster: brand_visual
- name: pcimg_indexpage_bg_logo_url
  data_type: string
  description: PC内页logo
  nullable: true
  cluster: brand_visual
- name: pcimg_browser_tab_icon_url
  data_type: string
  description: PC浏览器页签Icon
  nullable: true
  cluster: brand_visual
- name: pcimg_loginpage_banner_url
  data_type: string
  description: PC登录窗口横幅
  nullable: true
  cluster: brand_visual
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
  cluster: mp_account
- name: uat_mp_app_name
  data_type: string
  description: UAT小程序名称
  nullable: true
  cluster: mp_account
- name: uat_mp_wx_login_name
  data_type: string
  description: UAT公众登陆账号
  nullable: true
  cluster: mp_account
- name: uat_mp_wx_login_pwd
  data_type: string
  description: UAT公众号登录密码
  nullable: true
  cluster: mp_account
- name: prd_mp_app_id
  data_type: string
  description: 生产小程序appID
  nullable: true
  cluster: mp_account
- name: prd_mp_app_name
  data_type: string
  description: 生产小程序名称
  nullable: true
  cluster: mp_account
- name: prd_mp_wx_login_name
  data_type: string
  description: 生产公众号登录账号
  nullable: true
  cluster: mp_account
- name: prd_mp_wx_login_pwd
  data_type: string
  description: 生产公众号登录密码
  nullable: true
  cluster: mp_account
- name: need_hfive
  data_type: string
  description: 是否定制H5
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_need_hfive
- name: mobile_indexpage_bg_logo_url
  data_type: string
  description: 移动端首页背景图
  nullable: true
  cluster: brand_visual
- name: need_mp_wx
  data_type: string
  description: 是否定制小程序
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_need_mp_wx
- name: main_theme_color
  data_type: string
  description: 主题色
  nullable: true
  cluster: brand_visual
- name: status
  data_type: string
  description: 生效状态
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_status
- name: person_auth_agreement
  data_type: string
  description: 变更联系人授权书
  nullable: true
  cluster: agreement
- name: self_registration_flag
  data_type: string
  description: 是否放开自主注册
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_self_registration_flag
- name: company_share_flag
  data_type: string
  description: 客户认证数据是否可用于其他贴牌平台
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_company_share_flag
- name: mobile_indexpage_logo_url
  data_type: string
  description: 移动端首页logo
  nullable: true
  cluster: brand_visual
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
  cluster: service_ops
- name: operator_name
  data_type: string
  description: ''
  nullable: true
  cluster: service_ops
- name: operator_email
  data_type: string
  description: ''
  nullable: true
  cluster: service_ops
- name: send_email
  data_type: string
  description: ''
  nullable: true
  cluster: service_ops
- name: operator_ai_customer
  data_type: string
  description: ''
  nullable: true
  cluster: service_ops
- name: operator_wechat_code
  data_type: string
  description: 公众号码
  nullable: true
  cluster: service_ops
- name: operator_qr_code
  data_type: string
  description: 客服二维码
  nullable: true
  cluster: service_ops
- name: operator_applet_code
  data_type: string
  description: 客服小程序码
  nullable: true
  cluster: service_ops
- name: ai_zc_sysnum
  data_type: string
  description: 智能客服系统号
  nullable: true
  cluster: service_ops
- name: ai_zc_channel
  data_type: string
  description: 智能客服渠道号
  nullable: true
  cluster: service_ops
- name: portal_flag
  data_type: string
  description: 是否启用门户
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_portal_flag
- name: share_flag
  data_type: string
  description: 共享租户
  nullable: true
  cluster: flag_status
  dictionary: tenant_setting_config_share_share_flag
```
