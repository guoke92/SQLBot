---
type: table
title: 客户关联方信息主表
page_key: cust_shareholder_info
domain: 企业建档与认证状态机
status: draft
anchors: [cust_shareholder_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---















# 客户关联方信息主表

（基线页：31 字段，行数估计 6。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_shareholder_info
database: lowcode_pplatform
desc: 客户关联方信息主表
fields:
  - name: certification_type
    type: string
    phys: varchar(64)
    desc: 证件类型
    dict: cust_shareholder_info__certification_type
    topk: "CRET_ID"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: relation_type
    type: string
    phys: varchar(64)
    desc: 关联方类型
    dict: relation_type
    topk: "LEGAL_PERSON|SENIOR_MANAGER"
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
    topk: "base"
  - name: certification_no
    type: string
    phys: varchar(128)
    desc: 证件号码
    topk: "11|wertwetew"
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
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: currency
    type: string
    phys: varchar(128)
    desc: 出资币种
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "beehive-scf.qhhrly.cn"
  - name: email
    type: string
    phys: varchar(128)
    desc: 电子邮件
    topk: "11|wertewt"
  - name: fund_amount_act
    type: string
    phys: varchar(128)
    desc: 实际出资金额
    topk: "111|wretwewt"
  - name: fund_amount_ought
    type: string
    phys: varchar(128)
    desc: 应出资金额
  - name: fund_scale
    type: string
    phys: varchar(20)
    desc: 出资比例（%）
    topk: "11|wt"
  - name: fund_type
    type: string
    phys: varchar(128)
    desc: 出资方式
  - name: investment_date
    type: temporal
    phys: date
    desc: 投资日期
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: name
    type: string
    phys: varchar(128)
    desc: 关联方名称
    topk: "11|34|asdf|asdfdf"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 客户股东信息
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
    topk: "11|wert"
  - name: telephone
    type: string
    phys: varchar(128)
    desc: 联系电话
  - name: update_by
    type: string
    phys: varchar(100)
    desc: 更新人id
  - name: update_time
    type: temporal
    phys: datetime
    desc: 更新时间
  - name: update_user
    type: string
    phys: varchar(100)
    desc: 更新人名称
```

## 关联表

- [[cust_company_info]]：cust_shareholder_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustShareholderInfoDO.java，suggested）
- [[cust_company_info]]：cust_shareholder_info.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
