---
type: table
title: 客户信息主表
page_key: cust_company_info
belong: tables
domain: 基线
status: draft
anchors: [cust_company_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户信息主表

（基线页：139 字段，行数估计 91189。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_company_info
database: lowcode_pplatform
desc: 客户信息主表
inactive: false
fields:
  - name: cust_build_status
    type: string
    phys: varchar(64)
    desc: 认证状态
    dict: cust_build_status
    topk: AWAIT_CUST_CONFIRM|BUILDING|BUILD_ACTIVATE|BUILD_BACK
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
    topk: ADD|CHANGE|EFFECT|FREEZE
    roles: [query]
  - name: data_type
    type: string
    phys: varchar(4)
    desc: 数据类型：1,主数据，0记录数据
    dict: data_type
    topk: 0|1|2
    roles: [query]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
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
  - name: cust_build_type
    type: string
    phys: varchar(64)
    desc: 录入方式
    dict: cust_build_type
    topk: AGW_BUILD|PC_BUILD|SIMPLE
  - name: cust_scale
    type: string
    phys: varchar(128)
    desc: 企业规模
    dict: cust_scale
    topk: qw
  - name: cust_source
    type: string
    phys: varchar(64)
    desc: 建档数据来源
    dict: cust_source
    topk: MIGRATORY|PLATFORM|PLATFORM_PUSH|PPLATFORM
  - name: identify_style
    type: string
    phys: varchar(64)
    desc: 认证方式
    dict: identify_style
    topk: INVITE|INVITE_AGW|SELF|SIMPLE
  - name: legal_certification_type
    type: string
    phys: varchar(64)
    desc: 法人证件类型
    dict: legal_certification_type
    topk: CERT_GREEN_CARD|CERT_MAINLAND_PASS|CERT_OTHER|CERT_PASSPORT
  - name: sign_mode
    type: string
    phys: varchar(64)
    desc: 产品协议签署方式
    dict: sign_mode
    topk: ONLINE
  - name: abroad_cust
    type: string
    phys: varchar(512)
    desc: 是否境外
    topk: N|Y
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
    topk: 变更成功|审批中|待客户确认|认证失败
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: ISOLATE_TAG_JHYL|JHYL|QA2tiepai2|base
  - name: apply_data_id
    type: number
    phys: bigint(20)
    desc: 认证流程数据id
  - name: apply_type
    type: string
    phys: varchar(64)
    desc: 流程类型
    topk: add|update
  - name: approval_date
    type: temporal
    phys: date
    desc: 核准日期
    group: legal_certification_end_time_group
  - name: audit_back_flag
    type: string
    phys: varchar(2)
    desc: 审核退回标记
    topk: N|Y
  - name: auth_aggrement_supplement_flag
    type: string
    phys: varchar(2)
    desc: 是否授权书补签标识
    topk: N|Y
  - name: back_reason
    type: string
    phys: varchar(2000)
    desc: 退回原因
    topk: d|补充资料|退回
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
    topk: 个体户合伙企业|事业单位|企业法人|国有企业
  - name: bs_register_status
    type: string
    phys: varchar(2)
    desc: 上上签开通状态
    topk: N|Y
  - name: business_address
    type: string
    phys: varchar(128)
    desc: 经营地址
    topk: ly数据库填写的经营地址随便填写展示|经验地址随便填写展示
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
    group: business_license_end_time_group, business_license_start_time_group
  - name: business_license_start_time
    type: temporal
    phys: date
    desc: 企业营业执照开始时间
    group: business_license_start_time_group
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
  - name: ca_register_status
    type: string
    phys: varchar(2)
    desc: CA开通状态
    topk: N|P|Y
  - name: cash_contract_no
    type: string
    phys: text
    desc: 中原融资合同编号（补充字段）
  - name: cert_no_flag
    type: string
    phys: varchar(64)
    desc: 执行查询统一信用证编码
    topk: Y
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统一信用代码
  - name: check_status
    type: string
    phys: varchar(30)
    desc: 审核状态
    topk: CUST_CHECK_BACKTOCUSTOM|CUST_CHECK_CHECKING|CUST_CHECK_INIT|CUST_CHECK_PASS
  - name: client_type
    type: string
    phys: varchar(128)
    desc: 发起变更的客户端类型
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
    topk: qdqw
  - name: contact_city
    type: string
    phys: varchar(128)
    desc: 联系市
    topk: 克拉玛依市|澳门
  - name: contact_city_code
    type: string
    phys: varchar(128)
    desc: 联系城市代码
    topk: 650200|820000
  - name: contact_province
    type: string
    phys: varchar(128)
    desc: 联系省份
    topk: 新疆维吾尔自治区|澳门
  - name: contact_province_city
    type: string
    phys: varchar(512)
    desc: 联系省市
  - name: contact_province_code
    type: string
    phys: varchar(128)
    desc: 联系省份代码
    topk: 650000|820000
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
    group: create_time_group, project_create_time_group, update_time_group
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
    group: establishment_time_group, legal_birth_date_group
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
  - name: group_company
    type: string
    phys: varchar(512)
    desc: 是否归属集团或核心企业
    topk: 1|N|Y
  - name: head_company
    type: string
    phys: varchar(512)
    desc: 是否总公司
    topk: N|Y
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
    topk: 中国农业银行抚顺新城路分理处
  - name: invoicing_bank_code
    type: string
    phys: varchar(128)
    desc: 开票银行代码
  - name: invoicing_bank_name
    type: string
    phys: varchar(128)
    desc: 开票银行名称
    topk: 中国农业银行
  - name: invoicing_bank_no
    type: string
    phys: varchar(512)
    desc: 开票银行联行号
    topk: 103224031227|103304362024|103304362223
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
    topk: 深圳信息科技股份有限公司|深圳招商股份有限公司|深圳科学股份有限公司|深圳科技股份有限公司
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
    group: establishment_time_group, legal_birth_date_group
  - name: legal_certification_end_time
    type: temporal
    phys: date
    desc: 法人证件结束日期
    group: legal_birth_date_group, legal_certification_end_time_group, legal_certification_start_time_group
  - name: legal_certification_no
    type: string
    phys: varchar(128)
    desc: 法人证件号
  - name: legal_certification_start_time
    type: temporal
    phys: date
    desc: 法人证件开始日期
    group: legal_certification_end_time_group, legal_certification_start_time_group
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
  - name: legal_realname_status
    type: string
    phys: varchar(100)
    desc: 法人认证状态
    topk: N|Y
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
  - name: migarory_auth_aggrement_flag
    type: string
    phys: varchar(2)
    desc: "新旧渠道授权书补签标识，Y 新渠道:N 旧渠道"
    topk: N|Y
  - name: nationality
    type: string
    phys: varchar(128)
    desc: 国籍
  - name: nationality_en
    type: string
    phys: varchar(128)
    desc: 国籍英文
  - name: need_charge
    type: string
    phys: varchar(2)
    desc: 运营方是否涉及收费
    topk: N|Y
  - name: need_register_bs
    type: string
    phys: varchar(4)
    desc: 是否需要开通上上签电子签章
    topk: N|Y
  - name: need_register_ca
    type: string
    phys: varchar(2)
    desc: 开通电子签章
    topk: N|Y
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: outside_org
    type: string
    phys: varchar(512)
    desc: 外部机构
    topk: 0|1|N|Y
  - name: paid_in_capital
    type: string
    phys: varchar(128)
    desc: 实缴资本（元）
  - name: pc_task_id
    type: string
    phys: varchar(128)
    desc: 退回客户端补充资料taskId
    topk: 110022|130005|135035|140030
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
  - name: signing_mode
    type: string
    phys: varchar(64)
    desc: 签署模式
    topk: 01
  - name: tenant_flg_en
    type: string
    phys: varchar(128)
    desc: 项目标识（英文）
  - name: test_data
    type: string
    phys: varchar(4)
    desc: 是否测试数据
    topk: N|Y
  - name: third_auth_status
    type: string
    phys: varchar(8)
    desc: 第三方认证状态
    topk: 1
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
    group: create_time_group, project_effective_time_group, update_time_group
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
- [[cust_auth_application]]：cust_company_info.code → cust_auth_application.ref_parent_company（write-flow:CustProductDomainService.java，confirmed）
- [[cust_build_record]]：cust_company_info.id → cust_build_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_certification_info]]：cust_company_info.code → cust_certification_info.ref_cust_company_info（ref-convention:CustCertificationInfoDO.java，suggested）
- [[cust_change_record]]：cust_company_info.id → cust_change_record.cust_id（java-eq:OperCustFacade.java，suggested）
- [[cust_customized_product]]：cust_company_info.code → cust_customized_product.ref_cust_customized_product_cust_company_info（ref-convention:CustCustomizedProductDO.java，suggested）
- [[cust_group_rel]]：cust_company_info.id → cust_group_rel.root_cust_id（java-eq:CustGroupRelApplication.java，suggested）
- [[cust_head_company_info]]：cust_company_info.code → cust_head_company_info.ref_cust_head_company_info_cust_company_info（ref-convention:CustHeadCompanyInfoDO.java，suggested）
- [[cust_interworking_product]]：cust_company_info.code → cust_interworking_product.ref_cust_interworking_product_cust_company_info（ref-convention:CustInterworkingProductDO.java，suggested）
- [[cust_person_info]]：cust_company_info.code → cust_person_info.ref_cust_company_info（ref-convention:CustPersonInfoDO.java，suggested）
- [[cust_project_code_record]]：cust_company_info.id → cust_project_code_record.company_id（write-flow:CustProjectRelEnhanceService.java，confirmed）
- [[cust_project_rel]]：cust_company_info.code → cust_project_rel.ref_cust_project_rel_cust_company_info（ref-convention:CustProjectRelDO.java，suggested）
- [[cust_role_info]]：cust_company_info.code → cust_role_info.ref_cust_company_info（ref-convention:CustRoleInfoDO.java，suggested）
- [[cust_shareholder_info]]：cust_company_info.code → cust_shareholder_info.ref_cust_company_info（ref-convention:CustShareholderInfoDO.java，suggested）
- [[cust_user_rel]]：cust_company_info.id → cust_user_rel.company_id（write-flow:SubmitCustInfoEnhanceService.java，confirmed）
