---
type: table
title: CA认证信息
page_key: ca_certification_info
domain: CA证书认证
status: draft
anchors: [ca_certification_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












ca_certification_info 是「CA 证书认证（一证四步）」的落库主表：企业实名核验、被授权人公安二要素、意愿留痕、协议告知留痕与附件引用都按「一次认证一行」的形式沉淀在这一张表里，再以 [[ca_submit_status]] 描述的状态机推送给签章中台（cbsSubmitBizData）。行的身份既不靠 batch_no，也不靠单列唯一键，而是由 [[incremental_idempotent_key|增量落库幂等键]] 约束的 (cust_id, data_date, head_company_data, submit_status=PENDING) 组合决定；分公司场景下总公司一行、本企业一行各自独立成行，见 [[head_company_row|总公司主体行口径]] 与 [[head_company_data]]。

表上的列可以粗分为四簇：

- 主体与来源：cust_id、cust_type、data_source、data_date、head_company_data、op_type、enable；
- 上送状态：submit_status、batch_no、sign_platform_result、submit_time，语义见 [[cfca_sign_center_cert_status|签章中台证书状态]] 之外的本地上送态；
- 核验留痕 JSON：notify_agreement_json、enterprise_four_json、police_two_json，对应 [[enterprise_four_elements|企业实名四要素]] 与 [[notify_agreement|协议告知]]；
- 意愿与附件：intent_sms_json、intent_h_face_json、file_refs_json，其中附件列还承载 [[ca_upgrade_auth|CA 升级授权书]]。

写值口径上有三处容易误读：cust_type 恒为字面量 COMPANY（CUST_TYPE_COMPANY），不是数字字典键；op_type 代码仅写 INSERT（OP_TYPE_INSERT），UPDATE 分支存在但未使用；data_source 以枚举 .name() 落库，取值与分布见 [[operation_platform_source]]、[[fbp_portal_source]]、[[channel_openapi_source]]。data_date 由 createOrGetByKey 缺省取当天，CaActivationApplication 中的 resolvePersistRowDataDate 已定义但无调用点，属待确认的未生效分支。

## 需求背景

本表承载「一证四步」的三条落库入口：运营中台 notifyActivateCa 主动通知、产融门户 /cust-web/ca/realName/verify、开放渠道 OpenAPI。三条入口共用同一张表与同一套上送完整性要求（见 [[submit_completeness|一证四步上送完整性口径]] 与 [[submit_completeness_check]]），差异主要体现在是否强制意愿留痕（开放渠道免校验）以及总/分公司行的生成方式。上送前由 [[submit_data_length_truncate]] 控制单字段体量，上送后由 [[submit_success|上送完成口径]] 提供 AMS 复用数据。

## 版本演进

- v0：首次沉淀表结构语义。可见的演进痕迹是 batch_no 曾是幂等键的一部分，现已退出幂等键（batch_no 为 INC_ 前缀流水号，总/分公司两行各自独立），幂等只依赖 (cust_id, data_date, head_company_data, submit_status=PENDING)。这也意味着跨日重发会产生新行。
- op_type 的 UPDATE 分支在代码中保留但未落地，纳入后续演进观察。

```ground:table
table: ca_certification_info
database: lowcode_pplatform
desc: CA认证信息
fields:
  - name: cust_type
    type: string
    phys: varchar(64)
    desc: PERSON / COMPANY
    dict: ca_certification_info__cust_type
    topk: "COMPANY"
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: head_company_data
    type: string
    phys: varchar(2)
    desc: 是否总公司
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
  - name: submit_status
    type: string
    phys: varchar(64)
    desc: PENDING / SUCCESS / FAIL
    dict: submit_status
    topk: "FAIL|PENDING|SUCCESS"
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
  - name: batch_no
    type: string
    phys: varchar(64)
    desc: 批次号
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
    desc: 企业Id
  - name: data_date
    type: string
    phys: varchar(64)
    desc: 数据时间
  - name: data_source
    type: string
    phys: varchar(64)
    desc: 数据来源
    topk: "CHANNEL_OPENAPI|FBP_PORTAL|OPERATION_PLATFORM"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: enterprise_four_json
    type: string
    phys: text
    desc: 企业四要素
  - name: file_refs_json
    type: string
    phys: text
    desc: 附件
  - name: intent_h_face_json
    type: string
    phys: text
    desc: 意愿 H5_FACE
  - name: intent_sms_json
    type: string
    phys: text
    desc: 意愿 SMS_CODE
  - name: name
    type: string
    phys: varchar(64)
    desc: 名称
  - name: notify_agreement_json
    type: string
    phys: text
    desc: 协议通知
  - name: op_type
    type: string
    phys: varchar(64)
    desc: INSERT / UPDATE
    topk: "INSERT"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: police_two_json
    type: string
    phys: text
    desc: 实名 POLICE_TWO
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: sign_platform_result
    type: string
    phys: mediumtext
    desc: 中台返回结果
  - name: submit_time
    type: temporal
    phys: datetime
    desc: 提交时间
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

关联页面：[[ca_submit_status]]、[[incremental_idempotent_key]]、[[head_company_row]]、[[submit_completeness]]、[[incremental_idempotent_row]]、[[submit_idempotent_short_circuit]]、[[enterprise_four_elements]]、[[notify_agreement]]、[[batch_no]]。