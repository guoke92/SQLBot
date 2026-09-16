---
type: table
title: CA 认证上送行
page_key: ca_certification_info
domain: CA证书认证
status: draft
anchors: [ca_certification_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:CaCertificationInfoDO.java"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [ca_cert]
---

# CA 认证上送行

场景 [[ca_cert]] 的**主档**。`cust_id` 对应 [[cust_company_info]].id（总公司行时取 `cust_head_company_info.id`）。企业是否已开通签章看主档上的 `ca_register_status`，不是本表 `submit_status`。

`op_type` 代码只写 `INSERT`；`cust_type` 代码恒为 `COMPANY`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[ca_cert]]

`id`, `enable`, `create_time`, `update_time`, `cust_id`, `cust_type`, `data_source`, `head_company_data`, `op_type`, `submit_status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `batch_no`, `data_date`, `db_tenant_code`, `enterprise_four_json`, `file_refs_json`, `intent_h_face_json`, `intent_sms_json`, `name`, `notify_agreement_json`, `organization_id`, `police_two_json`, `remark`, `sign_platform_result`, `submit_time`

```ground:table
table: ca_certification_info
database: lowcode_pplatform
desc: CA认证信息
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [ca_cert]
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
    group: always
    scenes: [ca_cert]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [ca_cert]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [ca_cert]
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "报数主体企业 id"
    roles: [query]
    scenes: [ca_cert]
  - name: cust_type
    type: string
    phys: varchar(64)
    desc: "PERSON / COMPANY"
    dict: cust_type
    topk: "COMPANY"
    scenes: [ca_cert]
  - name: data_source
    type: string
    phys: varchar(64)
    desc: "数据来源"
    dict: ca_data_source
    topk: "CHANNEL_OPENAPI|FBP_PORTAL|OPERATION_PLATFORM"
    roles: [query]
    scenes: [ca_cert]
  - name: head_company_data
    type: string
    phys: varchar(2)
    desc: "是否总公司行"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [ca_cert]
  - name: op_type
    type: string
    phys: varchar(64)
    desc: "INSERT / UPDATE"
    topk: "INSERT"
    scenes: [ca_cert]
  - name: submit_status
    type: string
    phys: varchar(64)
    desc: "上送签章中台状态"
    dict: ca_submit_status
    topk: "FAIL|PENDING|SUCCESS"
    roles: [query]
    scenes: [ca_cert]
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
    topk: "base"
  - name: batch_no
    type: string
    phys: varchar(64)
    desc: "批次号"
  - name: data_date
    type: string
    phys: varchar(64)
    desc: "数据时间"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: enterprise_four_json
    type: string
    phys: text
    desc: "企业四要素"
  - name: file_refs_json
    type: string
    phys: text
    desc: "附件"
  - name: intent_h_face_json
    type: string
    phys: text
    desc: "意愿 H5_FACE"
  - name: intent_sms_json
    type: string
    phys: text
    desc: "意愿 SMS_CODE"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: notify_agreement_json
    type: string
    phys: text
    desc: "协议通知"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: police_two_json
    type: string
    phys: text
    desc: "实名 POLICE_TWO"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: sign_platform_result
    type: string
    phys: mediumtext
    desc: "中台返回结果"
  - name: submit_time
    type: temporal
    phys: datetime
    desc: "提交时间"
```

```ground:relation
type: EQUI_JOIN
left: ca_certification_info.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CaCertificationInfoDO.java
```
