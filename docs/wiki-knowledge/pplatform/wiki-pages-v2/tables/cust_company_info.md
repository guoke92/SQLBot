---
type: table
title: 客户信息主表
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
contract_version: "0.1"
belong: tables
---












cust_company_info 是平台内部服务对接的企业（客户）主数据表。平台侧的企业建档、认证、审核、冻结与注销都以本表记录为锚点，企业下的联系人、项目、角色与授权申请则通过企业业务编码 `code` 联结，因此它同时是客户服务端与运营端两侧服务共用的读写对象。

企业在平台上的两个生命周期维度分别落在两个字段上：`cust_build_status` 描述建档与认证过程（见 [[cust_build_status_flow]]），`cust_status` 描述企业本身的生效状态（见 [[cust_status_flow]]）。企业下的人员在 [[cust_person_info]]，二者通过 [[ref_cust_company_info]] 约定的关联企业编码字段联结；产品与项目侧关联见 [[cust_project_rel]]、[[cust_role_info]]、[[cust_auth_application]]。

## 需求背景
内部服务在企业维度上需要一份稳定的主数据：客户侧服务负责企业信息录入与确认，运营侧服务负责审核、冻结与注销，两侧读写同一张表。因此字段语义必须明确划分——哪些由客户填写（法人姓名、法人手机号、法人证件），哪些由平台维护（各类状态、租户编码、审核退回标志），哪些是跨表关联的键（`code`）。表中还保存统一社会信用代码与法人证件信息，用于认证类服务比对。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，作为契约初稿；字段物理类型与字典绑定尚未在证据中出现，暂留空。企业建档状态流转见 [[cust_build_status_flow]]，企业生效状态流转见 [[cust_status_flow]]。

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
fields:
  - name: cust_build_status
    type: string
    phys: varchar(64)
    desc: 认证状态
    dict: cust_build_status
    topk: "AWAIT_CUST_CONFIRM|BUILDING|BUILD_ACTIVATE|BUILD_BACK|BUILD_FAIL|BUILD_SUCCESS|CUST_AUDIT_AWAIT|CUST_BUILDING|CUST_BUILD_SUCCESS|CUST_CHANGE|CUST_CONFIRM_AWAIT|INIT"
    roles: [query, result]
  - name: cust_company_type
    type: string
    phys: varchar(200)
    desc: 企业角色
    roles: [query]
  - name: cust_status
    type: string
    phys: varchar(64)
    desc: 客户状态
    dict: cust_status
    topk: "ADD|CHANGE|EFFECT|FREEZE|WRITEOFF"
    roles: [query]
  - name: data_type
    type: string
    phys: varchar(4)
    desc: 数据类型：1,主数据，0记录数据
    dict: data_type
    topk: "0|1|2"
    roles: [query]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(256)
    desc: 客户名称
    roles: [query, result]
  - name: abroad_cust
    type: string
    phys: varchar(512)
    desc: 是否境外
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: apply_type
    type: string
    phys: varchar(64)
    desc: 流程类型
    dict: apply_type
    topk: "add|update"
  - name: audit_back_flag
    type: string
    phys: varchar(2)
    desc: 审核退回标记
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: auth_aggrement_supplement_flag
    type: string
    phys: varchar(2)
    desc: 是否授权书补签标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: bs_register_status
    type: string
    phys: varchar(2)
    desc: 上上签开通状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: ca_register_status
    type: string
    phys: varchar(2)
    desc: CA开通状态
    dict: ca_register_status
    topk: "N|P|Y"
  - name: cert_no_flag
    type: string
    phys: varchar(64)
    desc: 执行查询统一信用证编码
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: check_status
    type: string
    phys: varchar(30)
    desc: 审核状态
    dict: check_status
    topk: "CUST_CHECK_BACKTOCUSTOM|CUST_CHECK_CHECKING|CUST_CHECK_INIT|CUST_CHECK_PASS|CUST_CHECK_REJECT|EFFECT"
  - name: client_type
    type: string
    phys: varchar(128)
    desc: 发起变更的客户端类型
    dict: client_type
  - name: cust_build_type
    type: string
    phys: varchar(64)
    desc: 录入方式
    dict: cust_build_type
    topk: "AGW_BUILD|PC_BUILD|SIMPLE"
  - name: cust_source
    type: string
    phys: varchar(64)
    desc: 建档数据来源
    dict: cust_source
    topk: "MIGRATORY|PLATFORM|PLATFORM_PUSH|PPLATFORM"
  - name: group_company
    type: string
    phys: varchar(512)
    desc: 是否归属集团或核心企业
    dict: group_company
    topk: "1|N|Y"
    labels: "1:是|N:否|Y:是"
  - name: head_company
    type: string
    phys: varchar(512)
    desc: 是否总公司
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: identify_style
    type: string
    phys: varchar(64)
    desc: 认证方式
    dict: identify_style
    topk: "INVITE|INVITE_AGW|SELF|SIMPLE"
  - name: legal_certification_type
    type: string
    phys: varchar(64)
    desc: 法人证件类型
    dict: cust_company_info__legal_certification_type
    topk: "CERT_GREEN_CARD|CERT_MAINLAND_PASS|CERT_OTHER|CERT_PASSPORT|CERT_RESIDENT_PERMIT|CERT_TAIWAN|CREDENTIALS_ID|CRET_ID|CRET_ID_HK|身份证"
  - name: legal_realname_status
    type: string
    phys: varchar(100)
    desc: 法人认证状态
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: migarory_auth_aggrement_flag
    type: string
    phys: varchar(2)
    desc: 新旧渠道授权书补签标识，Y 新渠道:N 旧渠道
    dict: enable
    topk: "N|Y"
    labels: "N:旧渠道|Y:新渠道"
  - name: need_charge
    type: string
    phys: varchar(2)
    desc: 运营方是否涉及收费
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_register_bs
    type: string
    phys: varchar(4)
    desc: 是否需要开通上上签电子签章
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: need_register_ca
    type: string
    phys: varchar(2)
    desc: 开通电子签章
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: outside_org
    type: string
    phys: varchar(512)
    desc: 外部机构
    dict: outside_org
    topk: "0|1|N|Y"
    labels: "0:否|1:是|N:否|Y:是"
  - name: sign_mode
    type: string
    phys: varchar(64)
    desc: 产品协议签署方式
    dict: cust_company_info__sign_mode
    topk: "ONLINE"
  - name: signing_mode
    type: string
    phys: varchar(64)
    desc: 签署模式
    dict: signing_mode
    topk: "01"
  - name: test_data
    type: string
    phys: varchar(4)
    desc: 是否测试数据
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: third_auth_status
    type: string
    phys: varchar(8)
    desc: 第三方认证状态
    dict: third_auth_status
    topk: "1"
    labels: "1:是"
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
  - name: act_procinst_status
    type: string
    phys: varchar(64)
    desc: 当前审批状态
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: "ISOLATE_TAG_JHYL|JHYL|QA2tiepai2|base|common|zlskscf"
  - name: apply_data_id
    type: number
    phys: bigint(20)
    desc: 认证流程数据id
  - name: approval_date
    type: temporal
    phys: date
    desc: 核准日期
  - name: back_reason
    type: string
    phys: varchar(2000)
    desc: 退回原因
  - name: bank_branch
    type: string
    phys: varchar(200)
    desc: 银行分行名称（通用）(补充字段)
  - name: billing_type
    type: string
    phys: text
    desc: 开票类型（补充字段）
  - name: biz_cust_type
    type: string
    phys: varchar(64)
    desc: 工商类别
  - name: business_address
    type: string
    phys: varchar(128)
    desc: 经营地址
  - name: business_city
    type: string
    phys: varchar(128)
    desc: 经营市
  - name: business_city_code
    type: string
    phys: varchar(128)
    desc: 经营城市代码
  - name: business_license_end_time
    type: temporal
    phys: date
    desc: 企业营业执照结束时间
  - name: business_license_start_time
    type: temporal
    phys: date
    desc: 企业营业执照开始时间
  - name: business_province
    type: string
    phys: varchar(128)
    desc: 经营省份
  - name: business_province_city
    type: string
    phys: varchar(512)
    desc: 经营省市
  - name: business_province_code
    type: string
    phys: varchar(128)
    desc: 经营省份代码
  - name: business_scope
    type: string
    phys: text
    desc: 经营范围
  - name: business_status
    type: string
    phys: varchar(128)
    desc: 经营状态
  - name: cash_contract_no
    type: string
    phys: text
    desc: 中原融资合同编号（补充字段）
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统一信用代码
  - name: channel_code
    type: string
    phys: varchar(64)
    desc: 开放平台channelcode
    topk: "longteng"
  - name: code
    type: string
    phys: varchar(64)
    desc: 编码
  - name: company_ext_data
    type: structured
    phys: json
    desc: 企业拓展字段json
  - name: company_size
    type: string
    phys: text
    desc: 增值税纳税人类别（补充字段）
  - name: composite_field
    type: string
    phys: text
    desc: 工行供应链编号（补充字段）
  - name: contact_address
    type: string
    phys: varchar(128)
    desc: 联系地址
    topk: "qdqw"
  - name: contact_city
    type: string
    phys: varchar(128)
    desc: 联系市
  - name: contact_city_code
    type: string
    phys: varchar(128)
    desc: 联系城市代码
    topk: "650200|820000"
  - name: contact_province
    type: string
    phys: varchar(128)
    desc: 联系省份
  - name: contact_province_city
    type: string
    phys: varchar(512)
    desc: 联系省市
  - name: contact_province_code
    type: string
    phys: varchar(128)
    desc: 联系省份代码
    topk: "650000|820000"
  - name: contact_tel
    type: string
    phys: varchar(128)
    desc: 联系电话
  - name: contact_user_name
    type: string
    phys: varchar(128)
    desc: 联系人
  - name: core_bosc_company_id
    type: string
    phys: text
    desc: 关联核心企业（补充字段）
  - name: create_by
    type: string
    phys: varchar(100)
    desc: 创建人id
  - name: create_time
    type: temporal
    phys: datetime
    desc: 创建时间
    roles: [result]
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_email
    type: string
    phys: varchar(128)
    desc: 公司联系邮箱
  - name: cust_english_name
    type: string
    phys: varchar(200)
    desc: 客户英文名称
  - name: cust_english_short_name
    type: string
    phys: varchar(200)
    desc: 企业简称英文
  - name: cust_first_submit_auth
    type: temporal
    phys: datetime
    desc: 客户首次提交认证时间
  - name: cust_former_name
    type: string
    phys: varchar(128)
    desc: 曾用名
  - name: cust_from
    type: string
    phys: varchar(80)
    desc: 客户来源
  - name: cust_no
    type: string
    phys: varchar(128)
    desc: 客户编号
  - name: cust_profile
    type: string
    phys: varchar(128)
    desc: 企业简介
  - name: cust_scale
    type: string
    phys: varchar(128)
    desc: 企业规模
    topk: "qw"
  - name: cust_short_name
    type: string
    phys: varchar(128)
    desc: 企业简称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: establishment_time
    type: temporal
    phys: date
    desc: 成立日期
  - name: ext
    type: string
    phys: varchar(526)
    desc: 扩展信息
  - name: finance_org_code
    type: string
    phys: varchar(64)
    desc: 金融机构编码(补充字段)
  - name: finance_org_flag
    type: string
    phys: varchar(512)
    desc: 金融机构身份标识
  - name: finance_org_type
    type: string
    phys: varchar(64)
    desc: 金融机构类型(补充字段)
  - name: finance_org_type_name
    type: string
    phys: varchar(100)
  - name: industry_involved
    type: string
    phys: varchar(128)
    desc: 所属行业
  - name: invoicing_accont_no
    type: string
    phys: varchar(128)
    desc: 开票开户行账号
  - name: invoicing_address
    type: string
    phys: varchar(128)
    desc: 开票地址
  - name: invoicing_bank_branch
    type: string
    phys: varchar(128)
    desc: 开票银行支行
  - name: invoicing_bank_code
    type: string
    phys: varchar(128)
    desc: 开票银行代码
  - name: invoicing_bank_name
    type: string
    phys: varchar(128)
    desc: 开票银行名称
  - name: invoicing_bank_no
    type: string
    phys: varchar(512)
    desc: 开票银行联行号
  - name: invoicing_bank_province_city
    type: string
    phys: varchar(512)
    desc: 开票银行省市
  - name: invoicing_email
    type: string
    phys: varchar(128)
    desc: 开票电子邮箱
  - name: invoicing_name
    type: string
    phys: varchar(128)
    desc: 开票名称
  - name: invoicing_phone
    type: string
    phys: varchar(128)
    desc: 开票电话
  - name: invoicing_taxpayer_no
    type: string
    phys: varchar(128)
    desc: 开票纳税人识别号
  - name: legal_birth_date
    type: temporal
    phys: date
    desc: 法人生日
  - name: legal_certification_end_time
    type: temporal
    phys: date
    desc: 法人证件结束日期
  - name: legal_certification_no
    type: string
    phys: varchar(128)
    desc: 法人证件号
  - name: legal_certification_start_time
    type: temporal
    phys: date
    desc: 法人证件开始日期
  - name: legal_email
    type: string
    phys: varchar(128)
    desc: 法人邮箱
  - name: legal_name
    type: string
    phys: varchar(128)
    desc: 法人姓名
  - name: legal_name_english
    type: string
    phys: varchar(200)
    desc: 法人姓名(英文)
  - name: legal_name_english_end
    type: string
    phys: varchar(200)
    desc: 法人名(英文)
  - name: legal_phone
    type: string
    phys: varchar(128)
    desc: 法人手机号码
  - name: legal_time_permanent
    type: string
    phys: varchar(512)
    desc: 身份证有效期标志
  - name: lybank_cash_contract_no
    type: string
    phys: text
    desc: 洛阳融资合同编号（补充字段）
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: manager_id
    type: string
    phys: varchar(112)
    desc: 业务经理
  - name: nationality
    type: string
    phys: varchar(128)
    desc: 国籍
  - name: nationality_en
    type: string
    phys: varchar(128)
    desc: 国籍英文
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: paid_in_capital
    type: string
    phys: varchar(128)
    desc: 实缴资本（元）
  - name: pc_task_id
    type: string
    phys: varchar(128)
    desc: 退回客户端补充资料taskId
  - name: platform_cust_id
    type: number
    phys: bigint(20)
    desc: 运营中台id
  - name: regist_city
    type: string
    phys: varchar(128)
    desc: 注册市
  - name: regist_city_code
    type: string
    phys: varchar(128)
    desc: 注册城市代码
  - name: regist_city_english
    type: string
    phys: varchar(100)
    desc: 市（英文）
  - name: regist_province
    type: string
    phys: varchar(128)
    desc: 注册省份
  - name: regist_province_city
    type: string
    phys: varchar(512)
    desc: 注册省市
  - name: regist_province_city_english
    type: string
    phys: varchar(128)
    desc: 注册省市(英文)
  - name: regist_province_code
    type: string
    phys: varchar(128)
    desc: 注册省份代码
  - name: register_capital
    type: number
    phys: decimal(20,2)
    desc: 注册资本
  - name: registered_address
    type: string
    phys: varchar(128)
    desc: 注册地址
  - name: relate_company_id
    type: string
    phys: varchar(512)
    desc: 归属企业id
  - name: relate_company_name
    type: string
    phys: varchar(256)
    desc: 归属集团或企业
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: time_permanent
    type: string
    phys: varchar(512)
    desc: 营业执照有效期
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
  - name: workers_no
    type: string
    phys: varchar(128)
    desc: 员工
  - name: xib_factor_contract_no
    type: string
    phys: text
    desc: 厦银保理合同编号（补充字段）
  - name: zybank_cash_contract_amt
    type: string
    phys: text
    desc: 中原融资合同金额（补充字段）
