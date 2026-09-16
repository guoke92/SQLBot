---
type: table
title: 租户设置
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
contract_version: "0.3"
belong: tables
scenes: [tenant_config]
---

# 租户设置

场景 [[tenant_config]] 主档。有效读取 `enable='Y'`；`status='Y'` 为已生效租户。`bg_color`：L 彩色 / G 灰色。`operator_ai_customer` 库值为 `'0'`/`'1'`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[tenant_config]]

`id`, `enable`, `create_time`, `update_time`, `bg_color`, `db_tenant_code`, `send_email`, `share_flag`, `source`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_status`, `bank_branch_property_requried`, `billing_type_property_requried`, `cash_contract_no_property_requried`, `company_share_flag`, `company_size_property_requried`, `composite_field_property_requried`, `core_bosc_company_id_property_requried`, `finance_org_type_property_requried`, `generate_electronic_auth_flag`, `is_stack`, `lybank_cash_contract_no_property_requried`, `need_hfive`, `need_mp_wx`, `portal_flag`, `project_code_required`, `pushing_status`, `recall_auth_doc_flag`, `self_registration_flag`, `sign_flag`, `use_theme_after_login`, `xib_factor_contract_no_property_requried`, `zybank_cash_contract_amt_property_requried`, `access_mode`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `adapt_colour`, `ai_resource_color`, `ai_zc_channel`, `ai_zc_sysnum`, `apaas_tenant_code`, `app_tenant_code`, `auth_agreement`, `band_name`, `bank_branch`, `bank_branch_property_requried_config_cust_role`, `billing_type_property_requried_config_cust_role`, `cash_contract_no_property_requried_config_cust_role`, `company_size_property_requried_config_cust_role`, `composite_field_property_requried_company_role`, `composite_field_property_requried_config_company_role`, `composite_field_property_requried_config_cust_role`, `core_bosc_company_id_property_requried_config_cust_role`, `cust_service_number`, `customer_card_type`, `dbass_app_id`, `dbass_private_key`, `default_project_id`, `dev_domain`, `finance_org_type_property_requried_config_cust_role`, `hfive_dev_domain`, `hfive_prd_domain`, `hfive_test_domain`, `hfive_uat_domain`, `lybank_cash_contract_no_property_requried_config_cust_role`, `main_tenant_flg_en`, `main_theme_color`, `migratory_flag`, `mobile_indexpage_bg_logo_url`, `mobile_indexpage_logo_url`, `mp_dbass_app_id`, `mp_home_background_path`, `mp_logo_path`, `mp_sso_sys_channel`, `mp_sso_tenant_chanel`, `name`, `op_update_time`, `op_update_user`, `oper_auth_agreement`, `operator_ai_customer`, `operator_applet_code`, `operator_email`, `operator_id`, `operator_name`, `operator_qr_code`, `operator_wechat_code`, `organization_id`, `pc_home_background_path`, `pc_icon_path`, `pc_login_logo_path`, `pc_logo_path`, `pcimg_browser_tab_icon_url`, `pcimg_indexpage_bg_logo_url`, `pcimg_loginpage_banner_url`, `pcimg_loginpage_bg_logo_url`, `person_auth_agreement`, `platform_operator`, `platform_secret_key`, `platform_sms_signature`, `prd_domain`, `prd_mp_app_id`, `prd_mp_app_name`, `prd_mp_wx_login_name`, `prd_mp_wx_login_pwd`, `privacy_policy_agreement`, `remark`, `sit_domain`, `source_id`, `sso_sys_channel`, `sso_tenant_chanel`, `tenant_flag_zh`, `tenant_flg_en`, `uat_domain`, `uat_mp_app_id`, `uat_mp_app_name`, `uat_mp_wx_login_name`, `uat_mp_wx_login_pwd`, `uni_social_credit_code`, `user_protocol_agreement`, `web_logo_url`, `web_title`, `xib_factor_contract_no_property_requried_config_cust_role`, `zybank_cash_contract_amt_property_requried_config_cust_role`

```ground:table
table: tenant_setting_config
database: lowcode_pplatform
desc: 租户配置
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [tenant_config]
  - name: code
    type: string
    phys: varchar(64)
    desc: "编码"
    group: always
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "Y"
    labels: "Y:是"
    roles: [query]
    group: always
    scenes: [tenant_config]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [tenant_config]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [tenant_config]
  - name: create_by
    type: string
    phys: varchar(100)
    desc: "创建人id"
    group: always
  - name: create_user
    type: string
    phys: varchar(100)
    desc: "创建人名称"
    group: always
  - name: update_by
    type: string
    phys: varchar(100)
    desc: "更新人id"
    group: always
  - name: update_user
    type: string
    phys: varchar(100)
    desc: "更新人名称"
    group: always
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: bank_branch_property_requried
    type: string
    phys: varchar(2)
    desc: "银行分行名称（通用）（补充字段-是否必填）"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: bg_color
    type: string
    phys: varchar(10)
    desc: "灰度背景色"
    scenes: [tenant_config]
  - name: billing_type_property_requried
    type: string
    phys: varchar(4)
    desc: "开票类型（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: cash_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: "中原融资合同编号（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: company_share_flag
    type: string
    phys: varchar(4)
    desc: "客户认证数据是否可用于其他贴牌平台"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: company_size_property_requried
    type: string
    phys: varchar(4)
    desc: "增值税纳税人类别（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: composite_field_property_requried
    type: string
    phys: varchar(4)
    desc: "工行供应链编号（补充字段-是否必填）"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: core_bosc_company_id_property_requried
    type: string
    phys: varchar(4)
    desc: "关联核心企业（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    roles: [query]
    scenes: [tenant_config]
  - name: finance_org_type_property_requried
    type: string
    phys: varchar(2)
    desc: "金融机构类型（补充字段-是否必填）"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: generate_electronic_auth_flag
    type: string
    phys: varchar(1)
    desc: "是否生成电子版授权书：Y-是，N-否"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: is_stack
    type: string
    phys: varchar(64)
    desc: "是否存量数据"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: lybank_cash_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: "洛阳融资合同编号（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: need_hfive
    type: string
    phys: varchar(4)
    desc: "是否定制H5"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_mp_wx
    type: string
    phys: varchar(4)
    desc: "是否定制小程序"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: portal_flag
    type: string
    phys: varchar(4)
    desc: "是否启用门户"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: project_code_required
    type: string
    phys: varchar(1)
    desc: "项目码是否必填：Y/N"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: pushing_status
    type: string
    phys: varchar(2)
    desc: "租户推送状态"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: recall_auth_doc_flag
    type: string
    phys: varchar(64)
    desc: "是否需回收授权书标识"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: self_registration_flag
    type: string
    phys: varchar(64)
    desc: "是否放开自主注册"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: send_email
    type: string
    phys: varchar(100)
    desc: "是否发送运营邮件"
    topk: "0|1"
    labels: "0:否|1:是"
    scenes: [tenant_config]
  - name: share_flag
    type: string
    phys: varchar(2)
    desc: "是否走共享配置"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [tenant_config]
  - name: sign_flag
    type: string
    phys: varchar(10)
    desc: "接收跨贴牌数据是否强制重签授权书"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: source
    type: string
    phys: varchar(32)
    desc: "来源"
    dict: ca_data_source
    topk: "ACFLOW|pplatform"
    scenes: [tenant_config]
  - name: status
    type: string
    phys: varchar(4)
    desc: "是否已生效"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    scenes: [tenant_config]
  - name: use_theme_after_login
    type: string
    phys: varchar(1)
    desc: "登录后是否使用该色调：Y-是，N-否"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: xib_factor_contract_no_property_requried
    type: string
    phys: varchar(4)
    desc: "厦银保理合同编号（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: zybank_cash_contract_amt_property_requried
    type: string
    phys: varchar(4)
    desc: "中原融资合同金额（补充字段-是否必填）"
    dict: enable
    topk: "N"
    labels: "N:否"
  - name: access_mode
    type: string
    phys: varchar(64)
    desc: "接入模式"
    topk: "DIRECT_INIT"
  - name: act_procinst_date
    type: temporal
    phys: datetime
    desc: "审批结束时间"
  - name: act_procinst_id
    type: string
    phys: varchar(64)
    desc: "流程实例ID"
  - name: act_procinst_no
    type: string
    phys: varchar(255)
    desc: "流程申请编号"
  - name: adapt_colour
    type: string
    phys: varchar(32)
    desc: "适配背景颜色"
  - name: ai_resource_color
    type: string
    phys: varchar(20)
    desc: "智能客服按钮颜色"
  - name: ai_zc_channel
    type: string
    phys: varchar(64)
    desc: "智能客服渠道号"
  - name: ai_zc_sysnum
    type: string
    phys: varchar(64)
    desc: "智能客服系统号"
  - name: apaas_tenant_code
    type: string
    phys: varchar(128)
    desc: "aPaaS租户编码"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
  - name: auth_agreement
    type: string
    phys: varchar(64)
    desc: "授权书协议"
    topk: "CT-202404031808238683649|CT-202404081721209495040|CT-202503131441009438408|DT_202503191068|DT_202503251071|DT_202503271081|DT_202503283479|DT_202503303499|DT_202505230361|DT_202507181127|DT_202511253668|DT_202609071513"
  - name: band_name
    type: string
    phys: varchar(128)
    desc: "贴牌平台名称"
  - name: bank_branch
    type: string
    phys: varchar(100)
    desc: "分行适用角色"
  - name: bank_branch_property_requried_config_cust_role
    type: string
    phys: varchar(250)
    desc: "银行分行名称（通用）（补充字段-是否必填 企业角色）"
  - name: billing_type_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "开票类型（补充字段-是否必填，企业角色）"
  - name: cash_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "中原融资合同编号（补充字段-是否必填，企业角色）"
  - name: company_size_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "增值税纳税人类别（补充字段-是否必填，企业角色）"
  - name: composite_field_property_requried_company_role
    type: string
    phys: varchar(256)
    desc: "工行供应链编号（补充字段-企业角色）"
  - name: composite_field_property_requried_config_company_role
    type: string
    phys: varchar(256)
    desc: "工行供应链编号（补充字段-企业角色）"
  - name: composite_field_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "工行供应链编号（补充字段-企业角色）"
  - name: core_bosc_company_id_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "关联核心企业（补充字段-是否必填，企业角色）"
  - name: cust_service_number
    type: string
    phys: varchar(64)
    desc: "客服电话"
  - name: customer_card_type
    type: string
    phys: varchar(32)
    desc: "客服名片类型：WX_WORK=发送企微名片，WX=发送微信名片，与operCardType枚举一致"
    topk: "WX|WX_WORK"
    labels: "WX:发送微信名片|WX_WORK:发送企微名片"
  - name: dbass_app_id
    type: string
    phys: varchar(128)
    desc: "dbassAppId"
  - name: dbass_private_key
    type: string
    phys: varchar(2048)
    desc: "dbassPrivateKey"
  - name: default_project_id
    type: number
    phys: bigint(20)
    desc: "默认项目id"
  - name: dev_domain
    type: string
    phys: varchar(256)
    desc: "开发环境域名"
  - name: finance_org_type_property_requried_config_cust_role
    type: string
    phys: varchar(250)
    desc: "金融机构类型（补充字段-是否必填 企业角色）"
  - name: hfive_dev_domain
    type: string
    phys: varchar(256)
    desc: "H5开发环境域名"
  - name: hfive_prd_domain
    type: string
    phys: varchar(256)
    desc: "H5生产环境域名"
  - name: hfive_test_domain
    type: string
    phys: varchar(256)
    desc: "H5测试环境域名"
  - name: hfive_uat_domain
    type: string
    phys: varchar(256)
    desc: "H5UAT环境域名"
  - name: lybank_cash_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "洛阳融资合同编号（补充字段-是否必填，企业角色）"
  - name: main_tenant_flg_en
    type: string
    phys: varchar(64)
    desc: "主定制项目标识"
    topk: "HBLT|shendu"
  - name: main_theme_color
    type: string
    phys: varchar(32)
    desc: "主题色"
  - name: migratory_flag
    type: string
    phys: varchar(256)
    desc: "迁移标志"
  - name: mobile_indexpage_bg_logo_url
    type: string
    phys: text
    desc: "移动端首页背景图"
  - name: mobile_indexpage_logo_url
    type: string
    phys: text
    desc: "移动端首页logo"
  - name: mp_dbass_app_id
    type: string
    phys: varchar(128)
    desc: "小程序dbassAppId"
  - name: mp_home_background_path
    type: string
    phys: text
    desc: "小程序首页背景图"
  - name: mp_logo_path
    type: string
    phys: text
    desc: "移动端首页logo"
  - name: mp_sso_sys_channel
    type: string
    phys: varchar(128)
    desc: "mpSsoSysChannel"
    topk: "scpr-pplatform-mp"
  - name: mp_sso_tenant_chanel
    type: string
    phys: varchar(128)
    desc: "mpSsoTenantChanel"
  - name: name
    type: string
    phys: varchar(128)
    desc: "租户名称"
  - name: op_update_time
    type: temporal
    phys: datetime
    desc: "租户运营更新时间"
  - name: op_update_user
    type: string
    phys: varchar(100)
    desc: "租户运营更新人"
    topk: "chenqiuyun|duanyang|huangliyu|huangliyu3|linyanxiang|liuning|ruanbanliang|xieqingquan|zhuliping"
  - name: oper_auth_agreement
    type: string
    phys: varchar(50)
    desc: "子账户授权书"
    topk: "DT_202503171058|DT_202503251071|DT_202507181127"
  - name: operator_ai_customer
    type: string
    phys: varchar(100)
    desc: "是否开启智能客服"
    topk: "0|1"
    labels: "0:否|1:是"
  - name: operator_applet_code
    type: string
    phys: varchar(1024)
    desc: "客服小程序码"
  - name: operator_email
    type: string
    phys: varchar(100)
    desc: "运营人员邮箱"
    topk: "1198273@qq.com|177377@126.com|56789rtyu@qq.com|dd@linklogis.com|huangli@qq.com|liuyuming@linklogis.com|pengzhujun@linklogis.com"
  - name: operator_id
    type: string
    phys: varchar(100)
    desc: "运营人员id"
  - name: operator_name
    type: string
    phys: varchar(100)
    desc: "运营人员名称"
  - name: operator_qr_code
    type: string
    phys: varchar(1024)
    desc: "客服二维码"
  - name: operator_wechat_code
    type: string
    phys: varchar(1024)
    desc: "公众号码"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: pc_home_background_path
    type: string
    phys: text
    desc: "PC首页背景图"
  - name: pc_icon_path
    type: string
    phys: text
    desc: "PC浏览器页签Icon"
  - name: pc_login_logo_path
    type: string
    phys: text
    desc: "PC登录窗口横幅"
  - name: pc_logo_path
    type: string
    phys: text
    desc: "PC内页logo"
  - name: pcimg_browser_tab_icon_url
    type: string
    phys: text
    desc: "PC浏览器页签Icon"
  - name: pcimg_indexpage_bg_logo_url
    type: string
    phys: text
    desc: "PC内页logo"
  - name: pcimg_loginpage_banner_url
    type: string
    phys: text
    desc: "PC登录窗口横幅"
  - name: pcimg_loginpage_bg_logo_url
    type: string
    phys: text
    desc: "PC首页背景图"
  - name: person_auth_agreement
    type: string
    phys: varchar(64)
    desc: "变更联系人授权书"
    topk: "CT-202404031808238683649|CT-202404081721209495040|CT-202503131441009438408|DT_202503191068|DT_202503251071|DT_202503271081|DT_202503283479|DT_202503303499|DT_202505230361|DT_202507181127|DT_202511253668|Y"
  - name: platform_operator
    type: string
    phys: varchar(32)
    desc: "平台运营方"
  - name: platform_secret_key
    type: string
    phys: varchar(64)
    desc: "中台互通配置秘钥"
  - name: platform_sms_signature
    type: string
    phys: varchar(64)
    desc: "产融平台短信签名(无方括号)"
  - name: prd_domain
    type: string
    phys: varchar(256)
    desc: "生产环境域名"
  - name: prd_mp_app_id
    type: string
    phys: varchar(128)
    desc: "生产小程序appID"
  - name: prd_mp_app_name
    type: string
    phys: varchar(128)
    desc: "生产小程序名称"
  - name: prd_mp_wx_login_name
    type: string
    phys: varchar(128)
    desc: "生产公众号登录账号"
  - name: prd_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: "生产公众号登录密码"
  - name: privacy_policy_agreement
    type: string
    phys: varchar(64)
    desc: "隐私协议"
    topk: "CT-202405311653384958102|CT-202503131437224998812|DT_202503181060|DT_202503271077|DT_202503283481|DT_202503303500|DT_202505230361|DT_202507181127|DT_202509293314"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: sit_domain
    type: string
    phys: varchar(256)
    desc: "测试环境域名"
  - name: source_id
    type: string
    phys: varchar(32)
    desc: "租户来源id"
  - name: sso_sys_channel
    type: string
    phys: varchar(128)
    desc: "ssoSysChannel"
  - name: sso_tenant_chanel
    type: string
    phys: varchar(128)
    desc: "ssoTenantChanel"
  - name: tenant_flag_zh
    type: string
    phys: varchar(128)
    desc: "项目标识（中文）"
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: "项目标识（英文）"
  - name: uat_domain
    type: string
    phys: varchar(256)
    desc: "UAT环境域名"
  - name: uat_mp_app_id
    type: string
    phys: varchar(128)
    desc: "UAT小程序appID"
  - name: uat_mp_app_name
    type: string
    phys: varchar(128)
    desc: "UAT小程序名称"
  - name: uat_mp_wx_login_name
    type: string
    phys: varchar(128)
    desc: "UAT公众登陆账号"
  - name: uat_mp_wx_login_pwd
    type: string
    phys: varchar(128)
    desc: "UAT公众号登录密码"
  - name: uni_social_credit_code
    type: string
    phys: varchar(128)
    desc: "统一社会信用证"
  - name: user_protocol_agreement
    type: string
    phys: varchar(64)
    desc: "用户协议"
    topk: "CT-202405211357559370074|CT-202503131430531422546|DT_202503171058|DT_202503271073|DT_202503271078|DT_202503283480|DT_202503303498|DT_202505230361|DT_202507181127"
  - name: web_logo_url
    type: string
    phys: text
    desc: "网站logo"
  - name: web_title
    type: string
    phys: varchar(128)
    desc: "网站标题"
  - name: xib_factor_contract_no_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "厦银保理合同编号（补充字段-是否必填，企业角色"
  - name: zybank_cash_contract_amt_property_requried_config_cust_role
    type: string
    phys: varchar(256)
    desc: "中原融资合同金额（补充字段-是否必填，企业角色）"
```

```ground:relation
type: EQUI_JOIN
left: tenant_setting_config.default_project_id
right: tenant_project.id
cardinality: many_to_one
status: proposed
evidence: code_path:TenantDomainService.java
```
