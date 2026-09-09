---
type: table
title: 客户联系人表
page_key: cust_person_info
belong: tables
domain: 基线
status: draft
anchors: [cust_person_info]
oid: 1
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml", "enrich:wiki-admin"]
created: '2026-09-02'
updated: '2026-09-02'
contract_version: "0.1"
scope:
  databases: [lowcode_pplatform]
---

# 客户联系人表

（基线页：51 字段，行数估计 57298。行语义/常用过滤待语义摄取增强。）

```ground:table
table: cust_person_info
database: lowcode_pplatform
desc: 客户联系人表
inactive: false
fields:
  - name: company_type
    type: string
    phys: varchar(100)
    desc: 客户角色
    topk: CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER
    roles: [query, result]
  - name: cust_build_status
    type: string
    phys: varchar(30)
    desc: 建档状态
    dict: cust_build_status
    topk: BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING|CUST_CONFIRM_AWAIT
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    topk: N|Y
    roles: [query]
  - name: id
    type: number
    phys: bigint(22)
    desc: 表主键
    roles: [query, result]
  - name: name
    type: string
    phys: varchar(128)
    desc: 姓名
    roles: [query, result]
  - name: user_type
    type: string
    phys: varchar(512)
    desc: 联系人类型
    topk: accountAdmin|accountGuest|accountNormal
    roles: [query]
  - name: certification_type
    type: string
    phys: varchar(64)
    desc: 证件类型
    dict: legal_certification_type
    topk: CERT_GREEN_CARD|CERT_HK_AND_MACAU_PASS|CERT_MAINLAND_PASS|CERT_PASSPORT
  - name: face_status
    type: string
    phys: varchar(512)
    desc: 人脸认证结果
    dict: auto_verify_status
    topk: AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED
  - name: phone_realname_status
    type: string
    phys: varchar(200)
    desc: 手机实名状态
    dict: auto_verify_status
  - name: real_name_result
    type: string
    phys: varchar(32)
    desc: 实名认证结果
    dict: real_name_result
    topk: INIT|VERIFIED_FAILED|VERIFIED_SUCCESS
  - name: source
    type: string
    phys: varchar(64)
    desc: 来源
    dict: cust_person_info__source
    topk: AMS
  - name: status
    type: string
    phys: varchar(64)
    desc: 联系人账号状态
    dict: cust_status
    topk: ADD|EFFECT|FREEZE|N
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
    topk: QA2tiepai2|base|common|test
  - name: auth_application
    type: string
    phys: varchar(512)
    desc: 开通产品
  - name: birth_date
    type: temporal
    phys: date
    desc: 出生日期
    group: birth_date_group
  - name: certification_expire
    type: string
    phys: varchar(512)
    desc: 证件有效期
  - name: certification_no
    type: string
    phys: varchar(200)
    desc: 证件号码
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
    roles: [result]
    group: create_time_group, project_create_time_group, update_time_group
  - name: create_user
    type: string
    phys: varchar(100)
    desc: 创建人名称
  - name: cust_company_id
    type: number
    phys: bigint(22)
    desc: 冗余企业id
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: 数据租户标识
  - name: email
    type: string
    phys: varchar(128)
    desc: 邮箱
  - name: en_name
    type: string
    phys: varchar(300)
    desc: 姓名(英文)
  - name: en_name_end
    type: string
    phys: varchar(100)
    desc: 人名 (英文)
  - name: ext_data
    type: string
    phys: varchar(255)
    desc: 扩展字段
  - name: handby_person
    type: string
    phys: varchar(100)
    desc: 建档经办人
  - name: handby_person_name
    type: string
    phys: varchar(20)
    desc: 建档经办人名字
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: 主数据id
  - name: operator
    type: string
    phys: varchar(100)
    desc: 运营人
  - name: operator_id
    type: string
    phys: varchar(30)
    desc: 运营人id
  - name: operator_push_system
    type: string
    phys: varchar(500)
    desc: 经办人推送系统列表
    topk: ams_finance_pc|ams_proj_pc|ams_supplier_pc|smebee_pc
  - name: operator_realname
    type: string
    phys: varchar(30)
    desc: 运营人姓名
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: 机构编号
  - name: phone
    type: string
    phys: varchar(128)
    desc: 手机号
  - name: platform_user_id
    type: number
    phys: bigint(20)
    desc: 运营系统用户id
  - name: realname_status
    type: string
    phys: varchar(200)
    desc: 实名认证
    topk: AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 关联企业
  - name: remark
    type: string
    phys: varchar(1024)
    desc: remark
  - name: skip_auth_flag
    type: string
    phys: varchar(10)
    desc: 跳过实名认证标识
    topk: N|Y
  - name: test_data
    type: string
    phys: varchar(100)
    desc: 测试数据
    topk: N|Y
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
  - name: user_id
    type: number
    phys: bigint(20)
    desc: 关联用户
  - name: user_name
    type: string
    phys: varchar(64)
    desc: 登录账号
```

## 关联表

- [[cust_certification_info]]：cust_person_info.code → cust_certification_info.ref_cust_company_info（write-flow:MiniFaceServiceImpl.java，confirmed）
- [[cust_change_cfg]]：cust_person_info.ref_cust_company_info → cust_change_cfg.code（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_change_record]]：cust_person_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_person_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustPersonInfoDO.java，suggested）
