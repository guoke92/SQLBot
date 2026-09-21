---
type: table
title: 共享租户配置
page_key: tenant_setting_config_share
belong: tables
status: draft
anchors: [tenant_setting_config_share]
sources: ['database_schema:lowcode_pplatform.tenant_setting_config_share']
created: '2026-09-20'
updated: '2026-09-20'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [tenant_setting_config_share__code, tenant_setting_config_share__source_id,
  tenant_setting_config_share__source, tenant_setting_config_share__cust_service_number,
  tenant_setting_config_share__privacy_policy_agreement, tenant_setting_config_share__user_protocol_agreement,
  tenant_setting_config_share__auth_agreement, tenant_setting_config_share__dbass_app_id,
  tenant_setting_config_share__enable, tenant_setting_config_share__act_procinst_status,
  tenant_setting_config_share__tenant_flg_en, tenant_setting_config_share__uat_mp_app_id,
  tenant_setting_config_share__prd_mp_app_id, tenant_setting_config_share__need_hfive,
  tenant_setting_config_share__need_mp_wx, tenant_setting_config_share__status, tenant_setting_config_share__person_auth_agreement,
  tenant_setting_config_share__self_registration_flag, tenant_setting_config_share__company_share_flag,
  tenant_setting_config_share__portal_flag, tenant_setting_config_share__share_flag]
---

# 共享租户配置

L0 库侧合同（draft）。grain / 身份束关系均为 proposed，不得当认证 JOIN。

## 字段

```ground:table
table: tenant_setting_config_share
database: lowcode_pplatform
desc: 共享租户配置
inactive: false
primary_key: [id]
grain: 一行一记录（id）
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
  dict: [588b10dfc1394e3cab2425bb75e32401, c5f1dda347dd43aeaafff9f85a776855, 7ec6cd3c49894ac094c5e57367bf2f89,
    f8bbfcfffde4460380677bb04cf63ae8, 09a8f067d6c14e6eade8b24f1ce0615e, a6c9dbf3c4f145ecbf6539133cfb26d0,
    547f3006754b46d5a5a995a1b14bbf5e, c5efb99e854749febf64f2e633e2fc12, 6ed5745b4ec947848ee53c310692655c,
    e93f7a105bd34d99aac6232e0fdb2875, 974d473e73754925b1bfd737decf7bb0, 4e96ca4e9a59481bbfa45305cf6fdd19,
    bfdf9141f7454175bbc6d7e2b36dcbfe, 6ad1fcd18e1a4fc2870d7e236810494b, e229b2687c02409f8a730a7185783b0f,
    9278d4dfa17845fc8b4e7abddd539909, 291cf37d756044b1bb05e6ecfc3b38d0, b4065366c1ec4d6db1e81b24d83c0c07,
    62564b6790aa4d949e49a36cffd00be8, d7aa0e5cbfd44f71b79734740aa99588, 925693fdf69d4f0f9753225c84d841c3,
    20f68c6a9559400c84ad5982cf1f6e63, ab46bdfbc4ab492fb6d2e4f8c6691f96, 609cc1746f3d42f0a31bb3235f14128c,
    d24740df39ad4f6eb7be61e78b507bee, 8855fea4d6ed4fbb9f47e3a940d59124, fd958bc7b2564a0ab469368e56984122,
    1b499346ac034c5fa26f862945d3df3c, aa4c8bc5ea374c28bd13e26c71e89bad]
- name: source_id
  type: string
  desc: 租户来源id
  dict: ['105', '134', '116', '6931911680490856448', '102', '130', '112', '145', '125',
    '109', '141', '120', '6972474653471547392', '106', '139', '117', '6950272254899298304',
    '104', '133', '115', '146', '126', '110', '144', '121', '108', '140', '119', '6952907435533062144']
- name: source
  type: string
  desc: 租户来源
  dict: [ACFLOW]
- name: name
  type: string
  desc: 租户名称
- name: band_name
  type: string
  desc: 贴牌平台名称
- name: cust_service_number
  type: string
  desc: 客服电话
  dict: [400 025 0059, 0755-86951497]
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
  dict: [CT-202405311653384958102]
- name: user_protocol_agreement
  type: string
  desc: 用户协议
  dict: [CT-202405211357559370074]
- name: auth_agreement
  type: string
  desc: 授权书协议
  dict: [CT-202404081721209495040]
- name: apaas_tenant_code
  type: string
  desc: aPaaS租户编码
- name: dbass_app_id
  type: string
  desc: dbassAppId
  dict: [app_ChanRongPin336_20240529]
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
  dict: [huishangbank, hxfl, abc, jjbank, ahf, KTC, bankofdl, lande, beehiveBg, lybank,
    beehiveICBC, njsteel, bitland, psbc, boc, rongwin, bocom, scbCommon, ceb, sdhs,
    citicbank, sneb, czbank, spdb, dyr, uwlaser, gtdb, zybank, hsbc]
- name: uat_mp_app_id
  type: string
  desc: UAT小程序appID
  dict: [wx3bd724e38dc5df9c, wxd4e6b0c088fb4355, '5434341', wx5a4621f15abc7462, wxdb453231b9e2a54f]
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
  dict: [wx0821ca938ea7f8ee, wx2e8254825b33f21e, '85546', wxbb4672250373e63d, wxab90faadcc845329]
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
  dict: [Y]
- name: mobile_indexpage_bg_logo_url
  type: string
  desc: 移动端首页背景图
- name: need_mp_wx
  type: string
  desc: 是否定制小程序
  dict: [N, Y]
- name: main_theme_color
  type: string
  desc: 主题色
- name: status
  type: string
  desc: 生效状态
  dict: [N]
- name: person_auth_agreement
  type: string
  desc: 变更联系人授权书
  dict: [CT-202404081721209495040]
- name: self_registration_flag
  type: string
  desc: 是否放开自主注册
  dict: [Y]
- name: company_share_flag
  type: string
  desc: 客户认证数据是否可用于其他贴牌平台
  dict: [Y]
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
  dict: [Y, N]
- name: share_flag
  type: string
  desc: 共享租户
  dict: [N]
```

