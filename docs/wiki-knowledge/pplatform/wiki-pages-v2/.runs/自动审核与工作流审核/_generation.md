---FILE: tables/cust_company_info.md ---
---
type: table
title: "cust_company_info 企业建档主表"
page_key: "tables/cust_company_info"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业建档主表"
  - "企业信息表"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
  - "code_path:CustCompanyIfoEnchanceService.java:listEffectCompany,listEffectCompanyByTenantAndType"
  - "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate"
  - "code_path:CustSyncEventProvider.java:onEvent"
  - "code_path:CustValidatorProcessor.java:validate"
contract_version: "0.1"
---

`cust_company_info` 是企业客户从建档、认证到变更、注销全生命周期的主表。准入流程上的两个状态字段互不相同：`check_status` 记录单次工作流审核结论，`cust_build_status` 记录认证/建档的整体进度；企业生命周期则另由 `cust_status` 表达。三个字段的取值域与语义边界见 [[concepts/check_status]]、[[concepts/build_status]] 与 [[concepts/admission]]。

本表是 [[processes/company_build_status_machine]] 与 [[processes/workflow_check_status_machine]] 两个状态机的载体字段所在表，也是 [[calibers/effect_company]]（已生效企业口径）与 [[calibers/change_in_flight_block]]（变更在途阻断）的判定对象。

## 需求背景

需求文档要求企业准入必须经过审核，驳回后企业可修改信息重新提交，且企业状态按「待提交 → 审核中 → 已通过」流转、驳回后回到可再提交态。该主张与代码一致，业务叙述与双源证据见 [[processes/company_build_status_machine]]。变更审核通过/驳回后需通知企业，落库位置在 [[tables/cust_change_record]]。

## 版本演进

- 工作流回调的落库入口在演进中发生过切换：通过/拒绝由拉取式处理器处理，中间状态由事件提供者落库，见 [[rules/workflow_callback_routing]]。
- 旧状态处理器 `CustStatusCommitProcessor` 已标注 `@Deprecated`，其状态流转逻辑仅供参考，见 [[rules/legacy_status_processor_deprecated]]。
- 审核轨迹字段的填充规则（不同 `identify_style` 取不同条历史）见 [[rules/audit_track_fetch]] 与 [[calibers/callback_audit_track_fetch]]。
- 本表还参与统一社会信用代码一致性校验，阻断错误企业回调，见 [[rules/social_unified_code_check]]。

```ground:table
table: cust_company_info
fields:
  - name: check_status
    meaning: "企业建档/变更的工作流审核状态，由运营中台回调 RtfState.getCheckStaus().name() 写入，取值 CUST_CHECK_PASS/CUST_CHECK_REJECT/CUST_CHECK_BACKTOCUSTOM/CUST_CHECK_CHECKING"
    evidence: "code"
  - name: cust_build_status
    meaning: "企业认证/建档状态，由运营中台审核结果驱动流转（CustBuildStatusEnum）"
    evidence: "code"
  - name: identify_style
    meaning: "建档/认证方式，决定审核轨迹取数与状态流转分支：INVITE_AGW(平台录入)、INVITE(客户录入)、SELF(自主认证)、SIMPLE(简易认证)"
    evidence: "code"
  - name: cust_status
    meaning: "企业客户状态：EFFECT 生效、CHANGE 变更中、WRITEOFF 注销、FAILURE 失效、ADD"
    evidence: "code"
  - name: remark
    meaning: "变更审核回调写入的拒绝/退回原因（rtfComment）"
    evidence: "code"
```

相关：[[processes/company_build_status_machine]]、[[processes/workflow_check_status_machine]]、[[calibers/effect_company]]、[[concepts/build_status]]。

---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: "cust_change_record 企业变更记录表"
page_key: "tables/cust_change_record"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业变更记录表"
  - "变更记录表"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:changeMessage"
  - "code_path:CustStatusCommitProcessor.java:isMsgNotify"
  - "code_path:CustStatusCommitProcessor.java:getChangeRecord"
contract_version: "0.1"
---

`cust_change_record` 记录企业每一次变更申请及其审核结论，是变更审核链路的落地表。变更审核状态的流转见 [[processes/change_record_check_machine]]。本表以 `oper_cust_id`（运营中台客户 id）为回调查询依据，回调侧存在「最多轮询 15 次、每次间隔 1s」的回查等待口径，见 [[calibers/change_record_polling]]。

本表与 [[tables/cust_company_info]] 的关系：企业主表的 `cust_status` 表达「变更中」这类生命周期状态，而本表的 `status` 只表达某一条变更申请的审核结论，二者不可混用（边界见 [[concepts/check_status]]）。

## 需求背景

需求文档要求企业变更须经审核，审核通过后变更生效，驳回则记录状态为已驳回并通知企业。该主张已由代码印证，业务叙述与双源证据见 [[processes/change_record_check_machine]]。

## 版本演进

- 变更结果消息的发送采用「弱失败 + 去重」策略：消息发送异常不影响主流程，重入回调时依据本表 `msg_send` 去重，见 [[rules/message_send_weak_failure_dedup]] 与 [[calibers/callback_msg_idempotent]]。
- 退回场景下 `status` 会写入 `returnCust-yyyy-MM-dd HH:mm` 这类非枚举动态值，枚举化的状态口径不再完整覆盖该分支，见 [[processes/change_record_check_machine]]。
- 变更消息逻辑的原处理器 `CustStatusCommitProcessor` 已废弃，新链路为准，见 [[rules/legacy_status_processor_deprecated]]。

```ground:table
table: cust_change_record
fields:
  - name: status
    meaning: "变更记录审核状态，取值同 CheckStatus；退回场景写入动态值 returnCust-yyyy-MM-dd HH:mm"
    evidence: "code"
  - name: msg_send
    meaning: "变更结果消息是否已发送（EnableEnum.Y/N），用于回调幂等去重"
    evidence: "code"
  - name: alter_mode
    meaning: "变更方式：PLAT_ALTER 平台提交变更 / SELF_ALTER 企业自行提交变更（AlterModeEnum）"
    evidence: "code"
  - name: oper_cust_id
    meaning: "运营中台客户id，回调查询变更记录的主键依据"
    evidence: "code"
  - name: need_cust_confirm
    meaning: "是否需要客户确认"
    evidence: "code"
  - name: alter_type_id
    meaning: "变更项记录id，逗号分隔，关联 cust_change_cfg"
    evidence: "code"
```

相关：[[processes/change_record_check_machine]]、[[calibers/callback_msg_idempotent]]、[[rules/message_send_weak_failure_dedup]]。

---END FILE---

---FILE: tables/cust_certification_info.md ---
---
type: table
title: "cust_certification_info 企业核查认证信息表"
page_key: "tables/cust_certification_info"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业核查认证信息表"
  - "核查认证表"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:autoVerify"
  - "code_path:AutoVerifyController.java:saveManual"
  - "code_path:AutoVerifyController.java:getFaceQrCodeByCertificationNo"
  - "code_path:FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
---

`cust_certification_info` 承载准入前的资料/身份核查结果：自动核查（OCR、人脸、影像）与人工核查各自一条状态与说明，自动核查明细以 JSON 原文留存。该表是 [[processes/certification_verify_machine]] 的载体，也是 [[concepts/auto_verify]] 与 [[concepts/manual_verify]] 两个术语所指对象的落库位置。

