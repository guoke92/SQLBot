---
type: table
title: 客户变更配置
page_key: cust_change_cfg
domain: 企业变更与运营变更
status: draft
anchors: [cust_change_cfg]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












`cust_change_cfg` 是变更项配置表，`item_code` 为变更项编码（UN0008/UN0009/UN0012/UN0013/UN0015/UN0016 等）。它通过 `cust_change_record.alter_type_id` 被反查，是判断“本次变更是否需要重签授权书”的白名单依据。

## 需求背景
并非所有企业变更都涉及授权主体或授权要素变化，因此用变更项编码白名单收敛签署范围，减少不必要的电子授权书签署，见 [[offline_eauth_sign_trigger]]。

## 版本演进
UN 系列编码随变更项扩展而增加；授权书签署白名单（UN0016/UN0012/UN0013/UN0008/UN0015）在该表编码体系内被显式引用，说明白名单是在既有变更项体系上追加的语义。

```ground:table
table: cust_change_cfg
database: lowcode_pplatform
desc: 客户变更配置
fields:
  - name: client_type
    type: string
    phys: varchar(20)
    desc: 端类型
    dict: client_type
    topk: "ACCOUNT_PRODUCT|AGW"
  - name: cust_type
    type: string
    phys: varchar(512)
    desc: 客户类型
    dict: cust_type
    topk: "1|2|3"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: head_company
    type: string
    phys: varchar(10)
    desc: 是否总公司
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: identify_style
    type: string
    phys: varchar(512)
    desc: 认证方式
    dict: identify_style
    topk: "INVITE|INVITE_AGW|SELF|SIMPLE"
  - name: open_process
    type: string
    phys: varchar(10)
    desc: 开启流程
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
  - name: data_desc
    type: string
    phys: varchar(128)
    desc: 变更需要材料说明
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
    topk: "beehive-scf.lianyirong.com.cn|beehive-scf.qhhrly.cn"
  - name: item_code
    type: string
    phys: varchar(128)
    desc: 变更项编码
    topk: "UN0001|UN0002|UN0003|UN0004|UN0005|UN0006|UN0007|UN0008|UN0009|UN0010|UN0011|UN0012|UN0013|UN0014|UN0015|UN0016"
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: oper_item
    type: string
    phys: varchar(128)
    desc: 运营中台变更项
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: plat_item
    type: string
    phys: varchar(128)
    desc: 平台变更项
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
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

- [[cust_change_record]]：cust_change_cfg.id → cust_change_record.alter_type_id（read-flow:CustSyncEventProcessor.java，confirmed）
- [[cust_person_info]]：cust_change_cfg.code → cust_person_info.ref_cust_company_info（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_project_rel]]：cust_change_cfg.id → cust_project_rel.product_id（write-flow:PlatFormMigratoryApplication.java，confirmed）
