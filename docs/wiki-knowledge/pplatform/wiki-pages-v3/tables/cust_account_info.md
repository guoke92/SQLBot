---
type: table
title: 企业银行账户
page_key: cust_account_info
domain: 企业银行账户/集团/SFTP
status: draft
anchors: [cust_account_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [bank_account]
---

# 企业银行账户

场景 [[bank_account]] 主档。`ref_cust_company_info` → 企业 `code`。联系人保存账户时 `account_type` 写入 `AccountTypeEnum.BANK.getDictParam()`（枚举名 `BANK`）；枚举 dictKey 另有 `'1'`。问银行账户用库值 `BANK`。`auth_state` 才是打款认证过程。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[bank_account]]

`id`, `enable`, `create_time`, `update_time`, `account_name`, `account_no`, `account_type`, `auth_state`, `default_account_flag`, `payment_remaining_count`, `ref_cust_company_info`, `status`

### 未分窗

仍留表页，待代码证据划入场景：`act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `address`, `app_tenant_code`, `bank_branch_name`, `bank_city_code`, `bank_city_name`, `bank_code`, `bank_code_name`, `bank_id`, `bank_no`, `bank_province_code`, `bank_province_name`, `db_tenant_code`, `email`, `error_try_count`, `error_try_time`, `main_data_id`, `name`, `organization_id`, `receive_payment_type`, `remark`, `telephone`, `trace_no`, `trans_id`

```ground:table
table: cust_account_info
database: lowcode_pplatform
desc: 客户银行账号信息主表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    group: always
    scenes: [bank_account]
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
    roles: [query]
    group: always
    scenes: [bank_account]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    group: always
    scenes: [bank_account]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [bank_account]
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
  - name: account_name
    type: string
    phys: varchar(128)
    desc: "账户名称"
    roles: [result]
    scenes: [bank_account]
  - name: account_no
    type: string
    phys: varchar(128)
    desc: "账户账号"
    roles: [query]
    scenes: [bank_account]
  - name: account_type
    type: string
    phys: varchar(64)
    desc: "账户类型"
    dict: account_type
    topk: "1|BANK|OPERATION_FEE_ACCOUNT|received"
    labels: "1:银行|received:收款"
    roles: [query]
    scenes: [bank_account]
  - name: auth_state
    type: string
    phys: varchar(64)
    desc: "认证状态"
    dict: account_auth_state
    topk: "APPLY_00|APPLY_20|APPLY_40"
    roles: [query]
    scenes: [bank_account]
  - name: default_account_flag
    type: string
    phys: varchar(64)
    desc: "是否为默认账户"
    topk: "0|1"
    labels: "0:否|1:是"
    roles: [query]
    scenes: [bank_account]
  - name: payment_remaining_count
    type: number
    phys: int(10)
    desc: "剩余打款次数"
    scenes: [bank_account]
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: "客户账号信息"
    roles: [query]
    scenes: [bank_account]
  - name: status
    type: string
    phys: varchar(128)
    desc: "账户状态"
    topk: "INIT"
    scenes: [bank_account]
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
  - name: address
    type: string
    phys: varchar(128)
    desc: "地址"
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: "逻辑租户标识"
    topk: "QA2tiepai2|base"
  - name: bank_branch_name
    type: string
    phys: varchar(128)
    desc: "账户开户行"
  - name: bank_city_code
    type: string
    phys: varchar(128)
    desc: "银行城市代码"
  - name: bank_city_name
    type: string
    phys: varchar(128)
    desc: "银行城市名称"
  - name: bank_code
    type: string
    phys: varchar(128)
    desc: "银行(总行)代码"
  - name: bank_code_name
    type: string
    phys: varchar(128)
    desc: "银行(总行)名称"
  - name: bank_id
    type: string
    phys: varchar(128)
    desc: "银行ID"
  - name: bank_no
    type: string
    phys: varchar(512)
    desc: "联行号"
  - name: bank_province_code
    type: string
    phys: varchar(128)
    desc: "银行所属省份代码"
  - name: bank_province_name
    type: string
    phys: varchar(128)
    desc: "银行所属省份名称"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: email
    type: string
    phys: varchar(128)
    desc: "电子邮箱"
  - name: error_try_count
    type: number
    phys: int(10)
    desc: "打款金额错误次数"
    topk: "0"
    labels: "0:否"
  - name: error_try_time
    type: temporal
    phys: datetime
    desc: "最后一次错误时间"
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: "主数据id"
  - name: name
    type: string
    phys: varchar(128)
    desc: "名称-废弃"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: receive_payment_type
    type: string
    phys: varchar(128)
    desc: "收付类型"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: telephone
    type: string
    phys: varchar(128)
    desc: "电话"
  - name: trace_no
    type: string
    phys: varchar(128)
    desc: "系统跟踪号"
  - name: trans_id
    type: string
    phys: varchar(128)
    desc: "交易ID"
```

```ground:relation
type: EQUI_JOIN
left: cust_account_info.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustAccountInfoDO.java
```
