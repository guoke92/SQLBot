---
type: table
title: 租户配置
page_key: tenant_setting_config
domain: 租户配置/灰度/运营邮件
status: draft
anchors: [tenant_setting_config]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












tenant_setting_config 以 `db_tenant_code` 为主键维度保存租户级设置：`sso_tenant_chanel` 指定 SSO 租户渠道，`platform_secret_key` 保存平台密钥，`band_name` 为品牌名称，`platform_operator` 以 JSON 数组保存平台运营方配置。租户编码同时出现在 [[cust_company_info]]、[[cust_person_info]]、[[tenant_product]] 等表上，是内部服务跨表判定租户归属的公共维度。

## 需求背景
同一套内部服务要为多个租户提供服务，登录渠道、品牌展示与密钥必须按租户隔离；平台运营方以 JSON 数组形式配置，意味着读取该字段的服务需按数组结构解析。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: tenant_setting_config
database: lowcode_pplatform
desc: 租户配置
fields:
  - name: access_mode
    type: string
    phys: varchar(64)
    desc: 接入模式
    dict: access_mode
    topk: "DIRECT_INIT"
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: bank_branch_property_requried
    type: string
    phys: varchar(2)
    desc: 银行分行名称（通用）（补充字段-是否必填）
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: billing_type_property_requried
    type: string
    phys: varchar(4)
    desc: 开票类型（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: cash_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: 中原融资合同编号（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: company_share_flag
    type: string
    phys: varchar(4)
    desc: 客户认证数据是否可用于其他贴牌平台
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: company_size_property_requried
    type: string
    phys: varchar(4)
    desc: 增值税纳税人类别（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: composite_field_property_requried
    type: string
    phys: varchar(4)
    desc: 工行供应链编号（补充字段-是否必填）
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: core_bosc_company_id_property_requried
    type: string
    phys: varchar(4)
    desc: 关联核心企业（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: customer_card_type
    type: string
    phys: varchar(32)
    desc: 客服名片类型：WX_WORK=发送企微名片，WX=发送微信名片，与operCardType枚举一致
    dict: customer_card_type
    topk: "WX|WX_WORK"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: finance_org_type_property_requried
    type: string
    phys: varchar(2)
    desc: 金融机构类型（补充字段-是否必填）
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: generate_electronic_auth_flag
    type: string
    phys: varchar(1)
    desc: 是否生成电子版授权书：Y-是，N-否
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: is_stack
    type: string
    phys: varchar(64)
    desc: 是否存量数据
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: lybank_cash_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: 洛阳融资合同编号（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: need_hfive
    type: string
    phys: varchar(4)
    desc: 是否定制H5
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_mp_wx
    type: string
    phys: varchar(4)
    desc: 是否定制小程序
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: operator_ai_customer
    type: string
    phys: varchar(100)
    desc: 是否开启智能客服
    dict: operator_ai_customer
    topk: "0|1"
    labels: "0:否|1:是"
  - name: portal_flag
    type: string
    phys: varchar(4)
    desc: 是否启用门户
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: project_code_required
    type: string
    phys: varchar(1)
    desc: 项目码是否必填：Y/N
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: pushing_status
    type: string
    phys: varchar(2)
    desc: 租户推送状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: recall_auth_doc_flag
    type: string
    phys: varchar(64)
    desc: 是否需回收授权书标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: self_registration_flag
    type: string
    phys: varchar(64)
    desc: 是否放开自主注册
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: send_email
    type: string
    phys: varchar(100)
    desc: 是否发送邮件
    dict: tenant_setting_config__send_email
    topk: "0|1"
    labels: "0:否|1:是"
  - name: share_flag
    type: string
    phys: varchar(2)
    desc: 租户共享标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: sign_flag
    type: string
    phys: varchar(10)
    desc: 接收跨贴牌数据是否强制重签授权书
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: source
    type: string
    phys: varchar(32)
    desc: 租户来源
    dict: tenant_setting_config__source
    topk: "ACFLOW|pplatform"
  - name: status
    type: string
    phys: varchar(4)
    desc: 生效状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: use_theme_after_login
    type: string
    phys: varchar(1)
    desc: 登录后是否使用该色调：Y-是，N-否
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: xib_factor_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: 厦银保理合同编号（补充字段-是否必填）
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: zybank_cash_contract_amt_property_requried
    type: string
    phys: varchar(4)
    desc: 中原融资合同金额（补充字段-是否必填）
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
  - name: adapt_colour
    type: string
    phys: varchar(32)
    desc: 适配背景颜色
  - name: ai_resource_color
    type: string
    phys: varchar(20)
    desc: 智能客服按钮颜色
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
    topk: "CT-202404031808238683649|CT-202404081721209495040|CT-202503131441009438408|DT_202503191068|DT_202503251071|DT_202503271081|DT_202503283479|DT_202503303499|DT_202505230361|DT_202507181127|DT_202511253668|DT_202609071513"
  - name: band_name
    type: string
    phys: varchar(128)
    desc: 贴牌平台名称
  - name: bank_branch
    type: string
    phys: varchar(100)
    desc: 分行适用角色
  - name: bank_branch_property_requried_config_cust_role
    type: string
    phys: varchar(250)
    desc: 银行分行名称（通用）（补充字段-是否必填 企业角色）
  - name: bg_color
    type: string
    phys: varchar(10)
    desc: 背景颜色(L:彩色 G：灰色)
  - name: billing_type_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 开票类型（补充字段-是否必填，企业角色）
  - name: cash_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 中原融资合同编号（补充字段-是否必填，企业角色）
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_size_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 增值税纳税人类别（补充字段-是否必填，企业角色）
  - name: composite_field_property_requried_company_role
    type: string
    phys: varchar(256)
    desc: 工行供应链编号（补充字段-企业角色）
  - name: composite_field_property_requried_config_company_role
    type: string
    phys: varchar(256)
    desc: 工行供应链编号（补充字段-企业角色）
  - name: composite_field_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 工行供应链编号（补充字段-企业角色）
  - name: core_bosc_company_id_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 关联核心企业（补充字段-是否必填，企业角色）
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
  - name: dbass_app_id
    type: string
    phys: varchar(128)
    desc: dbassAppId
  - name: dbass_private_key
    type: string
    phys: varchar(2048)
    desc: dbassPrivateKey
  - name: default_project_id
    type: number
    phys: bigint(20)
    desc: 默认项目
  - name: dev_domain
    type: string
    phys: varchar(256)
    desc: 开发环境域名
  - name: finance_org_type_property_requried_config_cust_role
    type: string
    phys: varchar(250)
    desc: 金融机构类型（补充字段-是否必填 企业角色）
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
  - name: lybank_cash_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 洛阳融资合同编号（补充字段-是否必填，企业角色）
  - name: main_tenant_flg_en
    type: string
    phys: varchar(64)
    desc: 主定制项目标识
    topk: "HBLT|shendu"
  - name: main_theme_color
    type: string
    phys: varchar(32)
    desc: 主题色
  - name: migratory_flag
    type: string
    phys: varchar(256)
    desc: 迁移标志
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
    topk: "scpr-pplatform-mp"
  - name: mp_sso_tenant_chanel
    type: string
    phys: varchar(128)
    desc: mpSsoTenantChanel
  - name: name
    type: string
    phys: varchar(128)
    desc: 租户名称
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: 租户运营更新时间
  - name: op_update_user
    type: string
    phys: varchar(100)
    desc: 租户运营更新人
    topk: "chenqiuyun|duanyang|huangliyu|huangliyu3|linyanxiang|liuning|ruanbanliang|xieqingquan|zhuliping"
  - name: oper_auth_agreement
    type: string
    phys: varchar(50)
    desc: 子账户授权书
    topk: "DT_202503171058|DT_202503251071|DT_202507181127"
  - name: operator_applet_code
    type: string
    phys: varchar(1024)
    desc: 客服小程序码
  - name: operator_email
    type: string
    phys: varchar(100)
    desc: 运营人员邮箱
    topk: "1198273@qq.com|177377@126.com|56789rtyu@qq.com|dd@linklogis.com|huangli@qq.com|liuyuming@linklogis.com|pengzhujun@linklogis.com"
  - name: operator_id
    type: string
    phys: varchar(100)
    desc: 运营人员id
  - name: operator_name
    type: string
    phys: varchar(100)
    desc: 运营人员名称
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
    topk: "CT-202404031808238683649|CT-202404081721209495040|CT-202503131441009438408|DT_202503191068|DT_202503251071|DT_202503271081|DT_202503283479|DT_202503303499|DT_202505230361|DT_202507181127|DT_202511253668|Y"
  - name: platform_operator
    type: string
    phys: varchar(32)
    desc: 平台运营方
  - name: platform_secret_key
    type: string
    phys: varchar(64)
    desc: 中台互通配置秘钥
  - name: platform_sms_signature
    type: string
    phys: varchar(64)
    desc: 产融平台短信签名(无方括号)
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
  - name: prd_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: 生产公众号登录密码
  - name: privacy_policy_agreement
    type: string
    phys: varchar(64)
    desc: 隐私协议
    topk: "CT-202405311653384958102|CT-202503131437224998812|DT_202503181060|DT_202503271077|DT_202503283481|DT_202503303500|DT_202505230361|DT_202507181127|DT_202509293314"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sit_domain
    type: string
    phys: varchar(256)
    desc: 测试环境域名
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
  - name: uat_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: UAT公众号登录密码
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
    topk: "CT-202405211357559370074|CT-202503131430531422546|DT_202503171058|DT_202503271073|DT_202503271078|DT_202503283480|DT_202503303498|DT_202505230361|DT_202507181127"
  - name: web_logo_url
    type: string
    phys: text
    desc: 网站logo
  - name: web_title
    type: string
    phys: varchar(128)
    desc: 网站标题
  - name: xib_factor_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 厦银保理合同编号（补充字段-是否必填，企业角色
  - name: zybank_cash_contract_amt_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: 中原融资合同金额（补充字段-是否必填，企业角色）
```

## 关联表

- [[tenant_interworking_product]]：tenant_setting_config.code → tenant_interworking_product.ref_tenant_interworking_product_tenant_setting_config（ref-convention:TenantInterworkingProductDO.java，suggested）
- [[tenant_interworking_project]]：tenant_setting_config.code → tenant_interworking_project.ref_tenant_interworking_project_tenant_setting_config（ref-convention:TenantInterworkingProjectDO.java，suggested）
- [[tenant_product]]：tenant_setting_config.code → tenant_product.ref_tenant_product_tenant_setting_config（ref-convention:TenantProductDO.java，suggested）
