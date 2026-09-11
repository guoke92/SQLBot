---FILE: tables/ca_certification_info.md ---
---
type: table
title: ca_certification_info（CFCA 一证四步认证信息表）
page_key: table/ca_certification_info
domain: 微信生态/小程序/扫脸
status: draft
aliases: [CA认证信息表, 一证四步认证表, CFCA认证表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# ca_certification_info

CFCA 一证四步链路的认证信息主表，承载「意愿认证（H5 刷脸 / 短信验证码）+ 协议告知 + 企业工商核验 + 公安实名核验 + 附件」的落库，并提供签章中台上送状态与原文留存。本表是微信小程序扫脸结果回到主业务后的落库终点，与 [[cust_certification_info]] 通过时间 / 客户维度关联，但认证类型语义不同。

## 需求背景

一证四步要求在一次企业认证动作内聚合多渠道证据：H5 刷脸（[[face_scan]]）、短信验证码、企业工商核验、公安二要素核验。各块以独立 JSON 字段落库，上送时按约定的键包装后调用签章中台。为保障可回放与可审计，中台请求 / 响应原文不截断落库，且以幂等行避免重复建单。

## 版本演进

v0.1 为代码观测基线：`intent_h5_face_json` 采用 CfcaIntentItemDto 结构，`notify_agreement_json` 兼容新（JSONArray）/老（单 JSONObject）两种格式。历史字段迁移与上线时间线待补充。

```ground:table
table: ca_certification_info
fields:
  - field: intent_h5_face_json
    meaning: "CFCA 一证四步『意愿认证 - H5 刷脸』落库块。存 CfcaIntentItemDto JSON：authType=H5_FACE、sysId（Nacos dbass.appId）、custId、custType=COMPANY、dataDate(yyyyMMdd)、opType=INSERT、authTime(yyyyMMddHHmmss)、result、similarity（人脸相似度）、videoPath（刷脸视频 COS path）、busiSeqNo、noticeId、requestData（DBaaS 原始请求 JSON）、data（DBaaS 原始响应 JSON）、name、idNo、idTypeCode=01、bodyCheckResult。Java 属性名 intentHFaceJson。"
    evidence: code
  - field: submit_status
    meaning: "签章中台上送状态。落库初始 PENDING；submitToSignCenter 成功后 SUCCESS、失败 FAIL；markFailed 强制 FAIL（已 SUCCESS 行拒绝改）。"
    evidence: code
  - field: sign_platform_result
    meaning: "签章中台 cbsSubmitBizData 的完整『[requestId]+[payload]+[resp]』原文，失败时含异常信息或 markFailed 追加段，不截断。"
    evidence: code
  - field: batch_no
    meaning: "上送流水号，格式 INC_<yyyyMMddHHmmssSSS>_<UUID前6位hex>；总公司行与分公司行各自独立生成，不要求一致。"
    evidence: code
  - field: head_company_data
    meaning: "是否总公司数据：Y/N，仅接受 Y（大小写不敏感），其余/空回退 N；参与 (custId,dataDate,headCompanyData,submitStatus=PENDING) 幂等键。"
    evidence: code
  - field: data_source
    meaning: "CA 数据来源，CaDataSourceEnum；CHANNEL_OPENAPI 时豁免『至少一项意愿认证』的完整性校验。"
    evidence: code
  - field: notify_agreement_json
    meaning: "协议告知块。新格式存 JSONArray，上送时包装为 {notifyAgreementList:[...], notifyTextList:[]}；老格式单 JSONObject 兼容包成单元素数组。"
    evidence: code
  - field: enterprise_four_json
    meaning: "企业工商核验块；按 verifyMethod 分键上送：ENTERPRISE_THREE → authEnterpriseThree，ENTERPRISE_FOUR（含解析失败兜底）→ authEnterpriseFour。"
    evidence: code
  - field: police_two_json
    meaning: "公安二要素（姓名+身份证）实名核验块，上送键 authPersonPoliceTwo。"
    evidence: code
  - field: intent_sms_json
    meaning: "短信验证码意愿认证块，上送键 intentJson.checkCode。"
    evidence: code
  - field: file_refs_json
    meaning: "附件清单块，内含 embeddedFiles[{multipartField,path}]；path 落库为 COS key，上送前转带签名 HTTP 下载链。"
    evidence: code
```

相关：[[ca_submit_state_machine]]、[[ca_idempotent_row]]、[[latest_success_submit]]、[[h5_face_persist_soft_fail]]、[[submit_data_length_limit]]、[[certification_id]]。
---END FILE---

---FILE: tables/cust_certification_info.md ---
---
type: table
title: cust_certification_info（客户核查记录表）
page_key: table/cust_certification_info
domain: 微信生态/小程序/扫脸
status: draft
aliases: [核查记录表, 认证核查表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:AutoVerifyServiceImpl.java
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# cust_certification_info

客户核查记录表：一行代表一次「核查项」结果，核查项由 [[certification_type]] 枚举区分，覆盖企业四要素 / 二要素、法人三要素、授权人三要素、法人 OCR、授权人 OCR、营业执照 OCR、法人影音 OCR、授权人影音 OCR 与人脸核查（FACE_VERIFY）。扫脸链路通过 FACE_VERIFY 行承载，是 [[face_verify_passed]] 口径的物理落点。

## 需求背景

低代码核查引擎将 OCR、要素比对、人脸核身统一登记为核查行，自动核查与人工核查双轨并存，任一通过即视为通过，便于人工兜底。人脸核查额外落 `face_business_no`，用于按流水号回拉人脸影像文件。

## 版本演进

v0.1 记录核查项类型与结果字典取值。`auto_verify_count / manual_verify_count` 的「>=3 次」校验当前被代码注释，未生效，后续版本是否放开待定。

```ground:table
table: cust_certification_info
fields:
  - field: certification_type
    meaning: "核查项类型，CustCertificationTypeEnum.getDictParam()；出现值：COMPANY_FOUR_ELEMENTS、COMPANY_TWO_ELEMENTS、LEGAL_THREE_ELEMENTS、AUTH_THREE_ELEMENTS、LEGAL_OCR、AUTH_OCR、LICENSE_OCR、LEGAL_MEDIA_OCR、AUTH_MEDIA_OCR、FACE_VERIFY。"
    evidence: code
  - field: auto_verify_status
    meaning: "自动核查结果，取 CustCertificationResultTypeEnum 的 dictParam（自动通过/自动不通过等）。"
    evidence: code
  - field: manual_verify_status
    meaning: "人工核查结果；与 auto_verify_status 任一为『通过』即视为人脸/核查通过（FaceVerifyController.isFaceVerifyPassed）。"
    evidence: code
  - field: face_business_no
    meaning: "人脸识别业务流水号，用于按流水号拉取人脸影像文件（A0024）并回溯刷脸结果。"
    evidence: code
  - field: auto_verify_count / manual_verify_count
    meaning: "自动/人工核查累计次数，每次 write 自增 1；实名三要素链路有 >=3 次的注释校验位（当前被注释掉，未生效）。"
    evidence: code
```

相关：[[cust_person_info]]、[[face_verify_passed]]、[[realname_face_verify_state]]、[[face_business_no]]、[[face_scan]]。
---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info（企业联系人表）
page_key: table/cust_person_info
domain: 微信生态/小程序/扫脸
status: draft
aliases: [联系人表, 客户联系人表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:PlatFormUserApplication.java
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# cust_person_info

企业联系人表，记录管理员 / 经办人 / 游客三类联系人及其实名与人脸状态。联系人既是刷脸意愿主体（admin）的来源，也是 [[valid_contact]] 与 [[face_intent_subject]] 两个口径的判定对象。

## 需求背景

人脸认证与手机号实名认证分别落 `face_status`、`phone_realname_status`，再由 RealNameResultEnum 合成 `real_name_result` 对外呈现。查询有效联系人时剔除游客并限定状态，保证展示与推送口径一致。

## 版本演进

v0.1 记录联系人类型、状态限定与实名合成规则。经办人推送系统列表 `operator_push_system` 支撑变更后按渠道补推。

```ground:table
table: cust_person_info
fields:
  - field: face_status
    meaning: "该联系人的人脸认证结果，取 CustCertificationResultTypeEnum dictKey。"
    evidence: code
  - field: phone_realname_status
    meaning: "手机号实名认证状态（三要素/人脸回写），与 face_status 合成 real_name_result。"
    evidence: code
  - field: real_name_result
    meaning: "RealNameResultEnum.computeRealNameResult(faceStatus, phoneRealnameStatus) 的合成实名结果。"
    evidence: code
  - field: user_type
    meaning: "联系人类型：admin（客户管理员，刷脸意愿主体）/ operator（经办人）/ guest（游客，查询时被剔除）。"
    evidence: code
  - field: status
    meaning: "联系人账号状态；查询有效联系人时限定 ADD、EFFECT（CustPersonStatusConstant）。"
    evidence: code
  - field: operator_push_system
    meaning: "经办人已推送系统列表（逗号分隔 sysChannel），修改后按此列表逐个推送运营中台。"
    evidence: code
```

相关：[[cust_certification_info]]、[[face_intent_subject]]、[[valid_contact]]、[[operator_freeze_state]]、[[face_scan]]。
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户企业信息表）
page_key: table/cust_company_info
domain: 微信生态/小程序/扫脸
status: draft
aliases: [企业信息表, 客户企业表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# cust_company_info

客户企业信息表，记录企业维度是否需要开通签章、CA 开通状态与上上签开通状态。是刷脸意愿主体定位（`ref_cust_company_info`）与 CA 预检的上游依赖。

## 需求背景

签署子账号授权书前，若 `need_register_ca=Y`，需先做 CA 状态预检，避免在未开通 CA 的企业上发起授权流程。

## 版本演进

v0.1 记录 need_register_ca / ca_register_status / bs_register_status 三字段语义。

```ground:table
table: cust_company_info
fields:
  - field: need_register_ca / ca_register_status / bs_register_status
    meaning: "分别表示是否需要开通签章、CA 开通状态、上上签开通状态；need_register_ca=Y 时签署子账号授权书前要做 CA 状态预检。"
    evidence: code
```

相关：[[cust_person_info]]、[[face_intent_subject]]、[[ca_idempotent_row]]。
---END FILE---

---FILE: tables/wx_work_user.md ---
---
type: table
title: wx_work_user（企微成员表）
page_key: table/wx_work_user
domain: 微信生态/小程序/扫脸
status: draft
aliases: [企微成员, 企业微信成员表]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatContactService.java
contract_version: "0.1"
---

# wx_work_user

企业微信通讯录成员表。用于企微消息触达时的成员过滤：仅激活成员可被纳入内部审批 / 通知对象。

## 需求背景

`WechatContactService.pullContactList` 全量拉取通讯录时，按成员状态过滤停用 / 未激活成员，避免向无效成员推送消息。

## 版本演进

v0.1 仅记录成员状态过滤口径 [[wecom_active_member]]；成员字段全集待补充。

```ground:table
table: wx_work_user
fields:
  - field: status
    meaning: "企微成员状态；有效成员判定为 status IS NULL OR status = MEMBER_STATUS_ACTIVATED。"
    evidence: code_path:WechatContactService.java#isActiveMember
```

相关：[[wecom_active_member]]、[[wechat]]。
---END FILE---

---FILE: processes/ca_submit_state_machine.md ---
---
type: process
title: CA 一证四步上送状态机
page_key: process/ca_submit_state_machine
domain: 微信生态/小程序/扫脸
status: draft
aliases: [上送状态机, submit_status 状态机]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 一证四步上送状态机

描述 [[ca_certification_info]] 上送签章中台的状态流转：落库初始 PENDING，成功后 SUCCESS，失败 FAIL；SUCCESS 行具备幂等短路的保护语义。

## 需求背景

上送涉及外部中台，需要可重试且可人工干预。通过 PENDING 初始态 + SUCCESS 幂等短路 + markFailed 人工补录，保证重复调用不产生歧义、已成功结果不被覆盖。

## 版本演进

v0.1 记录三种状态与六条迁移路径。

```ground:process
state_machine: CA 一证四步上送状态机
field: ca_certification_info.submit_status
states:
  - value: PENDING
    label: 待上送
    source: code_enum
  - value: SUCCESS
    label: 上送成功
    source: code_enum
  - value: FAIL
    label: 上送失败
    source: code_enum
transitions:
  - from: "(新建)"
    event: createOrGetByKey 建行
    to: PENDING
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey
  - from: PENDING
    event: submitToSignCenter 中台返回 DBaaS code∈{0,200} 且 biz.status=SAVED
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: PENDING
    event: submitToSignCenter 抛异常 / DBaaS code 不成功 / biz.status≠SAVED
    to: FAIL
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: FAIL
    event: markFailed 人工补录强制置失败
    to: FAIL
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#markFailed
  - from: SUCCESS
    event: submitToSignCenter 重复调用（幂等短路）
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
  - from: SUCCESS
    event: markFailed（被拒绝，抛 CA_CERT_SUBMIT_ALREADY_SUCCESS）
    to: SUCCESS
    evidence: code_path:CaCertificationInfoAppServiceImpl.java#markFailed
```

相关：[[ca_certification_info]]、[[ca_idempotent_row]]、[[latest_success_submit]]、[[h5_face_persist_soft_fail]]。
---END FILE---

---FILE: processes/realname_face_verify_state.md ---
---
type: process
title: 实名/人脸核查结果状态
page_key: process/realname_face_verify_state
domain: 微信生态/小程序/扫脸
status: draft
aliases: [核查结果状态, 人脸核查状态]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:AutoVerifyServiceImpl.java
contract_version: "0.1"
---

# 实名/人脸核查结果状态

描述核查结果在自动核查与人工核查双轨下的取值与流转，作用于 [[cust_certification_info]] 的 auto/manual_verify_status，以及 [[cust_person_info]] 的 face_status / phone_realname_status。

## 需求背景

自动核查失败时需支持人工复核兜底；同时人脸回写要兼顾手机号实名与刷脸两个来源。`verifyFlag=YES` 且自动失败时提前返回，避免重复走三要素链路。

## 版本演进

v0.1 记录三种结果状态与四条迁移路径。

```ground:process
state_machine: 实名/人脸核查结果状态
field: cust_certification_info.auto_verify_status / manual_verify_status / cust_person_info.face_status / cust_person_info.phone_realname_status
states:
  - value: AUTOMATIC_AUTHENTICATION_PASSED
    label: 自动核查通过
    source: code_enum
  - value: AUTOMATIC_AUTHENTICATION_FAILED
    label: 自动核查不通过
    source: code_enum
  - value: MANUAL_AUTHENTICATION_PASSED
    label: 人工核查通过
    source: code_enum
transitions:
  - from: "(新建)"
    event: verifyThree 落实名三要素结果
    to: AUTOMATIC_AUTHENTICATION_PASSED / FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#verifyThree
  - from: "(新建)"
    event: finishedVerifyFace 拉小程序人脸结果回写 face_status + phone_realname_status
    to: AUTOMATIC_AUTHENTICATION_PASSED / FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#finishedVerifyFace
  - from: AUTOMATIC_AUTHENTICATION_FAILED
    event: saveManual 人工核查
    to: MANUAL_AUTHENTICATION_PASSED
    evidence: code_path:AutoVerifyServiceImpl.java#saveManual
  - from: 任意
    event: verifyFlag=YES 且自动失败 → 提前 return，不继续走三要素
    to: AUTOMATIC_AUTHENTICATION_FAILED
    evidence: code_path:AutoVerifyServiceImpl.java#verifyThree
```

相关：[[cust_certification_info]]、[[cust_person_info]]、[[face_verify_passed]]、[[face_scan]]。
---END FILE---

---FILE: processes/operator_freeze_state.md ---
---
type: process
title: 经办人冻结状态（SysCustUserRel）
page_key: process/operator_freeze_state
domain: 微信生态/小程序/扫脸
status: draft
aliases: [经办人冻结, is_freeze 状态]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:PlatFormUserApplication.java
  - code:CustSyncEventProvider.java
contract_version: "0.1"
---

# 经办人冻结状态（SysCustUserRel）

描述经办人账号在 sys_cust_user_rel.is_freeze 上的冻结 / 解冻流转。该状态参与 [[valid_contact]] 的过滤（`is_freeze='N'`），并影响扫脸主体有效性视图。

## 需求背景

运营中台同步删除经办人时，若同手机号兼管理员，只冻结经办人角色，避免误伤管理员账号。

## 版本演进

v0.1 记录 N/Y 两态与三条迁移路径。

```ground:process
state_machine: 经办人冻结状态（SysCustUserRel）
field: sys_cust_user_rel.is_freeze
states:
  - value: N
    label: 解冻/正常
    source: code_enum
  - value: Y
    label: 已冻结
    source: code_enum
transitions:
  - from: N
    event: freezeOrThawOperatorUser operationType=FREEZE
    to: Y
    evidence: code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser
  - from: Y
    event: freezeOrThawOperatorUser operationType=THAW
    to: N
    evidence: code_path:PlatFormUserApplication.java#freezeOrThawOperatorUser
  - from: N
    event: 运营中台 syncOperatorUser OperatorType=DELETE（同手机号兼管理员时只冻经办人角色）
    to: Y
    evidence: code_path:CustSyncEventProvider.java#syncOperatorUser
```

相关：[[cust_person_info]]、[[valid_contact]]、[[face_intent_subject]]。
---END FILE---

---FILE: calibers/face_verify_passed.md ---
---
type: caliber
title: 人脸核查通过
page_key: caliber/face_verify_passed
domain: 微信生态/小程序/扫脸
status: draft
aliases: [人脸通过, 刷脸通过]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# 人脸核查通过

人脸核查是否通过的判定口径：自动核查通过或人工核查通过，任一满足即视为通过。该口径决定是否回填 [[ca_certification_info]] 的 `intent_h5_face_json`。

## 需求背景

自动核查可能失败，需人工复核兜底，因此「通过」采用自动 / 人工或关系而非与关系。

## 版本演进

v0.1 记录单条判定谓词。

```ground:caliber
name: 人脸核查通过
predicate: "cust_certification_info.auto_verify_status = 'AUTOMATIC_AUTHENTICATION_PASSED' OR cust_certification_info.manual_verify_status = 'MANUAL_AUTHENTICATION_PASSED'"
scope: "FaceVerifyController#persistH5FaceIntentIfPassed 决定是否回填 intent_h5_face_json；两者任一通过即视为通过。"
evidence: code_path:FaceVerifyController.java#isFaceVerifyPassed
```

相关：[[cust_certification_info]]、[[realname_face_verify_state]]、[[h5_face_persist_soft_fail]]、[[face_scan]]。
---END FILE---

---FILE: calibers/valid_contact.md ---
---
type: caliber
title: 有效联系人（可展示）
page_key: caliber/valid_contact
domain: 微信生态/小程序/扫脸
status: draft
aliases: [有效联系人, 可展示联系人]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:PlatFormUserApplication.java
contract_version: "0.1"
---

# 有效联系人（可展示）

判定联系人是否可展示的口径：启用且账号状态为 ADD 或 EFFECT；随后按 productTypes 过滤 `is_freeze='N'` 的 SysCustUserRel。

## 需求背景

联系人列表需剔除游客与停用账号，并叠加经办人冻结过滤，保证展示与可操作对象一致。

## 版本演进

v0.1 记录基础谓词与冻结叠加过滤。

```ground:caliber
name: 有效联系人（可展示）
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.status IN ('ADD','EFFECT')"
scope: "listCompanyUser 按企业 id 查联系人；再按 productTypes 过滤 is_freeze='N' 的 SysCustUserRel。"
evidence: code_path:PlatFormUserApplication.java#listCompanyUser
```

相关：[[cust_person_info]]、[[operator_freeze_state]]、[[face_intent_subject]]。
---END FILE---

---FILE: calibers/face_intent_subject.md ---
---
type: caliber
title: 刷脸意愿主体（客户管理员）
page_key: caliber/face_intent_subject
domain: 微信生态/小程序/扫脸
status: draft
aliases: [刷脸主体, 意愿认证主体]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# 刷脸意愿主体（客户管理员）

取当前登录用户在本企业中的管理员作为刷脸意愿主体：user_type=admin、enable=Y、ref_cust_company_info 匹配企业 code、user_id 匹配当前登录用户。

## 需求背景

刷脸意向须绑定到有身份的客户管理员，保证小程序扫码刷脸的发起主体可追溯。

## 版本演进

v0.1 记录该主体定位谓词。

```ground:caliber
name: 刷脸意愿主体（客户管理员）
predicate: "cust_person_info.user_type = 'admin' AND cust_person_info.enable = 'Y' AND cust_person_info.ref_cust_company_info = <企业 code> AND cust_person_info.user_id = <当前登录用户>"
scope: "getFaceQrCode / resolveFaceIntentPerson 取当前登录用户在本企业的管理员作为刷脸主体。"
evidence: code_path:FaceVerifyController.java#resolveFaceIntentPerson
```

相关：[[cust_person_info]]、[[cust_company_info]]、[[miniprogram_qrcode]]、[[face_scan]]。
---END FILE---

---FILE: calibers/ca_idempotent_row.md ---
---
type: caliber
title: CA 幂等行
page_key: caliber/ca_idempotent_row
domain: 微信生态/小程序/扫脸
status: draft
aliases: [CA幂等键, 幂等行]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 幂等行

[[ca_certification_info]] 的建单幂等口径：以 (cust_id, data_date, head_company_data, submit_status=PENDING) 命中则返回既有 id，不新建；batch_no 不进幂等键。

## 需求背景

刷脸链路可能因小程序重试多次触发落库，需以幂等键避免重复建单。

## 版本演进

v0.1 记录幂等谓词与 batch_no 的排除说明。

```ground:caliber
name: CA 幂等行
predicate: "ca_certification_info.cust_id = ? AND data_date = ? AND head_company_data = ? AND submit_status = 'PENDING'"
scope: "createOrGetByKey 命中则直接返回既有 id，不新建；batch_no 不进幂等键。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[latest_success_submit]]。
---END FILE---

---FILE: calibers/latest_success_submit.md ---
---
type: caliber
title: 企业最新成功上送记录
page_key: caliber/latest_success_submit
domain: 微信生态/小程序/扫脸
status: draft
aliases: [最新成功上送, 基准行]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 企业最新成功上送记录

取企业最近一条成功上送并启用的 [[ca_certification_info]] 行作为基准：cust_id 匹配、submit_status=SUCCESS、enable=Y，按 submit_time、id 倒序取第一条。

## 需求背景

复用最新成功上送的报文作为业务基准（assembleLatestSuccessBizRequest / submitLatestSuccessBizRequest）。

## 版本演进

v0.1 记录基准行谓词。

```ground:caliber
name: 企业最新成功上送记录
predicate: "ca_certification_info.cust_id = ? AND submit_status = 'SUCCESS' AND enable = 'Y' ORDER BY submit_time DESC, id DESC LIMIT 1"
scope: "assembleLatestSuccessBizRequest / submitLatestSuccessBizRequest 取基准行。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#findLatestSuccessRow
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[ca_idempotent_row]]。
---END FILE---

---FILE: calibers/wecom_active_member.md ---
---
type: caliber
title: 企微有效成员
page_key: caliber/wecom_active_member
domain: 微信生态/小程序/扫脸
status: draft
aliases: [企微有效成员, 通讯录有效成员]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatContactService.java
contract_version: "0.1"
---

# 企微有效成员

企业微信通讯录的成员有效性口径：status 为空或等于 MEMBER_STATUS_ACTIVATED。用于全量拉取通讯录时的成员过滤。

## 需求背景

企微消息触达对象须为激活成员，避免向停用 / 未激活成员推送。

## 版本演进

v0.1 记录成员过滤谓词。

```ground:caliber
name: 企微有效成员
predicate: "wx_work_user.status IS NULL OR wx_work_user.status = MEMBER_STATUS_ACTIVATED"
scope: "WechatContactService.pullContactList 全量拉取通讯录时过滤停用/未激活成员。"
evidence: code_path:WechatContactService.java#isActiveMember
```

相关：[[wx_work_user]]、[[wechat]]。
---END FILE---

---FILE: calibers/submit_data_length_limit.md ---
---
type: caliber
title: 上送 data 字段长度上限
page_key: caliber/submit_data_length_limit
domain: 微信生态/小程序/扫脸
status: draft
aliases: [data长度上限, 上送裁剪口径]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# 上送 data 字段长度上限

上送前对 `data` 字段的长度约束口径：单字段不超过 1000，仅对 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 五处裁剪。

## 需求背景

中台对报文体积有限制，h5Face 的原始 requestData / data 可能较大，需按 JSON 叶子长度从长到短剔除，最后硬截断兜底。

## 版本演进

v0.1 记录长度上限与裁剪范围。

```ground:caliber
name: 上送 data 字段长度上限
predicate: "LENGTH(authRealNameJson.*.data / intentJson.*.data) <= 1000"
scope: "仅裁剪 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 五处 data，超长按 JSON 叶子从长到短剔除，最后硬截断兜底。"
evidence: code_path:CaCertificationInfoAppServiceImpl.java#truncateOversizedDataFieldsInSubmitPayload
```

相关：[[ca_certification_info]]、[[h5_face_persist_soft_fail]]、[[ca_submit_completeness_check]]。
---END FILE---

---FILE: concepts/face_scan.md ---
---
type: concept
title: 扫脸 / 人脸识别
page_key: concept/face_scan
domain: 微信生态/小程序/扫脸
status: draft
aliases: [H5_FACE, H5刷脸, 意愿认证, faceVerify, 刷脸]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
maps_to: "cust_certification_info.certification_type = 'FACE_VERIFY' 与 ca_certification_info.intent_h5_face_json（authType=H5_FACE）"
field_targets:
  - cust_certification_info.certification_type
  - ca_certification_info.intent_h5_face_json
adjudication: boundary
also_confused_with:
  - OCR 身份证核查（LEGAL_OCR/AUTH_OCR）
  - 三要素手机号实名（LEGAL_THREE_ELEMENTS/AUTH_THREE_ELEMENTS）
boundary: "扫脸=人脸比对（FaceVerifyController + miniFaceService），走小程序二维码；OCR/三要素属于证照识别与实名比对，同一张 cust_certification_info 表不同 certification_type 行，不可互相替代。"
contract_version: "0.1"
---

# 扫脸 / 人脸识别

「扫脸 / 人脸识别 / H5 刷脸」是同一业务动作的不同叫法，指通过微信小程序二维码完成的人脸比对与意愿认证。它落在两处：核查记录侧为 `cust_certification_info.certification_type = FACE_VERIFY`，一证四步侧为 `ca_certification_info.intent_h5_face_json`（authType = H5_FACE）。

## 需求背景

扫脸既是核身手段也是意愿表达手段，需要与证照 OCR、三要素实名区分，避免口径混用。

## 版本演进

v0.1 建立术语边界：扫脸 ≠ OCR ≠ 三要素手机号实名。

## 边界说明

扫脸走小程序二维码与人脸比对服务；OCR / 三要素同在 [[cust_certification_info]] 表、以不同 [[certification_type]] 区分，不可互相替代。

相关：[[certification_type]]、[[miniprogram_qrcode]]、[[face_verify_passed]]、[[face_intent_subject]]、[[face_business_no]]。
---END FILE---

---FILE: concepts/wechat.md ---
---
type: concept
title: 微信（企微 / 服务号 / 小程序分流）
page_key: concept/wechat
domain: 微信生态/小程序/扫脸
status: draft
aliases: [微信通知, WechatNotificationService, 企微]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:WechatNotifyFacade.java
  - code:WechatWorkMessageService.java
  - code:WechatNotificationService.java
maps_to: "需拆分：WechatNotifyFacade/WechatWorkMessageService 直连『企业微信 message/send』；WechatNotificationService（sso 组件）为另一路微信触达抽象。"
adjudication: boundary
also_confused_with:
  - 企业微信（企微）
  - 微信服务号
  - 小程序
boundary: "企微消息面向内部审批人（touser=企微 userId，textcard）；小程序链路（MiniProgramController）面向 C 端小程序，用 api.weixin.qq.com accessToken。二者接入主体与 token 体系不同。"
contract_version: "0.1"
---

# 微信（企微 / 服务号 / 小程序分流）

「微信」在本域内并非单一通道，需拆为至少两类：面向内部审批人的企业微信消息（WechatNotifyFacade / WechatWorkMessageService），以及面向 C 端的小程序链路（MiniProgramController）。另有 sso 组件的 WechatNotificationService 抽象。

## 需求背景

内部通知与 C 端刷脸接入主体、凭证体系不同，必须分流建模，否则会误把企微凭证用于小程序调用。

## 版本演进

v0.1 明确三类触达通道的边界。

## 边界说明

企微消息用企微 userId（touser）+ textcard；小程序链路用 api.weixin.qq.com accessToken（见 [[access_token]]）。

相关：[[wx_work_user]]、[[wecom_active_member]]、[[access_token]]、[[miniprogram_qrcode]]。
---END FILE---

---FILE: concepts/miniprogram_qrcode.md ---
---
type: concept
title: 小程序二维码
page_key: concept/miniprogram_qrcode
domain: 微信生态/小程序/扫脸
status: draft
aliases: [getFaceQrCode, getCustBuildQrCode, 二维码]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniFaceService.java
  - code:FaceVerifyController.java
maps_to: "MiniFaceService.getFaceQrCode（扫脸/建档场景）与 MiniFaceService.getCustBuildQrCode（建档场景）"
adjudication: boundary
also_confused_with:
  - CA 关联的 certificationId 生成的二维码
boundary: "当传 certificationId 时 busiSeqNo=certificationId+LocalDate.now()，否则 busiSeqNo=custId+LocalDate.now()；busiSeqNo 语义随入参改变，是同一接口内的分支语义，不是同一个业务标识。"
contract_version: "0.1"
---

# 小程序二维码

小程序二维码用于扫脸 / 建档场景，由 MiniFaceService 生成：getFaceQrCode（扫脸 / 建档）与 getCustBuildQrCode（建档）。二维码内承载 busiSeqNo 查询键。

## 需求背景

扫码刷脸需一个可回查的查询键，busiSeqNo 依据入参不同而产生分支语义。

## 版本演进

v0.1 明确 busiSeqNo 的分支语义，避免被当作同一业务标识。

## 边界说明

当传 certificationId 时 busiSeqNo=certificationId+LocalDate.now()，否则 busiSeqNo=custId+LocalDate.now()。

相关：[[face_scan]]、[[face_business_no]]、[[certification_id]]、[[face_intent_subject]]。
---END FILE---

---FILE: concepts/access_token.md ---
---
type: concept
title: accessToken（小程序 / 企微 / SSO）
page_key: concept/access_token
domain: 微信生态/小程序/扫脸
status: draft
aliases: [小程序 accessToken, 微信 token]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
maps_to: "MiniProgramController.getOrigAccessToken：api.weixin.qq.com/cgi-bin/token，Redis key = FBP_WECHAT_TOKEN_PREFIX + appid + secret"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
adjudication: boundary
also_confused_with:
  - 企业微信 access_token（WechatWorkApiClient 内部，未在本层给出）
  - SSO token
boundary: "小程序 accessToken 由 appid+secret 换取并缓存（expires_in-300 秒）；企微消息走 WechatWorkApiClient 的另一套凭证，缓存 key 与刷新逻辑不同。"
contract_version: "0.1"
---

# accessToken（小程序 / 企微 / SSO）

accessToken 有多套：小程序 accessToken（MiniProgramController 通过 appid+secret 换取，Redis key = FBP_WECHAT_TOKEN_PREFIX + appid + secret）、企微 access_token（WechatWorkApiClient 内部）、SSO token。

## 需求背景

不同通道凭证来源与刷新逻辑不同，混用会导致调用失败或串号。

## 版本演进

v0.1 区分小程序与企微两套 token 体系。

## 边界说明

小程序 accessToken 按 expires_in-300 秒缓存；企微凭证另有一套缓存 key 与刷新逻辑。

相关：[[wechat]]、[[miniprogram_access_token_cache]]、[[miniprogram_scheme_retry]]。
---END FILE---

---FILE: concepts/face_business_no.md ---
---
type: concept
title: faceBusinessNo / businessNo / busiSeqNo（业务流水号）
page_key: concept/face_business_no
domain: 微信生态/小程序/扫脸
status: draft
aliases: [业务流水号]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniFaceService.java
  - code:FaceVerifyController.java
maps_to: "cust_certification_info.face_business_no；MiniFaceService.queryResult(businessNo)；GetFaceQrCodeReqDTO.busiSeqNo"
field_targets:
  - cust_certification_info.face_business_no
adjudication: boundary
also_confused_with:
  - ca_certification_info.batch_no
boundary: "busiSeqNo 是生成二维码时组装的查询键（custId/certificationId + 日期）；faceBusinessNo 是人脸服务返回的流水号，回写时 busiSeqNo 优先取 faceResult.getFaceBusinessNo()，其次取 snapshot.getBusinessNo()；batch_no 是签章中台上送流水号，三者不同源。"
contract_version: "0.1"
---

# faceBusinessNo / businessNo / busiSeqNo（业务流水号）

三个易混的流水号：busiSeqNo 是生成二维码时组装的查询键（custId/certificationId + 日期）；faceBusinessNo 是人脸服务返回的流水号，用于按流水号拉取人脸影像（A0024）；batch_no 是签章中台上送流水号（见 [[ca_certification_info]]）。

## 需求背景

刷脸回写时需要从一个流水号回查到人脸结果与影像文件，若把三者当同一标识会取错数据源。

## 版本演进

v0.1 明确三者不同源及回写优先级。

## 边界说明

回写时 busiSeqNo 优先取 faceResult.getFaceBusinessNo()，其次取 snapshot.getBusinessNo()。

相关：[[miniprogram_qrcode]]、[[face_scan]]、[[certification_id]]、[[ca_certification_info]]。
---END FILE---

---FILE: concepts/certification_id.md ---
---
type: concept
title: certificationId
page_key: concept/certification_id
domain: 微信生态/小程序/扫脸
status: draft
aliases: [认证 id]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
maps_to: "在 FaceVerifyController.faceVerifyQuery / getFaceQrCode 中为 ca_certification_info.id（Long，CFCA 一证四步链路）"
field_targets:
  - ca_certification_info.id
adjudication: boundary
also_confused_with:
  - cust_certification_info.id（低代码核查记录主键）
boundary: "凡 FaceVerifyController 入参 certificationId 均指 ca_certification_info.id，用于 updateIntentByType/mergeEmbeddedFilePath 定位行；cust_certification_info 表行通过 certification_type + ref_cust_company_info 定位，无 certificationId 入参。"
contract_version: "0.1"
---

# certificationId

在 FaceVerifyController 的刷脸链路入参中，certificationId 指 [[ca_certification_info]] 的主键 id（Long），用于 updateIntentByType / mergeEmbeddedFilePath 定位行，进而回填 [[face_scan]] 相关数据。

## 需求背景

刷脸回填需要精确定位到具体的 CA 认证行，避免与低代码核查记录行的主键混淆。

## 版本演进

v0.1 明确 certificationId 的归属表。

## 边界说明

[[cust_certification_info]] 表行通过 certification_type + ref_cust_company_info 定位，无 certificationId 入参。

相关：[[ca_certification_info]]、[[cust_certification_info]]、[[miniprogram_qrcode]]、[[face_business_no]]。
---END FILE---

---FILE: rules/miniprogram_access_token_cache.md ---
---
type: rule
title: 小程序 accessToken 缓存与重试
page_key: rule/miniprogram_access_token_cache
domain: 微信生态/小程序/扫脸
status: draft
aliases: [accessToken缓存, token重试]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
contract_version: "0.1"
---

# 小程序 accessToken 缓存与重试

小程序 accessToken 的获取规则：以 appid+secret 为 key 查 Redis，未命中则调 api.weixin.qq.com/cgi-bin/token，失败最多重试 5 次（间隔 200ms），成功按 expires_in-300 秒缓存。

## 需求背景

频繁换取 token 会触发票据频率限制，需要缓存；网络抖动需有限重试兜底。

## 版本演进

v0.1 记录缓存 key、重试上限与缓存时长。

```ground:rule
name: 小程序 accessToken 缓存与重试
content: "以 appid+secret 为 key 查 Redis；未命中则调 api.weixin.qq.com/cgi-bin/token，失败最多重试 5 次（间隔 200ms），成功按 expires_in-300 秒缓存；未取到 access_token 时直接返回微信原始报文，5 次后抛 IOException。"
impact: "并发下多实例可能同时刷新；缓存过期窗口留 300 秒冗余。"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
evidence: code_path:MiniProgramController.java#getOrigAccessToken
```

相关：[[access_token]]、[[wechat]]、[[miniprogram_scheme_retry]]。
---END FILE---

---FILE: rules/miniprogram_scheme_retry.md ---
---
type: rule
title: 小程序 Scheme 生成失败重试一次
page_key: rule/miniprogram_scheme_retry
domain: 微信生态/小程序/扫脸
status: draft
aliases: [Scheme重试, 小程序Scheme]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:MiniProgramController.java
contract_version: "0.1"
---

# 小程序 Scheme 生成失败重试一次

生成小程序 Scheme 时，若首次失败（errcode≠0）且 reTry=false，则删除 Redis accessToken 缓存后以 reTry=true 重试一次；仍失败抛 IOException。expire_type=1、expire_interval=1（有效期 1 天）。

## 需求背景

token 失效是 Scheme 生成失败的主因，通过清缓存重试一次来规避。

## 版本演进

v0.1 记录重试策略与有效期参数。

```ground:rule
name: 小程序 Scheme 生成失败重试一次
content: "generateMiniProgramScheme 首次失败（errcode≠0）且 reTry=false 时，删除 Redis accessToken 缓存后以 reTry=true 重试一次；仍失败抛 IOException。expire_type=1、expire_interval=1（有效期 1 天）。"
impact: "避免 token 失效导致的 Scheme 生成失败；重试仅一次。"
field_targets:
  - FBP_WECHAT_TOKEN_PREFIX+appid+secret
evidence: code_path:MiniProgramController.java#generateMiniProgramScheme
```

相关：[[access_token]]、[[miniprogram_qrcode]]、[[miniprogram_access_token_cache]]。
---END FILE---

---FILE: rules/h5_face_persist_soft_fail.md ---
---
type: rule
title: H5 刷脸落库弱失败
page_key: rule/h5_face_persist_soft_fail
domain: 微信生态/小程序/扫脸
status: draft
aliases: [刷脸落库弱失败, 静默落库]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:FaceVerifyController.java
contract_version: "0.1"
---

# H5 刷脸落库弱失败

persistH5FaceIntentIfPassed 中，updateIntentByType / mergeEmbeddedFilePath 异常仅记 error 日志，不抛出，不阻断 faceVerifyQuery 返回人脸结果；未传 certificationId、人脸未通过、快照缺失均直接跳过回填。

## 需求背景

主链路可用性优先于落库完整性，落库失败不应影响用户拿到刷脸结果，代价是需靠日志审计静默缺失。

## 版本演进

v0.1 记录弱失败策略与跳过条件。

```ground:rule
name: H5 刷脸落库弱失败
content: "persistH5FaceIntentIfPassed 中 updateIntentByType / mergeEmbeddedFilePath 异常仅 error 日志，不抛出，不阻断 faceVerifyQuery 返回人脸结果；未传 certificationId、人脸未通过、快照缺失（snapshot 为空或 !isCaptured）均直接跳过回填。"
impact: "主链路可用性优先；代价是落库可能静默缺失，需靠日志审计。"
field_targets:
  - ca_certification_info.intent_h5_face_json
  - ca_certification_info.file_refs_json
evidence: code_path:FaceVerifyController.java#persistH5FaceIntentIfPassed
```

相关：[[face_verify_passed]]、[[face_scan]]、[[certification_id]]、[[ca_certification_info]]。
---END FILE---

---FILE: rules/ca_submit_completeness_check.md ---
---
type: rule
title: CA 上送完整性校验
page_key: rule/ca_submit_completeness_check
domain: 微信生态/小程序/扫脸
status: draft
aliases: [上送完整性校验, 完整性校验]
oid: 1
scope:
  databases: [dbass]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

# CA 上送完整性校验

submitToSignCenter 前的完整性校验规则：notify_agreement_json 非空；enterprise_four_json 或 police_two_json 至少一项非空；以及意愿认证相关约束（`data_source=CHANNEL_OPENAPI` 时豁免「至少一项意愿认证」，见 [[ca_certification_info]] 的 data_source）。

## 需求背景

签章中台要求报文具备协议告知与至少一类身份核验证据，否则拒绝受理。

## 版本演进

v0.1 记录校验前置条件；完整校验清单在语义分析中此处被截断，待补充。

```ground:rule
name: CA 上送完整性校验
content: "submitToSignCenter 前校验：notify_agreement_json 非空；enterprise_four_json 或 police_two_json 至少一项非空；intent…（原文在语义分析中截断，待补全）。"
impact: "保障中台报文具备协议告知与至少一类身份核验证据；CHANNEL_OPENAPI 数据源豁免意愿认证完整性校验。"
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.data_source
evidence: code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter
```

相关：[[ca_certification_info]]、[[ca_submit_state_machine]]、[[submit_data_length_limit]]、[[ca_idempotent_row]]。
---END FILE---

---REVIEW: table | table/ca_certification_info ---
所有页面 frontmatter 的 `scope.databases` 暂填 `dbass`（依据语义分析中出现的 Nacos `dbass.appId`），语义分析未给出物理库名证据，无法逐字确认。涉及表（ca_certification_info / cust_certification_info / cust_person_info / cust_company_info / wx_work_user）的实际物理库名需补充 [DB] 证据后修订。
---END REVIEW---

---REVIEW: rule | CA 上送完整性校验 ---
规则 `CA 上送完整性校验` 的 content 在语义分析原文中以 `；intent` 截断，无法确定「意愿认证」维度的完整校验条件（是否要求 intent_h5_face_json / intent_sms_json 至少一项，以及 CHANNEL_OPENAPI 豁免的精确边界）。当前 ground 块只写入已确证部分，完整清单待补。
---END REVIEW---