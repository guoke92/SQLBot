---
type: table
title: cust_certification_info
page_key: cust_certification_info
belong: tables
domain: 基线
status: draft
anchors: [cust_certification_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# cust_certification_info

（基线页：31 字段，行数估计 7127。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_certification_info
database: lowcode_pplatform
desc: cust_certification_info
inactive: false
fields:
  - name: auto_verify_status
    type: string
    phys: varchar(64)
    dict: auto_verify_status
    topk: AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|TO_BE_VERIFIED
  - name: certification_type
    type: string
    phys: varchar(64)
    dict: certification_type
    topk: AUTH_MEDIA_OCR|AUTH_THREE_ELEMENTS|COMPANY_TWO_ELEMENTS|FACE_VERIFY
  - name: act_procinst_date
    type: temporal
    phys: datetime
  - name: act_procinst_id
    type: string
    phys: varchar(64)
  - name: act_procinst_no
    type: string
    phys: varchar(255)
  - name: act_procinst_status
    type: string
    phys: varchar(64)
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    topk: base|common
  - name: auto_verify_count
    type: number
    phys: int(11)
    topk: -1|-3|-7|0
    group: auto_verify_count_group, auto_verify_time_group, create_time_group
  - name: auto_verify_data
    type: string
    phys: text
  - name: auto_verify_msg
    type: string
    phys: varchar(604)
    desc: 自动核查结果
    topk: OK|不一致
  - name: auto_verify_time
    type: temporal
    phys: datetime
    group: auto_verify_count_group, auto_verify_time_group
  - name: code
    type: string
    phys: varchar(64)
  - name: create_by
    type: string
    phys: varchar(100)
  - name: create_time
    type: temporal
    phys: datetime
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
  - name: db_tenant_code
    type: string
    phys: varchar(100)
  - name: enable
    type: string
    phys: varchar(4)
    topk: Y
  - name: face_business_no
    type: string
    phys: varchar(128)
  - name: id
    type: number
    phys: bigint(20)
  - name: manual_verify_count
    type: number
    phys: int(11)
    group: manual_verify_count_group
  - name: manual_verify_msg
    type: string
    phys: varchar(128)
    topk: 1|321|自动化测试人工核查通过
  - name: manual_verify_status
    type: string
    phys: varchar(64)
    topk: MANUAL_AUTHENTICATION_PASSED
  - name: manual_verify_time
    type: temporal
    phys: datetime
    group: manual_verify_count_group
  - name: name
    type: string
    phys: varchar(64)
  - name: organization_id
    type: string
    phys: varchar(30)
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
  - name: remark
    type: string
    phys: varchar(1024)
  - name: update_by
    type: string
    phys: varchar(100)
  - name: update_time
    type: temporal
    phys: datetime
    group: create_time_group, project_effective_time_group, update_time_group
  - name: update_user
    type: string
    phys: varchar(100)
  - name: verify_score
    type: number
    phys: double
```

## 关联表

- [[cust_company_info]]：cust_certification_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustCertificationInfoDO.java，suggested）
- [[cust_person_info]]：cust_certification_info.ref_cust_company_info → cust_person_info.code（write-flow:MiniFaceServiceImpl.java，confirmed）
