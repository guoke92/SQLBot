---
type: table
title: 企业联系人
page_key: cust_person_info
domain: 经办人/联系人/管理员管理
status: draft
anchors: [cust_person_info]
oid: 1
scope:
  databases: [lowcode_pplatform]
sources: ["db:db-catalog.yaml", "code:extract-catalog.yaml"]
created: '2026-09-14'
updated: '2026-09-14'
contract_version: "0.3"
belong: tables
scenes: [company_contact]
---

# 企业联系人

场景 [[company_contact]] 的主档。`ref_cust_company_info` → 企业 `code`；`cust_company_id` → 企业 `id`。`user_type` 是管理员/经办人/游客；`company_type` 是企业角色切片。账号激活看 `status`（未激活/已激活），建档过程看 `cust_build_status`。`real_name_result` 由人脸与手机号实名综合得出，不要单用 `face_status` 当综合结论。`cust_build_status` 常从企业主档拷贝。

## 场景字段划分

本表字段与库列对齐。各场景窗口是该问法实际用到的列；always 列每个引用本表的场景都会带上。未分窗的列仍在本页，问题点到列名时才会展开。

### always

各场景默认带：`id`, `code`, `enable`, `create_time`, `update_time`, `create_by`, `create_user`, `update_by`, `update_user`

### [[company_contact]]

`id`, `enable`, `create_time`, `update_time`, `company_type`, `cust_build_status`, `cust_company_id`, `face_status`, `name`, `phone`, `phone_realname_status`, `real_name_result`, `ref_cust_company_info`, `status`, `user_type`

### [[oper_change]]

`id`, `enable`, `create_time`, `update_time`, `name`, `ref_cust_company_info`

### 未分窗

仍留表页，待代码证据划入场景：`certification_type`, `skip_auth_flag`, `source`, `test_data`, `act_procinst_date`, `act_procinst_id`, `act_procinst_no`, `act_procinst_status`, `app_tenant_code`, `auth_application`, `birth_date`, `certification_expire`, `certification_no`, `db_tenant_code`, `email`, `en_name`, `en_name_end`, `ext_data`, `handby_person`, `handby_person_name`, `main_data_id`, `operator`, `operator_id`, `operator_push_system`, `operator_realname`, `organization_id`, `platform_user_id`, `realname_status`, `remark`, `user_id`, `user_name`

