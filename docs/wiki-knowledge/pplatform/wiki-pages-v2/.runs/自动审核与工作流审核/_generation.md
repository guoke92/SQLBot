---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 企业主档表
page_key: cust_company_info
domain: 客户中心
status: draft
aliases:
  - 企业信息表
  - 企业主档
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java
  - code_path:CustCompanyIfoEnchanceService.java
  - code_path:ClientCustCommitValidatorSyncService.java
contract_version: "0.1"
---

cust_company_info 保存企业级客户的主档信息，是企业建档/认证、变更审核、电子签章开通等主链路的落库表。企业级状态字段集中在此表：建档状态 cust_build_status、审核状态 check_status、业务状态 cust_status，以及认证方式与 CA/上上签开通标记。相关流转见 [[company_build_status]]、[[workflow_check]]、[[e_signature]]。

```ground:table
table: cust_company_info
fields:
  - name: cust_build_status
    type: varchar
    desc: 企业建档/认证状态。取值来自 CustBuildStatusEnum，代码中按 getDictKey() 落库与比较。
    dict: CustBuildStatusEnum
  - name: identify_style
    type: varchar
    desc: 企业认证方式。取值来自 IdentifyTypeConstant：SELF 自主认证、INVITE 客户录入、INVITE_AGW 平台录入、SIMPLE 简易认证。
    dict: IdentifyTypeConstant
  - name: check_status
    type: varchar
    desc: 企业审核状态。取值来自 OperApiConstants.CheckStatus，工作流回调按 .name() 写入；缺省时同步接口会补字面量 CUST_CHECK_PASS。
    dict: OperApiConstants.CheckStatus
  - name: cust_status
    type: varchar
    desc: 客户业务状态。代码使用 CustStatusEnum / CustStatusConstant，可见 EFFECT、CHANGE、ADD、WRITEOFF、FAILURE 等。
    dict: CustStatusEnum / CustStatusConstant
  - name: need_register_ca
    type: varchar
    desc: 是否需要开通电子签章（CA）。取值 OpenStatus.Y/N/P，isOpenCa、createCaDoc 按 Y/N/P 判断。
    dict: OpenStatus
  - name: ca_register_status
    type: varchar
    desc: CFCA/电子签章开通状态。取值 OpenStatus.Y/N/P，审核/开通链路按 Y、N、P 判断并回写。
    dict: OpenStatus
  - name: bs_register_status
    type: varchar
    desc: 上上签开通状态。取值 OpenStatus.Y/N/P，setSignRegister、isOpenCa 按 Y、N、P 判断并回写。
    dict: OpenStatus
```

## 需求背景

当前语义分析未提供与 cust_company_info 相关的 reqdoc（需求文档）主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: cust_change_record 客户变更记录表
page_key: cust_change_record
domain: 客户中心
status: draft
aliases:
  - 变更记录表
  - 客户变更审核记录
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:changeMessage
  - code_path:CustStatusCommitProcessor.java:isMsgNotify
contract_version: "0.1"
---

cust_change_record 记录每一次客户变更提交及其审核结果，是变更审核状态机 [[cust_change_check]] 的落库载体。字段 status 承接工作流回调写入，msg_send 用于审核消息幂等去重，alter_type_id 与 cust_change_cfg 关联描述本次变更项。相关口径见 [[change_msg_sent]]。

