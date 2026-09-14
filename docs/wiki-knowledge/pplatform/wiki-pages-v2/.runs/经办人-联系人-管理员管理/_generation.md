---FILE: tables/cust_person_info.md ---
---
type: table
title: 客户联系人表 cust_person_info
page_key: cust_person_info
domain: 经办人/联系人/管理员管理
status: draft
aliases: [客户联系人表, 联系人表, 经办人表]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info", "code:CustPersonApplication.java", "code:CustPersonController.java", "code:CustCompanyUserRelApplication.java"]
contract_version: "0.1"
---

cust_person_info 是本主题的主表，承载客户联系人（企业管理员 / 经办人 / 游客）的账号、实名认证、建档与运营归属信息。业务上同一企业下按 company_type 划分角色，每个角色同一时刻只允许一个生效管理员（user_type=accountAdmin），其余联系人为经办人（accountNormal）或游客（accountGuest）。管理员换人不是原地改一条记录，而是"冻结旧记录 + 新建记录"，因此表里会长期并存同一手机号的历史冻结行，任何查询都必须带上 enable / status 口径（见 [[valid_person]]、[[company_admin]]、[[normal_person]]）。

认证相关字段分两套码值：phone_realname_status / face_status 共用一套，real_name_result 使用另一套 INIT/VERIFIED_*，混用会直接影响待办与弹框判断（见 [[phone_realname_status]]、[[real_name_result]]）。联系人所属产品虽然在本表 auth_application 里落了一份 JSON 数组字符串，但"已开通产品"的查询口径以 [[sys_cust_user_rel]] / [[cust_auth_application]] 为准。

## 需求背景
- 企业实名建档与管理员唯一性是本表的两个核心约束：同企业同角色唯一管理员（[[unique_admin_per_company_role]]），企业内手机号/身份证号唯一（[[unique_phone_idcard_in_company]]）。
- 运营归属（operator_id / operator / operator_realname）来自运营中台而非 sys_user，发送邀请码与客服名片前必须已分配运营（[[operator_assign_before_invite]]、[[operator]]）。
- 建档状态在企业和联系人两侧各存一份，重建关联时取企业侧值（[[build_status]]、[[cust_build_status]]）。

## 版本演进
- 当前版本已包含 status（ADD/EFFECT/FREEZE）、enable（Y/N）双轨的账号生命周期控制，管理员变更走"冻结旧 + 新建"路径（[[cust_person_status]]、[[admin_change_freeze_create]]）。
- 实名认证继承逻辑已存在：同租户下已有认证通过记录时，新经办人直接继承（[[new_person_inherit_verified]]）。
- 来源字段目前区分 AMS 与 longteng；longteng 只有 DB 分布、代码枚举未声明，属待回填项。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    type: ""
    desc: "联系人类型（同一企业角色下的用户身份）：accountAdmin=企业管理员、accountNormal=经办人、accountGuest=游客；查询时通常以 user_type 过滤业务语义"
    dict: ""
  - name: status
    type: ""
    desc: "联系人账号状态：ADD=新增待生效、EFFECT=生效、FREEZE=冻结（管理员被换人后旧记录置 FREEZE）"
    dict: ""
  - name: enable
    type: ""
    desc: "逻辑启用标志 Y/N；管理员变更后旧记录 enable=N，退出所有按 enable=Y 的查询"
    dict: ""
  - name: cust_build_status
    type: ""
    desc: "联系人维度的建档状态（与 cust_company_info.cust_build_status 同码值，另存一份）；参与 sys_cust_user_rel 重建判定的取企业侧值"
    dict: ""
  - name: face_status
    type: ""
    desc: "人脸认证结果，取值与实名认证结果共用一套码：TO_BE_VERIFIED / AUTOMATIC_AUTHENTICATION_PASSED / MANUAL_AUTHENTICATION_PASSED / AUTOMATIC_AUTHENTICATION_FAILED"
    dict: ""
  - name: phone_realname_status
    type: ""
    desc: "手机号实名认证状态，码值同 face_status；AUTO/MANUAL_AUTHENTICATION_PASSED 时前端不再弹认证框"
    dict: ""
  - name: real_name_result
    type: ""
    desc: "实名认证结果：INIT=待认证、VERIFIED_SUCCESS=认证成功、VERIFIED_FAILED=认证失败（另一套码值，勿与 phone_realname_status 混用）"
    dict: ""
  - name: skip_auth_flag
    type: ""
    desc: "跳过实名认证标识 Y/N，由 /skip/real/name/auth 写入"
    dict: ""
  - name: source
    type: ""
    desc: "联系人来源：AMS=运营中台同步（新增时默认不置建档成功）、longteng=龙腾（DB 69 行，代码枚举未声明）"
    dict: ""
  - name: operator_id
    type: ""
    desc: "平台分配的运营人员ID（运营中台 OperUserDTO.id，字符串），非 sys_user.id"
    dict: ""
  - name: operator
    type: ""
    desc: "运营人员登录名（运营中台 userName）"
    dict: ""
  - name: operator_realname
    type: ""
    desc: "运营人员真实姓名，用于批量换运营模板导出"
    dict: ""
  - name: operator_push_system
    type: ""
    desc: "经办人已推送的第三方系统渠道列表：ams_finance_pc / ams_proj_pc / ams_supplier_pc / smebee_pc（对应租户产品 targetSysChannel）"
    dict: ""
  - name: ref_cust_company_info
    type: ""
    desc: "关联企业编码（对应 cust_company_info.code），企业维度过滤主键"
    dict: ""
  - name: cust_company_id
    type: ""
    desc: "冗余企业自增id（对应 cust_company_info.id），支持按 id 维度查询"
    dict: ""
  - name: user_id
    type: ""
    desc: "关联登录用户id（sys_user.id），为空表示尚未开户/未同步用户中心"
    dict: ""
  - name: phone
    type: ""
    desc: "手机号，落库为密文（查询需 metaDataEncryptionHandler.encryptAndBase64Str 后比较）"
    dict: ""
  - name: certification_type
    type: ""
    desc: "证件类型，默认 CRET_ID；DB 存在代码枚举未声明的 CREDENTIALS_ID"
    dict: ""
  - name: auth_application
    type: ""
    desc: "联系人开通产品（JSON 数组字符串）；但“联系人已开通产品”查询实际以 sys_cust_user_rel 为准，该字段非查询口径"
    dict: ""
  - name: company_type
    type: ""
    desc: "联系人所属企业角色类型（CORE/SUPPLIER/FINANCE/DEALER/PROJECT_COMPANY/CORPORATION_COMPANY/PLATFORM_OPERATOR_COMPANY/CORE_MANAGER），决定管理员角色码"
    dict: ""
