---
type: table
title: CA认证信息
page_key: ca_certification_info
belong: tables
domain: 基线
status: draft
anchors: [ca_certification_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# CA认证信息

（基线页：34 字段，行数估计 671。行语义/常用过滤待语义摄取增强。）

```ground:table
table: ca_certification_info
database: lowcode_pplatform
desc: CA认证信息
inactive: false
fields:
  - name: cust_type
    type: string
    phys: varchar(64)
    desc: PERSON / COMPANY
    dict: cust_type
    topk: COMPANY
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
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
  - name: batch_no
    type: string
    phys: varchar(64)
    desc: 批次号
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 企业Id
  - name: data_date
    type: string
    phys: varchar(64)
    desc: 数据时间
  - name: data_source
    type: string
    phys: varchar(64)
    desc: 数据来源
    topk: CHANNEL_OPENAPI|FBP_PORTAL|OPERATION_PLATFORM
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: ISOLATE_TAG_CJTZ|ISOLATE_TAG_HBLT|ISOLATE_TAG_cdxctz|ISOLATE_TAG_hscc
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: enterprise_four_json
    type: string
    phys: text
    desc: 企业四要素
  - name: file_refs_json
    type: string
    phys: text
    desc: 附件
  - name: head_company_data
    type: string
    phys: varchar(2)
    desc: 是否总公司
    topk: N|Y
  - name: intent_h_face_json
    type: string
    phys: text
    desc: 意愿 H5_FACE
  - name: intent_sms_json
    type: string
    phys: text
    desc: 意愿 SMS_CODE
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: notify_agreement_json
    type: string
    phys: text
    desc: "协议通知 "
  - name: op_type
    type: string
    phys: varchar(64)
    desc: INSERT / UPDATE
    topk: INSERT
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: police_two_json
    type: string
    phys: text
    desc: 实名 POLICE_TWO
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sign_platform_result
    type: string
    phys: mediumtext
    desc: 中台返回结果
  - name: submit_status
    type: string
    phys: varchar(64)
    desc: PENDING / SUCCESS / FAIL
    topk: FAIL|PENDING|SUCCESS
  - name: submit_time
    type: temporal
    phys: datetime
    desc: 提交时间
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
