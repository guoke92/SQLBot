---
type: table
title: 客户银行账号信息主表
page_key: cust_account_info
domain: 基线
status: draft
anchors: [cust_account_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户银行账号信息主表

（基线页：44 字段，行数估计 43755。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_account_info
database: lowcode_pplatform
desc: 客户银行账号信息主表
inactive: false
fields:
  - name: account_type
    type: string
    phys: varchar(64)
    desc: 账户类型
    dict: account_type
    topk: 1|BANK|OPERATION_FEE_ACCOUNT|received
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: receive_payment_type
    type: string
    phys: varchar(128)
    desc: 收付类型
    dict: receive_payment_type
  - name: account_name
    type: string
    phys: varchar(128)
    desc: 账户名称
  - name: account_no
    type: string
    phys: varchar(128)
    desc: 账户账号
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
  - name: address
    type: string
    phys: varchar(128)
    desc: 地址
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    desc: 逻辑租户标识
    topk: QA2tiepai2|base
  - name: auth_state
    type: string
    phys: varchar(64)
    desc: 认证状态
    topk: APPLY_00|APPLY_20|APPLY_40
  - name: bank_branch_name
    type: string
    phys: varchar(128)
    desc: 账户开户行
  - name: bank_city_code
    type: string
    phys: varchar(128)
    desc: 银行城市代码
  - name: bank_city_name
    type: string
    phys: varchar(128)
    desc: 银行城市名称
  - name: bank_code
    type: string
    phys: varchar(128)
    desc: 银行(总行)代码
  - name: bank_code_name
    type: string
    phys: varchar(128)
    desc: 银行(总行)名称
  - name: bank_id
    type: string
    phys: varchar(128)
    desc: 银行ID
    topk: 102|103|105|302
  - name: bank_no
    type: string
    phys: varchar(512)
    desc: 联行号
  - name: bank_province_code
    type: string
    phys: varchar(128)
    desc: 银行所属省份代码
  - name: bank_province_name
    type: string
    phys: varchar(128)
    desc: 银行所属省份名称
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
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: default_account_flag
    type: string
    phys: varchar(64)
    desc: 是否为默认账户
    topk: 0|1
  - name: email
    type: string
    phys: varchar(128)
    desc: 电子邮箱
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: Y
  - name: error_try_count
    type: number
    phys: int(10)
    desc: 打款金额错误次数
    topk: 0
  - name: error_try_time
    type: temporal
    phys: datetime
    desc: 最后一次错误时间
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: name
    type: string
    phys: varchar(128)
    desc: 名称-废弃
    topk: 111|324234|测试账户
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: payment_remaining_count
    type: number
    phys: int(10)
    desc: 剩余打款次数
    topk: 0|1|2|3
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户账号信息
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: status
    type: string
    phys: varchar(128)
    desc: 账户状态
    topk: INIT
  - name: telephone
    type: string
    phys: varchar(128)
    desc: 电话
  - name: trace_no
    type: string
    phys: varchar(128)
    desc: 系统跟踪号
    topk: 2404131814132811112013460|2404151021232451112015937|2404151137482561112011729
  - name: trans_id
    type: string
    phys: varchar(128)
    desc: 交易ID
    topk: 202404131814139790|202404151021236195|202404151137486|202404151541566515
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

- [[cust_company_info]]：cust_account_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustAccountInfoDO.java，suggested）
