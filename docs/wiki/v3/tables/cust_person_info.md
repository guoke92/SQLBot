---
type: table
title: 客户联系人表
page_key: cust_person_info
belong: tables
status: draft
anchors: [cust_person_info]
sources: ['database_schema:lowcode_pplatform.cust_person_info', 'code_path:CustCompanyInfoApplication.java:1553']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_build_record, cust_oper_change_record, cust_company_info, cust_person_info__enable,
  cust_person_info__certification_type, cust_person_info__status, cust_person_info__user_type,
  cust_person_info__face_status, cust_person_info__realname_status, cust_person_info__test_data,
  cust_person_info__company_type, cust_person_info__cust_build_status, cust_person_info__operator_push_system,
  cust_person_info__skip_auth_flag, cust_person_info__source, cust_person_info__real_name_result]
---

# 客户联系人表

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_person_info
database: lowcode_pplatform
desc: 客户联系人表
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, en_name, handby_person_name, user_name]
fields:
- name: id
  type: number
  desc: 表主键
  nullable: false
- name: code
  type: string
  desc: 编码
- name: name
  type: string
  desc: 姓名
- name: enable
  type: string
  desc: enable
  dict: [Y, N]
  written_with: [status]
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
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
  desc: 机构编号
- name: phone
  type: string
  desc: 手机号
- name: certification_type
  type: string
  desc: 证件类型
  dict: [CRET_ID, CREDENTIALS_ID, CERT_RESIDENT_PERMIT, CERT_PASSPORT, CERT_GREEN_CARD,
    CERT_TAIWAN, CERT_MAINLAND_PASS, CERT_HK_AND_MACAU_PASS, CRET_ID_HK]
  label: {CRET_ID: 二代居民身份证, CERT_RESIDENT_PERMIT: 港澳台居民居住证, CERT_PASSPORT: 护照, CERT_GREEN_CARD: 外国人永久居留证,
    CERT_TAIWAN: 台胞证, CERT_MAINLAND_PASS: 港澳居民来往内地通行证, CERT_HK_AND_MACAU_PASS: 港澳通行证,
    CRET_ID_HK: 香港身份证}
- name: certification_no
  type: string
  desc: 证件号码
- name: certification_expire
  type: string
  desc: 证件有效期
- name: email
  type: string
  desc: 邮箱
- name: user_id
  type: number
  desc: 关联用户
- name: main_data_id
  type: number
  desc: 主数据id
- name: ref_cust_company_info
  type: string
  desc: 关联企业
- name: status
  type: string
  desc: 联系人账号状态
  dict: [ADD, EFFECT, FREEZE, N, WRITEOFF]
  label: {ADD: 未激活, EFFECT: 已激活, FREEZE: 冻结, WRITEOFF: 注销}
  written_with: [enable]
- name: cust_company_id
  type: number
  desc: 冗余企业id
- name: user_type
  type: string
  desc: 联系人类型
  dict: [accountAdmin, accountNormal, accountGuest]
  label: [管理员, 经办人, 游客]
- name: face_status
  type: string
  desc: 人脸认证结果
  dict: [TO_BE_VERIFIED, AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED,
    AUTOMATIC_AUTHENTICATION_FAILED]
- name: auth_application
  type: string
  desc: 开通产品
- name: realname_status
  type: string
  desc: 实名认证
  dict: [TO_BE_VERIFIED, AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED,
    AUTOMATIC_AUTHENTICATION_FAILED]
- name: platform_user_id
  type: number
  desc: 运营系统用户id
- name: en_name
  type: string
  desc: 姓名(英文)
- name: birth_date
  type: temporal
  desc: 出生日期
- name: en_name_end
  type: string
  desc: 人名 (英文)
- name: test_data
  type: string
  dict: [N, Y]
- name: company_type
  type: string
  dict: [SUPPLIER, CORE, FINANCE, PROJECT_COMPANY, CORPORATION_COMPANY, PLATFORM_OPERATOR_COMPANY,
    DEALER, CORE_MANAGER, '["SUPPLIER"]', CORE_FUNCTIONAL_DEPARTMENT, CORE_SUB, CORE_BRANCH,
    FACTOR_COMPANY, PLATFORM_COMPANY]
  label: {SUPPLIER: 供应商, CORE: 核心企业, FINANCE: 金融机构, PROJECT_COMPANY: 项目公司, CORPORATION_COMPANY: 集团公司,
    PLATFORM_OPERATOR_COMPANY: 平台运营方, DEALER: 经销商, CORE_MANAGER: 核心企业管理机构, CORE_FUNCTIONAL_DEPARTMENT: 核心企业职能部门,
    CORE_SUB: 核心企业子公司, CORE_BRANCH: 核心企业分公司, FACTOR_COMPANY: 保理买卖方, PLATFORM_COMPANY: 平台方}
