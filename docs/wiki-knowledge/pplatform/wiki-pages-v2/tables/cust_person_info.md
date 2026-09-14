---
type: table
title: 客户联系人表
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
contract_version: "0.1"
belong: tables
---












cust_person_info 保存企业下的联系人（人员）记录：每条记录通过 `ref_cust_company_info` 归属到一家企业，通过 `user_id` 关联到系统用户 [[sys_user]]，并通过 `user_type` 区分身份。落库键是 `UserTypeEnum.getDictKey()`：`accountAdmin` 管理员 / `accountNormal` 经办人 / `accountGuest` 游客（不是 Java 名 admin/operator/guest）。企业角色维度另由 `company_type` 表达。

人员记录带有自己的建档状态 `cust_build_status`、启用状态 `enable` 与状态 `status`（取值见 CustPersonStatusConstant），因此联系人列表类服务在查询时需要同时施加启用与状态的过滤条件，见口径 [[valid_person]]。运营人员信息（`operator_id`、`operator_realname`、`operator`）也随人员记录一起保存，用于运营侧服务回溯经办关系。

## 需求背景
企业被创建后，客户侧服务需要为企业登记联系人并为其分配系统账号；运营侧服务需要按企业、按用户类型查询这些联系人，并在冻结等场景下排除失效数据。手机号以加密方式存储，因此读取该字段的服务需要具备解密能力，不能直接按明文比对。用户类型与管理口径（管理员、经办人）见 [[user_type_role]]、[[admin_user]]、[[operator_user]]。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

```ground:table
table: cust_person_info
database: lowcode_pplatform
desc: 客户联系人表
fields:
  - name: company_type
    type: string
    phys: varchar(100)
    desc: 客户角色
    dict: cust_person_info__company_type
    topk: "CORE|CORE_MANAGER|CORPORATION_COMPANY|DEALER|FINANCE|PLATFORM_OPERATOR_COMPANY|PROJECT_COMPANY|SUPPLIER|[\"SUPPLIER\"]"
    roles: [query, result]
  - name: cust_build_status
    type: string
    phys: varchar(30)
    desc: 建档状态
    dict: cust_build_status
    topk: "BUILD_FAIL|BUILD_SUCCESS|CUST_BUILDING|CUST_CONFIRM_AWAIT|INIT"
    roles: [query, result]
  - name: enable
    type: string
    phys: varchar(4)
    desc: enable
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
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
    dict: user_type
    topk: "accountAdmin|accountGuest|accountNormal"
    roles: [query]
  - name: real_name_result
    type: string
    phys: varchar(32)
    desc: 实名认证结果
    dict: real_name_result
    topk: "INIT|VERIFIED_FAILED|VERIFIED_SUCCESS"
  - name: realname_status
    type: string
    phys: varchar(200)
    desc: 实名认证
    dict: realname_status
    topk: "AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED|TO_BE_VERIFIED"
  - name: skip_auth_flag
    type: string
    phys: varchar(10)
    desc: 跳过实名认证标识
    dict: enable
    topk: "N|Y"
    labels: "N:否|Y:是"
  - name: source
    type: string
    phys: varchar(64)
    desc: 来源
    dict: cust_person_info__source
    topk: "AMS|longteng"
  - name: status
    type: string
    phys: varchar(64)
    desc: 联系人账号状态
    dict: cust_person_info__status
    topk: "ADD|EFFECT|FREEZE|N"
  - name: test_data
    type: string
    phys: varchar(100)
    desc: 测试数据
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
    topk: "QA2tiepai2|base|common|test|zlskscf"
  - name: auth_application
    type: string
    phys: varchar(512)
    desc: 开通产品
  - name: birth_date
    type: temporal
    phys: date
    desc: 出生日期
  - name: certification_expire
    type: string
    phys: varchar(512)
    desc: 证件有效期
  - name: certification_no
    type: string
    phys: varchar(200)
    desc: 证件号码
  - name: certification_type
    type: string
    phys: varchar(64)
    desc: 证件类型
    topk: "CERT_GREEN_CARD|CERT_HK_AND_MACAU_PASS|CERT_MAINLAND_PASS|CERT_PASSPORT|CERT_RESIDENT_PERMIT|CERT_TAIWAN|CREDENTIALS_ID|CRET_ID|CRET_ID_HK"
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
  - name: face_status
    type: string
    phys: varchar(512)
    desc: 人脸认证结果
    topk: "AUTOMATIC_AUTHENTICATION_FAILED|AUTOMATIC_AUTHENTICATION_PASSED|MANUAL_AUTHENTICATION_PASSED|TO_BE_VERIFIED"
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
    topk: "ams_finance_pc|ams_proj_pc|ams_supplier_pc|smebee_pc"
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
  - name: phone_realname_status
    type: string
    phys: varchar(200)
    desc: 手机实名状态
  - name: platform_user_id
    type: number
    phys: bigint(20)
    desc: 运营系统用户id
  - name: ref_cust_company_info
    type: string
    phys: varchar(128)
    desc: 关联企业
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

- [[cust_account_info]]：cust_person_info.ref_cust_company_info → cust_account_info.ref_cust_company_info（copy:CustPersonController.java，suggested）
- [[cust_certification_info]]：cust_person_info.code → cust_certification_info.ref_cust_company_info（write-flow:MiniFaceServiceImpl.java，confirmed）
- [[cust_change_cfg]]：cust_person_info.ref_cust_company_info → cust_change_cfg.code（java-eq:CustCompanyInfoApplication.java，suggested）
- [[cust_change_record]]：cust_person_info.ref_cust_company_info → cust_change_record.code（java-eq:CustSyncEventProcessor.java，suggested）
- [[cust_company_info]]：cust_person_info.cust_build_status → cust_company_info.cust_build_status（copy:CustCompanyIfoEnchanceService.java，suggested）
- [[cust_company_info]]：cust_person_info.cust_company_id → cust_company_info.id（mapper:CustCompanyQueryMapper.xml，confirmed）
- [[cust_company_info]]：cust_person_info.ref_cust_company_info → cust_company_info.code（ref-convention:CustPersonInfoDO.java，suggested）
- [[cust_company_info]]：cust_person_info.ref_cust_company_info → cust_company_info.id（db-index:ref_-naming，suggested）
- [[cust_project_rel]]：cust_person_info.company_type → cust_project_rel.company_type（copy:PlatFormMigratoryApplication.java，suggested）
- [[cust_role_info]]：cust_person_info.ref_cust_company_info → cust_role_info.ref_cust_company_info（java-eq-same:AbstractSmsMessageService.java，suggested）
- [[cust_user_rel]]：cust_person_info.user_type → cust_user_rel.user_type（copy:SubmitCustInfoEnhanceService.java，suggested）
- [[migratory_user_record]]：cust_person_info.user_id → migratory_user_record.user_id（copy:PlatFormMigratoryApplication.java，suggested）
