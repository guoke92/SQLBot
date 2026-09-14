---
type: table
title: cust_certification_info
page_key: cust_certification_info
domain: 企业建档与认证状态机
status: draft
anchors: [cust_certification_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.1"
belong: tables
---












# cust_certification_info（企业认证记录表）

## 业务定位

本表记录企业主体在各认证类型下的核查结论与次数，是 [[processes/certification_verify_status|人脸/实名认证结果状态]] 的载体表。企业四要素认证（`COMPANY_FOUR_ELEMENTS`）与扫脸意愿认证（`FACE_VERIFY`）通过 `certification_type` 区分，`ref_cust_company_info` 回指 [[tables/cust_company_info|企业主表]] 的 `code`。人脸识别业务流水号落在 `face_business_no`，供影像查询使用。

## 需求背景

扫脸链路需要把「自动核查」与「人工核查」两条结果通路分开留痕：自动核查通过由 `AutoVerifyServiceImpl:saveOrUpdate` 写入 `auto_verify_status` 并累加 `auto_verify_count`；人工核查通过由 `saveManual` 写入 `manual_verify_status`。下游取数口径见 [[calibers/face_verify_passed|人脸认证通过]] 与 [[calibers/manual_verify_passed|人工认证通过]]。

## 版本演进

自动核查失败后再次通过可回写为通过；人工核查通过后 `verifyThree` 会短路返回已通过结论。写入路径使用字典 `getDictParam()`、人脸通过判断使用 `getDictKey()`，二者存在读写键不一致风险，见 [[rules/verify_status_dict_key_consistency|核查状态字典键一致性规则]]。

```ground:table
table: cust_certification_info
database: lowcode_pplatform
desc: cust_certification_info
fields:
  - name: auto_verify_status
    type: string
    phys: varchar(64)
    desc: 自动核查结果。FaceVerifyController.isFaceVerifyPassed 与 CustCertificationResultTypeEnum.AUTOMATIC_AUTHENTICATION_PASSED 比较。
    dict: auto_verify_status
    topk: "AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|TO_BE_VERIFIED"
  - name: certification_type
    type: string
    phys: varchar(64)
    desc: 认证类型（COMPANY_FOUR_ELEMENTS / FACE_VERIFY 等），写入用 CustCertificationTypeEnum.getDictParam()
    dict: certification_type
    topk: "AUTH_MEDIA_OCR|AUTH_THREE_ELEMENTS|COMPANY_TWO_ELEMENTS|FACE_VERIFY|LEGAL_OCR|LEGAL_REAL_NAME|LEGAL_THREE_ELEMENTS"
  - name: enable
    type: string
    phys: varchar(4)
    dict: enable
    topk: "Y"
    labels: "Y:是"
  - name: manual_verify_status
    type: string
    phys: varchar(64)
    desc: 人工核查结果。FaceVerifyController.isFaceVerifyPassed 与 CustCertificationResultTypeEnum.MANUAL_AUTHENTICATION_PASSED 比较。
    dict: manual_verify_status
    topk: "MANUAL_AUTHENTICATION_PASSED"
  - name: act_procinst_date
    type: temporal
    phys: datetime
  - name: act_procinst_id
    type: string
    phys: varchar(64)
  - name: act_procinst_no
    type: string
    phys: varchar(255)
  - name: act_procinst_status
    type: string
    phys: varchar(64)
  - name: app_tenant_code
    type: string
    phys: varchar(100)
    topk: "base|common"
  - name: auto_verify_count
    type: number
    phys: int(11)
    desc: 自动核查次数，saveOrUpdate 每次 +1
  - name: auto_verify_data
    type: string
    phys: text
    desc: 自动核查原始数据 JSON。CustPersonApplication.getFaceVerifyQueryVideoDTO 从该字段反序列化 VerifyResultQueryResp。
  - name: auto_verify_msg
    type: string
    phys: varchar(604)
    desc: 自动核查结果
  - name: auto_verify_time
    type: temporal
    phys: datetime
  - name: code
    type: string
    phys: varchar(64)
  - name: create_by
    type: string
    phys: varchar(100)
  - name: create_time
    type: temporal
    phys: datetime
  - name: create_user
    type: string
    phys: varchar(100)
  - name: db_tenant_code
    type: string
    phys: varchar(100)
  - name: face_business_no
    type: string
    phys: varchar(128)
    desc: 人脸识别业务流水号，用于影像查询
  - name: id
    type: number
    phys: bigint(20)
  - name: manual_verify_count
    type: number
    phys: int(11)
  - name: manual_verify_msg
    type: string
    phys: varchar(128)
  - name: manual_verify_time
    type: temporal
    phys: datetime
  - name: name
    type: string
    phys: varchar(64)
  - name: organization_id
    type: string
    phys: varchar(30)
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 关联企业 code；与企业主表 code 对应
  - name: remark
    type: string
    phys: varchar(1024)
  - name: update_by
    type: string
    phys: varchar(100)
  - name: update_time
    type: temporal
    phys: datetime
  - name: update_user
    type: string
    phys: varchar(100)
  - name: verify_score
    type: number
    phys: double
```

## 关联表

- [[cust_company_info]]：cust_certification_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustCertificationInfoDO.java，suggested）
- [[cust_company_info]]：cust_certification_info.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[cust_person_info]]：cust_certification_info.ref_cust_company_info → cust_person_info.code（write-flow:MiniFaceServiceImpl.java，confirmed）