```ground:table
table: cust_change_record
fields:
  - name: status
    type: varchar
    desc: 客户变更审核状态。工作流回调写入 CheckStatus.name()，如 CUST_CHECK_PASS、CUST_CHECK_REJECT、CUST_CHECK_BACKTOCUSTOM；自行变更退回时写入动态值 returnCust-yyyy-MM-dd HH:mm。
    dict: OperApiConstants.CheckStatus
  - name: alter_mode
    type: varchar
    desc: 变更方式。AlterModeEnum，代码区分 PLAT_ALTER（平台提交变更）与 SELF_ALTER（企业自行提交变更）。
    dict: AlterModeEnum
  - name: msg_send
    type: varchar
    desc: 变更审核消息是否已发送。审核回调后写 EnableEnum.Y.name()，用于幂等去重。
    dict: EnableEnum
  - name: oper_cust_id
    type: bigint
    desc: 运营中台客户 id。变更回调通过该字段反查本地变更记录。
    dict: ""
  - name: cust_id
    type: bigint
    desc: 本地客户记录 id，关联 cust_company_info.id。
    dict: cust_company_info.id
  - name: alter_type_id
    type: varchar
    desc: 变更项记录 id 列表，逗号分隔，关联 cust_change_cfg.id，用于同步运营中台变更项。
    dict: cust_change_cfg.id
```

## 需求背景

当前语义分析未提供与 cust_change_record 相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info 企业联系人表
page_key: cust_person_info
domain: 客户中心
status: draft
aliases:
  - 联系人表
  - 企业人员表
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:ifNessaryFrzAdm
  - code_path:CustPersonApplication.java:listCompanyManagerUserId
contract_version: "0.1"
---

cust_person_info 保存企业下的联系人账号，涵盖管理员、经办人、游客，是 [[admin]]、[[person_account_status]] 与实名/人脸相关口径的落库表。注意其中 cust_build_status 为冗余字段，企业级建档状态以 [[cust_company_info]] 为准。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    type: varchar
    desc: 联系人类型。UserTypeEnum，代码使用 admin（管理员）、operator（经办人）、guest（游客）。
    dict: UserTypeEnum
  - name: status
    type: varchar
    desc: 联系人账号状态。CustPersonStatusConstant，代码可见 ADD、EFFECT、FREEZE。
    dict: CustPersonStatusConstant
  - name: phone_realname_status
    type: varchar
    desc: 手机实名状态。CustCertificationResultTypeEnum，代码可见 TO_BE_VERIFIED、AUTOMATIC_AUTHENTICATION_PASSED、MANUAL_AUTHENTICATION_PASSED。
    dict: CustCertificationResultTypeEnum
  - name: face_status
    type: varchar
    desc: 人脸认证状态。与 CustCertificationResultTypeEnum 的自动/人工认证通过值比较。
    dict: CustCertificationResultTypeEnum
  - name: real_name_result
    type: varchar
    desc: 实名认证结果。CustPersonApplication.updateFaceStatus、updateVerifyNameStatus 中写 RealNameResultEnum.VERIFIED_SUCCESS.getDictKey()。
    dict: RealNameResultEnum
```

## 需求背景

当前语义分析未提供与 cust_person_info 相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: tables/cust_certification_info.md ---
---
type: table
title: cust_certification_info 认证核查信息表
page_key: cust_certification_info
domain: 客户中心
status: draft
aliases:
  - 认证信息表
  - 核查信息表
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
  - code_path:CustPersonApplication.java:getFaceVerifyQueryVideoDTO
contract_version: "0.1"
---

cust_certification_info 保存自动/人工核查的结果与原始数据，是 [[auto_verify]]、[[certification_verify_result]] 与口径 [[face_verify_passed]] 的落库表。自动核查写入 auto_verify_status 与 auto_verify_data，人工核查写入 manual_verify_status。

```ground:table
table: cust_certification_info
fields:
  - name: auto_verify_status
    type: varchar
    desc: 自动核查结果。FaceVerifyController.isFaceVerifyPassed 与 CustCertificationResultTypeEnum.AUTOMATIC_AUTHENTICATION_PASSED 比较。
    dict: CustCertificationResultTypeEnum
  - name: manual_verify_status
    type: varchar
    desc: 人工核查结果。FaceVerifyController.isFaceVerifyPassed 与 CustCertificationResultTypeEnum.MANUAL_AUTHENTICATION_PASSED 比较。
    dict: CustCertificationResultTypeEnum
  - name: auto_verify_data
    type: text
    desc: 自动核查原始数据 JSON。CustPersonApplication.getFaceVerifyQueryVideoDTO 从该字段反序列化 VerifyResultQueryResp。
    dict: ""