```

相关页面：[[cust_company_info]]、[[cust_person_status]]、[[company_admin]]、[[normal_person]]、[[valid_person]]、[[unique_admin_per_company_role]]、[[rel_rebuild_precondition]]。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业表 cust_company_info
page_key: cust_company_info
domain: 经办人/联系人/管理员管理
status: draft
aliases: [客户企业表, 企业表]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.ref_cust_company_info", "code:CustCompanyInfoApplication.java", "code:CustPersonApplication.java"]
contract_version: "0.1"
---

cust_company_info 是企业侧主体表，联系人通过 ref_cust_company_info（企业编码 code）与 cust_company_id（企业自增 id）两个维度挂靠到本表。本主题中它主要承担三类判定：企业是否可参与关联重建、管理员变更是否可发起、企业级冻结/注销如何级联到联系人（[[rel_rebuild_company]]、[[admin_change_company_flow]]、[[company_status_cascade_person]]）。

## 需求背景
- 建档状态在企业侧与联系人侧同名同码值各存一份，重建 sys_cust_user_rel 时以企业侧为准（[[build_status]]、[[rel_rebuild_precondition]]）。
- 管理员变更必须由企业变更流程承载，因此企业状态是能否换管理员的前置条件。

## 版本演进
- 当前版本下企业状态未处于 EFFECT 时，管理员变更流程静默不启动（不抛异常），这是与"校验拦截"不同的处理风格，排障时需注意（[[admin_change_company_flow]]）。

```ground:table
table: cust_company_info
fields:
  - name: code
    type: ""
    desc: "关联企业编码（对应 cust_company_info.code），企业维度过滤主键"
    dict: ""
  - name: id
    type: ""
    desc: "冗余企业自增id（对应 cust_company_info.id），支持按 id 维度查询"
    dict: ""
  - name: cust_build_status
    type: ""
    desc: "建档状态（与 cust_person_info.cust_build_status 同名同码值，企业表与联系人表各存一份）；重建 sys_cust_user_rel 时判定用企业侧"
    dict: ""
  - name: cust_status
    type: ""
    desc: "企业状态；仅当 cust_company_info.cust_status=EFFECT 时才 copyCustRecordAndStartApply 启动管理员变更流程"
    dict: ""
  - name: enable
    type: ""
    desc: "企业启用标志；关联重建前置条件要求企业 enable=Y"
    dict: ""
```

相关页面：[[cust_person_info]]、[[cust_build_status]]、[[build_status]]、[[rel_rebuild_precondition]]。

---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: 客户-用户关联表 sys_cust_user_rel
page_key: sys_cust_user_rel
domain: 经办人/联系人/管理员管理
status: draft
aliases: [客户用户关联表, 关联表]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany", "code:CustCompanyInfoApplication.java#deleteCustInfo"]
contract_version: "0.1"
---

sys_cust_user_rel 保存企业-用户-产品-角色维度的关联关系，是"联系人已开通产品"的实际查询口径（[[cust_person_info]] 的 auth_application 字段不是查询口径）。关联关系由重建流程写入，写入与否受企业与产品状态约束（[[rel_rebuild_precondition]]、[[opened_product]]）。

## 需求背景
- 重建以 productId_roleId 为幂等键，已在关联集中的组合直接跳过，避免重复写入。
- 企业删除时以 is_freeze='N' 判断关联关系是否仍有效，进而决定能否清理 sys_user（[[not_frozen_rel]]）。

## 版本演进
- 当前版本的关联重建已有角色码来源：管理员角色码取自 custNacosProperties.getAuthUserRoleCode(companyType)，经办人固定 ROLE_CODE_NORMAL（[[rel_rebuild_precondition]]）。

```ground:table
table: sys_cust_user_rel
fields:
  - name: is_freeze
    type: ""
    desc: "关联关系冻结标志；未冻结的关联关系 = 'N'（sys_cust_user_rel.is_freeze = 'N'），企业删除时用于判断是否可清理 sys_user"
    dict: ""
```

相关页面：[[cust_company_info]]、[[rel_rebuild_company]]、[[not_frozen_rel]]、[[opened_product]]。

---END FILE---

---FILE: tables/cust_auth_application.md ---
---
type: table
title: 客户产品开通表 cust_auth_application
page_key: cust_auth_application
domain: 经办人/联系人/管理员管理
status: draft
aliases: [产品开通表, 开通表]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany", "code:CustCompanyQueryApplication.java#queryOpenedProductsByCompanies"]
contract_version: "0.1"
---

cust_auth_application 记录企业/联系人的产品开通状态，是关联重建与"已开通产品"展示的状态源。仅当存在 open_status=OPENED 的产品时，关联重建才会继续（[[opened_product]]、[[rel_rebuild_precondition]]）。

## 需求背景
- 产品开通状态既参与重建前置校验，也参与产品开通状态展示；展示口径除 OPENED 外还包含 OPENING。

## 版本演进
- 当前版本未记录产品状态机的完整流转，仅确认取值集合与两个消费点。

```ground:table
table: cust_auth_application
fields:
  - name: open_status
    type: ""
    desc: "产品开通状态，取值含 OPENED / OPENING；关联重建要求存在 open_status='OPENED' 的产品"
    dict: ""
```

相关页面：[[sys_cust_user_rel]]、[[opened_product]]、[[rel_rebuild_precondition]]。

---END FILE---

---FILE: processes/cust_person_status.md ---
---
type: process
title: 联系人账号状态（status）
page_key: cust_person_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [账号状态, status, ADD, EFFECT, FREEZE]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.status", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
---

联系人账号状态描述一条联系人记录从新增到生效、再到被冻结的生命周期。它与 enable（Y/N）配合使用：管理员换人时旧记录的 status 置 FREEZE 且 enable 置 N，新记录置 EFFECT，因此"当前有效管理员"实际是 status/enable 两个口径叠加的结果（[[valid_person]]、[[company_admin]]、[[admin_change_freeze_create]]）。

## 需求背景
- 管理员唯一性依赖冻结旧记录，而不是删除旧记录，历史留痕与审计由此保证（[[unique_admin_per_company_role]]）。
- 简易认证路径换手机号同样走"冻结 + 新建"，但触发条件与普通变更不同（[[simple_auth_phone_change]]）。

## 版本演进
- 当前版本已支持新增即 ADD、变更即 FREEZE/EFFECT 的完整闭环；冻结同时会删除其在 sys 的角色关联（[[rel_rebuild_precondition]]）。

```ground:process
name: 联系人账号状态
field: cust_person_info.status
states:
  - value: ADD
    label: 新增待生效
    source: db_dist
  - value: EFFECT
    label: 生效
    source: db_dist
  - value: FREEZE
    label: 冻结
    source: db_dist
transitions:
  - from: ""
    event: "新建联系人/法人同步为管理员（新增时置 ADD）"
    to: ADD
    evidence: "code_path:CustPersonApplication.java:saveFromCustLegal"
  - from: EFFECT
    event: "管理员变更（旧管理员冻结：enable=N, status=FREEZE）"
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm"
  - from: ""
    event: "生成新管理员记录"
    to: EFFECT
    evidence: "code_path:CustPersonApplication.java:ifNessaryFrzAdm(cpf.setStatus(CustPersonStatusConstant.EFFECT))"
  - from: EFFECT
    event: "简易认证变更管理员且手机号变化"
    to: FREEZE
    evidence: "code_path:CustPersonApplication.java:simpleChangePerson(setStatus(CustPersonStatusConstant.FREEZE))"
```

相关页面：[[cust_person_info]]、[[admin_change_freeze_create]]、[[simple_auth_phone_change]]、[[company_status_cascade_person]]。

---END FILE---

---FILE: processes/phone_realname_status.md ---
---
type: process
title: 联系人实名认证状态（phone_realname_status）
page_key: phone_realname_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [手机号实名认证状态, 实名认证状态, face_status]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.phone_realname_status", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
---

phone_realname_status 表示手机号维度的实名认证进度，与 face_status 共用同一套码值。前端在 AUTO/MANUAL_AUTHENTICATION_PASSED 时不再弹认证框，因此该字段直接影响交互；它与 real_name_result 是两套码值，不可互换（[[real_name_result]]、[[realname_status]]）。

## 需求背景
- 同租户下已有认证通过记录时，新增经办人直接继承认证通过，减少重复认证成本（[[new_person_inherit_verified]]）。
- 免认证白名单只覆盖特定租户与角色（[[skip_realname_auth_whitelist]]）。

## 版本演进
- 当前版本的新增默认值为 TO_BE_VERIFIED；人工核验通过由 updateVerifyNameStatus 写入 MANUAL_AUTHENTICATION_PASSED；不通过状态当前仅见 DB 分布。

```ground:process
name: 联系人实名认证状态
field: cust_person_info.phone_realname_status
states:
  - value: TO_BE_VERIFIED
    label: 待核查
    source: db_dist
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动认证不通过
    source: db_dist
