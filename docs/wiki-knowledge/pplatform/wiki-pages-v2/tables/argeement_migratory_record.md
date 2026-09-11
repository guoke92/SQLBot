---
type: table
title: argeement_migratory_record（协议迁移记录表）
page_key: table.argeement_migratory_record
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议迁移记录表
  - 协议迁移拉取记录
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
  - code:PlatFormMigratoryApplication.java
contract_version: "0.1"
---


`argeement_migratory_record` 是「协议」主题的落地载体：每个客户 × 每个产品 × 每类协议各生成一条待拉取记录，由迁移初始化写入，再由定时任务消费拉取，直到 `status` 置 `1`（拉取结束）。它同时承载签署模式、协议文件路径与协议编号，因此是 [[concepts/agreement]] 与 [[concepts/authorization-agreement]] 的分界线：本表存协议文本与拉取事实，不记录「谁授过权」的授权关系。

相关的判定口径见 [[calibers/pending-pull-agreement-records]]、[[calibers/migratory-init-five-agreements]]、[[calibers/ams-bs-channel]]；状态流转见 [[processes/agreement-migratory-pull-status]] 与 [[processes/agreement-sign-mode]]。产品维度上，`platform_product_code`（AMS/ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER）既决定拉取哪一产品的协议，也决定产品协议类型映射；AMS 走 [[concepts/ca-cfca|上上签 BS 通道]]，其余产品走 CFCA。

## 需求背景
存量客户的协议分散在旧渠道，需要按客户维度逐产品、逐协议类型向客户端拉取并落库，因此需要一张拉取队列表：既能标记「已结束」避免重复拉取，也能限制失败重试次数（`pull_num` < 配置值 `cust.agreemeent.pull.num`，默认 20）。`is_new` 用于区分新老渠道协议，`agreement_no` 用于合同表判重，避免重复迁移。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张），故无标 (document_claim，未证实) 的条目。

```ground:table
table: argeement_migratory_record
database: lowcode_pplatform
desc: 协议迁移记录
fields:
  - name: id
    type: number
    desc: 表主键
  - name: sign_mode
    type: string
    desc: 签署模式
    dict: sign_mode
  - name: act_procinst_date
    type: temporal
    desc: 审批结束时间
  - name: act_procinst_id
    type: string
    desc: 流程实例ID
  - name: act_procinst_no
    type: string
    desc: 流程申请编号
  - name: act_procinst_status
    type: string
    desc: 当前审批状态
  - name: agreement_name
    type: string
    desc: 协议名称
  - name: agreement_no
    type: string
    desc: 协议编号
  - name: agreement_path
    type: string
    desc: 协议路径
  - name: agreement_type
    type: string
    desc: 协议类型
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识
  - name: code
    type: string
    desc: 编码
  - name: create_by
    type: string
    desc: 创建人id
  - name: create_time
    type: temporal
    desc: 创建时间
  - name: create_user
    type: string
    desc: 创建人名称
  - name: cust_id
    type: number
    desc: 产融客户id
  - name: db_tenant_code
    type: string
    desc: 数据租户标识
  - name: effect_date
    type: temporal
    desc: 协议生效日
  - name: enable
    type: string
    desc: enable
  - name: expire_date
    type: temporal
    desc: 失效时间
  - name: is_new
    type: string
    desc: 是否新数据
  - name: name
    type: string
    desc: 名称
  - name: organization_id
    type: string
    desc: 机构编号
  - name: platform_product_code
    type: string
    desc: 产品编码
  - name: pull_num
    type: number
    desc: 拉取次数
  - name: remark
    type: string
    desc: remark
  - name: sign_date
    type: temporal
    desc: 签署日期
  - name: status
    type: number
    desc: 状态
  - name: update_by
    type: string
    desc: 更新人id
  - name: update_time
    type: temporal
    desc: 更新时间
  - name: update_user
    type: string
    desc: 更新人名称
```

```ground:field
table: argeement_migratory_record
fields:
  - field: status
    meaning: "协议迁移拉取状态：'0'（BooleanEnum.no）=待拉取/未处理；'1'（BooleanEnum.yes）=拉取流程已结束（客户端返回了协议，或确认客户端无该协议后置终态，置 1 后不再进入待拉取队列）"
    evidence: db
  - field: pull_num
    meaning: "已拉取尝试次数；pull() 只捞 pull_num < 配置值（cust.agreemeent.pull.num，默认 20）的记录，失败时 +1"
    evidence: code
  - field: is_new
    meaning: "是否新数据：'yes'/'no'（BooleanEnum.name()）；迁移初始化写 isNew，用于区分新老渠道协议"
    evidence: db
  - field: sign_mode
    meaning: "协议签署模式，语义对应 SignModeEnum 三态（NO_SIGN / OFF_LINE / ON_LINE）；DB 实存 '01' / '02' / '03'，代码未给出数值与枚举的显式映射"
    evidence: db
  - field: agreement_type
    meaning: "协议类型 key（AgreementDocType.getAgreementType()）：BS_Auth（AMS 上上签）/CFCA_Auth/ProductProtocol*/CustPersonLicense/UserProtocol/PrivacyPolicy"
    evidence: db
  - field: agreement_path
    meaning: "协议文件在对象存储（COS，FBP_SYSTEM 桶）的存储路径；为空表示未取到文件，createContractInfo 会过滤掉"
    evidence: code
  - field: agreement_no
    meaning: "协议编号（客户端 contractAgreementNo），agreementExist 用它做合同表判重，避免重复迁移"
    evidence: code
  - field: platform_product_code
    meaning: "产品编码（AMS/ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER），决定拉取哪一产品的协议及产品协议类型映射"
    evidence: db
```