- name: operator
  type: string
- name: handby_person
  type: string
- name: operator_id
  type: string
  desc: 运营人id
- name: operator_realname
  type: string
  desc: 运营人姓名
- name: phone_realname_status
  type: string
  desc: 手机实名状态
- name: handby_person_name
  type: string
  desc: 建档经办人名字
- name: user_name
  type: string
  desc: 登录账号
- name: cust_build_status
  type: string
  desc: 建档状态
  dict: [CUST_CONFIRM_AWAIT, BUILD_SUCCESS, BUILD_FAIL, CUST_BUILDING, INIT]
- name: operator_push_system
  type: string
  desc: 经办人推送系统列表
  dict: [ams_supplier_pc, ams_proj_pc, ams_finance_pc, smebee_pc]
- name: skip_auth_flag
  type: string
  desc: 跳过实名认证标识
  dict: [N, Y]
- name: source
  type: string
  desc: 来源
  dict: [longteng, AMS, jingke]
  label: {longteng: 龙腾, AMS: 管理员}
- name: ext_data
  type: string
  desc: 扩展字段
- name: real_name_result
  type: string
  desc: 实名认证结果
  dict: [INIT, VERIFIED_SUCCESS, VERIFIED_FAILED]
default_filter:
  predicate: cust_person_info.enable = 'Y'
  trust: confirmed
  evidence: code_path:CustCompanyInfoApplication.java:1553
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_person_info.ref_cust_company_info
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustCompanyInfoApplication.java:1553
source: l1_code
join_role: identity
priority: primary
authenticity_note: 人员主引用是企业 code。L0 把 id 接到 ref 列是假边。
```

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.cust_company_id
cardinality: one_to_many
trust: confirmed
authenticity: likely
evidence: code_path:CustPersonApplication.java:740
source: l1_code
join_role: identity
priority: secondary
name_evidence:
  match: stem_info
  stem: cust_company
  comment: 冗余企业id
overlap:
  probed: true
  ratio: 0.9939
  sample_size: 165
  miss: 1
  deepened: false
  query_ok: true
  authenticity: likely
authenticity_note: 冗余企业 id，查询里与 code 引用并存，不是 ref_cust_company_info。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_person_info.ref_cust_company_info
cardinality: one_to_many
trust: disputed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_person_info.ref_cust_company_info;database_profile:lowcode_pplatform.cust_person_info.ref_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: exact_table
  stem: cust_company_info
  comment: 关联企业
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_person_info.ref_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_person_info.ref_cust_company_info,
  trust: proposed}
```

## 页面链接

### 关联表

- [[tables/cust_build_record]]
- [[tables/cust_oper_change_record]]
- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_person_info__enable]]（`cust_person_info.enable`）
- [[dicts/cust_person_info__certification_type]]（`cust_person_info.certification_type`）
- [[dicts/cust_person_info__status]]（`cust_person_info.status`）
- [[dicts/cust_person_info__user_type]]（`cust_person_info.user_type`）
- [[dicts/cust_person_info__face_status]]（`cust_person_info.face_status`）
- [[dicts/cust_person_info__realname_status]]（`cust_person_info.realname_status`）
- [[dicts/cust_person_info__test_data]]（`cust_person_info.test_data`）
- [[dicts/cust_person_info__company_type]]（`cust_person_info.company_type`）
- [[dicts/cust_person_info__cust_build_status]]（`cust_person_info.cust_build_status`）
- [[dicts/cust_person_info__operator_push_system]]（`cust_person_info.operator_push_system`）
- [[dicts/cust_person_info__skip_auth_flag]]（`cust_person_info.skip_auth_flag`）
- [[dicts/cust_person_info__source]]（`cust_person_info.source`）
- [[dicts/cust_person_info__real_name_result]]（`cust_person_info.real_name_result`）