```

## 关联表

- [[authorization_agreement]]：cust_company_info.id → authorization_agreement.cust_id（write-flow:CustAuthAgreementDomainServiceTest.java，confirmed）
- [[cust_account_info]]：cust_company_info.code → cust_account_info.ref_cust_company_info（ref-convention:CustAccountInfoDO.java，suggested）
- [[cust_auth_application]]：cust_company_info.code → cust_auth_application.ref_cust_company_info（ref-convention:CustAuthApplicationDO.java，suggested）
- [[cust_auth_application]]：cust_company_info.code → cust_auth_application.ref_parent_company（write-flow:CustProductDomainService.java，confirmed）
- [[cust_auth_application]]：cust_company_info.id → cust_auth_application.main_data_id（write-flow:CustProductDomainService.java，confirmed）
- [[cust_build_record]]：cust_company_info.id → cust_build_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_certification_info]]：cust_company_info.code → cust_certification_info.ref_cust_company_info（ref-convention:CustCertificationInfoDO.java，suggested）
- [[cust_change_record]]：cust_company_info.id → cust_change_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_customized_product]]：cust_company_info.code → cust_customized_product.ref_cust_customized_product_cust_company_info（ref-convention:CustCustomizedProductDO.java，suggested）
- [[cust_group_rel]]：cust_company_info.id → cust_group_rel.cust_id（mapper:CustGroupMapper.xml，confirmed）
- [[cust_group_rel]]：cust_company_info.id → cust_group_rel.parent_cust_id（java-eq:CustGroupRelApplication.java，suggested）
- [[cust_group_rel]]：cust_company_info.id → cust_group_rel.root_cust_id（java-eq:CustGroupRelApplication.java，suggested）
- [[cust_head_company_info]]：cust_company_info.code → cust_head_company_info.ref_cust_head_company_info_cust_company_info（ref-convention:CustHeadCompanyInfoDO.java，suggested）
- [[cust_interworking_product]]：cust_company_info.code → cust_interworking_product.ref_cust_interworking_product_cust_company_info（ref-convention:CustInterworkingProductDO.java，suggested）
- [[cust_person_info]]：cust_company_info.code → cust_person_info.ref_cust_company_info（ref-convention:CustPersonInfoDO.java，suggested）
- [[cust_person_info]]：cust_company_info.cust_build_status → cust_person_info.cust_build_status（copy:CustCompanyIfoEnchanceService.java，suggested）
- [[cust_person_info]]：cust_company_info.id → cust_person_info.cust_company_id（mapper:CustCompanyQueryMapper.xml，confirmed）
- [[cust_project_code_record]]：cust_company_info.id → cust_project_code_record.company_id（write-flow:CustProjectRelEnhanceService.java，confirmed）
- [[cust_project_rel]]：cust_company_info.code → cust_project_rel.ref_cust_project_rel_cust_company_info（ref-convention:CustProjectRelDO.java，suggested）
- [[cust_role_info]]：cust_company_info.code → cust_role_info.ref_cust_company_info（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_shareholder_info]]：cust_company_info.code → cust_shareholder_info.ref_cust_company_info（ref-convention:CustShareholderInfoDO.java，suggested）
- [[cust_user_rel]]：cust_company_info.id → cust_user_rel.company_id（write-flow:SubmitCustInfoEnhanceService.java，confirmed）