transitions:
  - from: ""
    event: "新增经办人默认待核查"
    to: TO_BE_VERIFIED
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson(setPhoneRealnameStatus(TO_BE_VERIFIED))"
  - from: TO_BE_VERIFIED
    event: "同租户下已存在认证通过记录，新增时继承"
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson"
  - from: TO_BE_VERIFIED
    event: "人工实名核验通过"
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: "code_path:CustPersonApplication.java:updateVerifyNameStatus"
  - from: AUTOMATIC_AUTHENTICATION_PASSED
    event: "运营/风控侧回写不通过"
    to: AUTOMATIC_AUTHENTICATION_FAILED
    evidence: "db_dist:cust_person_info.phone_realname_status"
```

相关页面：[[cust_person_info]]、[[real_name_result]]、[[realname_status]]、[[new_person_inherit_verified]]。

---END FILE---

---FILE: processes/real_name_result.md ---
---
type: process
title: 联系人实名结果（real_name_result）
page_key: real_name_result
domain: 经办人/联系人/管理员管理
status: draft
aliases: [实名结果, INIT, VERIFIED_SUCCESS, VERIFIED_FAILED]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.real_name_result", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
---

real_name_result 是实名认证结果字段，使用 INIT / VERIFIED_SUCCESS / VERIFIED_FAILED 一套独立码值，与 phone_realname_status、face_status 的认证码值并行存在。人脸认证回写与人工核验通过都会推进到 VERIFIED_SUCCESS（[[phone_realname_status]]、[[realname_status]]）。

## 需求背景
- 继承逻辑除了写 phone_realname_status，还会写 real_name_result=VERIFIED_SUCCESS 并继承证件号/类型/有效期（[[new_person_inherit_verified]]）。

## 版本演进
- 当前版本中 INIT 是初始态；VERIFIED_FAILED 目前仅有 DB 分布证据，未定位到写值代码路径。

```ground:process
name: 联系人实名结果
field: cust_person_info.real_name_result
states:
  - value: INIT
    label: 初始化/待认证
    source: db_dist
  - value: VERIFIED_SUCCESS
    label: 认证成功
    source: code_enum
  - value: VERIFIED_FAILED
    label: 认证失败
    source: db_dist
transitions:
  - from: INIT
    event: "人脸认证回写"
    to: VERIFIED_SUCCESS
    evidence: "code_path:CustPersonApplication.java:updateFaceStatus"
  - from: INIT
    event: "人工实名核验通过"
    to: VERIFIED_SUCCESS
    evidence: "code_path:CustPersonApplication.java:updateVerifyNameStatus"
  - from: INIT
    event: "认证不通过"
    to: VERIFIED_FAILED
    evidence: "db_dist:cust_person_info.real_name_result"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[realname_status]]。

---END FILE---

---FILE: processes/cust_build_status.md ---
---
type: process
title: 企业建档状态（决定管理员是否赋权）
page_key: cust_build_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [建档状态, custBuildStatus, BUILD_SUCCESS, CUST_CHANGE]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.cust_build_status", "code_path:CustCompanyInfoApplication.java", "code_path:CustPersonApplication.java"]
contract_version: "0.1"
---

企业建档状态描述企业从初始化到认证成功/失败的审核流转，同时决定联系人（管理员）是否赋权、关联关系能否重建。该状态在企业表与联系人表各存一份，重建判定使用企业侧值（[[build_status]]、[[cust_company_info]]、[[rel_rebuild_company]]）。

## 需求背景
- 审核流转与运营中台直接交互（提交送审、退回），是 ams 来源数据的主要驱动链路。
- 非 AMS 来源新增经办人直接置建档成功，AMS 来源不置（[[ams_source_not_build_success]]）。

## 版本演进
- 当前版本新增了 CUST_CHANGE（企业变更）作为重建可参与状态之一（[[rel_rebuild_precondition]]）。

```ground:process
name: 企业建档状态（决定管理员是否赋权）
field: cust_person_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: db_dist
  - value: CUST_CONFIRM_AWAIT
    label: 待客户认证
    source: db_dist
  - value: CUST_BUILDING
    label: 审核中
    source: db_dist
  - value: BUILD_SUCCESS
    label: 认证成功
    source: db_dist
  - value: BUILD_FAIL
    label: 认证失败
    source: db_dist
transitions:
  - from: INIT
    event: "邀请认证-客户录入/自主注册提交"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: "邀请认证-平台录入提交"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: "客户提交送运营中台审核"
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: "运营中台审核退回"
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: "审核通过"
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: ""
    event: "非 AMS 来源新增经办人直接置建档成功"
    to: BUILD_SUCCESS
    evidence: "code_path:CustPersonApplication.java:insertOrUpdatePerson"
```

相关页面：[[cust_company_info]]、[[cust_person_info]]、[[build_status]]、[[ams_source_not_build_success]]。

---END FILE---

---FILE: calibers/valid_person.md ---
---
type: caliber
title: 有效联系人
page_key: valid_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [enable=Y, 未冻结联系人]
oid: 1
scope.databases: [unknown]
sources: ["code:CustPersonApplication.java#listCompanyPerson/getAdminByCustCodeCompanyType"]
contract_version: "0.1"
---

"有效联系人"是所有联系人查询与管理员定位的基础口径：只有 enable='Y' 的记录参与。管理员换人后旧记录 enable=N，虽然物理行仍在 [[cust_person_info]] 中，但不会再出现在列表与管理员定位结果里（[[cust_person_status]]、[[company_admin]]）。

## 需求背景
- 该口径是"管理员唯一性"校验、列表分页、运营人汇总的共同前置过滤，任何绕过 enable 的查询都可能取到已被换掉的旧管理员（[[unique_admin_per_company_role]]）。

## 版本演进
- 当前版本中 enable 与 status 并行：冻结写 enable=N + status=FREEZE，两个字段需同时成立才视为失效。

```ground:caliber
name: 有效联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 所有联系人查询/管理员定位
evidence: "code:CustPersonApplication.java#listCompanyPerson/getAdminByCustCodeCompanyType"
```

相关页面：[[cust_person_info]]、[[company_admin]]、[[cust_person_status]]、[[admin_change_freeze_create]]。

---END FILE---

---FILE: calibers/company_admin.md ---
---
type: caliber
title: 企业管理员
page_key: company_admin
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountAdmin, 管理员口径]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type 分布(55375)", "code:CustPersonApplication.java#listCompanyManagerUserId"]
contract_version: "0.1"
---

"企业管理员"口径 = user_type='accountAdmin'，用于管理员定位、管理员唯一性校验与关联重建。它与平台运营人员（operator_id）是两个完全不同的实体，后者来自运营中台（[[operator]]、[[admin]]）。