```

## 需求背景

当前语义分析未提供与 cust_certification_info 相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: tables/cust_auth_application.md ---
---
type: table
title: cust_auth_application 客户产品开通申请表
page_key: cust_auth_application
domain: 客户中心
status: draft
aliases:
  - 产品开通申请
  - 开通申请表
oid: 1
scope:
  databases: [cust]
sources:
  - db:open_status 实测取值 NOT_OPENED、OPENING、OPENED
contract_version: "0.1"
---

cust_auth_application 记录客户产品开通申请的流程数据。本页仅纳入已由 DB 实测确认的字段 open_status；其余字段在本次语义分析中无证据，暂不纳入。

```ground:table
table: cust_auth_application
fields:
  - name: open_status
    type: varchar
    desc: 客户产品开通状态。DB 实测取值 NOT_OPENED、OPENING、OPENED。
    dict: 无枚举（DB 字面量）
```

## 需求背景

当前语义分析未提供与 cust_auth_application 相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: processes/company_build_status.md ---
---
type: process
title: 企业建档/认证状态机
page_key: company_build_status
domain: 客户中心
status: draft
aliases:
  - 建档状态流转
  - cust_build_status 流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMsgSend
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
---

企业建档/认证状态机描述 [[cust_company_info]].cust_build_status 在邀请录入、客户确认、运营中台审核回调之间的流转，是 [[build]] 术语的落地过程。状态来源为 CustBuildStatusEnum（code_enum）。

```ground:process
name: 企业建档/认证状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中/建档中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败
    source: code_enum
  - value: CUST_CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证客户录入提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMsgSend
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台审核/客户确认提交
    to: CUST_BUILDING
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: 运营中台审核退回/待客户确认
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_CONFIRM_AWAIT
    event: CUST_CHECK_CHECKING 回调
    to: CUST_BUILDING
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_BACKTOCUSTOM 回调
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_PASS 回调
    to: BUILD_SUCCESS
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
  - from: CUST_BUILDING
    event: CUST_CHECK_REJECT 回调
    to: BUILD_FAIL
    evidence: code_path:CustStatusCommitProcessor.java:checkMessage
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: processes/cust_change_check.md ---
---
type: process
title: 客户变更审核状态机
page_key: cust_change_check
domain: 客户中心
status: draft
aliases:
  - 变更审核流转
  - cust_change_record.status 流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
---

客户变更审核状态机描述 [[cust_change_record]].status 在运营中台审核回调下的流转，是 [[back_to_custom]]、[[reject]] 术语在变更路径上的落地过程。状态来源为 OperApiConstants.CheckStatus（code_const）。

```ground:process
name: 客户变更审核状态机
field: cust_change_record.status
states:
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_const
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_const
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_const
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户确认
    source: code_const
  - value: returnCust-yyyy-MM-dd HH:mm
    label: 退回客户（自行变更路径动态状态）
    source: code_const
transitions:
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核通过
    to: CUST_CHECK_PASS
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 运营中台审核拒绝
    to: CUST_CHECK_REJECT
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 运营中台退回待客户确认
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
  - from: CUST_CHECK_CHECKING
    event: 审核意见包含“退回”且 alterMode=SELF_ALTER
    to: returnCust-yyyy-MM-dd HH:mm
    evidence: code_path:CustStatusCommitProcessor.java:changeMessage
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: processes/certification_verify_result.md ---
---
type: process
title: 自动/人工认证结果状态机
page_key: certification_verify_result
domain: 客户中心
status: draft
aliases:
  - 核查结果流转
  - 自动人工认证流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
  - code_path:CustPersonApplication.java:updateVerifyNameStatus
contract_version: "0.1"
---

自动/人工认证结果状态机描述 [[cust_certification_info]] 的 auto_verify_status 与 manual_verify_status 从待认证到通过的流转，是 [[auto_verify]] 术语的落地过程。状态来源为 CustCertificationResultTypeEnum（code_const）。

```ground:process
name: 自动/人工认证结果状态机
field: cust_certification_info.auto_verify_status / cust_certification_info.manual_verify_status
states:
  - value: TO_BE_VERIFIED
    label: 待认证
    source: code_const
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动认证通过
    source: code_const
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工认证通过
    source: code_const
