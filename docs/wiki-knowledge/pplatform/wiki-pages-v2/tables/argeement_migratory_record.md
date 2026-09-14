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
contract_version: "0.1"
belong: tables
---












迁移时不为客户直接搬协议原文，而是先生成"待拉取清单"，再由定时任务按产品/客户分组去业务系统拉取协议文件并归档。本表既是清单也是重试状态机，见 [[agreement_pull_status]]、口径 [[pending_agreement_pull]] 与规则 [[agreement_migratory_init]]、[[agreement_pull_throttle]]。

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
desc: 协议迁移记录
fields:
  - name: agreement_type
    type: string
    phys: varchar(64)
    desc: 协议类型
    dict: agreement_type
    topk: "BS_Auth|CFCA_Auth|CustPersonLicense|PrivacyPolicy|ProductProtocolAcflow|ProductProtocolAms|ProductProtocolBeecredit|ProductProtocolOrder|ProductProtocolRvsfactor_PC|ProductProtocolStorage|ProductProtocolVoucher|UserProtocol"
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
  - name: is_new
    type: string
    phys: varchar(10)
    desc: 是否新数据
    dict: is_new
    topk: "no|yes"
    labels: "no:否|yes:是"
  - name: sign_mode
    type: string
    phys: varchar(20)
    desc: 签署模式
    dict: sign_mode
    topk: "01|02|03"
  - name: status
    type: number
    phys: int(10)
    desc: 状态
    dict: argeement_migratory_record__status
    topk: "0|1"
    labels: "0:否|1:是"
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
  - name: agreement_name
    type: string
    phys: varchar(128)
    desc: 协议名称
  - name: agreement_no
    type: string
    phys: varchar(64)
    desc: 协议编号
  - name: agreement_path
    type: string
    phys: varchar(128)
    desc: 协议路径
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
  - name: cust_id
    type: number
    phys: bigint(20)
    desc: 产融客户id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: effect_date
    type: temporal
    phys: date
    desc: 协议生效日
  - name: expire_date
    type: temporal
    phys: date
    desc: 失效时间
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: platform_product_code
    type: string
    phys: varchar(64)
    desc: 产品编码
    topk: "ACFLOW|AMS|BEECREDIT|ORDER|RVSFACTOR_PC|STORAGE|VOUCHER"
  - name: pull_num
    type: number
    phys: int(10)
    desc: 拉取次数
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sign_date
    type: temporal
    phys: date
    desc: 签署日期
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

## 需求背景

需求要求迁移企业协议不丢失：CA 授权书、产品协议、企业授权书、用户协议、隐私政策五类协议需在迁移后逐步从业务系统拉回并归档，其中已确认业务系统无该协议的记录也允许置为已完成，不得无限重试。

## 版本演进

初始 `status='N'`、`pull_num=0`、`is_new=Y`；拉取成功后 `status='Y'`，失败仅 `pull_num+1` 并保持 N 等下一轮。`enable` 与 `excludeProductCode` 用于灰度与例外产品隔离。`is_new` 的落库写法与 `status` 不一致（`isNew.name()` vs `getDictKey`），属历史遗留。