## 需求背景
- 管理员定位需要叠加 enable 与 company_type 条件，才能得到某企业某角色下的唯一有效管理员（[[valid_person]]、[[unique_admin_per_company_role]]）。
- 关联重建时管理员角色码由 company_type 映射得到（[[rel_rebuild_precondition]]）。

## 版本演进
- DB 分布显示 accountAdmin 记录数（55375）远多于 accountNormal（4205），说明历史冻结行被大量保留。

```ground:caliber
name: 企业管理员
predicate: "cust_person_info.user_type = 'accountAdmin'"
scope: 管理员定位、管理员唯一性校验、关联重建
evidence: "db:cust_person_info.user_type 分布(55375) + code:CustPersonApplication.java#listCompanyManagerUserId"
```

相关页面：[[cust_person_info]]、[[admin]]、[[normal_person]]、[[unique_admin_per_company_role]]。

---END FILE---

---FILE: calibers/normal_person.md ---
---
type: caliber
title: 经办人
page_key: normal_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountNormal, 经办人口径]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type 分布(4205)", "code:CustPersonController.java#getOperInfo"]
contract_version: "0.1"
---

"经办人"口径 = user_type='accountNormal'，用于经办人列表与实名认证待办判定。注意 [[cust_person_info]] 是表级统称，接口入参常直接叫 CustPersonInfoDO，并不代表该行就是经办人（[[contact_person]]）。

## 需求背景
- 经办人列表需排除游客，避免游客污染分页结果（[[exclude_guest]]）。
- 经办人实名认证待办与免认证白名单均围绕该口径展开（[[phone_realname_status]]、[[skip_realname_auth_whitelist]]）。

## 版本演进
- 当前版本经办人在关联重建中固定使用 ROLE_CODE_NORMAL（[[rel_rebuild_precondition]]）。

```ground:caliber
name: 经办人
predicate: "cust_person_info.user_type = 'accountNormal'"
scope: 经办人列表、实名认证待办判定
evidence: "db:cust_person_info.user_type 分布(4205) + code:CustPersonController.java#getOperInfo"
```

相关页面：[[cust_person_info]]、[[contact_person]]、[[company_admin]]、[[exclude_guest]]。

---END FILE---

---FILE: calibers/exclude_guest.md ---
---
type: caliber
title: 排除游客
page_key: exclude_guest
domain: 经办人/联系人/管理员管理
status: draft
aliases: [accountGuest, 非游客]
oid: 1
scope.databases: [unknown]
sources: ["code:CustPersonApplication.java#pagePerson"]
contract_version: "0.1"
---

"排除游客"口径用于联系人分页与运营人汇总：查询条件为 user_type <> 'accountGuest'，避免游客记录进入业务列表（[[normal_person]]、[[contact_person]]）。

## 需求背景
- 游客（user_type=accountGuest）与经办人共用 [[cust_person_info]] 表，若不过滤会污染经办人列表与运营人统计口径。

## 版本演进
- 当前版本以 .ne("user_type", UserTypeEnum.guest.getDictKey()) 实现，属于代码侧显式排除而非 SQL 视图。

```ground:caliber
name: 排除游客
predicate: "cust_person_info.user_type <> 'accountGuest'"
scope: 联系人分页、运营人汇总，避免游客污染列表
evidence: "code:CustPersonApplication.java#pagePerson(.ne(\"user_type\", UserTypeEnum.guest.getDictKey()))"
```

相关页面：[[cust_person_info]]、[[normal_person]]、[[contact_person]]、[[valid_person]]。

---END FILE---