需要强调边界：本表的核查结论（`auto_verify_status` / `manual_verify_status`）**不是**运营中台的工作流审核结论；前者是准入审核前的核查环节，后者落在 [[tables/cust_company_info]] 的 `check_status`。核查方式的二选一分支见 [[calibers/auto_verify_type_branch]]。

## 需求背景

需求文档称「自动审核通过后自动通过准入并更新企业状态为已通过」，以及「需人工审核时进入人工审核队列」。两条主张在现有代码链路中均未被证实：自动核查接口只触发核查流程，未见写 `cust_status`/`cust_build_status` 为已通过；人工审核只有提交接口，未见队列结构与消费逻辑。详见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]] 的版本演进说明。(document_claim，未证实)

## 版本演进

- 自动核查按 `checkType` 分支到信息核查或影像核查两条实现，见 [[calibers/auto_verify_type_branch]]。
- 人脸核验以 `face_business_no` 关联业务流水，二维码取码入口在自动核查通过后即抛异常拒绝重复取码，见 [[processes/certification_verify_machine]]。
- 人工核查与运营中台工作流审批人是两个不同角色，不可互相代入，见 [[concepts/manual_verify]]。

```ground:table
table: cust_certification_info
fields:
  - name: auto_verify_status
    meaning: "自动核查（自动化核查）结果状态"
    evidence: "code"
  - name: manual_verify_status
    meaning: "人工核查结果状态"
    evidence: "code"
  - name: auto_verify_msg
    meaning: "自动核查结果说明/失败原因"
    evidence: "code"
  - name: auto_verify_data
    meaning: "自动核查明细JSON原文，含人脸核验结果 FaceVerifyResp.videoPath"
    evidence: "code"
  - name: manual_verify_msg
    meaning: "人工核查结果说明"
    evidence: "code"
  - name: face_business_no
    meaning: "人脸核验业务流水号"
    evidence: "code"
  - name: certification_type
    meaning: "核查/认证类型（如 LEGAL_OCR、法人OCR）"
    evidence: "code"
```

相关：[[processes/certification_verify_machine]]、[[concepts/auto_verify]]、[[concepts/manual_verify]]。

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: "cust_person_info 企业联系人信息表"
page_key: "tables/cust_person_info"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业联系人信息表"
  - "联系人表"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustPersonApplication.java:checkBeforeSave,updateAuthorAndApply"
  - "code_path:CustAuthValidatorProcessor.java:validate"
contract_version: "0.1"
---

`cust_person_info` 保存企业侧联系人及其实名、人脸认证结果，并以 `user_type` 区分管理员、经办人与游客。管理员在企业内唯一，是变更提交与权限判定的前置条件，口径见 [[calibers/company_admin_unique_check]]，退回豁免见 [[rules/admin_unique_check_reject_exemption]]。

## 需求背景

需求文档中的「企业修改信息后重新提交」实际上要求联系人信息在驳回/退回后仍可再次提交，因此审核回调侧对退回、拒绝、补充三类场景豁免了管理员信息唯一性校验，避免回传被阻断，见 [[rules/admin_unique_check_reject_exemption]]。

## 版本演进

- 管理员的唯一性判定口径从「保存时校验」扩展到「更新授权与申请时校验」，两处共用同一 predicate，见 [[calibers/company_admin_unique_check]]。
- 实名与人脸认证结果字段的取值域与核查状态机共用同一枚举族，见 [[processes/certification_verify_machine]] 与 [[concepts/auto_verify]]。

```ground:table
table: cust_person_info
fields:
  - name: phone_realname_status
    meaning: "手机/实名状态，取值 CustCertificationResultTypeEnum：TO_BE_VERIFIED / AUTOMATIC_AUTHENTICATION_PASSED / MANUAL_AUTHENTICATION_PASSED"
    evidence: "code"
  - name: real_name_result
    meaning: "实名认证结果，VERIFIED_SUCCESS 表示通过（RealNameResultEnum）"
    evidence: "code"
  - name: face_status
    meaning: "人脸认证结果，取值同 CustCertificationResultTypeEnum"
    evidence: "code"
  - name: user_type
    meaning: "联系人类型：admin 管理员 / operator 经办人 / guest 游客（UserTypeEnum）"
    evidence: "code"
  - name: company_type
    meaning: "客户角色（CustCompanyTypeEnum，如 CORE/SUPPLIER/FINANCE/PLATFORM_OPERATOR_COMPANY）"
    evidence: "code"
```

相关：[[calibers/company_admin_unique_check]]、[[rules/admin_unique_check_reject_exemption]]、[[processes/certification_verify_machine]]。

---END FILE---

---FILE: processes/company_build_status_machine.md ---
---
type: process
title: "企业建档认证状态机"
page_key: "processes/company_build_status_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "建档状态流转"
  - "认证状态流转"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
contract_version: "0.1"
---

企业建档认证状态机描述 `cust_company_info.cust_build_status` 的取值与流转：从初始待提交，到客户确认、中台审核中，最终落到建档成功或失败；已生效企业的后续变更则进入「变更中」。该字段与单次工作流审核结论 `check_status` 不是同一维度，边界见 [[concepts/build_status]] 与 [[concepts/check_status]]。

## 需求背景

需求文档主张：企业状态流转为「待提交 → 审核中 → 已通过」，「已驳回 → 待提交」，即驳回后企业可修改信息重新提交。该主张与代码一致，代码依据为 `CustStatusCommitProcessor.java:checkMessage`：`CUST_CHECK_REJECT` 落 `BUILD_FAIL`，`CUST_CHECK_BACKTOCUSTOM` 落 `CUST_CONFIRM_AWAIT`，从而允许重新提交。

驳回后的展示口径与 [[tables/cust_company_info]] 的 `cust_build_status` 直接相关；审核通过/拒绝的落库入口切换见 [[rules/workflow_callback_routing]]。

## 版本演进

- 状态流转的原实现类 `CustStatusCommitProcessor` 已 `@Deprecated`，本页流转仅作参考，新链路以拉取式处理器为准，见 [[rules/legacy_status_processor_deprecated]] 与 [[rules/workflow_callback_routing]]。
- 平台录入（`INVITE_AGW`）存在专门的退回分支，见本页 transitions；与之对应的审核轨迹取数口径见 [[calibers/callback_audit_track_fetch]]。
- 已生效企业的「变更中」状态会阻断新的变更提交，见 [[calibers/change_in_flight_block]]。

```ground:process
name: 企业建档认证状态机
field: cust_company_info.cust_build_status
states:
  - value: "INIT"
    label: "初始/待提交"
    source: "code_enum"
  - value: "CUST_CONFIRM_AWAIT"
    label: "待客户确认"
    source: "code_enum"
  - value: "CUST_BUILDING"
    label: "认证审核中（运营中台审核）"
    source: "code_enum"
  - value: "BUILD_SUCCESS"
    label: "认证/建档成功"
    source: "code_enum"
  - value: "BUILD_FAIL"
    label: "认证/建档失败（拒绝）"
    source: "code_enum"
  - value: "CUST_CHANGE"
    label: "变更中"
    source: "code_enum"
transitions:
  - from: "CUST_CONFIRM_AWAIT"
    event: "客户提交、运营中台审核中(CUST_CHECK_CHECKING)"
    to: "CUST_BUILDING"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台退回待客户确认(CUST_CHECK_BACKTOCUSTOM)"
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台审核通过(CUST_CHECK_PASS)"
    to: "BUILD_SUCCESS"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "运营中台审核拒绝(CUST_CHECK_REJECT)"
    to: "BUILD_FAIL"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
  - from: "CUST_BUILDING"
    event: "平台录入(INVITE_AGW)审核退回待客户确认"
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage"
reqdoc_anchors:
  - claim: "审核驳回则企业状态置为已驳回，企业修改信息后重新提交"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage + reqdoc:company-reject-to-fail-resubmit"
  - claim: "企业状态流转：待提交 → 审核中 → 已通过；已驳回 → 待提交"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage + reqdoc:company-status-flow"
```