## 页面链接

### 字典

- [[dicts/tenant_setting_config_share__code]]（`tenant_setting_config_share.code`）
- [[dicts/tenant_setting_config_share__source_id]]（`tenant_setting_config_share.source_id`）
- [[dicts/tenant_setting_config_share__source]]（`tenant_setting_config_share.source`）
- [[dicts/tenant_setting_config_share__cust_service_number]]（`tenant_setting_config_share.cust_service_number`）
- [[dicts/tenant_setting_config_share__privacy_policy_agreement]]（`tenant_setting_config_share.privacy_policy_agreement`）
- [[dicts/tenant_setting_config_share__user_protocol_agreement]]（`tenant_setting_config_share.user_protocol_agreement`）
- [[dicts/tenant_setting_config_share__auth_agreement]]（`tenant_setting_config_share.auth_agreement`）
- [[dicts/tenant_setting_config_share__dbass_app_id]]（`tenant_setting_config_share.dbass_app_id`）
- [[dicts/tenant_setting_config_share__enable]]（`tenant_setting_config_share.enable`）
- [[dicts/tenant_setting_config_share__act_procinst_status]]（`tenant_setting_config_share.act_procinst_status`）
- [[dicts/tenant_setting_config_share__tenant_flg_en]]（`tenant_setting_config_share.tenant_flg_en`）
- [[dicts/tenant_setting_config_share__uat_mp_app_id]]（`tenant_setting_config_share.uat_mp_app_id`）
- [[dicts/tenant_setting_config_share__prd_mp_app_id]]（`tenant_setting_config_share.prd_mp_app_id`）
- [[dicts/tenant_setting_config_share__need_hfive]]（`tenant_setting_config_share.need_hfive`）
- [[dicts/tenant_setting_config_share__need_mp_wx]]（`tenant_setting_config_share.need_mp_wx`）
- [[dicts/tenant_setting_config_share__status]]（`tenant_setting_config_share.status`）
- [[dicts/tenant_setting_config_share__person_auth_agreement]]（`tenant_setting_config_share.person_auth_agreement`）
- [[dicts/tenant_setting_config_share__self_registration_flag]]（`tenant_setting_config_share.self_registration_flag`）
- [[dicts/tenant_setting_config_share__company_share_flag]]（`tenant_setting_config_share.company_share_flag`）
- [[dicts/tenant_setting_config_share__portal_flag]]（`tenant_setting_config_share.portal_flag`）
- [[dicts/tenant_setting_config_share__share_flag]]（`tenant_setting_config_share.share_flag`）