---FILE: calibers/rel_rebuild_company.md ---
---
type: caliber
title: 可参与关联重建的企业
page_key: rel_rebuild_company
domain: 经办人/联系人/管理员管理
status: draft
aliases: [BUILD_SUCCESS, CUST_CHANGE, 重建企业口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany"]
contract_version: "0.1"
---

"可参与关联重建的企业"口径 = cust_company_info.cust_build_status='BUILD_SUCCESS'，用于 sys_cust_user_rel 重建（含 CUST_CHANGE 场景）。联系人侧同名字段不参与该判定（[[build_status]]、[[rel_rebuild_precondition]]）。

## 需求背景
- 重建的完整前置条件还包括企业 enable=Y、存在 OPENED 产品、管理员 user_id>0（[[sys_cust_user_rel]]、[[opened_product]]）。

## 版本演进
- 当前版本将 CUST_CHANGE 纳入可重建状态集合，服务企业变更场景。

```ground:caliber
name: 可参与关联重建的企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: sys_cust_user_rel 重建（含 CUST_CHANGE）
evidence: "code:CustCompanyUserRelApplication.java#processSingleCompany"
```

相关页面：[[cust_company_info]]、[[sys_cust_user_rel]]、[[rel_rebuild_precondition]]、[[build_status]]。

---END FILE---

---FILE: calibers/opened_product.md ---
---
type: caliber
title: 已开通产品
page_key: opened_product
domain: 经办人/联系人/管理员管理
status: draft
aliases: [OPENED, open_status, 产品开通口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyUserRelApplication.java#processSingleCompany", "code:CustCompanyQueryApplication.java#queryOpenedProductsByCompanies"]
contract_version: "0.1"
---

"已开通产品"口径 = cust_auth_application.open_status='OPENED'，用于关联重建前置校验与产品开通状态展示（展示侧另含 OPENING）。它是"联系人已开通产品"的真实查询口径，[[cust_person_info]] 的 auth_application 字段不是（[[cust_auth_application]]、[[sys_cust_user_rel]]）。

## 需求背景
- 重建要求企业至少存在一个 OPENED 产品，否则不写入关联关系（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本展示侧口径包含 OPENED 与 OPENING 两种状态，重建侧只认 OPENED。

```ground:caliber
name: 已开通产品
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: 关联重建、产品开通状态展示（另含 OPENING）
evidence: "code:CustCompanyUserRelApplication.java#processSingleCompany + CustCompanyQueryApplication.java#queryOpenedProductsByCompanies"
```

相关页面：[[cust_auth_application]]、[[sys_cust_user_rel]]、[[rel_rebuild_precondition]]。

---END FILE---

---FILE: calibers/not_frozen_rel.md ---
---
type: caliber
title: 未冻结的关联关系
page_key: not_frozen_rel
domain: 经办人/联系人/管理员管理
status: draft
aliases: [is_freeze=N, 关联有效口径]
oid: 1
scope.databases: [unknown]
sources: ["code:CustCompanyInfoApplication.java#deleteCustInfo"]
contract_version: "0.1"
---

"未冻结的关联关系"口径 = sys_cust_user_rel.is_freeze='N'，在企业删除时用于判断是否还可以清理 sys_user。冻结的关联视为仍有业务挂靠，不能直接清理用户（[[sys_cust_user_rel]]）。

## 需求背景
- 该口径是企业级删除/冻结操作的安全阀，与联系人侧 enable 口径共同决定账号可否被回收（[[valid_person]]、[[company_status_cascade_person]]）。

## 版本演进
- 当前版本仅确认该口径存在于企业删除路径，未覆盖全部消费点。

```ground:caliber
name: 未冻结的关联关系
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 企业删除时判断是否可清理 sys_user
evidence: "code:CustCompanyInfoApplication.java#deleteCustInfo"
```

相关页面：[[sys_cust_user_rel]]、[[company_status_cascade_person]]、[[valid_person]]。

---END FILE---

---FILE: concepts/contact_person.md ---
---
type: concept
title: 联系人
page_key: contact_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [经办人, 客户联系人, cust_person_info, accountNormal]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type", "code:CustPersonController.java#getOperInfo"]
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets:
  - cust_person_info.user_type
adjudication: boundary
also_confused_with:
  - "cust_person_info.user_type = 'accountAdmin'"
  - "cust_person_info.user_type = 'accountGuest'"
boundary: "cust_person_info 是表级统称（客户联系人表），“经办人”仅指 user_type=accountNormal 的行，管理员为 accountAdmin、游客为 accountGuest；接口入参常直接叫 CustPersonInfoDO，不代表就是经办人。"
---

"联系人"是对 [[cust_person_info]] 表级数据的统称，实际业务语义由 user_type 决定：accountAdmin=企业管理员、accountNormal=经办人、accountGuest=游客。日常口语里"联系人"和"经办人"经常混用，但在口径层面必须区分（[[normal_person]]、[[company_admin]]）。

## 需求背景
- 经办人列表、管理员定位、游客排除三个口径分别对应 user_type 的三个取值，混用会直接导致列表与校验结果错误（[[exclude_guest]]、[[valid_person]]）。

## 版本演进
- 当前版本的接口入参仍以 CustPersonInfoDO 命名，命名未体现 user_type，是概念混淆的主要来源。

相关页面：[[cust_person_info]]、[[normal_person]]、[[company_admin]]、[[exclude_guest]]。

---END FILE---

---FILE: concepts/admin.md ---
---
type: concept
title: 管理员
page_key: admin
domain: 经办人/联系人/管理员管理
status: draft
aliases: [企业管理员, accountAdmin, 授权人]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.user_type", "code:CustPersonApplication.java#checkBeforeSave"]
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
adjudication: boundary
also_confused_with:
  - cust_person_info.operator_id
boundary: "本主题的“管理员”是企业侧管理员（同一企业+角色只能有一个）；operator_id/operator/operator_realname 指平台分派的运营人员（运营中台 OperUserDTO），是另一个实体，切勿混同。"
---

本主题的"管理员"特指企业侧管理员（user_type=accountAdmin），同一企业同一角色只能有一个。它与平台运营人员（[[operator]]）是完全不同的实体，前者是客户方授权人，后者是平台运营中台分派的人员（[[company_admin]]）。

## 需求背景
- 管理员新增/变更前需校验同企业同角色唯一性（[[unique_admin_per_company_role]]）。
- 管理员换人采用"冻结旧 + 新建"而非原地修改（[[admin_change_freeze_create]]）。

## 版本演进
- 当前版本新增了 company_type 维度的角色划分，管理员唯一性校验按 company_type + ref_cust_company_info 组合生效。

相关页面：[[cust_person_info]]、[[company_admin]]、[[operator]]、[[unique_admin_per_company_role]]。

---END FILE---

---FILE: concepts/operator.md ---
---
type: concept
title: 运营人员
page_key: operator
domain: 经办人/联系人/管理员管理
status: draft
aliases: [运营, 客户经理, custManagerName, operator]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.operator_id", "code:CustPersonController.java#sendHaveInvitationCode"]
contract_version: "0.1"
maps_to: cust_person_info.operator_id
field_targets:
  - cust_person_info.operator_id
  - cust_person_info.operator
  - cust_person_info.operator_realname
adjudication: boundary
also_confused_with:
  - cust_person_info.user_id
boundary: "operator_id 来自运营中台（OperUserDTO.id），不是 sys_user.id，也不是 cust_person_info.user_id；发送邀请码/客服名片前要求 operator_id 非空。"
---

"运营人员"指平台分派给客户的运营/客户经理，标识为 operator_id（运营中台 OperUserDTO.id），登录名与姓名分别落在 operator、operator_realname。它不是客户侧的联系人，也不是 sys_user 中的用户（[[admin]]、[[cust_person_info]]）。

## 需求背景
- 发送邀请码与客服名片前必须已分配运营，否则业务不可用（[[operator_assign_before_invite]]）。
- 批量换运营以 operator_realname 作为模板导出内容（[[batch_change_operator_template]]）。

## 版本演进
- 当前版本支持批量更换运营，但要求 operatorIds 与 projectIds 互斥且有数量上限。

相关页面：[[cust_person_info]]、[[admin]]、[[operator_assign_before_invite]]、[[batch_change_operator_template]]。

---END FILE---

---FILE: concepts/realname_status.md ---
---
type: concept
title: 实名认证状态
page_key: realname_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [phone_realname_status, face_status, realname_status]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.phone_realname_status", "db:cust_person_info.real_name_result", "code_path:CustPersonApplication.java:updateVerifyNameStatus"]
contract_version: "0.1"
maps_to: cust_person_info.phone_realname_status
field_targets:
  - cust_person_info.phone_realname_status
  - cust_person_info.face_status
  - cust_person_info.real_name_result
adjudication: boundary
also_confused_with:
  - cust_person_info.real_name_result
  - cust_person_info.face_status
  - cust_person_info.realname_status
boundary: "phone_realname_status 与 face_status 共用同一套认证结果码值（TO_BE_VERIFIED/AUTO_PASSED/MANUAL_PASSED/AUTO_FAILED），real_name_result 是另一套 INIT/VERIFIED_* 码值；DB 中 realname_status 与 phone_realname_status 并存但分布差异极大，需区分使用。"
---

"实名认证状态"在代码与需求文档里指代多个字段，必须按字段区分：phone_realname_status（手机号维度）与 face_status（人脸维度）共用同一套认证码值；real_name_result 使用 INIT/VERIFIED_* 另一套码值（[[phone_realname_status]]、[[real_name_result]]）。

## 需求背景
- 前端弹框判断依赖认证通过状态，因此字段选错会直接表现为"认证框重复弹出/不弹出"。
- 新增经办人继承逻辑会同时写 phone_realname_status 与 real_name_result（[[new_person_inherit_verified]]）。

## 版本演进
- DB 中 realname_status 与 phone_realname_status 并存且分布差异极大，realname_status 未纳入本次字段语义清单，使用前需另行核实。

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[real_name_result]]、[[new_person_inherit_verified]]。

---END FILE---

---FILE: concepts/build_status.md ---
---
type: concept
title: 建档状态
page_key: build_status
domain: 经办人/联系人/管理员管理
status: draft
aliases: [cust_build_status, custBuildStatus]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.cust_build_status", "db:cust_company_info.cust_build_status", "code:CustCompanyUserRelApplication.java#processSingleCompany"]
contract_version: "0.1"
maps_to: cust_person_info.cust_build_status
field_targets:
  - cust_person_info.cust_build_status
  - cust_company_info.cust_build_status
adjudication: boundary
also_confused_with:
  - cust_company_info.cust_build_status
boundary: "同名同码值，企业表与联系人表各存一份；重建 sys_cust_user_rel 时判定用企业侧，联系人侧仅表示该联系人自身建档进度。"
---

"建档状态"在 [[cust_company_info]] 与 [[cust_person_info]] 中各存一份，码值相同但语义主体不同：企业侧决定企业能否进入审核/重建流程，联系人侧表示该联系人自身建档进度（[[cust_build_status]]、[[rel_rebuild_company]]）。

## 需求背景
- 重建 sys_cust_user_rel 的判定取企业侧值，取错一侧会导致关联关系不写入或误写入（[[rel_rebuild_precondition]]）。
- AMS 来源的新增经办人不写建档成功，避免与运营中台流程冲突（[[ams_source_not_build_success]]）。

## 版本演进
- 当前版本联系人侧建档状态仅供展示与自身进度判断，未参与重建判定。

相关页面：[[cust_company_info]]、[[cust_person_info]]、[[cust_build_status]]、[[rel_rebuild_company]]。

---END FILE---

---FILE: concepts/source.md ---
---
type: concept
title: 来源
page_key: source
domain: 经办人/联系人/管理员管理
status: draft
aliases: [source, AMS, longteng]
oid: 1
scope.databases: [unknown]
sources: ["db:cust_person_info.source", "code_path:CustPersonApplication.java:insertOrUpdatePerson"]
contract_version: "0.1"
maps_to: cust_person_info.source
field_targets:
  - cust_person_info.source
adjudication: boundary
also_confused_with:
  - cust_person_info.user_type
boundary: "source 表示数据来路（AMS=运营中台同步，longteng=龙腾），不是联系人身份；代码对比用 .name()/字面量，DB 中 AMS=417、longteng=69。"
---

"来源"表示联系人数据的来路（AMS=运营中台同步，longteng=龙腾），不是联系人身份。代码中的比较既有 .name() 也有字面量写法，排查时需注意大小写与枚举一致性（[[cust_person_info]]、[[contact_person]]）。

## 需求背景
- 来源决定新增时是否直接置建档成功：AMS 来源不置，其余来源直接置 BUILD_SUCCESS（[[ams_source_not_build_success]]）。

## 版本演进
- DB 中 AMS=417、longteng=69；longteng 在代码枚举中未声明，属需要回填的取值点。

相关页面：[[cust_person_info]]、[[contact_person]]、[[ams_source_not_build_success]]、[[cust_build_status]]。

---END FILE---

---FILE: rules/unique_phone_idcard_in_company.md ---
---
type: rule
title: 企业内手机号/身份证号唯一
page_key: unique_phone_idcard_in_company
domain: 经办人/联系人/管理员管理
status: draft
aliases: [手机号唯一, 身份证唯一, checkBeforeSave]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#checkBeforeSave"]
contract_version: "0.1"
---

新增/编辑联系人前的强制校验：同一企业（ref_cust_company_info）下手机号或身份证号不允许重复，命中即抛业务异常并中断保存（[[cust_person_info]]）。

## 需求背景
- 手机号在库内是密文存储，校验需先做加密比较，因此该校验与普通字段唯一性校验实现方式不同（[[cust_person_info]]、[[valid_person]]）。

## 版本演进
- 当前版本按企业维度汇总存量后比对，跨企业不拦截。

```ground:rule
name: 企业内手机号/身份证号唯一
content: "保存联系人前按 ref_cust_company_info 汇总存量，手机号或身份证号重复则抛“当前组织下已存在手机号【x】成员！/身份证号【x】成员！”"
impact: 新增/编辑联系人被拦截
field_targets:
  - cust_person_info.phone
  - cust_person_info.certification_no
  - cust_person_info.ref_cust_company_info
evidence: "code_path:CustPersonApplication.java#checkBeforeSave"
```

相关页面：[[cust_person_info]]、[[unique_admin_per_company_role]]、[[valid_person]]。

---END FILE---

---FILE: rules/unique_admin_per_company_role.md ---
---
type: rule
title: 同企业同角色唯一管理员
page_key: unique_admin_per_company_role
domain: 经办人/联系人/管理员管理
status: draft
aliases: [管理员唯一性, accountAdmin唯一]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#checkBeforeSave,#updateAuthorAndApply"]
contract_version: "0.1"
---

管理员新增/变更的前置校验：同一 company_type + ref_cust_company_info 下，user_type=accountAdmin 且 enable=Y 的记录数必须为 0，否则拒绝操作（[[company_admin]]、[[valid_person]]）。

## 需求背景
- 该校验把"角色"（company_type）与"身份"（user_type=accountAdmin）叠加，所以同一企业不同角色可以各有一个管理员。
- 变更场景下必须先冻结旧管理员，否则校验会命中自身（[[admin_change_freeze_create]]）。

## 版本演进
- 当前版本以 enable=Y 为统计条件，冻结记录不计入。

```ground:rule
name: 同企业同角色唯一管理员
content: "统计同一 company_type + ref_cust_company_info 下 user_type=accountAdmin 且 enable=Y 的记录数必须为 0，否则抛“当前企业已经存在该客户角色的管理员”"
impact: 管理员新增/变更前置校验
field_targets:
  - cust_person_info.user_type
  - cust_person_info.company_type
  - cust_person_info.enable
evidence: "code_path:CustPersonApplication.java#checkBeforeSave,#updateAuthorAndApply"
```

相关页面：[[cust_person_info]]、[[company_admin]]、[[admin_change_freeze_create]]、[[valid_person]]。

---END FILE---

---FILE: rules/admin_change_company_flow.md ---
---
type: rule
title: 管理员变更走企业变更流程
page_key: admin_change_company_flow
domain: 经办人/联系人/管理员管理
status: draft
aliases: [copyCustRecordAndStartApply, cust_status=EFFECT]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#updateAuthorAndApply"]
contract_version: "0.1"
---

管理员变更不是独立动作，而是通过企业变更流程（copyCustRecordAndStartApply）承载；仅当企业 cust_status=EFFECT 时才启动，非 EFFECT 状态下静默不启动、不抛异常（[[cust_company_info]]、[[admin]]）。

## 需求背景
- 由于是"静默不启动"，冻结/注销企业下的变更请求表现为"提交成功但无后续流程"，排障时需优先检查企业状态（[[company_status_cascade_person]]）。

## 版本演进
- 当前版本未对非 EFFECT 场景给出用户提示，属已知行为差异。

```ground:rule
name: 管理员变更走企业变更流程
content: "仅当企业 cust_company_info.cust_status=EFFECT 时才 copyCustRecordAndStartApply 启动变更流程；非 EFFECT 时静默不启动（不抛异常）"
impact: 冻结/注销企业无法发起管理员变更
field_targets:
  - cust_company_info.cust_status
evidence: "code_path:CustPersonApplication.java#updateAuthorAndApply"
```

相关页面：[[cust_company_info]]、[[admin]]、[[company_status_cascade_person]]、[[admin_change_freeze_create]]。

---END FILE---

---FILE: rules/admin_change_freeze_create.md ---
---
type: rule
title: 管理员换人=冻结旧+新建
page_key: admin_change_freeze_create
domain: 经办人/联系人/管理员管理
status: draft
aliases: [ifNessaryFrzAdm, UN0012, UN0013, UN0014]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#ifNessaryFrzAdm"]
contract_version: "0.1"
---

管理员换人由 isAdminChange（外部 alterTypes 命中 UN0012/UN0013/UN0014）触发：旧记录 enable=N、status=FREEZE，删除其在 sys 的角色关联，再复制生成新记录（status=EFFECT，清空 userId/userName），最后绑组织与授权协议（[[cust_person_status]]、[[admin]]）。

## 需求背景
- 该实现保证同一时刻只有一个有效管理员用户，同时保留历史留痕（[[unique_admin_per_company_role]]、[[valid_person]]）。
- 新记录清空 userId/userName，意味着换人后需重新建立登录用户关联（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本已覆盖冻结、解绑、复制、绑组织与授权协议的完整链路。

```ground:rule
name: 管理员换人=冻结旧+新建
content: "isAdminChange(ext alterTypes 命中 UN0012/UN0013/UN0014) 时：旧记录 enable=N、status=FREEZE，删除其在 sys 的角色关联，复制生成新记录（status=EFFECT, 清空 userId/userName），再绑组织与授权协议"
impact: 同一时刻只有一个有效管理员用户
field_targets:
  - cust_person_info.enable
  - cust_person_info.status
  - cust_person_info.user_id
evidence: "code_path:CustPersonApplication.java#ifNessaryFrzAdm"
```

相关页面：[[cust_person_info]]、[[cust_person_status]]、[[admin]]、[[unique_admin_per_company_role]]。

---END FILE---

---FILE: rules/simple_auth_phone_change.md ---
---
type: rule
title: 简易认证换手机号即换人
page_key: simple_auth_phone_change
domain: 经办人/联系人/管理员管理
status: draft
aliases: [simpleChangePerson, 简易认证管理员变更]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#simpleChangePerson"]
contract_version: "0.1"
---

简易认证场景下判定"换人"的触发条件是手机号是否变化：手机号变化则冻结旧管理员、删角色关联、删组织用户、新建管理员记录、绑机构并直通授权书；手机号未变则仅更新，并同步登录邮箱（旧业务邮箱=登录邮箱，或仅关联一个企业时才同步）（[[admin_change_freeze_create]]、[[admin]]）。

## 需求背景
- 该路径与 UN0012/UN0013/UN0014 触发的普通变更路径并存，二者判定依据不同，不能互相替代（[[admin_change_freeze_create]]）。

## 版本演进
- 当前版本已包含手机号未变时的邮箱同步旁路逻辑。

```ground:rule
name: 简易认证换手机号即换人
content: "simpleChangePerson 中手机号变化：冻结旧管理员、删角色关联、删组织用户、新建管理员记录、绑机构并直通授权书；手机号未变时仅更新并同步登录邮箱（旧业务邮箱=登录邮箱或仅关联一个企业才同步）"
impact: 简易认证企业管理员变更路径
field_targets:
  - cust_person_info.phone
  - cust_person_info.enable
  - cust_person_info.status
evidence: "code_path:CustPersonApplication.java#simpleChangePerson"
```

相关页面：[[cust_person_info]]、[[admin_change_freeze_create]]、[[admin]]、[[cust_person_status]]。

---END FILE---

---FILE: rules/new_person_inherit_verified.md ---
---
type: rule
title: 新增经办人继承已认证信息
page_key: new_person_inherit_verified
domain: 经办人/联系人/管理员管理
status: draft
aliases: [实名继承, insertOrUpdatePerson]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#insertOrUpdatePerson"]
contract_version: "0.1"
---

同一 db_tenant_code 下若已存在 phone_realname_status ∈ {AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED} 的记录，新增经办人直接置自动认证通过 + real_name_result=VERIFIED_SUCCESS，并继承证件号/证件类型/有效期（[[phone_realname_status]]、[[real_name_result]]）。

## 需求背景
- 该规则实现跨企业复用实名结果，减少重复认证；继承范围含证件信息，若证件有效期过期仍会沿用，需注意（[[realname_status]]）。

## 版本演进
- 当前版本继承判定按 db_tenant_code 维度，而非企业维度。

```ground:rule
name: 新增经办人继承已认证信息
content: "同 db_tenant_code 下若存在 phone_realname_status ∈ {AUTOMATIC_AUTHENTICATION_PASSED, MANUAL_AUTHENTICATION_PASSED} 的记录，则新经办人直接置自动认证通过 + real_name_result=VERIFIED_SUCCESS，并继承证件号/证件类型/有效期"
impact: 跨企业复用实名结果，减少重复认证
field_targets:
  - cust_person_info.phone_realname_status
  - cust_person_info.real_name_result
  - cust_person_info.certification_no
evidence: "code_path:CustPersonApplication.java#insertOrUpdatePerson"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[real_name_result]]、[[realname_status]]。

---END FILE---

---FILE: rules/ams_source_not_build_success.md ---
---
type: rule
title: AMS 来源不置建档成功
page_key: ams_source_not_build_success
domain: 经办人/联系人/管理员管理
status: draft
aliases: [AMS, source≠AMS, 建档成功写入条件]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#insertOrUpdatePerson"]
contract_version: "0.1"
---

新增经办人仅当 source ≠ AMS 时才写 setCustBuildStatus(BUILD_SUCCESS)；AMS 来源交由运营中台流程驱动，不在此处置为已建档（[[source]]、[[cust_build_status]]）。

## 需求背景
- 该规则用于防止外部同步数据被误标为已建档，进而误触发关联重建（[[rel_rebuild_precondition]]）。

## 版本演进
- 当前版本以 AMS 为唯一排除值；longteng 等其他来源不在排除范围内。

```ground:rule
name: AMS 来源不置建档成功
content: "新增经办人仅当 source ≠ AMS 时才 setCustBuildStatus(BUILD_SUCCESS)；AMS 来源交由运营中台流程驱动"
impact: 防止外部同步数据被误标为已建档
field_targets:
  - cust_person_info.source
  - cust_person_info.cust_build_status
evidence: "code_path:CustPersonApplication.java#insertOrUpdatePerson"
```

相关页面：[[cust_person_info]]、[[source]]、[[cust_build_status]]、[[rel_rebuild_precondition]]。

---END FILE---

---FILE: rules/rel_rebuild_precondition.md ---
---
type: rule
title: 关联重建前置条件
page_key: rel_rebuild_precondition
domain: 经办人/联系人/管理员管理
status: draft
aliases: [processSingleCompany, reBuildSysCustUserRel, 关联重建]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustCompanyUserRelApplication.java#processSingleCompany,#reBuildSysCustUserRel"]
contract_version: "0.1"
---

processSingleCompany / reBuildSysCustUserRel 的完整前置条件：企业 enable=Y、cust_build_status ∈ {BUILD_SUCCESS, CUST_CHANGE}、存在 open_status=OPENED 的产品、管理员 user_id>0；管理员角色码取 custNacosProperties.getAuthUserRoleCode(companyType)，经办人固定 ROLE_CODE_NORMAL；若 (productId, roleId) 已在关联集中则跳过（[[sys_cust_user_rel]]、[[rel_rebuild_company]]、[[opened_product]]）。

## 需求背景
- 该规则决定 sys_cust_user_rel 是否写入，是"已开通产品"与权限关联的唯一入口（[[opened_product]]）。
- 管理员 user_id 为空（尚未开户/未同步用户中心）时重建被跳过，需先完成用户开户（[[cust_person_info]]）。

## 版本演进
- 当前版本已按 (productId, roleId) 做幂等去重，重复重建不会产生重复关联。

```ground:rule
name: 关联重建前置条件
content: "processSingleCompany/ reBuildSysCustUserRel 要求：企业 enable=Y、cust_build_status ∈ {BUILD_SUCCESS, CUST_CHANGE}、存在 open_status=OPENED 的产品、管理员 user_id>0；管理员角色码取 custNacosProperties.getAuthUserRoleCode(companyType)，经办人固定 ROLE_CODE_NORMAL；已在关联集（productId_roleId）中则跳过"
impact: 决定 sys_cust_user_rel 是否写入
field_targets:
  - cust_company_info.cust_build_status
  - cust_person_info.user_type
  - cust_person_info.user_id
evidence: "code_path:CustCompanyUserRelApplication.java#processSingleCompany,#reBuildSysCustUserRel"
```

相关页面：[[sys_cust_user_rel]]、[[cust_company_info]]、[[cust_person_info]]、[[opened_product]]、[[rel_rebuild_company]]。

---END FILE---

---FILE: rules/skip_realname_auth_whitelist.md ---
---
type: rule
title: 跳过实名认证白名单
page_key: skip_realname_auth_whitelist
domain: 经办人/联系人/管理员管理
status: draft
aliases: [skip_auth_flag, HBLT, 免认证]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonController.java#skipRealNameAuth"]
contract_version: "0.1"
---

只有租户 mainTenantFlgEn=HBLT，或联系人 company_type ∈ {CORE, PROJECT_COMPANY} 时，才允许置 skip_auth_flag=Y；否则抛"不支持该角色的经办人跳过实名认证"（[[cust_person_info]]、[[phone_realname_status]]）。

## 需求背景
- 该规则限制免认证范围，避免任意角色绕过实名认证流程（[[skip_auth_flag]] 所在表见 [[cust_person_info]]）。

## 版本演进
- 当前版本的免认证白名单由租户标志与角色类型两个条件之一满足即可。

```ground:rule
name: 跳过实名认证白名单
content: "仅当租户 mainTenantFlgEn=HBLT 或 company_type ∈ {CORE, PROJECT_COMPANY} 时允许置 skip_auth_flag=Y，否则抛“不支持该角色的经办人跳过实名认证”"
impact: 限制免认证范围
field_targets:
  - cust_person_info.skip_auth_flag
  - cust_person_info.company_type
evidence: "code_path:CustPersonController.java#skipRealNameAuth"
```

相关页面：[[cust_person_info]]、[[phone_realname_status]]、[[normal_person]]、[[contact_person]]。

---END FILE---

---FILE: rules/company_status_cascade_person.md ---
---
type: rule
title: 企业状态级联到联系人
page_key: company_status_cascade_person
domain: 经办人/联系人/管理员管理
status: draft
aliases: [freeze, diable, userStatusSync, 级联冻结]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustCompanyInfoApplication.java#freeze,#diable,#userStatusSync"]
contract_version: "0.1"
---

企业级操作会级联到联系人账号：冻结企业同时冻结企业管理员；注销企业冻结全部用户，并按 company_type 逐个同步用户状态（[[cust_company_info]]、[[valid_person]]）。

## 需求背景
- 级联冻结后联系人 enable 变化，所有按 enable=Y 的查询随之失效（[[valid_person]]）。
- 企业删除时还会以 sys_cust_user_rel.is_freeze='N' 判断能否清理 sys_user（[[not_frozen_rel]]）。

## 版本演进
- 当前版本冻结与注销走不同级联范围（管理员 vs 全部用户），同步粒度按 company_type 区分。

```ground:rule
name: 企业状态级联到联系人
content: "冻结企业同时冻结企业管理员；注销企业冻结全部用户并按 company_type 逐个同步用户状态"
impact: 企业级操作对联系人账号的连带影响
field_targets:
  - cust_person_info.enable
  - cust_company_info.cust_status
evidence: "code_path:CustCompanyInfoApplication.java#freeze,#diable,#userStatusSync"
```

相关页面：[[cust_company_info]]、[[cust_person_info]]、[[valid_person]]、[[not_frozen_rel]]。

---END FILE---

---FILE: rules/operator_assign_before_invite.md ---
---
type: rule
title: 发送邀请码/客服名片需先分配运营
page_key: operator_assign_before_invite
domain: 经办人/联系人/管理员管理
status: draft
aliases: [sendHaveInvitationCode, sendOperationQrCode, 分配运营]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonController.java#sendHaveInvitationCode,#sendOperationQrCode + CustPersonApplication.java#getCustomerOperatorQrCode"]
contract_version: "0.1"
---

sendHaveInvitationCode 与 sendOperationQrCode 接口均校验 operator_id 非空，否则提示"请先完成分配运营"；客服名片还要求角色表/企业表能取到 platformCustId 且租户配置了 customer_card_type（[[operator]]、[[cust_person_info]]）。

## 需求背景
- 该规则把运营分配设为邀请码与客服名片的硬前置，运营未分配时相关功能不可用（[[operator]]）。

## 版本演进
- 当前版本客服名片新增了两项额外前置：platformCustId 可获取、租户配置 customer_card_type。

```ground:rule
name: 发送邀请码/客服名片需先分配运营
content: "sendHaveInvitationCode 与 sendOperationQrCode 接口校验 operator_id 非空，否则提示“请先完成分配运营”。客服名片要求角色表/企业表能取到 platformCustId 且租户配置了 customer_card_type"
impact: 运营未分配时业务不可用
field_targets:
  - cust_person_info.operator_id
evidence: "code_path:CustPersonController.java#sendHaveInvitationCode,#sendOperationQrCode + CustPersonApplication.java#getCustomerOperatorQrCode"
```

相关页面：[[cust_person_info]]、[[operator]]、[[batch_change_operator_template]]。

---END FILE---

---FILE: rules/batch_change_operator_template.md ---
---
type: rule
title: 批量更换运营模板二选一
page_key: batch_change_operator_template
domain: 经办人/联系人/管理员管理
status: draft
aliases: [batchChangeOperatorTemplateDownload, 批量换运营]
oid: 1
scope.databases: [unknown]
sources: ["code_path:CustPersonApplication.java#batchChangeOperatorTemplateDownload"]
contract_version: "0.1"
---

batchChangeOperatorTemplateDownload 要求 operatorIds 与 projectIds 互斥（XOR），且各自勾选数量 ≤ BATCH_CHANGE_OPERATOR_TEMPLATE_SELECTION_MAX；导入时按"企业名+租户名"定位企业，同名新运营人员（>1）报错（[[operator]]、[[cust_person_info]]）。

## 需求背景
- 该规则限制批量换运营的输入规模并消除企业定位歧义，避免一次导入命中多义企业或超量数据（[[operator_assign_before_invite]]）。

## 版本演进
- 当前版本导出模板使用 operator_realname 作为运营人员标识（[[operator]]）。

```ground:rule
name: 批量更换运营模板二选一
content: "batchChangeOperatorTemplateDownload 要求 operatorIds 与 projectIds 互斥（XOR），且各自勾选数量 ≤ BATCH_CHANGE_OPERATOR_TEMPLATE_SELECTION_MAX；导入按“企业名+租户名”定位企业，同名新运营人员（>1）报错"
impact: 限制批量换运营的输入规模与歧义
field_targets:
  - cust_person_info.operator_id
  - cust_person_info.operator_realname
evidence: "code_path:CustPersonApplication.java#batchChangeOperatorTemplateDownload"
```

相关页面：[[operator]]、[[cust_person_info]]、[[operator_assign_before_invite]]。

---END FILE---

---REVIEW: table | 物理库名待确认 ---
语义分析未给出任何物理库名，全部页面的 scope.databases 暂以 unknown 占位。待确认 cust_person_info / cust_company_info / sys_cust_user_rel / cust_auth_application 所属物理库后统一回填。
---END REVIEW---

---REVIEW: table | cust_person_info 中代码枚举未声明的 DB 取值 ---
source 的 longteng（DB 69 行）、certification_type 的 CREDENTIALS_ID 均只有 DB 证据、代码枚举未声明；realname_status 与 phone_realname_status 并存且分布差异极大但未纳入字段语义清单。三处取值/字段需业务与研发共同确认后再升级契约。
---END REVIEW---

---REVIEW: rule | 批量更换运营模板二选一 ---
该规则的 evidence 在语义分析中被截断（原始为 "code_path:CustPersonApplication.java#batchChangeOperatorTemplateDownload,#bat…"）。当前页面只写入已确认的方法名锚点，被截断的第二个代码位置待补齐后回填 evidence。
---END REVIEW---