相关：[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]、[[concepts/build_status]]、[[calibers/effect_company]]。

---END FILE---

---FILE: processes/workflow_check_status_machine.md ---
---
type: process
title: "工作流审核状态机"
page_key: "processes/workflow_check_status_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "审核状态流转"
  - "check_status 状态机"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - "code_path:CustStatusCommitProcessor.java:process(RtfState.getByDesc->getCheckStaus)"
  - "code_path:CustStatusCommitProcessor.java:checkMessage(CUST_CHECK_CHECKING && CUST_CONFIRM_AWAIT -> CUST_BUILDING)"
contract_version: "0.1"
---

工作流审核状态机描述 `cust_company_info.check_status` 的四个取值及其流转。回调侧以运营中台的 `RtfState`（中文描述，如通过/拒绝/退回客户）解读事件，落库前统一转成 `CheckStatus` 枚举名，术语映射见 [[concepts/check_status]]。本状态机与 [[processes/company_build_status_machine]] 联动：`check_status` 的结论驱动 `cust_build_status` 进度。

## 需求背景

企业准入须经运营中台工作流审核，审核「通过」后企业进入建档成功，「拒绝」后进入失败，「退回客户」则回到待客户确认并由客户修改后重新提交。这是 [[processes/company_build_status_machine]] 中需求主张在本状态机上的对应实现。

## 版本演进

- 本状态机的写入入口分两路：通过/拒绝由拉取式处理器完成，中间状态由同步事件提供者落库，见 [[rules/workflow_callback_routing]]。
- 执行器注释声称「仅处理拒绝」，但实现同时处理通过与拒绝，阅读时以代码为准，见 [[rules/workflow_processor_scope_comment_mismatch]]。
- 回调会校验统一社会信用代码一致性，不一致直接阻断，见 [[rules/social_unified_code_check]]。
- 审核轨迹（审批人）取数按 `identify_style` 分支，见 [[calibers/callback_audit_track_fetch]] 与 [[rules/audit_track_fetch]]。
- 本状态机所在的原处理器已废弃，历史流转仅供参考，见 [[rules/legacy_status_processor_deprecated]]。

```ground:process
name: 工作流审核状态机
field: cust_company_info.check_status
states:
  - value: "CUST_CHECK_CHECKING"
    label: "审核中"
    source: "code_enum"
  - value: "CUST_CHECK_BACKTOCUSTOM"
    label: "退回客户确认"
    source: "code_enum"
  - value: "CUST_CHECK_PASS"
    label: "审核通过"
    source: "code_enum"
  - value: "CUST_CHECK_REJECT"
    label: "审核拒绝"
    source: "code_enum"
transitions:
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台工作流回调 rtfState=通过(RtfState.PASS)"
    to: "CUST_CHECK_PASS"
    evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台工作流回调 rtfState=拒绝(RtfState.REJECT)"
    to: "CUST_CHECK_REJECT"
    evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台回调 rtfState=退回客户/提交客户确认（CheckStatus.CUST_CHECK_BACKTOCUSTOM）"
    to: "CUST_CHECK_BACKTOCUSTOM"
    evidence: "code_path:CustStatusCommitProcessor.java:process(RtfState.getByDesc->getCheckStaus)"
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "客户确认后重新提交，运营中台回调 rtfState=审核中"
    to: "CUST_CHECK_CHECKING"
    evidence: "code_path:CustStatusCommitProcessor.java:checkMessage(CUST_CHECK_CHECKING && CUST_CONFIRM_AWAIT -> CUST_BUILDING)"
```

相关：[[tables/cust_company_info]]、[[processes/company_build_status_machine]]、[[concepts/check_status]]、[[rules/workflow_callback_routing]]。

---END FILE---

---FILE: processes/change_record_check_machine.md ---
---
type: process
title: "变更记录审核状态机"
page_key: "processes/change_record_check_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "变更审核流转"
  - "cust_change_record.status 状态机"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:changeMessage(recordDO.setStatus + setMsgSend=Y)"
  - "code_path:CustStatusCommitProcessor.java:changeMessage"
  - "code_path:CustStatusCommitProcessor.java:changeMessage(checkAdvice.contains(\"退回\") && SELF_ALTER)"
contract_version: "0.1"
---

变更记录审核状态机描述 `cust_change_record.status` 的流转。与工作流审核状态机不同，本状态机在退回场景会写入 `returnCust-yyyy-MM-dd HH:mm` 这类按分钟动态生成的非枚举值，因此基于枚举的状态口径不能完整覆盖该分支，需以 [[tables/cust_change_record]] 的实际值为准。

## 需求背景

需求文档主张：企业变更需经审核，审核通过后变更生效，驳回则记录状态为已驳回并通知。该主张与代码一致：`CustStatusCommitProcessor.java:changeMessage` 按 `CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 更新 `cust_change_record.status`，并在同处写入 `msg_send=Y` 并发起短信/站内信通知。

通知的幂等与弱失败策略见 [[rules/message_send_weak_failure_dedup]] 与 [[calibers/callback_msg_idempotent]]；回查等待见 [[calibers/change_record_polling]]。

## 版本演进

- 退回分支从「统一枚举」演化为「按分钟动态值」，动态值仅在 `rtfComment` 含「退回」且变更方式为企业自行提交（`SELF_ALTER`）时写入，见本页 transitions。
- 本状态机的变更消息逻辑所在处理器已 `@Deprecated`，新链路替代，见 [[rules/legacy_status_processor_deprecated]]。

```ground:process
name: 变更记录审核状态机
field: cust_change_record.status
states:
  - value: "CUST_CHECK_PASS"
    label: "审核通过"
    source: "code_enum"
  - value: "CUST_CHECK_REJECT"
    label: "审核拒绝"
    source: "code_enum"
  - value: "CUST_CHECK_BACKTOCUSTOM"
    label: "待客户确认"
    source: "code_enum"
  - value: "returnCust-yyyy-MM-dd HH:mm"
    label: "退回（自行变更场景，按分钟动态生成）"
    source: "code_enum"
