---
type: table
title: 客户总公司信息
page_key: cust_head_company_info
domain: 基线
status: draft
anchors: [cust_head_company_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-10'
updated: '2026-09-10'
contract_version: "0.1"
---

# 客户总公司信息

（基线页：39 字段，行数估计 893。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_head_company_info
database: lowcode_pplatform
desc: 客户总公司信息
inactive: false
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: legal_certification_type
    type: string
    phys: varchar(512)
    desc: 法人证件类型
    dict: legal_certification_type
    topk: CERT_GREEN_CARD|CERT_MAINLAND_PASS|CERT_PASSPORT|CERT_TAIWAN
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
    topk: base
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 统一社会信用代码
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
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_english_name
    type: string
    phys: varchar(200)
    desc: 企业名称(英文)
  - name: cust_english_short_name
    type: string
    phys: varchar(200)
    desc: 企业简称(英文)
  - name: cust_short_name
    type: string
    phys: varchar(200)
    desc: 企业简称
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: establishment_time
    type: temporal
    phys: date
    desc: 注册日期
    group: establishment_time_group, legal_birth_date_group
  - name: head_approval_date
    type: temporal
    phys: date
    desc: 总公司核准日期
  - name: head_business_scope
    type: string
    phys: varchar(2000)
    desc: 总公司经营范围
  - name: legal_birth_date
    type: temporal
    phys: date
    desc: 法人生日
    group: establishment_time_group, legal_birth_date_group
  - name: legal_certification_no
    type: string
    phys: varchar(128)
    desc: 法人证件号
  - name: legal_english_first_name
    type: string
    phys: varchar(200)
    desc: 法人英文姓
  - name: legal_english_sec_name
    type: string
    phys: varchar(200)
    desc: 法人英文名
  - name: legal_name
    type: string
    phys: varchar(128)
    desc: 法人姓名
  - name: legal_phone
    type: string
    phys: varchar(128)
    desc: 法人手机号
  - name: legal_time_permanent
    type: string
    phys: varchar(512)
    desc: 法人证件有效期
  - name: name
    type: string
    phys: varchar(200)
    desc: 企业名称
  - name: organization_id
    type: string
    phys: varchar(30)
  - name: ref_cust_head_company_info_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户信息和总公司信息
  - name: regist_province_city
    type: string
    phys: varchar(512)
    desc: 注册省份
  - name: regist_province_city_english
    type: string
    phys: varchar(128)
    desc: 注册省市(英文)
  - name: regist_province_city_english_end
    type: string
    phys: varchar(100)
    desc: 注册市(英文)
  - name: registered_address
    type: string
    phys: varchar(500)
    desc: 注册地址
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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
```

## 关联表

- [[cust_company_info]]：cust_head_company_info.ref_cust_head_company_info_cust_company_info → cust_company_info.code（ref-convention:CustHeadCompanyInfoDO.java，suggested）