transitions:
  - from: TO_BE_VERIFIED
    event: 自动核查通过
    to: AUTOMATIC_AUTHENTICATION_PASSED
    evidence: code_path:FaceVerifyController.java:isFaceVerifyPassed
  - from: TO_BE_VERIFIED
    event: 人工审核通过
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: code_path:CustPersonApplication.java:updateVerifyNameStatus
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: processes/person_account_status.md ---
---
type: process
title: 联系人账号状态机
page_key: person_account_status
domain: 客户中心
status: draft
aliases:
  - 联系人状态流转
  - 管理员状态流转
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:ifNessaryFrzAdm
contract_version: "0.1"
---

联系人账号状态机描述 [[cust_person_info]].status 在管理员生效/冻结等动作下的流转，与 [[admin]]、[[available_admin]] 口径配合使用。状态来源为 CustPersonStatusConstant（code_const）。

```ground:process
name: 联系人账号状态机
field: cust_person_info.status
states:
  - value: ADD
    label: 新增/待生效
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_const
  - value: FREEZE
    label: 冻结
    source: code_const
transitions:
  - from: ADD
    event: 保存法人作为管理员
    to: EFFECT
    evidence: code_path:CustPersonApplication.java:ifNessaryFrzAdm
  - from: EFFECT
    event: 管理员变更/手机号变更冻结旧管理员
    to: FREEZE
    evidence: code_path:CustPersonApplication.java:ifNessaryFrzAdm
```

## 需求背景

当前语义分析未提供与本状态机相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/face_verify_passed.md ---
---
type: caliber
title: 人脸认证通过
page_key: face_verify_passed
domain: 客户中心
status: draft
aliases:
  - isFaceVerifyPassed
  - 人脸核查通过
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
contract_version: "0.1"
---

人脸认证通过口径用于判定一次人脸核查是否成功：自动核查或人工核查任一通过即视为通过。落在 [[cust_certification_info]] 上，与 [[auto_verify]] 术语边界一致（人脸状态另有 cust_person_info.face_status）。

```ground:caliber
name: 人脸认证通过
predicate: cust_certification_info.auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED' OR cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'
scope: FaceVerifyController.isFaceVerifyPassed
evidence: code_path:FaceVerifyController.java:isFaceVerifyPassed
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/company_effect.md ---
---
type: caliber
title: 企业生效
page_key: company_effect
domain: 客户中心
status: draft
aliases:
  - listEffectCompany
  - 生效企业
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
contract_version: "0.1"
---

企业生效口径用于筛选已认证成功、业务状态生效且数据有效的企业。关联 [[cust_company_info]]、状态机 [[company_build_status]] 与术语 [[build]]。

```ground:caliber
name: 企业生效
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1'
scope: listEffectCompany / listEffectCompanyByTenantAndType
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/available_admin.md ---
---
type: caliber
title: 可用管理员
page_key: available_admin
domain: 客户中心
status: draft
aliases:
  - listCompanyManagerUserId
  - 有效管理员
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:listCompanyManagerUserId
contract_version: "0.1"
---

可用管理员口径用于管理员查询、通知与变更校验场景，只认类型为 admin 且启用标记为 Y 的联系人。关联 [[cust_person_info]]、术语 [[admin]] 与状态机 [[person_account_status]]。