transitions:
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "运营中台变更审核通过(CUST_CHECK_PASS)"
    to: "CUST_CHECK_PASS"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage(recordDO.setStatus + setMsgSend=Y)"
  - from: "CUST_CHECK_BACKTOCUSTOM"
    event: "运营中台变更审核拒绝(CUST_CHECK_REJECT)"
    to: "CUST_CHECK_REJECT"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage"
  - from: "CUST_CHECK_CHECKING"
    event: "运营中台退回待客户确认(CUST_CHECK_BACKTOCUSTOM)"
    to: "CUST_CHECK_BACKTOCUSTOM"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage"
  - from: "CUST_CHECK_CHECKING"
    event: "rtfComment 含『退回』且变更为企业自行提交(SELF_ALTER)"
    to: "returnCust-yyyy-MM-dd HH:mm"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage(checkAdvice.contains(\"退回\") && SELF_ALTER)"
reqdoc_anchors:
  - claim: "企业变更需经审核，审核通过后变更生效，驳回则记录状态为已驳回并通知"
    evidence: "code_path:CustStatusCommitProcessor.java:changeMessage + reqdoc:company-change-audit-notify"
```

相关：[[tables/cust_change_record]]、[[calibers/callback_msg_idempotent]]、[[rules/message_send_weak_failure_dedup]]。

---END FILE---

---FILE: processes/certification_verify_machine.md ---
---
type: process
title: "核查/实名认证状态机"
page_key: "processes/certification_verify_machine"
domain: "customer-onboarding"
status: draft
aliases:
  - "自动核查状态机"
  - "认证核查流转"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:getFaceQrCodeByCertificationNo(autoCheckResult != AUTOMATIC_AUTHENTICATION_PASSED 抛异常)"
  - "code_path:AutoVerifyController.java:saveManual + FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
---

核查/实名认证状态机描述 `cust_certification_info.auto_verify_status` 的取值流转，覆盖自动核查与人工核查两条通道。这是「自动审核」一词在代码中的实际落点，与运营中台的工作流审核结论不是同一环节，边界见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]]。

## 需求背景

需求文档称自动审核可自动通过准入，并可在失败时进入人工审核队列。现有代码只提供了自动核查与人工提交核查结论两个入口，未见自动写企业准入状态、也未见人工审核队列结构与消费逻辑，故相关主张在本链路中未获证实，详见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]] 的版本演进说明。(document_claim，未证实)

## 版本演进

- 自动核查按 `checkType` 分支为信息核查与影像核查两条实现路径，见 [[calibers/auto_verify_type_branch]]。
- 人脸核验二维码取码前置了「自动核查未通过即抛异常」的拦截，见本页 transitions。
- 核查结果字段族（实名、人脸、手机实名）与 [[tables/cust_person_info]] 共用同一枚举族。

```ground:process
name: 核查/实名认证状态机
field: cust_certification_info.auto_verify_status
states:
  - value: "TO_BE_VERIFIED"
    label: "待核查/待认证"
    source: "code_enum"
  - value: "AUTOMATIC_AUTHENTICATION_PASSED"
    label: "自动核查通过"
    source: "code_enum"
  - value: "MANUAL_AUTHENTICATION_PASSED"
    label: "人工核查通过"
    source: "code_enum"
transitions:
  - from: "TO_BE_VERIFIED"
    event: "自动核查(OCR/人脸/影像)结果通过"
    to: "AUTOMATIC_AUTHENTICATION_PASSED"
    evidence: "code_path:AutoVerifyController.java:getFaceQrCodeByCertificationNo(autoCheckResult != AUTOMATIC_AUTHENTICATION_PASSED 抛异常)"
  - from: "TO_BE_VERIFIED"
    event: "人工审核提交(saveManual)"
    to: "MANUAL_AUTHENTICATION_PASSED"
    evidence: "code_path:AutoVerifyController.java:saveManual + FaceVerifyController.java:isFaceVerifyPassed"
```

相关：[[tables/cust_certification_info]]、[[tables/cust_person_info]]、[[concepts/auto_verify]]、[[calibers/auto_verify_type_branch]]。

---END FILE---

---FILE: calibers/auto_verify_type_branch.md ---
---
type: caliber
title: "自动核查类型分支"
page_key: "calibers/auto_verify_type_branch"
domain: "customer-onboarding"
status: draft
aliases:
  - "checkType=INFO 分支"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:autoVerify"
contract_version: "0.1"
---

本口径决定自动核查走哪条实现：命中 `CustAutoCheckTypeEnum.INFO` 走信息核查，否则走影像核查。它解释了统计「自动核查通过率」时为何必须按 `checkType` 分类，否则两类核查口径会被混算。相关状态机见 [[processes/certification_verify_machine]]，术语见 [[concepts/auto_verify]]。

## 需求背景

需求文档把「自动审核」作为单一环节描述，但代码中存在两条核查实现，取数与耗时特征不同；对账与统计时需要按本口径拆分。

## 版本演进

- 当前为二分支结构（INFO / 非 INFO）；若后续新增核查类型，本口径的 `else` 分支会静默吞掉新类型，需要同步维护。

```ground:caliber
name: "自动核查类型分支"
predicate: "FlowAutoMediaVerifyReqDTO.checkType = 'INFO'"
scope: "AutoVerifyController.autoVerify：命中 CustAutoCheckTypeEnum.INFO 走 autoVerifyService.autoVerify(appNo)，否则走 autoMediaVerify(appNo)"
evidence: "code_path:AutoVerifyController.java:autoVerify"
```

相关：[[processes/certification_verify_machine]]、[[tables/cust_certification_info]]、[[concepts/auto_verify]]。

---END FILE---

---FILE: calibers/effect_company.md ---
---
type: caliber
title: "已生效企业口径"
page_key: "calibers/effect_company"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业有效性口径"
  - "生效企业判定"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code:code_path:CustCompanyIfoEnchanceService.java:listEffectCompany,listEffectCompanyByTenantAndType"
contract_version: "0.1"
---

本口径是企业「有效性」的统一判定：同时满足建档成功、客户状态生效、数据标识与启用标识，才被计入已生效企业。任一条件不满足（如处于变更中、已注销、已失效）都不计入。与之相对的是变更在途阻断口径 [[calibers/change_in_flight_block]]。

## 需求背景

需求文档要求企业准入通过后才可用，本口径是「已通过」在查询层面的落地判定；统计口径若漏掉 `cust_build_status` 或 `cust_status` 任一条件，会把变更中/失效企业算作生效。

## 版本演进

- 口径以 predicate 形式在多处查询复用，新增查询入口时应复用同一 predicate，避免派生口径漂移，见 [[tables/cust_company_info]]。

```ground:caliber
name: "已生效企业口径"
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = '1' AND cust_company_info.enable = 'Y'"
scope: "listEffectCompany / listEffectCompanyByTenantAndType 等企业有效性查询"
evidence: "code:code_path:CustCompanyIfoEnchanceService.java:listEffectCompany,listEffectCompanyByTenantAndType"
```

相关：[[tables/cust_company_info]]、[[processes/company_build_status_machine]]、[[concepts/build_status]]。

---END FILE---

---FILE: calibers/change_in_flight_block.md ---
---
type: caliber
title: "变更在途阻断"
page_key: "calibers/change_in_flight_block"
domain: "customer-onboarding"
status: draft
aliases:
  - "在途变更阻断"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate"
  - "code_path:CustCompanyIfoEnchanceService.java:isOpenCa"
contract_version: "0.1"
---

企业存在在途变更时，主表 `cust_status` 处于变更中状态，此时新的变更提交与部分能力（如 CA 开通）会被阻断并给出显式提示。这是「同一企业同一时刻只允许一条变更流程」的口径表达。状态载体见 [[tables/cust_company_info]]，变更记录见 [[tables/cust_change_record]]。

## 需求背景

需求文档要求变更须经审核并生效，为保持审核对象唯一，需要阻断并发的第二笔变更。

## 版本演进

- 阻断点从变更提交入口扩展到能力开通入口，两处均以同一字段值判定，见 [[processes/change_record_check_machine]]。

```ground:caliber
name: "变更在途阻断"
predicate: "cust_company_info.cust_status = 'CHANGE'"
scope: "adminChangeSaveOrUpdate 抛『有在途变更流程，请检查!』；isOpenCa 阻断『企业信息变更流程处理中』"
evidence: "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate;CustCompanyIfoEnchanceService.java:isOpenCa"
```

相关：[[tables/cust_company_info]]、[[processes/change_record_check_machine]]、[[concepts/build_status]]。

---END FILE---

---FILE: calibers/callback_msg_idempotent.md ---
---
type: caliber
title: "回调消息幂等去重"
page_key: "calibers/callback_msg_idempotent"
domain: "customer-onboarding"
status: draft
aliases:
  - "通知去重口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:isMsgNotify"
contract_version: "0.1"
---

运营中台回调可能重入，为避免同一审核结论重复发短信/站内信，发送前按「状态相同且已发送」判定跳过。该口径依赖 [[tables/cust_change_record]] 的 `msg_send` 标记，配合消息发送的弱失败策略见 [[rules/message_send_weak_failure_dedup]]。

## 需求背景

需求文档要求驳回等结果需通知企业；通知需保证「不重不漏」，重入场景以本口径去重。

## 版本演进

- 去重键由单纯状态比较演进为「状态 + 发送标记」双条件，避免同状态二次流转被误判。

```ground:caliber
name: "回调消息幂等去重"
predicate: "cust_change_record.status = 本次审核状态 AND cust_change_record.msg_send = 'Y'"
scope: "isMsgNotify 判定消息无需重复发送"
evidence: "code_path:CustStatusCommitProcessor.java:isMsgNotify"
```

相关：[[tables/cust_change_record]]、[[rules/message_send_weak_failure_dedup]]、[[processes/change_record_check_machine]]。

---END FILE---

---FILE: calibers/change_record_polling.md ---
---
type: caliber
title: "变更记录回查等待"
page_key: "calibers/change_record_polling"
domain: "customer-onboarding"
status: draft
aliases:
  - "变更记录轮询口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:getChangeRecord"
contract_version: "0.1"
---

回调到达时变更记录可能尚未落库，因此按运营中台客户 id 回查，并限定轮询次数与间隔，超时即按未取到处理。该口径决定了「回调成功但记录未更新」这一现象的边界条件。相关表见 [[tables/cust_change_record]]，状态机见 [[processes/change_record_check_machine]]。

## 需求背景

需求文档要求变更审核结果可靠回传，回查等待是为处理中台与本域写入时序差而设的工程约束。

## 版本演进

- 当前为固定次数+固定间隔的同步轮询；轮询上限一旦变化，「回调丢失」类问题的排查结论会随之改变。

```ground:caliber
name: "变更记录回查等待"
predicate: "cust_change_record.oper_cust_id = 运营中台客户id"
scope: "getChangeRecord 最多轮询15次、每次间隔1s"
evidence: "code_path:CustStatusCommitProcessor.java:getChangeRecord"
```

相关：[[tables/cust_change_record]]、[[processes/change_record_check_machine]]、[[calibers/callback_msg_idempotent]]。

---END FILE---

---FILE: calibers/company_admin_unique_check.md ---
---
type: caliber
title: "企业管理员唯一校验"
page_key: "calibers/company_admin_unique_check"
domain: "customer-onboarding"
status: draft
aliases:
  - "管理员唯一性口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustPersonApplication.java:checkBeforeSave,updateAuthorAndApply"
contract_version: "0.1"
---

同一企业、同一客户角色下，只允许一个启用状态的管理员联系人。校验在保存与更新授权/申请两处复用，命中即为冲突。字段载体见 [[tables/cust_person_info]]，退回场景的豁免见 [[rules/admin_unique_check_reject_exemption]]。

## 需求背景

需求文档要求企业管理员唯一，作为变更提交与授权判定的前置条件。

## 版本演进

- 校验入口由单点保存扩展到授权/申请链路，两处必须保持同一 predicate，否则会出现「保存拦得住、申请拦不住」的漏洞。

```ground:caliber
name: "企业管理员唯一校验"
predicate: "cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y' AND ref_cust_company_info = X AND company_type = Y AND id != 当前id"
scope: "checkBeforeSave/updateAuthorAndApply：count 必须为 0"
evidence: "code_path:CustPersonApplication.java:checkBeforeSave,updateAuthorAndApply"
```

相关：[[tables/cust_person_info]]、[[rules/admin_unique_check_reject_exemption]]。

---END FILE---

---FILE: calibers/callback_audit_track_fetch.md ---
---
type: caliber
title: "回调审核轨迹取数"
page_key: "calibers/callback_audit_track_fetch"
domain: "customer-onboarding"
status: draft
aliases:
  - "审批人取数口径"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

回填审核轨迹（审批人与审批人名称）时，取数位置随建档方式而变：平台录入取审批历史第 1 条，其他方式取最后 1 条。落库字段见 [[tables/cust_company_info]]，规则条目见 [[rules/audit_track_fetch]]。

## 需求背景

需求文档要求审核结论可溯源到操作人；由于平台录入由平台侧发起、审批历史顺序与客户自主认证相反，取数位置需要分支处理。

## 版本演进

- 分支条件绑定 `identify_style`，新增建档方式时若未归类，会默认落入「取最后 1 条」分支，需同步维护。

```ground:caliber
name: "回调审核轨迹取数"
predicate: "identify_style = 'INVITE_AGW' 取 custWkflAppHistoryList 第 1 条；否则取最后 1 条"
scope: "CustWorkflowAuditCommitProcessor 填充 checkBy/checkByName"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[tables/cust_company_info]]、[[rules/audit_track_fetch]]、[[processes/workflow_check_status_machine]]。

---END FILE---

---FILE: rules/workflow_callback_routing.md ---
---
type: rule
title: "工作流回调路由规则"
page_key: "rules/workflow_callback_routing"
domain: "customer-onboarding"
status: draft
aliases:
  - "通过拒绝走拉取处理器"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustSyncEventProvider.java:onEvent"
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

运营中台建档审核回调进入本域后被拆成两路：终态事件被同步事件提供者跳过，改由工作流审核执行器主动拉取中台数据后处理；中间状态（审核中、退回）仍由事件提供者落库。这条规则决定了「通过/拒绝」的唯一落库入口，避免重复处理。相关状态机见 [[processes/workflow_check_status_machine]]。

## 需求背景

中台回调仅携带状态描述，终态所需的审批轨迹等数据需二次拉取；因此把终态从事件通道中摘出，交由拉取式执行器完成，是保证数据完整的工程约束。

## 版本演进

- 路由方式从「事件通道全量处理」演进为「终态拉取 + 中间态事件」的双通道；排查状态未更新问题时需先确认事件属于哪一通道。

```ground:rule
name: "工作流回调路由规则"
content: "运营中台建档审核回调中，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的事件被 CustSyncEventProvider.onEvent 直接跳过，改由 CustWorkflowAuditCommitProcessor 拉取中台数据后处理；CustSyncEventProvider 只落审核中/退回等中间状态。"
impact: "决定通过/拒绝的落库入口，避免重复处理"
field_targets:
  - "cust_company_info.check_status"
  - "cust_build_status"
evidence: "code_path:CustSyncEventProvider.java:onEvent;CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[processes/workflow_check_status_machine]]、[[tables/cust_company_info]]、[[rules/workflow_processor_scope_comment_mismatch]]。

---END FILE---

---FILE: rules/workflow_processor_scope_comment_mismatch.md ---
---
type: rule
title: "工作流执行器实际处理范围与注释不一致"
page_key: "rules/workflow_processor_scope_comment_mismatch"
domain: "customer-onboarding"
status: draft
aliases:
  - "注释与实现不一致"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

执行器注释写「仅处理拒绝，中间状态不处理」，但代码的实际守卫条件是「既非通过、也非拒绝才 return」，因此通过和拒绝都会进入处理逻辑。阅读与排障时应以代码为准，不要依据注释推断处理范围。相关入口规则见 [[rules/workflow_callback_routing]]。

## 需求背景

需求文档要求审核通过后企业状态变为已通过；该能力正是由本执行器实现，注释滞后于实现。

## 版本演进

- 该差异属于历史注释未同步，尚未见修复；若后续以「按注释重构」的方式收敛，处理范围可能变化，需回归验证 [[processes/company_build_status_machine]]。

```ground:rule
name: "工作流执行器实际处理范围与注释不一致"
content: "CustWorkflowAuditCommitProcessor 注释写『仅处拒绝，中间状态不处理』，但代码判断 rtfs != RtfState.PASS && rtfs != RtfState.REJECT 才 return，实际同时处理通过和拒绝。"
impact: "注释与实现存在差异，阅读时需以代码为准"
field_targets:
  - "cust_company_info.check_status"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[processes/workflow_check_status_machine]]、[[rules/workflow_callback_routing]]。