```ground:table
table: cust_person_info
database: lowcode_pplatform
desc: 客户联系人表
fields:
  - name: id
    type: number
    phys: bigint(22)
    desc: "表主键"
    roles: [query, result]
    group: always
    scenes: [company_contact, oper_change]
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
    roles: [query]
    group: always
    scenes: [company_contact, oper_change]
  - name: create_time
    type: temporal
    phys: datetime
    desc: "创建时间"
    roles: [result]
    group: always
    scenes: [company_contact, oper_change]
  - name: update_time
    type: temporal
    phys: datetime
    desc: "更新时间"
    group: always
    scenes: [company_contact, oper_change]
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
  - name: certification_type
    type: string
    phys: varchar(64)
    desc: "证件类型"
    dict: certification_type
    topk: "CERT_GREEN_CARD|CERT_HK_AND_MACAU_PASS|CERT_MAINLAND_PASS|CERT_PASSPORT|CERT_RESIDENT_PERMIT|CERT_TAIWAN|CREDENTIALS_ID|CRET_ID|CRET_ID_HK"
    labels: "CERT_GREEN_CARD:外国人永久居留证|CERT_HK_AND_MACAU_PASS:港澳通行证|CERT_MAINLAND_PASS:港澳居民来往内地通行证|CERT_PASSPORT:护照|CERT_RESIDENT_PERMIT:港澳台居民居住证|CERT_TAIWAN:台胞证|CRET_ID:二代居民身份证|CRET_ID_HK:香港身份证"
  - name: company_type
    type: string
    phys: varchar(100)
    desc: "客户角色"
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|["SUPPLIER"]"
    roles: [query, result]
    scenes: [company_contact]
  - name: cust_build_status
    type: string
    phys: varchar(30)
    desc: "建档状态"
    dict: cust_build_status
    topk: "BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING|CUST_CONFIRM_AWAIT|INIT"
    labels: "BUILD_FAIL:认证失败|BUILD_SUCCESS:认证成功|CUST_BUILDING:审核中|CUST_CONFIRM_AWAIT:待客户认证|INIT:初始化"
    roles: [query, result]
    scenes: [company_contact]
  - name: cust_company_id
    type: number
    phys: bigint(22)
    desc: "冗余企业id"
    scenes: [company_contact]
  - name: face_status
    type: string
    phys: varchar(512)
    desc: "人脸认证结果"
    dict: face_status
    topk: "AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED|TO_BE_VERIFIED"
    labels: "AUTOMATIC_AUTHENTICATION_FAILED:自动认证不通过|AUTOMATIC_AUTHENTICATION_PASSED:自动认证通过|MANUAL_AUTHENTICATION_PASSED:人工认证通过|TO_BE_VERIFIED:待核查"
    scenes: [company_contact]
  - name: name
    type: string
    phys: varchar(128)
    desc: "姓名"
    roles: [query, result]
    scenes: [company_contact, oper_change]
  - name: phone
    type: string
    phys: varchar(128)
    desc: "手机号"
    scenes: [company_contact]
  - name: phone_realname_status
    type: string
    phys: varchar(200)
    desc: "手机实名状态"
    dict: phone_realname_status
    labels: "TO_BE_VERIFIED:待核查|AUTOMATIC_AUTHENTICATION_PASSED:自动认证通过|AUTOMATIC_AUTHENTICATION_FAILED:自动认证不通过|MANUAL_AUTHENTICATION_PASSED:人工认证通过|MANUAL_AUTHENTICATION__FAILED:人工认证不通过|NO_RECORD:库无记录"
    scenes: [company_contact]
  - name: real_name_result
    type: string
    phys: varchar(32)
    desc: "实名认证结果"
    dict: real_name_result
    topk: "INIT|VERIFIED_FAILED|VERIFIED_SUCCESS"
    labels: "INIT:未认证|VERIFIED_FAILED:认证失败|VERIFIED_SUCCESS:认证成功"
    scenes: [company_contact]
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: "关联企业"
    scenes: [company_contact, oper_change]
  - name: skip_auth_flag
    type: string
    phys: varchar(10)
    desc: "跳过实名认证标识"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: source
    type: string
    phys: varchar(64)
    desc: "来源"
    dict: ca_data_source
    topk: "AMS|longteng"
    labels: "AMS:管理员"
  - name: status
    type: string
    phys: varchar(64)
    desc: "联系人账号状态"
    topk: "ADD|EFFECT|FREEZE|N"
    scenes: [company_contact]
  - name: test_data
    type: string
    phys: varchar(100)
    desc: "测试数据"
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: user_type
    type: string
    phys: varchar(512)
    desc: "联系人类型"
    dict: user_type
    topk: "accountAdmin|accountGuest|accountNormal"
    labels: "accountAdmin:管理员|accountGuest:游客|accountNormal:经办人"
    roles: [query]
    scenes: [company_contact]
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
    topk: "QA2tiepai2|base|common|test|zlskscf"
  - name: auth_application
    type: string
    phys: varchar(512)
    desc: "开通产品"
  - name: birth_date
    type: temporal
    phys: date
    desc: "出生日期"
  - name: certification_expire
    type: string
    phys: varchar(512)
    desc: "证件有效期"
  - name: certification_no
    type: string
    phys: varchar(200)
    desc: "证件号码"
  - name: db_tenant_code
    type: string
    phys: varchar(100)
    desc: "数据租户标识"
  - name: email
    type: string
    phys: varchar(128)
    desc: "邮箱"
  - name: en_name
    type: string
    phys: varchar(300)
    desc: "姓名(英文)"
  - name: en_name_end
    type: string
    phys: varchar(100)
    desc: "人名 (英文)"
  - name: ext_data
    type: string
    phys: varchar(255)
    desc: "扩展字段"
  - name: handby_person
    type: string
    phys: varchar(100)
    desc: "建档经办人"
  - name: handby_person_name
    type: string
    phys: varchar(20)
    desc: "建档经办人名字"
  - name: main_data_id
    type: number
    phys: bigint(20)
    desc: "主数据id"
  - name: operator
    type: string
    phys: varchar(100)
    desc: "运营人"
  - name: operator_id
    type: string
    phys: varchar(30)
    desc: "运营人id"
  - name: operator_push_system
    type: string
    phys: varchar(500)
    desc: "经办人推送系统列表"
    topk: "ams_finance_pc|ams_proj_pc|ams_supplier_pc|smebee_pc"
  - name: operator_realname
    type: string
    phys: varchar(30)
    desc: "运营人姓名"
  - name: organization_id
    type: string
    phys: varchar(30)
    desc: "机构编号"
  - name: platform_user_id
    type: number
    phys: bigint(20)
    desc: "运营系统用户id"
  - name: realname_status
    type: string
    phys: varchar(200)
    desc: "实名认证"
    topk: "AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED|TO_BE_VERIFIED"
  - name: remark
    type: string
    phys: varchar(1024)
    desc: "remark"
  - name: user_id
    type: number
    phys: bigint(20)
    desc: "关联用户"
  - name: user_name
    type: string
    phys: varchar(64)
    desc: "登录账号"
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.ref_cust_company_info
right: cust_company_info.code
cardinality: many_to_one
status: proposed
evidence: code_path:CustPersonInfoDO.java
```

```ground:relation
type: EQUI_JOIN
left: cust_person_info.cust_company_id
right: cust_company_info.id
cardinality: many_to_one
status: proposed
evidence: code_path:CustCompanyQueryMapper.xml
```
