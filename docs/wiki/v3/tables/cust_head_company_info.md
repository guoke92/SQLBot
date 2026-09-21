---
type: table
title: 客户总公司信息
page_key: cust_head_company_info
belong: tables
status: draft
anchors: [cust_head_company_info]
sources: ['database_schema:lowcode_pplatform.cust_head_company_info']
created: '2026-09-21'
updated: '2026-09-21'
contract_version: '0.1'
databases: [lowcode_pplatform]
related: [cust_company_info, cust_head_company_info__legal_certification_type, cust_head_company_info__enable]
---

# 客户总公司信息

L1 源码增强合同（draft）。无 code_path 的关系仍不得当认证 JOIN。

## 字段

```ground:table
table: cust_head_company_info
database: lowcode_pplatform
desc: 客户总公司信息
inactive: false
primary_key: [id]
grain: 一行一记录（id）
name_anchors: [code, name, cust_short_name, cust_english_name, cust_english_short_name,
  legal_name, legal_english_first_name, legal_english_sec_name]
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
  desc: 企业名称
- name: cust_short_name
  type: string
  desc: 企业简称
- name: cust_english_name
  type: string
  desc: 企业名称(英文)
- name: cust_english_short_name
  type: string
  desc: 企业简称(英文)
- name: certification_no
  type: string
  desc: 统一社会信用代码
- name: time_permanent
  type: string
  desc: 营业执照有效期
- name: establishment_time
  type: temporal
  desc: 注册日期
- name: regist_province_city
  type: string
  desc: 注册省份
- name: regist_province_city_english
  type: string
  desc: 注册省市(英文)
- name: registered_address
  type: string
  desc: 注册地址
- name: legal_name
  type: string
  desc: 法人姓名
- name: legal_phone
  type: string
  desc: 法人手机号
- name: legal_certification_no
  type: string
  desc: 法人证件号
- name: legal_certification_type
  type: string
  desc: 法人证件类型
  dict: [CRET_ID, CERT_MAINLAND_PASS, CERT_PASSPORT, 身份证, CERT_GREEN_CARD, CERT_TAIWAN,
    CRET_ID_HK]
- name: legal_time_permanent
  type: string
  desc: 法人证件有效期
- name: ref_cust_head_company_info_cust_company_info
  type: string
  desc: 客户信息和总公司信息
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
- name: act_procinst_date
  type: temporal
  desc: 审批结束时间
- name: organization_id
  type: string
- name: legal_english_first_name
  type: string
  desc: 法人英文姓
- name: legal_english_sec_name
  type: string
  desc: 法人英文名
- name: legal_birth_date
  type: temporal
  desc: 法人生日
- name: regist_province_city_english_end
  type: string
  desc: 注册市(英文)
- name: head_approval_date
  type: temporal
  desc: 总公司核准日期
- name: head_business_scope
  type: string
  desc: 总公司经营范围
```

## 关联关系

### likely — 值域支持且列名/注释有关联语义

```ground:relation
type: EQUI_JOIN
left: cust_company_info.code
right: cust_head_company_info.ref_cust_head_company_info_cust_company_info
cardinality: one_to_one
trust: confirmed
authenticity: likely
evidence: code_path:CustDocFacade.java:952
source: l1_code
join_role: identity
priority: primary
authenticity_note: 总公司资料按企业 code 关联，不是 id。
```

### disputed — 与已确认边冲突

```ground:relation
type: EQUI_JOIN
left: cust_company_info.id
right: cust_head_company_info.ref_cust_head_company_info_cust_company_info
cardinality: one_to_many
trust: disputed
authenticity: unlikely
evidence: database_schema:lowcode_pplatform.cust_head_company_info.ref_cust_head_company_info_cust_company_info;database_profile:lowcode_pplatform.cust_head_company_info.ref_cust_head_company_info_cust_company_info
source: name
join_role: identity
priority: primary
name_evidence:
  match: long_ref
  stem: cust_company_info
  comment: 客户信息和总公司信息
overlap:
  probed: true
  ratio: 0.0
  sample_size: 200
  miss: 200
  deepened: false
  query_ok: true
  authenticity: unlikely
sides:
- {source: l1_code, left: cust_company_info.code, right: cust_head_company_info.ref_cust_head_company_info_cust_company_info,
  trust: confirmed}
- {source: name, left: cust_company_info.id, right: cust_head_company_info.ref_cust_head_company_info_cust_company_info,
  trust: proposed}
```

## 页面链接

### 关联表

- [[tables/cust_company_info]]

### 字典

- [[dicts/cust_head_company_info__legal_certification_type]]（`cust_head_company_info.legal_certification_type`）
- [[dicts/cust_head_company_info__enable]]（`cust_head_company_info.enable`）