---END FILE---

---FILE: rules/social_unified_code_check.md ---
---
type: rule
title: "统一社会信用代码一致性校验"
page_key: "rules/social_unified_code_check"
domain: "customer-onboarding"
status: draft
aliases:
  - "信用代码一致性校验"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustValidatorProcessor.java:validate"
contract_version: "0.1"
---

回调携带的统一社会信用代码必须与本地企业的 `certification_no` 一致，否则直接抛异常阻断；变更流程与来源 id 缺失的场景被显式放行。这条规则是防止串户的关键闸门，载体表见 [[tables/cust_company_info]]。

## 需求背景

中台以 sourceId 关联企业，若中台侧代码与企业绑定发生错位，会把 A 企业的审核结论写到 B 企业上，因此需要代码级一致性校验。

## 版本演进

- 放行条件（`process=change` 或 `sourceId` 为空）是后加的兼容分支，变更流程不走该校验；因此变更链路的防串户依赖其他机制，见 [[processes/change_record_check_machine]]。

```ground:rule
name: "统一社会信用代码一致性校验"
content: "运营中台回调校验：process=change 或 sourceId 为空直接放行；否则按 sourceId 查企业，回调 socialUnifiedCode 与企业 certificationNo 不一致时抛『统一信用代码不一致』。"
impact: "阻断错误企业回调"
field_targets:
  - "cust_company_info.certification_no"
evidence: "code_path:CustValidatorProcessor.java:validate"
```

