---
type: table
title: 共享租户配置
page_key: tenant_setting_config_share
domain: 租户配置/灰度/运营邮件
status: draft
anchors: [tenant_setting_config_share]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 共享租户配置

（基线页：86 字段，行数估计 29。行语义/常用过滤待语义摄取增强。）

```ground:table
table: tenant_setting_config_share
database: lowcode_pplatform
desc: 共享租户配置
fields:
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: company_share_flag
    type: string
    phys: varchar(4)
    desc: 客户认证数据是否可用于其他贴牌平台
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: need_hfive
    type: string
    phys: varchar(4)
    desc: 是否定制H5
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: need_mp_wx
    type: string
    phys: varchar(4)
    desc: 是否定制小程序
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: portal_flag
    type: string
    phys: varchar(4)
    desc: 是否启用门户
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: self_registration_flag
    type: string
    phys: varchar(64)
    desc: 是否放开自主注册
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: share_flag
    type: string
    phys: varchar(4)
    desc: 共享租户
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: status
    type: string
    phys: varchar(4)
    desc: 生效状态
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: 流程申请编号
  - name: ai_zc_channel
    type: string
    phys: varchar(64)
    desc: 智能客服渠道号
  - name: ai_zc_sysnum
    type: string
    phys: varchar(64)
    desc: 智能客服系统号
  - name: apaas_tenant_code
    type: string
    phys: varchar(128)
    desc: aPaaS租户编码
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
  - name: auth_agreement
    type: string
    phys: varchar(64)
    desc: 授权书协议
    topk: "CT-202404081721209495040"
  - name: band_name
    type: string
    phys: varchar(128)
    desc: 贴牌平台名称
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_service_number
    type: string
    phys: varchar(64)
    desc: 客服电话
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "beehive-scf.qhhrly.cn"
  - name: dbass_app_id
    type: string
    phys: varchar(128)
    desc: dbassAppId
  - name: dbass_private_key
    type: string
    phys: varchar(2048)
    desc: dbassPrivateKey
  - name: dev_domain
    type: string
    phys: varchar(256)
    desc: 开发环境域名
  - name: hfive_dev_domain
    type: string
    phys: varchar(256)
    desc: H5开发环境域名
  - name: hfive_prd_domain
    type: string
    phys: varchar(256)
    desc: H5生产环境域名
  - name: hfive_test_domain
    type: string
    phys: varchar(256)
    desc: H5测试环境域名
  - name: hfive_uat_domain
    type: string
    phys: varchar(256)
    desc: H5UAT环境域名
  - name: main_theme_color
    type: string
    phys: varchar(32)
    desc: 主题色
  - name: mobile_indexpage_bg_logo_url
    type: string
    phys: text
    desc: 移动端首页背景图
  - name: mobile_indexpage_logo_url
    type: string
    phys: text
    desc: 移动端首页logo
  - name: mp_dbass_app_id
    type: string
    phys: varchar(128)
    desc: 小程序dbassAppId
  - name: mp_home_background_path
    type: string
    phys: text
    desc: 小程序首页背景图
  - name: mp_logo_path
    type: string
    phys: text
    desc: 移动端首页logo
  - name: mp_sso_sys_channel
    type: string
    phys: varchar(128)
    desc: mpSsoSysChannel
  - name: mp_sso_tenant_chanel
    type: string
    phys: varchar(128)
    desc: mpSsoTenantChanel
  - name: name
    type: string
    phys: varchar(128)
    desc: 租户名称
  - name: operator_ai_customer
    type: string
    phys: varchar(100)
  - name: operator_applet_code
    type: string
    phys: varchar(1024)
    desc: 客服小程序码
  - name: operator_email
    type: string
    phys: varchar(100)
  - name: operator_id
    type: string
    phys: varchar(100)
  - name: operator_name
    type: string
    phys: varchar(100)
  - name: operator_qr_code
    type: string
    phys: varchar(1024)
    desc: 客服二维码
  - name: operator_wechat_code
    type: string
    phys: varchar(1024)
    desc: 公众号码
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: pc_home_background_path
    type: string
    phys: text
    desc: PC首页背景图
  - name: pc_icon_path
    type: string
    phys: text
    desc: PC浏览器页签Icon
  - name: pc_login_logo_path
    type: string
    phys: text
    desc: PC登录窗口横幅
  - name: pc_logo_path
    type: string
    phys: text
    desc: PC内页logo
  - name: pcimg_browser_tab_icon_url
    type: string
    phys: text
    desc: PC浏览器页签Icon
  - name: pcimg_indexpage_bg_logo_url
    type: string
    phys: text
    desc: PC内页logo
  - name: pcimg_loginpage_banner_url
    type: string
    phys: text
    desc: PC登录窗口横幅
  - name: pcimg_loginpage_bg_logo_url
    type: string
    phys: text
    desc: PC首页背景图
  - name: person_auth_agreement
    type: string
    phys: varchar(64)
    desc: 变更联系人授权书
    topk: "CT-202404081721209495040"
  - name: platform_operator
    type: string
    phys: varchar(32)
    desc: 平台运营方
  - name: prd_domain
    type: string
    phys: varchar(256)
    desc: 生产环境域名
  - name: prd_mp_app_id
    type: string
    phys: varchar(128)
    desc: 生产小程序appID
  - name: prd_mp_app_name
    type: string
    phys: varchar(128)
    desc: 生产小程序名称
  - name: prd_mp_wx_login_name
    type: string
    phys: varchar(128)
    desc: 生产公众号登录账号
    topk: "guolil2021@126.com|serxfh"
  - name: prd_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: 生产公众号登录密码
    topk: "Aa11111.|lls16888"
  - name: privacy_policy_agreement
    type: string
    phys: varchar(64)
    desc: 隐私协议
    topk: "CT-202405311653384958102"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: send_email
    type: string
    phys: varchar(100)
  - name: sit_domain
    type: string
    phys: varchar(256)
    desc: 测试环境域名
  - name: source
    type: string
    phys: varchar(32)
    desc: 租户来源
    topk: "ACFLOW"
  - name: source_id
    type: string
    phys: varchar(32)
    desc: 租户来源id
  - name: sso_sys_channel
    type: string
    phys: varchar(128)
    desc: ssoSysChannel
  - name: sso_tenant_chanel
    type: string
    phys: varchar(128)
    desc: ssoTenantChanel
  - name: tenant_flag_zh
    type: string
    phys: varchar(128)
    desc: 项目标识（中文）
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: uat_domain
    type: string
    phys: varchar(256)
    desc: UAT环境域名
  - name: uat_mp_app_id
    type: string
    phys: varchar(128)
    desc: UAT小程序appID
  - name: uat_mp_app_name
    type: string
    phys: varchar(128)
    desc: UAT小程序名称
  - name: uat_mp_wx_login_name
    type: string
    phys: varchar(128)
    desc: UAT公众登陆账号
    topk: "dshk|guolil2021@126.com"
  - name: uat_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: UAT公众号登录密码
    topk: "Aa11111.|Gl920326"
  - name: uni_social_credit_code
    type: string
    phys: varchar(128)
    desc: 统一社会信用证
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
  - name: user_protocol_agreement
    type: string
    phys: varchar(64)
    desc: 用户协议
    topk: "CT-202405211357559370074"
  - name: web_logo_url
    type: string
    phys: text
    desc: 网站logo
  - name: web_title
    type: string
    phys: varchar(128)
    desc: 网站标题
```
