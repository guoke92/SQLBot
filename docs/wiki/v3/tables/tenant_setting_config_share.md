---
type: table
title: 共享租户配置
page_key: tenant_setting_config_share
belong: tables
status: draft
anchors:
- tenant_setting_config_share
sources:
- database_schema:lowcode_pplatform.tenant_setting_config_share
created: '2026-09-21'
updated: '2026-09-23'
contract_version: '0.1'
databases:
- lowcode_pplatform
related:
- tenant_setting_config
- tenant_setting_config_share__enable
- tenant_setting_config_share__act_procinst_status
- tenant_setting_config_share__need_hfive
- tenant_setting_config_share__need_mp_wx
- tenant_setting_config_share__status
- tenant_setting_config_share__self_registration_flag
- tenant_setting_config_share__company_share_flag
- tenant_setting_config_share__portal_flag
- tenant_setting_config_share__share_flag
---
# 共享租户配置

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: tenant_setting_config_share
database: lowcode_pplatform
desc: 共享租户配置
inactive: false
primary_key:
- id
grain: 共享租户配置副本（apaas 生成，业务侧少查）
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
  dict:
  - ACFLOW
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
- name: uni_social_credit_code
  type: string
  desc: 统一社会信用证
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
  dict:
  - N
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
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: mobile_indexpage_bg_logo_url
  type: string
  desc: 移动端首页背景图
- name: need_mp_wx
  type: string
  desc: 是否定制小程序
  dict:
  - N
  - Y
  label:
    N: 否
    Y: 是
- name: main_theme_color
  type: string
  desc: 主题色
- name: status
  type: string
  desc: 生效状态
  dict:
  - N
  label:
  - 否
- name: person_auth_agreement
  type: string
  desc: 变更联系人授权书
- name: self_registration_flag
  type: string
  desc: 是否放开自主注册
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: company_share_flag
  type: string
  desc: 客户认证数据是否可用于其他贴牌平台
  dict:
  - Y
  - N
  label:
  - 是
  - 否
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
  dict:
  - Y
  - N
  label:
  - 是
  - 否
- name: share_flag
  type: string
  desc: 共享租户
  dict:
  - N
  - Y
  label:
  - 否
  - 是
```


## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.dbass_app_id
right: tenant_setting_config_share.dbass_app_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: live_validate:fk_like;reextract:共享租户与租户配置
source: reextract_joins
join_role: business_code
priority: primary
authenticity_note: 共享租户与租户配置
```
## 页面链接

### 关联表

- [[tables/tenant_setting_config]]

### 字典

- [[dicts/tenant_setting_config_share__source]]（`tenant_setting_config_share.source`）
- [[dicts/tenant_setting_config_share__enable]]（`tenant_setting_config_share.enable`）
- [[dicts/tenant_setting_config_share__act_procinst_status]]（`tenant_setting_config_share.act_procinst_status`）
- [[dicts/tenant_setting_config_share__need_hfive]]（`tenant_setting_config_share.need_hfive`）
- [[dicts/tenant_setting_config_share__need_mp_wx]]（`tenant_setting_config_share.need_mp_wx`）
- [[dicts/tenant_setting_config_share__status]]（`tenant_setting_config_share.status`）
- [[dicts/tenant_setting_config_share__self_registration_flag]]（`tenant_setting_config_share.self_registration_flag`）
- [[dicts/tenant_setting_config_share__company_share_flag]]（`tenant_setting_config_share.company_share_flag`）
- [[dicts/tenant_setting_config_share__portal_flag]]（`tenant_setting_config_share.portal_flag`）
- [[dicts/tenant_setting_config_share__share_flag]]（`tenant_setting_config_share.share_flag`）