相关：[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]。

---END FILE---

---FILE: rules/admin_unique_check_reject_exemption.md ---
---
type: rule
title: "管理员唯一校验的退回豁免"
page_key: "rules/admin_unique_check_reject_exemption"
domain: "customer-onboarding"
status: draft
aliases:
  - "退回场景豁免唯一校验"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustAuthValidatorProcessor.java:validate"
contract_version: "0.1"
---

回调校验链中，若 `rtfState` 含「拒绝」「退回」「补充」，校验器直接返回，不再执行管理员信息唯一性校验。这是为了让退回/补充场景的回传不被本地校验阻断，与 [[calibers/company_admin_unique_check]] 的唯一性口径配套。

## 需求背景

需求文档要求企业修改信息后重新提交；在退回/补充阶段，联系人信息可能处于中间态（尚未替换完成），若仍执行唯一校验会阻断整个回传链路。

## 版本演进

- 豁免以 `rtfState` 文案包含关系判定（含「拒绝」「退回」「补充」），而非枚举匹配；中台文案变化可能使豁免失效，需回归 [[tables/cust_person_info]] 相关校验。

```ground:rule
name: "管理员唯一校验的退回豁免"
content: "CustAuthValidatorProcessor.validate 中，rtfState 含『拒绝』『退回』『补充』时直接 return，不执行管理员信息唯一性校验。"
impact: "退回/补充场景不阻断回传"
field_targets:
  - "cust_person_info.name"
  - "cust_person_info.certification_no"
  - "cust_person_info.email"
evidence: "code_path:CustAuthValidatorProcessor.java:validate"
```

相关：[[calibers/company_admin_unique_check]]、[[tables/cust_person_info]]、[[processes/company_build_status_machine]]。

---END FILE---

---FILE: rules/message_send_weak_failure_dedup.md ---
---
type: rule
title: "消息发送弱失败与去重"
page_key: "rules/message_send_weak_failure_dedup"
domain: "customer-onboarding"
status: draft
aliases:
  - "消息弱失败"
  - "通知去重规则"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustMessageSendService.java:sendSms,isSend"
  - "code_path:CustStatusCommitProcessor.java:isMsgNotify"
contract_version: "0.1"
---

所有短信、站内信、消息发送接口均以 try-catch 包裹并仅记日志、不向上抛出；变更回调在发送前先查最近一次通知的发送标记，已发送则跳过。结果是：消息通道可用性不影响状态落库，且回调可安全重入。去重口径见 [[calibers/callback_msg_idempotent]]，标记字段见 [[tables/cust_change_record]]。

## 需求背景

需求文档要求审核结果通知企业；同时状态落库不能因为通知失败而回滚，因此把通知定义为「尽力而为 + 幂等」。

## 版本演进

- 由「发送失败即影响主流程」演进为弱失败；去重标记 `msg_send` 随之成为回调可重入的前提。

```ground:rule
name: "消息发送弱失败与去重"
content: "CustMessageSendService 所有 sendSms/sendNotice/sendMessage 均 try-catch 记录日志不抛出；变更回调发送前用 isSend()/isMsgNotify() 查询最近一次通知，已发送则跳过。"
impact: "消息失败不影响主流程，回调可重入"
field_targets:
  - "cust_change_record.msg_send"
evidence: "code_path:CustMessageSendService.java:sendSms,isSend;CustStatusCommitProcessor.java:isMsgNotify"
```

相关：[[calibers/callback_msg_idempotent]]、[[processes/change_record_check_machine]]、[[tables/cust_change_record]]。

---END FILE---

---FILE: rules/audit_track_fetch.md ---
---
type: rule
title: "审核轨迹取数规则"
page_key: "rules/audit_track_fetch"
domain: "customer-onboarding"
status: draft
aliases:
  - "审批人取数规则"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process"
contract_version: "0.1"
---

平台录入场景取审批历史第 1 条作为审批人，其他认证方式取最后 1 条，落库到企业主表的审批人与审批人名称字段。口径细节见 [[calibers/callback_audit_track_fetch]]，载体见 [[tables/cust_company_info]]。

## 需求背景

需求文档要求审核结果可追溯到操作人；不同发起方式下审批历史的方向不同，故需分支取数。

## 版本演进

- 该规则随拉取式执行器一并引入（见 [[rules/workflow_callback_routing]]）；被废弃的旧处理器不负责轨迹回填。

```ground:rule
name: "审核轨迹取数规则"
content: "平台录入(INVITE_AGW)取审批历史第 1 条作为审批人，其他认证方式取最后 1 条。"
impact: "决定 checkBy/checkByName 落库值"
field_targets:
  - "cust_company_info.check_by"
  - "check_by_name"
evidence: "code_path:CustWorkflowAuditCommitProcessor.java:process"
```

相关：[[calibers/callback_audit_track_fetch]]、[[tables/cust_company_info]]、[[processes/workflow_check_status_machine]]。

---END FILE---

