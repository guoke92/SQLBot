---
type: table
title: 授权确认书
page_key: authorization_agreement
domain: 授权协议与电子授权
status: draft
anchors: [authorization_agreement]
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

# 授权确认书

`cust_id` → 企业 id。`authed_status` 写入 BooleanEnum 的 Y/N。`creation_type` 落库是 dictKey：`CUST_BUILD_INIT` / `AUTO` / `COMPANY_MANAGER_CHANGE_CODE` / `COMPANY_AUTH_AGGREMENT`。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[authorization]]

`id`, `enable`, `create_time`, `update_time`, `authed_status`, `company_type`, `creation_type`, `cust_id`, `cust_manager_id`, `platform_product_code`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `cust_manager_name`, `cust_name`, `db_tenant_code`, `name`, `organization_id`, `original_cust_id`, `remark`

```ground:table
table: authorization_agreement
database: lowcode_pplatform
desc: 授权确认书表
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
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: authed_status
    type: string
    phys: varchar(512)
    desc: "授权书认证状态"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
    scenes: [authorization]
  - name: company_type
    type: string
    phys: varchar(512)
    desc: "企业角色"
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FACTOR_COMPANY|FINANCE|PLATFORM_OPERATOR_COMPANY|PLATFORM_OPREATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|["CORE"]|["FINANCE"]|["PROJECT_COMPANY"]"
    scenes: [authorization]
  - name: creation_type
    type: string
    phys: varchar(32)
    desc: "创建类型"
    topk: "AUTO|COMPANY_MANAGER_CHANGE_CODE|CUST_BUILD_INIT"
    scenes: [authorization]
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: "企业id"
    scenes: [authorization]
  - name: cust_manager_id
    type: number
    phys: bigint(20)
    desc: "企业管理员id"
    scenes: [authorization]
  - name: platform_product_code
    type: string
    phys: varchar(128)
    desc: "平台产品id"
    topk: "ACFLOW|AMS|BEECREDIT|ORDER|PLATFORM|RVSFACTOR|RVSFACTOR_PC|STORAGE|VOUCHER|pplatform"
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
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "JHYL|LLS|QA2tiepai2|base|common"
  - name: cust_manager_name
    type: string
    phys: varchar(256)
    desc: "客户管理员名称"
  - name: cust_name
    type: string
    phys: varchar(128)
    desc: "企业名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: name
    type: string
    phys: varchar(300)
    desc: "名称"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: original_cust_id
    type: string
    phys: varchar(128)
    desc: "源系统custid"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
```

```ground:relation
type: EQUI_JOIN
left: authorization_agreement.cust_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:AuthorizationAgreementDO.java
```