```ground:caliber
name: 可用管理员
predicate: cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y'
scope: 管理员查询、通知、变更校验
evidence: code_path:CustPersonApplication.java:listCompanyManagerUserId
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/change_in_progress_block.md ---
---
type: caliber
title: 变更在途阻断
page_key: change_in_progress_block
domain: 客户中心
status: draft
aliases:
  - ADMIN_CHANGE 阻断
  - 变更中阻断
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:adminChangeSaveOrUpdate
contract_version: "0.1"
---

变更在途阻断口径用于在发起新变更前判断企业是否正处变更流程，避免并发变更。关联 [[cust_company_info]]、[[change_in_progress_block]] 与状态机 [[company_build_status]]（CUST_CHANGE 态）。

```ground:caliber
name: 变更在途阻断
predicate: cust_company_info.cust_status = 'CHANGE'
scope: adminChangeSaveOrUpdate 发起新变更前阻断
evidence: code_path:CustPersonApplication.java:adminChangeSaveOrUpdate
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/ca_open_block.md ---
---
type: caliber
title: CA开通阻断
page_key: ca_open_block
domain: 客户中心
status: draft
aliases:
  - isOpenCa 阻断
  - 建档变更中阻断
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:isOpenCa
contract_version: "0.1"
---

CA开通阻断口径用于在 isOpenCa 判断时，若企业处于建档变更流程则返回处理中提示、阻断开通。关联 [[cust_company_info]]、术语 [[e_signature]] 与状态机 [[company_build_status]]。

```ground:caliber
name: CA开通阻断
predicate: cust_company_info.cust_build_status = 'CUST_CHANGE'
scope: isOpenCa 返回变更流程处理中阻断提示
evidence: code_path:CustCompanyIfoEnchanceService.java:isOpenCa
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/change_msg_sent.md ---
---
type: caliber
title: 变更消息已发送
page_key: change_msg_sent
domain: 客户中心
status: draft
aliases:
  - isMsgNotify
  - 变更消息幂等
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:isMsgNotify
contract_version: "0.1"
---

变更消息已发送口径用于审核回调的幂等判断：同一变更记录在当前审核状态下若消息已发送（msg_send=Y）则不再重复通知。关联 [[cust_change_record]] 与状态机 [[cust_change_check]]。

```ground:caliber
name: 变更消息已发送
predicate: "cust_change_record.status = '<当前审核状态>' AND cust_change_record.msg_send = 'Y'"
scope: isMsgNotify 幂等判断
evidence: code_path:CustStatusCommitProcessor.java:isMsgNotify
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: calibers/plat_default_project.md ---
---
type: caliber
title: 运营方默认项目
page_key: plat_default_project
domain: 客户中心
status: draft
aliases:
  - setPlatClientCustProject
  - 运营方项目
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:ClientCustCommitValidatorSyncService.java:setPlatClientCustProject
contract_version: "0.1"
---

运营方默认项目口径用于在同步建档时识别运营方企业，从而走默认项目逻辑。关联 [[cust_company_info]]。

```ground:caliber
name: 运营方默认项目
predicate: "cust_company_info.cust_company_type = '[\"PLATFORM_OPERATOR_COMPANY\"]'"
scope: setPlatClientCustProject 运营方走默认项目
evidence: code_path:ClientCustCommitValidatorSyncService.java:setPlatClientCustProject
```

## 需求背景

当前语义分析未提供与本口径相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/auto_verify.md ---
---
type: concept
title: 自动审核
page_key: auto_verify
domain: 客户中心
status: draft
aliases:
  - 自动核查
  - autoVerify
  - autoMediaVerify
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:isFaceVerifyPassed
  - code_path:CustPersonApplication.java:getFaceVerifyQueryVideoDTO
contract_version: "0.1"
maps_to: cust_certification_info.auto_verify_status
also_confused_with:
  - cust_certification_info.manual_verify_status
  - cust_person_info.face_status