---FILE: rules/legacy_status_processor_deprecated.md ---
---
type: rule
title: "旧状态处理器已废弃"
page_key: "rules/legacy_status_processor_deprecated"
domain: "customer-onboarding"
status: draft
aliases:
  - "CustStatusCommitProcessor 废弃"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:类注解"
contract_version: "0.1"
---

`CustStatusCommitProcessor` 已标注 `@Deprecated`，且其 `@DubboService` 注解被注释掉，变更消息等逻辑已由新处理器替代。因此以该类为证据的状态流转描述只能作为旁证，正式口径应以新链路为准，见 [[rules/workflow_callback_routing]]。

## 需求背景

需求文档描述的状态流转与旧实现一致，但当前运行时生效的是新链路；引用旧类结论时必须在文档中声明其旁证地位。

## 版本演进

- 从「唯一状态处理器」到「废弃旁证」：本仓库中多个页面的状态机证据源自该类，后续若新链路补齐同类分支，应把证据迁移到新处理器；迁移影响 [[processes/company_build_status_machine]]、[[processes/workflow_check_status_machine]]、[[processes/change_record_check_machine]] 三个状态机的证据可信度。

```ground:rule
name: "旧状态处理器已废弃"
content: "CustStatusCommitProcessor 标注 @Deprecated 且 @DubboService 被注释，变更消息逻辑已被新处理器替代。"
impact: "相关状态流转仅供参考，需以新链路为准"
field_targets:
  - "cust_change_record.status"
evidence: "code_path:CustStatusCommitProcessor.java:类注解"
```

相关：[[processes/change_record_check_machine]]、[[rules/workflow_callback_routing]]。

---END FILE---

---FILE: concepts/auto_verify.md ---
---
type: concept
title: "自动审核"
page_key: "concepts/auto_verify"
domain: "customer-onboarding"
status: draft
aliases:
  - "自动化核查"
  - "自动核查"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:autoVerify"
  - "code_path:AutoVerifyController.java:saveManual"
  - "code_path:FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
maps_to: "AutoVerifyService.autoVerify(信息核查)/autoMediaVerify(影像核查)，以及 cust_certification_info.auto_verify_status"
field_targets:
  - "cust_certification_info.auto_verify_status"
adjudication: "boundary"
also_confused_with:
  - "CustWorkflowAuditCommitProcessor 的工作流审核通过/拒绝"
  - "cust_company_info.check_status=CUST_CHECK_PASS"
boundary: "『自动核查』是准入审核前的资料/身份核查环节（OCR、人脸、影像），产出 auto_verify_status；『审核通过』是运营中台工作流/自动审核后的准入结论，产出 check_status=CUST_CHECK_PASS 与 cust_build_status=BUILD_SUCCESS。二者是前后置关系，不是同一值。"
---

> (document_claim，未证实) 本页版本演进包含需求文档主张，尚未在代码中得到证实。

「自动审核」在业务口语中常被当作准入结论，但在代码里它对应的是准入前置的核查环节：对 OCR、人脸、影像等资料做自动化核查，结果写入 [[tables/cust_certification_info]] 的 `auto_verify_status`。它**不是** [[concepts/check_status]]，也不等于 [[concepts/admission]]。

## 边界

`boundary`：『自动核查』是准入审核前的资料/身份核查环节（OCR、人脸、影像），产出 `auto_verify_status`；『审核通过』是运营中台工作流/自动审核后的准入结论，产出 `check_status=CUST_CHECK_PASS` 与 `cust_build_status=BUILD_SUCCESS`。二者是前后置关系，不是同一值。

相关状态机见 [[processes/certification_verify_machine]]，分支口径见 [[calibers/auto_verify_type_branch]]；与之相对的人工环节见 [[concepts/manual_verify]]。

## 需求背景

需求文档把自动审核描述为准入的自动通过条件；代码中可见的只是核查触发与核查结果落库，准入结论仍由工作流链路写入 [[tables/cust_company_info]]。

## 版本演进

- (document_claim，未证实) 需求文档称「企业准入流程中『自动审核通过』后自动通过准入并更新企业状态为已通过」。代码证据：`code_path:AutoVerifyController.java:autoVerify`——仅触发 `autoVerify`/`autoMediaVerify`，未见于本链路写 `cust_status`/`cust_build_status` 为已通过。该主张**未证实**。
- (document_claim，未证实) 需求文档称「自动审核规则：企业征信评分>=60、法人无不良信用记录、经营状态正常、行业不在黑名单」。代码证据：未在提供的 service/mapper 链路中出现征信评分/黑名单判定实现。该主张**未证实**，且不应写入任何统计口径。
- 自动核查的类型分支（信息核查 / 影像核查）已落地，见 [[calibers/auto_verify_type_branch]]。

---END FILE---

---FILE: concepts/manual_verify.md ---
---
type: concept
title: "人工审核"
page_key: "concepts/manual_verify"
domain: "customer-onboarding"
status: draft
aliases:
  - "人工核查"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:AutoVerifyController.java:saveManual"
  - "code_path:FaceVerifyController.java:isFaceVerifyPassed"
contract_version: "0.1"
maps_to: "AutoVerifyController.saveManual + cust_certification_info.manual_verify_status=MANUAL_AUTHENTICATION_PASSED"
field_targets:
  - "cust_certification_info.manual_verify_status"
adjudication: "boundary"
also_confused_with:
  - "运营中台工作流审批人审核"
boundary: "人工核查作用于单条认证影像/实名的核查结论；运营中台工作流审核作用于企业建档/变更流程结论，前者不改变 cust_build_status。"
---

> (document_claim，未证实) 本页版本演进包含需求文档主张，尚未在代码中得到证实。

「人工核查」指由人工对单条认证影像或实名结果给出核查结论，写入 [[tables/cust_certification_info]] 的 `manual_verify_status`。它与运营中台的**工作流审批人**是两类角色：前者不改变 [[tables/cust_company_info]] 的 `cust_build_status`，后者才是准入/变更结论的来源，见 [[processes/workflow_check_status_machine]]。

## 边界

`boundary`：人工核查作用于单条认证影像/实名的核查结论；运营中台工作流审核作用于企业建档/变更流程结论，前者不改变 `cust_build_status`。

自动通道见 [[concepts/auto_verify]]；核查状态机见 [[processes/certification_verify_machine]]。

## 需求背景

需求文档把人工审核描述为准入流程中的一个队列环节；代码中可见的只有人工结论提交入口，准入结论仍由工作流链路驱动。

## 版本演进

- (document_claim，未证实) 需求文档称「需人工审核时进入人工审核队列，由审核人员审核」。代码证据：`code_path:AutoVerifyController.java:saveManual`——有人工审核提交接口，但未见队列数据结构与消费逻辑。该主张**未证实**。
- 人工核查结论的枚举取值与自动核查共用同一枚举族，见 [[processes/certification_verify_machine]]。

---END FILE---

---FILE: concepts/build_status.md ---
---
type: concept
title: "建档状态"
page_key: "concepts/build_status"
domain: "customer-onboarding"
status: draft
aliases:
  - "认证状态"
  - "cust_build_status"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
contract_version: "0.1"
maps_to: "CustBuildStatusEnum"
field_targets:
  - "cust_company_info.cust_build_status"
adjudication: "boundary"
also_confused_with:
  - "客户状态 cust_status(CustStatusEnum)"
  - "审核状态 check_status(CheckStatus)"
