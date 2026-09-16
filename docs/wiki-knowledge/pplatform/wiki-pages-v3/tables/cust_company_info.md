---
type: table
title: 企业主档
page_key: cust_company_info
domain: 企业建档与认证状态机
status: draft
anchors: [cust_company_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_build, ca_fee, ca_cert, company_change, company_contact, product_activation, company_role, bank_account, company_group, authorization, company_project, tenant_migration, company_survey, oper_change]
---

# 企业主档

本表是场景 [[company_build]] 的**主档**，同时被收费/认证/变更/联系人/产品开通/角色/账户/集团/授权/项目绑定/迁移/问卷/运营变更等场景引用为身份或状态源。不要把建档、缴费、开通、变更、联系人激活几条状态线互相替代。迁移来源企业看 `cust_source='MIGRATORY'`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[authorization]]

`id`, `code`, `enable`, `create_time`, `update_time`, `name`

### [[bank_account]]

`id`, `code`, `enable`, `create_time`, `update_time`, `name`

### [[ca_cert]]

`id`, `code`, `enable`, `create_time`, `update_time`, `ca_register_status`, `certification_no`, `name`, `need_register_ca`

### [[ca_fee]]

`id`, `code`, `enable`, `create_time`, `update_time`, `certification_no`, `name`

### [[company_build]]

`id`, `code`, `enable`, `create_time`, `update_time`, `certification_no`, `cust_build_status`, `cust_company_type`, `cust_status`, `data_type`, `identify_style`, `name`

### [[company_change]]

`id`, `code`, `enable`, `create_time`, `update_time`, `check_status`, `cust_status`, `data_type`, `head_company`, `identify_style`

### [[company_contact]]

`id`, `code`, `enable`, `create_time`, `update_time`, `cust_status`, `name`

### [[company_group]]

`id`, `code`, `enable`, `create_time`, `update_time`, `cust_company_type`, `name`

### [[company_project]]

`id`, `code`, `enable`, `create_time`, `update_time`, `name`

### [[company_role]]

`id`, `code`, `enable`, `create_time`, `update_time`, `cust_company_type`

### [[company_survey]]

`id`, `enable`, `create_time`, `update_time`, `cust_company_type`

### [[product_activation]]

`id`, `code`, `enable`, `create_time`, `update_time`, `name`

### [[tenant_migration]]

`id`, `code`, `enable`, `create_time`, `update_time`, `cust_build_status`, `cust_source`, `cust_status`

### 未分窗