adjudication: boundary
---

「自动审核」在客户中心语境下指系统侧自动核查，别名包括自动核查、autoVerify、autoMediaVerify，落库到 [[cust_certification_info]] 的 auto_verify_status 与 auto_verify_data。它与人工核查（manual_verify_status）是并行结果列，也不同于联系人的人脸状态（cust_person_info.face_status）。流转见 [[certification_verify_result]]，判定口径见 [[face_verify_passed]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/workflow_check.md ---
---
type: concept
title: 工作流审核
page_key: workflow_check
domain: 客户中心
status: draft
aliases:
  - 运营中台审核
  - 工作流审核执行器
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
maps_to: cust_company_info.check_status
also_confused_with:
  - cust_change_record.status
adjudication: boundary
---

「工作流审核」指运营中台对建档提交的审核环节，结果写入 [[cust_company_info]] 的 check_status（按 CheckStatus 枚举 .name()）。它不指客户变更审核——后者写入 [[cust_change_record]].status，属于不同表的不同列，切勿混用。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/check_pass.md ---
---
type: concept
title: 审核通过
page_key: check_pass
domain: 客户中心
status: draft
aliases:
  - 通过
  - PASS
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
maps_to: "cust_company_info.check_status = 'CUST_CHECK_PASS'"
also_confused_with:
  - "cust_change_record.status = 'CUST_CHECK_PASS'"
  - RtfState.PASS
adjudication: synonym
---

「审核通过」在运营中台回调中映射为 CheckStatus.CUST_CHECK_PASS，随后按业务写企业侧（[[cust_company_info]].check_status）或变更侧（[[cust_change_record]].status）。同名常量出现在两张表中含义不同，需按落库对象区分。运营中台 rtfState 的通过态也映射到该常量。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/reject.md ---
---
type: concept
title: 拒绝
page_key: reject
domain: 客户中心
status: draft
aliases:
  - 驳回
  - REJECT
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
maps_to: "cust_company_info.check_status = 'CUST_CHECK_REJECT'"
also_confused_with:
  - "cust_change_record.status = 'CUST_CHECK_REJECT'"
  - "rtfState 包含‘拒绝’"
adjudication: synonym
---

「拒绝/驳回」映射为 CheckStatus.CUST_CHECK_REJECT，按业务写企业侧或变更侧。与「审核通过」类似，同名常量在 [[cust_company_info]] 与 [[cust_change_record]] 中出现，需要按落库对象区分；此外 CustAuthValidatorProcessor 对 rtfState 文本包含「拒绝」的情形会直接 return，属流程侧分支而非落库值。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/back_to_custom.md ---
---
type: concept
title: 退回
page_key: back_to_custom
domain: 客户中心
status: draft
aliases:
  - 退回客户
  - BACKTOCUSTOM
  - returnCust
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:changeMessage
contract_version: "0.1"
maps_to: "cust_change_record.status = 'CUST_CHECK_BACKTOCUSTOM'"
also_confused_with:
  - "动态状态 returnCust-yyyy-MM-dd HH:mm"
adjudication: boundary
---

「退回」有两类落库：标准退回客户确认为 [[cust_change_record]].status = CUST_CHECK_BACKTOCUSTOM；企业自行变更（alterMode=SELF_ALTER）且审核意见含「退回」时，写入动态值 returnCust-yyyy-MM-dd HH:mm。两者语义相近但取值形态不同，流转见 [[cust_change_check]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/build.md ---
---
type: concept
title: 建档
page_key: build
domain: 客户中心
status: draft
aliases:
  - 认证
  - 企业认证
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustStatusCommitProcessor.java:checkMessage
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status
also_confused_with:
  - cust_person_info.cust_build_status
adjudication: boundary
---

「建档/认证」统一指企业级建档状态 [[cust_company_info]].cust_build_status，取值来自 CustBuildStatusEnum，流转见 [[company_build_status]]。注意 [[cust_person_info]] 上存在同名字段 cust_build_status，属联系人维度的冗余字段，企业级判定应以企业主档为准。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/admin.md ---
---
type: concept
title: 管理员
page_key: admin
domain: 客户中心
status: draft
aliases:
  - 企业管理员
  - admin
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustPersonApplication.java:listCompanyManagerUserId
contract_version: "0.1"
maps_to: "cust_person_info.user_type = 'admin'"
also_confused_with:
  - "cust_person_info.user_type = 'operator'"
  - "cust_person_info.user_type = 'guest'"
adjudication: boundary
---

「管理员」由 [[cust_person_info]].user_type = admin 标识，与经办人（operator）、游客（guest）同列区分。管理员查询/通知/校验的可口径见 [[available_admin]]，账号状态流转见 [[person_account_status]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: concepts/e_signature.md ---
---
type: concept
title: 电子签章
page_key: e_signature
domain: 客户中心
status: draft
aliases:
  - CA开通
  - CFCA
  - 上上签
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:isOpenCa
contract_version: "0.1"
maps_to: cust_company_info.need_register_ca
also_confused_with:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
adjudication: boundary
---

「电子签章」相关字段都在 [[cust_company_info]]：need_register_ca 表示是否需要开通（Y/N/P），ca_register_status 表示 CFCA/电子签章的实际开通状态，bs_register_status 表示上上签的实际开通状态。三者不可混用——「需不需要」与「通没通」是不同问题，供应商也有 CFCA 与上上签之分。开通阻断口径见 [[ca_open_block]]。

## 需求背景

当前语义分析未提供与本概念相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---FILE: rules/auto_check_pass_required.md ---
---
type: rule
title: 自动审核结果必须为自动认证通过才继续
page_key: auto_check_pass_required
domain: 客户中心
status: draft
aliases:
  - autoCheckMsg 阻断
  - 自动核查前置校验
oid: 1
scope:
  databases: [cust]
sources:
  - code_path:FaceVerifyController.java:getFaceQrCodeByCertificationNo
contract_version: "0.1"
---

该规则在获取人脸二维码前做前置校验：若自动核查结果不是自动认证通过，则抛出 autoCheckMsg 阻断后续流程。作用于 [[cust_certification_info]].auto_verify_status，与 [[auto_verify]] 术语及 [[face_verify_passed]] 口径相关。

```ground:rule
name: 自动审核结果必须为自动认证通过才继续
content: getFaceQrCodeByCertificationNo 中调用 verifyPersonOCR，若 autoCheckResult 不等于 AUTOMATIC_AUTHENTICATION_PASSED 则抛出 autoCheckMsg。
impact: 阻断后续人脸二维码与建档流程。
field_targets:
  - cust_certification_info.auto_verify_status
evidence: code_path:FaceVerifyController.java:getFaceQrCodeByCertificationNo
```

## 需求背景

当前语义分析未提供与本规则相关的 reqdoc 主张，本页暂无需求背景锚点。

## 版本演进

暂无 document_claim（未证实）主张。
---END FILE---

---REVIEW: rule | 规则清单截断---
语义分析 rules 数组除首条（自动审核结果必须为自动认证通过才继续）外被截断，仅见一个未闭合对象起始符 `{`，无字段内容。其余规则未产出页面，待补充完整证据后追加。
---END REVIEW---

---REVIEW: table | scope.databases 物理库名无证据---
语义分析未给出各表的物理库名，本批 table/concept 页 frontmatter 的 scope.databases 统一填 `cust` 为占位，尚缺 [DB] 证据证实，待确认后统一回改。
---END REVIEW---

---REVIEW: table | 字段类型非逐字证据---
各表 fields 的 type（varchar/bigint/text）依据取值形态推断，语义分析未直接给出 DDL 类型；desc/dict 均为证据逐字。类型待 DDL 佐证后校正。
---END REVIEW---