boundary: "cust_build_status 描述认证/建档进度；cust_status 描述企业生效/变更/注销生命周期；check_status 描述单次工作流审核结论。三者取值域互不相同。"
---

「建档状态」（亦称认证状态）描述企业在准入流程中的进度：初始、待客户确认、审核中、成功、失败、变更中。取值域由 `CustBuildStatusEnum` 定义，流转见 [[processes/company_build_status_machine]]。

## 边界

`boundary`：`cust_build_status` 描述认证/建档进度；`cust_status` 描述企业生效/变更/注销生命周期；`check_status` 描述单次工作流审核结论。三者取值域互不相同。

因此「企业已生效」这类判断必须同时看建档状态与客户状态，口径见 [[calibers/effect_company]]；单次审核结论见 [[concepts/check_status]]。

## 需求背景

需求文档中的「企业状态」实指本字段，其「已通过」对应 `BUILD_SUCCESS`，与工作流审核的 `CUST_CHECK_PASS` 不等价（后者经流转后才会导致前者），详见 [[concepts/check_status]]。

## 版本演进

- 建档状态的写入证据目前主要来自旧处理器 `CustStatusCommitProcessor`，该类已废弃，见 [[rules/legacy_status_processor_deprecated]]；新链路下应回归验证。

---END FILE---

---FILE: concepts/check_status.md ---
---
type: concept
title: "审核状态"
page_key: "concepts/check_status"
domain: "customer-onboarding"
status: draft
aliases:
  - "check_status"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustWorkflowAuditCommitProcessor.java:process(setCheckStatus=rtfs.getCheckStaus().name())"
  - "code_path:CustStatusCommitProcessor.java:changeMessage"
contract_version: "0.1"
maps_to: "OperApiConstants.RtfState.getCheckStaus().name() → OperApiConstants.CheckStatus"
field_targets:
  - "cust_company_info.check_status"
  - "cust_change_record.status"
adjudication: "synonym"
also_confused_with:
  - "变更记录 cust_change_record.status"
boundary: "回调解读用 RtfState（中文描述，如 通过/拒绝/退回客户），落库前统一转 CheckStatus 枚举名；cust_change_record.status 在退回场景还会写入 returnCust-时间 的非枚举值。"
---

「审核状态」指工作流审核的结论枚举。回调报文里的状态是运营中台的 `RtfState`（中文描述），落库前统一转换为 `CheckStatus` 枚举名，因此同一结论在链路上有两套表述。主表落点见 [[tables/cust_company_info]]，状态机见 [[processes/workflow_check_status_machine]]。

## 边界

`boundary`：回调解读用 `RtfState`（中文描述，如 通过/拒绝/退回客户），落库前统一转 `CheckStatus` 枚举名；`cust_change_record.status` 在退回场景还会写入 `returnCust-时间` 的非枚举值。

因此对变更记录做枚举统计时，必须显式处理动态退回值，见 [[processes/change_record_check_machine]] 与 [[tables/cust_change_record]]。本概念与 [[concepts/build_status]] 是不同维度，两者通过流转联动。

## 需求背景

需求文档中的「审核中 / 已通过 / 已驳回」在本域对应的落库值分别是 `CUST_CHECK_CHECKING`、`CUST_CHECK_PASS`、`CUST_CHECK_REJECT`；「退回」对应 `CUST_CHECK_BACKTOCUSTOM`。

## 版本演进

- 通过/拒绝与中间状态分属两条落库通道，见 [[rules/workflow_callback_routing]]。
- 执行器对该状态的处理范围与注释不一致，见 [[rules/workflow_processor_scope_comment_mismatch]]。

---END FILE---

---FILE: concepts/admission.md ---
---
type: concept
title: "准入"
page_key: "concepts/admission"
domain: "customer-onboarding"
status: draft
aliases:
  - "企业准入"
  - "建档"
oid: 1
scope:
  databases: [UNSPECIFIED]
sources:
  - "code_path:CustStatusCommitProcessor.java:checkMessage"
  - "code_path:CustAuthValidatorProcessor.java:validate"
contract_version: "0.1"
maps_to: "企业建档/认证全流程（cust_build_status 从 INIT 到 BUILD_SUCCESS）"
field_targets:
  - "cust_company_info.cust_build_status"
adjudication: "boundary"
also_confused_with:
  - "产品开通 cust_auth_application.open_status"
boundary: "准入/建档指企业与联系人资格认证；产品开通（OPENING/OPENED/NOT_OPENED）指企业开通具体产品，属于建档成功后的独立流程。"
---

「准入」（亦称建档）指企业与联系人资格从提交到认证通过的全流程，终点是 [[tables/cust_company_info]] 的 `cust_build_status = BUILD_SUCCESS`；查询层面的有效性判定见 [[calibers/effect_company]]。

## 边界

`boundary`：准入/建档指企业与联系人资格认证；产品开通（OPENING/OPENED/NOT_OPENED）指企业开通具体产品，属于建档成功后的独立流程。

因此「准入通过」不能等同于「产品已开通」，也不等于单次审核结论 [[concepts/check_status]]。

## 需求背景

需求文档要求准入须经审核，驳回后可修改重提；本概念是这一要求的对象集合，流程见 [[processes/company_build_status_machine]]。

## 版本演进

- 准入链路的核查前置环节（自动/人工核查）与准入结论已明确解耦，见 [[concepts/auto_verify]] 与 [[concepts/manual_verify]]。
- 需求文档中关于自动审核直接通过准入、征信评分规则的表述，在本链路中未获证实，见 [[concepts/auto_verify]]。

---END FILE---

---REVIEW: caliber | scope.databases 物理库名未提供---
语义分析未给出任何物理库名，本批页面 `scope.databases` 统一填 `UNSPECIFIED`。请维护者补充 `cust_company_info` / `cust_change_record` / `cust_certification_info` / `cust_person_info` 所在物理库名后统一回填（涉及全部 tables/processes/calibers/rules/concepts 页面）。

追加待确认：`cust_change_cfg`（`cust_change_record.alter_type_id` 关联目标）与 `cust_auth_application`（产品开通，[[concepts/admission]] 的 also_confused_with 提及）未在 field_semantics 中定义，本次未建表页，是否需要补页请确认。
---END REVIEW---

---REVIEW: process | 需求文档主张的 reqdoc slug 未提供---
语义分析中 `reqdoc_claims` 只给出 claim 文本，未给出 slug。三个 action=anchor 的主张已分别写入 [[processes/company_build_status_machine]]（2 条）与 [[processes/change_record_check_machine]]（1 条）的 `ground:process` 块 `reqdoc_anchors` 的 evidence 双源中，slug 暂按 claim 语义派生：`company-reject-to-fail-resubmit`、`company-status-flow`、`company-change-audit-notify`。请以需求文档真实 slug 替换。

另：`cust_change_record.status` 为 `returnCust-yyyy-MM-dd HH:mm` 动态值，语义分析把它列为 `source: code_enum` 的 state；若确认为非枚举动态值，应改为 `source: code_dynamic`。
---END REVIEW---

---REVIEW: rule | 需求文档『邀请码随机生成 8 位、30 天内有效』主张被否定且证据截断---
语义分析在该条 `reqdoc_claims` 处被截断（`code_status: refuted`，`code_evidence` 内容不完整），无法逐字引用，故本次未为「邀请码」主题建立 ground 块，也未在本主题页面中固化该结论。请在补齐完整语义分析后重跑，确认「邀请码」主题归属页面（建议 `concepts/`）及其被否定的代码证据。
---END REVIEW---