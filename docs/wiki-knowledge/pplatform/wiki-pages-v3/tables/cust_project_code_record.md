---
type: table
title: 项目码录入记录
page_key: cust_project_code_record
domain: 项目报表/统计/上报
status: draft
anchors: [cust_project_code_record]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_project]
---

# 项目码录入记录

`company_id` → 企业 id。`status` 写入 BooleanEnum。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_project]]

`id`, `enable`, `create_time`, `update_time`, `channel_code`, `company_id`, `status`, `type`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `company_type`, `db_tenant_code`, `name`, `organization_id`, `remark`, `use_id`

```ground:table
table: cust_project_code_record
database: lowcode_pplatform
desc: 企业项目码输入记录
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [company_project]
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
    scenes: [company_project]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [company_project]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_project]
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
  - name: channel_code
    type: string
    phys: varchar(32)
    desc: "项目码/渠道码"
    roles: [query]
    scenes: [company_project]
  - name: company_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    roles: [query]
    scenes: [company_project]
  - name: status
    type: string
    phys: varchar(4)
    desc: "是否正确"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [company_project]
  - name: type
    type: string
    phys: varchar(32)
    desc: "类型"
    topk: "PC_BUILD|userCompanyRegister|产品中心|产品中心-企业认证成功"
    scenes: [company_project]
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
    topk: "base|common|xyc.llschain.com"
  - name: company_type
    type: string
    phys: varchar(200)
    desc: "企业角色"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
    topk: "HKC|ISOLATE_TAG_HBCI|ISOLATE_TAG_LONGYANCHENGFA|ISOLATE_TAG_NAURA|ISOLATE_TAG_lygs|ISOLATE_TAG_yccsfzjt|ISOLATE_TAG_ytzl|JFT|LN1|beehive-scf.qhhrly.cn|cdpd|dhhk|jiuersanzuhu|jkny|lho2zuhu2|ning|spsi.beehive-scf.qhhrly.cn|wukong|zhongtieqijujituanyouxiangongsi|zuhuyanshi01"
  - name: name
    type: string
    phys: varchar(64)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: use_id
    type: number
    phys: bigint(20)
    desc: "用户id"
```

```ground:relation
type: EQUI_JOIN
left: cust_project_code_record.company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustProjectRelEnhanceService.java
```
