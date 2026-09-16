---
type: table
title: 协议迁移记录
page_key: argeement_migratory_record
domain: 授权协议与电子授权
status: draft
anchors: [argeement_migratory_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [authorization]
---

# 协议迁移记录

表名以库为准。`status` 写入 BooleanEnum yes/no 的 dictKey，库内为 `1`/`0`。`sign_mode`：`01` 线上 / `02` 线下 / `03` 无需签署。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[authorization]]

`id`, `enable`, `create_time`, `update_time`, `agreement_type`, `cust_id`, `is_new`, `platform_product_code`, `sign_mode`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `agreement_name`, `agreement_no`, `agreement_path`, `app_tenant_code`, `db_tenant_code`, `effect_date`, `expire_date`, `name`, `organization_id`, `pull_num`, `remark`, `sign_date`

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
desc: 协议迁移记录
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [authorization]
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
    scenes: [authorization]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [authorization]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [authorization]
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
  - name: agreement_type
    type: string
    phys: varchar(64)
    desc: "协议类型"
    topk: "BS_Auth|CFCA_Auth|CustPersonLicense|PrivacyPolicy|ProductProtocolAcflow|ProductProtocolAms|ProductProtocolBeecredit|ProductProtocolOrder|ProductProtocolRvsfactor_PC|ProductProtocolStorage|ProductProtocolVoucher|UserProtocol"
    roles: [query]
    scenes: [authorization]
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "产融客户id"
    roles: [query]
    scenes: [authorization]
  - name: is_new
    type: string
    phys: varchar(10)
    desc: "是否新数据"
    topk: "no|yes"
    labels: "no:否|yes:是"
    scenes: [authorization]
  - name: platform_product_code
    type: string
    phys: varchar(64)
    desc: "产品编码"
    topk: "ACFLOW|AMS|BEECREDIT|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
    roles: [query]
    scenes: [authorization]
  - name: sign_mode
    type: string
    phys: varchar(20)
    desc: "签署模式"
    dict: sign_mode
    topk: "01|02|03"
    labels: "01:线上|02:线下|03:无需签署"
    roles: [query]
    scenes: [authorization]
  - name: status
    type: number
    phys: int(10)
    desc: "状态"
    topk: "0|1"
    labels: "0:否|1:是"
    roles: [query]
    scenes: [authorization]
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
  - name: agreement_name
    type: string
    phys: varchar(128)
    desc: "协议名称"
  - name: agreement_no
    type: string
    phys: varchar(64)
    desc: "协议编号"
  - name: agreement_path
    type: string
    phys: varchar(128)
    desc: "协议路径"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: effect_date
    type: temporal
    phys: date
    desc: "协议生效日"
  - name: expire_date
    type: temporal
    phys: date
    desc: "失效时间"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: pull_num
    type: number
    phys: int(10)
    desc: "拉取次数"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: sign_date
    type: temporal
    phys: date
    desc: "签署日期"
```

```ground:relation
type: EQUI_JOIN
left: argeement_migratory_record.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:AgreementMigratoryService.java
```