仍留表页，待代码证据划入场景：`abroad_cust`, `audit_back_flag`, `auth_aggrement_supplement_flag`, `bs_register_status`, `cert_no_flag`, `legal_certification_type`, `legal_realname_status`, `migarory_auth_aggrement_flag`, `need_charge`, `need_register_bs`, `sign_mode`, `test_data`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `apply_data_id`, `apply_type`, `approval_date`, `back_reason`, `bank_branch`, `billing_type`, `biz_cust_type`, `business_address`, `business_city`, `business_city_code`, `business_license_end_time`, `business_license_start_time`, `business_province`, `business_province_city`, `business_province_code`, `business_scope`, `business_status`, `cash_contract_no`, `channel_code`, `client_type`, `company_ext_data`, `company_size`, `composite_field`, `contact_address`, `contact_city`, `contact_city_code`, `contact_province`, `contact_province_city`, `contact_province_code`, `contact_tel`, `contact_user_name`, `core_bosc_company_id`, `cust_build_type`, `cust_email`, `cust_english_name`, `cust_english_short_name`, `cust_first_submit_auth`, `cust_former_name`, `cust_from`, `cust_no`, `cust_profile`, `cust_scale`, `cust_short_name`, `db_tenant_code`, `establishment_time`, `ext`, `finance_org_code`, `finance_org_flag`, `finance_org_type`, `finance_org_type_name`, `group_company`, `industry_involved`, `invoicing_accont_no`, `invoicing_address`, `invoicing_bank_branch`, `invoicing_bank_code`, `invoicing_bank_name`, `invoicing_bank_no`, `invoicing_bank_province_city`, `invoicing_email`, `invoicing_name`, `invoicing_phone`, `invoicing_taxpayer_no`, `legal_birth_date`, `legal_certification_end_time`, `legal_certification_no`, `legal_certification_start_time`, `legal_email`, `legal_name`, `legal_name_english`, `legal_name_english_end`, `legal_phone`, `legal_time_permanent`, `lybank_cash_contract_no`, `main_data_id`, `manager_id`, `nationality`, `nationality_en`, `organization_id`, `outside_org`, `paid_in_capital`, `pc_task_id`, `platform_cust_id`, `regist_city`, `regist_city_code`, `regist_city_english`, `regist_province`, `regist_province_city`, `regist_province_city_english`, `regist_province_code`, `register_capital`, `registered_address`, `relate_company_id`, `relate_company_name`, `remark`, `signing_mode`, `tenant_flg_en`, `third_auth_status`, `time_permanent`, `workers_no`, `xib_factor_contract_no`, `zybank_cash_contract_amt`

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "主键"
    roles: [query]
    group: always
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_change, company_contact, company_group, company_project, company_role, company_survey, product_activation, tenant_migration]
  - name: code
    type: string
    phys: varchar(64)
    desc: "企业业务编码"
    roles: [query]
    group: always
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_change, company_contact, company_group, company_project, company_role, product_activation, tenant_migration]
  - name: enable
    type: string
    phys: varchar(4)
    desc: "enable"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    group: always
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_change, company_contact, company_group, company_project, company_role, company_survey, product_activation, tenant_migration]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_change, company_contact, company_group, company_project, company_role, company_survey, product_activation, tenant_migration]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_change, company_contact, company_group, company_project, company_role, company_survey, product_activation, tenant_migration]
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
  - name: abroad_cust
    type: string
    phys: varchar(512)
    desc: "是否境外"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: audit_back_flag
    type: string
    phys: varchar(2)
    desc: "审核退回标记"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: auth_aggrement_supplement_flag
    type: string
    phys: varchar(2)
    desc: "是否授权书补签标识"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: bs_register_status
    type: string
    phys: varchar(2)
    desc: "上上签开通状态"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: ca_register_status
    type: string
    phys: varchar(2)
    desc: "CFCA 数字证书开通状态"
    dict: open_status
    topk: "N|P|Y"
    roles: [query]
    scenes: [ca_cert]
  - name: cert_no_flag
    type: string
    phys: varchar(64)
    desc: "执行查询统一信用证编码"
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: "统一社会信用代码"
    roles: [query]
    scenes: [ca_cert, ca_fee, company_build]
  - name: check_status
    type: string
    phys: varchar(30)
    desc: "企业准入审核状态"
    dict: check_status
    topk: "CUST_CHECK_BACKTOCUSTOM|CUST_CHECK_CHECKING|CUST_CHECK_INIT|CUST_CHECK_PASS|CUST_CHECK_REJECT|EFFECT"
    roles: [query]
    scenes: [company_change]
  - name: cust_build_status
    type: string
    phys: varchar(64)
    desc: "认证/建档过程状态"
    dict: cust_build_status
    topk: "AWAIT_CUST_CONFIRM|BUILDING|BUILD_ACTIVATE|BUILD_BACK|BUILD_FAIL|BUILD_SUCCESS|CUST_AUDIT_AWAIT|CUST_BUILDING|CUST_BUILD_SUCCESS|CUST_CHANGE|CUST_CONFIRM_AWAIT|INIT"
    labels: "AWAIT_CUST_CONFIRM:待客户确认|BUILDING:建档中|BUILD_ACTIVATE:待激活|BUILD_BACK:退回|BUILD_FAIL:认证失败|BUILD_SUCCESS:认证成功|CUST_AUDIT_AWAIT:待审核|CUST_BUILDING:审核中|CUST_BUILD_SUCCESS:审核通过|CUST_CHANGE:变更|CUST_CONFIRM_AWAIT:待客户认证|INIT:初始化"
    roles: [query]
    scenes: [company_build, tenant_migration]
  - name: cust_company_type
    type: string
    phys: varchar(200)
    desc: "企业角色"
    dict: company_type
    roles: [query]
    scenes: [company_build, company_group, company_role, company_survey]
  - name: cust_source
    type: string
    phys: varchar(64)
    desc: "客户来源"
    dict: cust_source
    topk: "MIGRATORY|PLATFORM|PLATFORM_PUSH|PPLATFORM"
    labels: "MIGRATORY:存量迁移企业|PLATFORM_PUSH:运营中台推送|PPLATFORM:产融自建企业"
    roles: [query]
    scenes: [tenant_migration]
  - name: cust_status
    type: string
    phys: varchar(64)
    desc: "企业状态"
    dict: cust_status
    topk: "ADD|CHANGE|EFFECT|FREEZE|WRITEOFF"
    labels: "ADD:新增|CHANGE:变更|EFFECT:生效|FREEZE:冻结|WRITEOFF:注销"
    roles: [query]
    scenes: [company_build, company_change, company_contact, tenant_migration]
  - name: data_type
    type: string
    phys: varchar(4)
    desc: "数据类型：1,主数据，0记录数据"
    dict: data_type
    topk: "0|1|2"
    labels: "0:流程数据|1:主数据|2:编辑过程"
    roles: [query]
    scenes: [company_build, company_change]
  - name: head_company
    type: string
    phys: varchar(512)
    desc: "是否总公司"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_change]
  - name: identify_style
    type: string
    phys: varchar(64)
    desc: "认证方式"
    dict: identify_style
    topk: "INVITE|INVITE_AGW|SELF|SIMPLE"
    labels: "INVITE:邀请认证-客户录入|INVITE_AGW:邀请认证-内管录入|SELF:自主认证|SIMPLE:简易认证"
    scenes: [company_build, company_change]
  - name: legal_certification_type
    type: string
    phys: varchar(64)
    desc: "法人证件类型"
    dict: legal_certification_type
    topk: "CERT_GREEN_CARD|CERT_MAINLAND_PASS|CERT_OTHER|CERT_PASSPORT|CERT_RESIDENT_PERMIT|CERT_TAIWAN|CREDENTIALS_ID|CRET_ID|CRET_ID_HK|身份证"
    labels: "CERT_GREEN_CARD:外国人永久居留证|CERT_MAINLAND_PASS:港澳居民来往内地通行证|CERT_OTHER:其他|CERT_PASSPORT:护照|CERT_RESIDENT_PERMIT:港澳台居民居住证|CERT_TAIWAN:台胞证|CRET_ID:二代居民身份证|CRET_ID_HK:香港身份证"
  - name: legal_realname_status
    type: string
    phys: varchar(100)
    desc: "法人认证状态"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: migarory_auth_aggrement_flag
    type: string
    phys: varchar(2)
    desc: "新旧渠道授权书补签标识，Y 新渠道:N 旧渠道"
    dict: enable
    topk: "N|Y"
    labels: "N:旧渠道|Y:新渠道"
  - name: name
    type: string
    phys: varchar(256)
    desc: "企业名称"
    roles: [result]
    scenes: [authorization, bank_account, ca_cert, ca_fee, company_build, company_contact, company_group, company_project, product_activation]
  - name: need_charge
    type: string
    phys: varchar(2)
    desc: "运营方是否涉及收费"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_register_bs
    type: string
    phys: varchar(4)
    desc: "是否需要开通上上签电子签章"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_register_ca
    type: string
    phys: varchar(2)
    desc: "是否需要开通 CA"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
    scenes: [ca_cert]
  - name: sign_mode
    type: string
    phys: varchar(64)
    desc: "产品协议签署方式"
    dict: sign_mode
    topk: "ONLINE"
  - name: test_data
    type: string
    phys: varchar(4)
    desc: "是否测试数据"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: "当前审批状态"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "ISOLATE_TAG_JHYL|JHYL|QA2tiepai2|base|common|zlskscf"
  - name: apply_data_id
    type: number
    phys: bigint(20)
    desc: "认证流程数据id"
  - name: apply_type
    type: string
    phys: varchar(64)
    desc: "流程类型"
    topk: "add|update"
  - name: approval_date
    type: temporal
    phys: date
    desc: "核准日期"
  - name: back_reason
    type: string
    phys: varchar(2000)
    desc: "退回原因"
  - name: bank_branch
    type: string
    phys: varchar(200)
    desc: "银行分行名称（通用）(补充字段)"
  - name: billing_type
    type: string
    phys: text
    desc: "开票类型（补充字段）"
  - name: biz_cust_type
    type: string
    phys: varchar(64)
    desc: "工商类别"
  - name: business_address
    type: string
    phys: varchar(128)
    desc: "经营地址"
  - name: business_city
    type: string
    phys: varchar(128)
    desc: "经营市"
  - name: business_city_code
    type: string
    phys: varchar(128)
    desc: "经营城市代码"
  - name: business_license_end_time
    type: temporal
    phys: date
    desc: "企业营业执照结束时间"
  - name: business_license_start_time
    type: temporal
    phys: date
    desc: "企业营业执照开始时间"
  - name: business_province
    type: string
    phys: varchar(128)
    desc: "经营省份"
  - name: business_province_city
    type: string
    phys: varchar(512)
    desc: "经营省市"
  - name: business_province_code
    type: string
    phys: varchar(128)
    desc: "经营省份代码"
  - name: business_scope
    type: string
    phys: text
    desc: "经营范围"
  - name: business_status
    type: string
    phys: varchar(128)
    desc: "经营状态"
  - name: cash_contract_no
    type: string
    phys: text
    desc: "中原融资合同编号（补充字段）"
  - name: channel_code
    type: string
    phys: varchar(64)
    desc: "开放平台channelcode"
    topk: "longteng"
  - name: client_type
    type: string
    phys: varchar(128)
    desc: "发起变更的客户端类型"
  - name: company_ext_data
    type: structured
    phys: json
    desc: "企业拓展字段json"
  - name: company_size
    type: string
    phys: text
    desc: "增值税纳税人类别（补充字段）"
  - name: composite_field
    type: string
    phys: text
    desc: "工行供应链编号（补充字段）"
  - name: contact_address
    type: string
    phys: varchar(128)
    desc: "联系地址"
    topk: "qdqw"
  - name: contact_city
    type: string
    phys: varchar(128)
    desc: "联系市"
  - name: contact_city_code
    type: string
    phys: varchar(128)
    desc: "联系城市代码"
    topk: "650200|820000"
  - name: contact_province
    type: string
    phys: varchar(128)
    desc: "联系省份"
  - name: contact_province_city
    type: string
    phys: varchar(512)
    desc: "联系省市"
  - name: contact_province_code
    type: string
    phys: varchar(128)
    desc: "联系省份代码"
    topk: "650000|820000"
  - name: contact_tel
    type: string
    phys: varchar(128)
    desc: "联系电话"
  - name: contact_user_name
    type: string
    phys: varchar(128)
    desc: "联系人"
  - name: core_bosc_company_id
    type: string
    phys: text
    desc: "关联核心企业（补充字段）"
  - name: cust_build_type
    type: string
    phys: varchar(64)
    desc: "录入方式"
    topk: "AGW_BUILD|PC_BUILD|SIMPLE"
  - name: cust_email
    type: string
    phys: varchar(128)
    desc: "公司联系邮箱"
  - name: cust_english_name
    type: string
    phys: varchar(200)
    desc: "客户英文名称"
  - name: cust_english_short_name
    type: string
    phys: varchar(200)
    desc: "企业简称英文"
  - name: cust_first_submit_auth
    type: temporal
    phys: datetime
    desc: "客户首次提交认证时间"
  - name: cust_former_name
    type: string
    phys: varchar(128)
    desc: "曾用名"
  - name: cust_from
    type: string
    phys: varchar(80)
    desc: "客户来源"
  - name: cust_no
    type: string
    phys: varchar(128)
    desc: "客户编号"
  - name: cust_profile
    type: string
    phys: varchar(128)
    desc: "企业简介"
  - name: cust_scale
    type: string
    phys: varchar(128)
    desc: "企业规模"
    topk: "qw"
  - name: cust_short_name
    type: string
    phys: varchar(128)
    desc: "企业简称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: establishment_time
    type: temporal
    phys: date
    desc: "成立日期"
  - name: ext
    type: string
    phys: varchar(526)
    desc: "扩展信息"
  - name: finance_org_code
    type: string
    phys: varchar(64)
    desc: "金融机构编码(补充字段)"
  - name: finance_org_flag
    type: string
    phys: varchar(512)
    desc: "金融机构身份标识"
  - name: finance_org_type
    type: string
    phys: varchar(64)
    desc: "金融机构类型(补充字段)"
  - name: finance_org_type_name
    type: string
    phys: varchar(100)
  - name: group_company
    type: string
    phys: varchar(512)
    desc: "是否归属集团或核心企业"
    topk: "1|N|Y"
    labels: "1:是|N:否|Y:是"
  - name: industry_involved
    type: string
    phys: varchar(128)
    desc: "所属行业"
  - name: invoicing_accont_no
    type: string
    phys: varchar(128)
    desc: "开票开户行账号"
  - name: invoicing_address
    type: string
    phys: varchar(128)
    desc: "开票地址"
  - name: invoicing_bank_branch
    type: string
    phys: varchar(128)
    desc: "开票银行支行"
  - name: invoicing_bank_code
    type: string
    phys: varchar(128)
    desc: "开票银行代码"
  - name: invoicing_bank_name
    type: string
    phys: varchar(128)
    desc: "开票银行名称"
  - name: invoicing_bank_no
    type: string
    phys: varchar(512)
    desc: "开票银行联行号"
  - name: invoicing_bank_province_city
    type: string
    phys: varchar(512)
    desc: "开票银行省市"
  - name: invoicing_email
    type: string
    phys: varchar(128)
    desc: "开票电子邮箱"
  - name: invoicing_name
    type: string
    phys: varchar(128)
    desc: "开票名称"
  - name: invoicing_phone
    type: string
    phys: varchar(128)
    desc: "开票电话"
  - name: invoicing_taxpayer_no
    type: string
    phys: varchar(128)
    desc: "开票纳税人识别号"
  - name: legal_birth_date
    type: temporal
    phys: date
    desc: "法人生日"
  - name: legal_certification_end_time
    type: temporal
    phys: date
    desc: "法人证件结束日期"
  - name: legal_certification_no
    type: string
    phys: varchar(128)
    desc: "法人证件号"
  - name: legal_certification_start_time
    type: temporal
    phys: date
    desc: "法人证件开始日期"
  - name: legal_email
    type: string
    phys: varchar(128)
    desc: "法人邮箱"
  - name: legal_name
    type: string
    phys: varchar(128)
    desc: "法人姓名"
  - name: legal_name_english
    type: string
    phys: varchar(200)
    desc: "法人姓名(英文)"
  - name: legal_name_english_end
    type: string
    phys: varchar(200)
    desc: "法人名(英文)"
  - name: legal_phone
    type: string
    phys: varchar(128)
    desc: "法人手机号码"
  - name: legal_time_permanent
    type: string
    phys: varchar(512)
    desc: "身份证有效期标志"
  - name: lybank_cash_contract_no
    type: string
    phys: text
    desc: "洛阳融资合同编号（补充字段）"
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: "主数据id"
  - name: manager_id
    type: string
    phys: varchar(112)
    desc: "业务经理"
  - name: nationality
    type: string
    phys: varchar(128)
    desc: "国籍"
  - name: nationality_en
    type: string
    phys: varchar(128)
    desc: "国籍英文"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: outside_org
    type: string
    phys: varchar(512)
    desc: "外部机构"
    topk: "0|1|N|Y"
    labels: "0:否|1:是|N:否|Y:是"
  - name: paid_in_capital
    type: string
    phys: varchar(128)
    desc: "实缴资本（元）"
  - name: pc_task_id
    type: string
    phys: varchar(128)
    desc: "退回客户端补充资料taskId"
  - name: platform_cust_id
    type: number
    phys: bigint(20)
    desc: "运营中台id"
  - name: regist_city
    type: string
    phys: varchar(128)
    desc: "注册市"
  - name: regist_city_code
    type: string
    phys: varchar(128)
    desc: "注册城市代码"
  - name: regist_city_english
    type: string
    phys: varchar(100)
    desc: "市（英文）"
  - name: regist_province
    type: string
    phys: varchar(128)
    desc: "注册省份"
  - name: regist_province_city
    type: string
    phys: varchar(512)
    desc: "注册省市"
  - name: regist_province_city_english
    type: string
    phys: varchar(128)
    desc: "注册省市(英文)"
  - name: regist_province_code
    type: string
    phys: varchar(128)
    desc: "注册省份代码"
  - name: register_capital
    type: number
    phys: decimal(20,2)
    desc: "注册资本"
  - name: registered_address
    type: string
    phys: varchar(128)
    desc: "注册地址"
  - name: relate_company_id
    type: string
    phys: varchar(512)
    desc: "归属企业id"
  - name: relate_company_name
    type: string
    phys: varchar(256)
    desc: "归属集团或企业"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: signing_mode
    type: string
    phys: varchar(64)
    desc: "签署模式"
    topk: "01"
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: "项目标识（英文）"
  - name: third_auth_status
    type: string
    phys: varchar(8)
    desc: "第三方认证状态"
    topk: "1"
    labels: "1:是"
  - name: time_permanent
    type: string
    phys: varchar(512)
    desc: "营业执照有效期"
  - name: workers_no
    type: string
    phys: varchar(128)
    desc: "员工"
  - name: xib_factor_contract_no
    type: string
    phys: text
    desc: "厦银保理合同编号（补充字段）"
  - name: zybank_cash_contract_amt
    type: string
    phys: text
    desc: "中原融资合同金额（补充字段）"
```
