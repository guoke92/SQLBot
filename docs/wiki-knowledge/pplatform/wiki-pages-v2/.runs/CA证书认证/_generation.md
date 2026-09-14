---FILE: tables/ca_certification_info.md ---
---
type: table
title: CA 认证信息表（ca_certification_info）
page_key: ca_certification_info
domain: CA证书认证
status: draft
aliases: [CA认证信息, 一证四步落库表, ca_certification_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - code:CaActivationApplication.java
  - code:CaCertificationRealNameApplication.java
  - code:CaCertificationConfirmApplication.java
  - code:CaCertificationPreCheckApplication.java
  - db:ca_certification_info
contract_version: "0.1"
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
fields:
  - name: cust_id
    type: unknown
    desc: 报数主体企业id（产融 cust_company_info.id）；head_company_data='Y' 行取总公司 cust_head_company_info.id
    dict: ""
  - name: cust_type
    type: unknown
    desc: 客户类型，代码落库值恒为字面量 COMPANY（CUST_TYPE_COMPANY），非数字字典键
    dict: ""
  - name: data_source
    type: unknown
    desc: 数据来源，.name() 落库：OPERATION_PLATFORM（运营中台推送）/ FBP_PORTAL（产融门户一证四步）/ CHANNEL_OPENAPI（开放渠道）
    dict: ""
  - name: data_date
    type: unknown
    desc: 数据日期 yyyyMMdd；createOrGetByKey 缺省取当天，CaActivationApplication 的 resolvePersistRowDataDate 已定义但无调用点
    dict: ""
  - name: head_company_data
    type: unknown
    desc: 是否总公司行：Y=总公司主体行（来源 head_company_info），N=本企业/分公司自身行；用字面量 'Y'/'N' 写入
    dict: ""
  - name: op_type
    type: unknown
    desc: 操作类型，代码仅写 INSERT（OP_TYPE_INSERT），UPDATE 未使用
    dict: ""
  - name: submit_status
    type: unknown
    desc: 上送签章中台（cbsSubmitBizData）状态，.name() 落库 PENDING/SUCCESS/FAIL
    dict: ""
  - name: batch_no
    type: unknown
    desc: 批次流水号 INC_<yyyyMMddHHmmssSSS>_<6位hex>；已不再进入幂等键，总/分公司两行各自独立
    dict: ""
  - name: notify_agreement_json
    type: unknown
    desc: 协议告知留痕：CfcaNotifyAgreementItemDto 列表序列化为 JSONArray（固定数组结构）
    dict: ""
  - name: enterprise_four_json
    type: unknown
    desc: 企业实名核验 JSON；四要素(ENTERPRISE_FOUR)与企业三要素(ENTERPRISE_THREE)共用本列
    dict: ""
  - name: police_two_json
    type: unknown
    desc: 被授权人公安二要素（POLICE_TWO）核验 JSON（含请求/响应快照）
    dict: ""
  - name: intent_sms_json
    type: unknown
    desc: 短信意愿（SMS_CODE）留痕 JSON
    dict: ""
  - name: intent_h_face_json
    type: unknown
    desc: H5 刷脸意愿（H5_FACE）留痕 JSON，含 similarity / videoPath
    dict: ""
  - name: file_refs_json
    type: unknown
    desc: 附件引用：embeddedFiles[{multipartField,path}]，上送前 path 临时转 HTTP 下载链，库内保留 COS key
    dict: ""
  - name: sign_platform_result
    type: unknown
    desc: 签章中台上送的请求+响应（或异常）原文，用于事后回查
    dict: ""
  - name: submit_time
    type: unknown
    desc: 上送签章中台完成时间（writeSubmitResult 写入）
    dict: ""
  - name: enable
    type: unknown
    desc: 逻辑有效标识，创建恒为 Y
    dict: ""
```

关联页面：[[ca_submit_status]]、[[incremental_idempotent_key]]、[[head_company_row]]、[[submit_completeness]]、[[incremental_idempotent_row]]、[[submit_idempotent_short_circuit]]、[[enterprise_four_elements]]、[[notify_agreement]]、[[batch_no]]。

---END FILE---

---FILE: tables/ca_cfca_upgrade_report.md ---
---
type: table
title: CFCA 升级授权书报表（ca_cfca_upgrade_report）
page_key: ca_cfca_upgrade_report
domain: CA证书认证
status: draft
aliases: [CA升级授权书报表, ca_cfca_upgrade_report]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:ca_cfca_upgrade_report
contract_version: "0.1"
---

ca_cfca_upgrade_report 记录 [[ca_upgrade_auth|CA 升级授权书]] 的出具情况：谁是被授权人、企业以什么角色出具、影像来自哪个来源系统、由哪个业务模块触发、是否已经触发待办/消息。它与 [[ca_certification_info]] 的 file_refs_json 是"业务实体"与"附件引用"的关系——授权书的文件路径最终落在 ca_certification_info.file_refs_json 的 embeddedFiles 里（serviceKey=CaUpgradeAuth），本表记录的是授权书这笔业务事实本身。

使用本表时有两点必须注意：company_type 是企业角色枚举（CORE/SUPPLIER/FINANCE/PLATFORM_COMPANY 等），不是客户类型；biz_module 在存量数据中存在 CFCA_CA_UPGRADE 与中文「CFCA证书升级」两种写法，做维度汇总时需先归一。

## 需求背景

升级授权书在运营侧存在多个影像来源系统（ACFLOW/RVSFACTOR_PC/ORDER/国内信用证），本表的 source_system 即用于区分；todo_triggered 用于标识是否已推动待办/消息。授权书盖章的前置条件与 [[non_build_success_no_ca]] 中描述的建档状态要求相关（要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)）。

## 版本演进

- v0：首次沉淀本表语义。biz_module 的中英双写法属历史遗留，尚未统一。

```ground:table
table: ca_cfca_upgrade_report
fields:
  - name: authorized_user_name
    type: unknown
    desc: CA 升级授权书被授权人姓名
    dict: ""
  - name: company_type
    type: unknown
    desc: 企业角色（CORE/SUPPLIER/FINANCE/PLATFORM_COMPANY 等）
    dict: ""
  - name: source_system
    type: unknown
    desc: 升级授权书影像来源系统（ACFLOW/RVSFACTOR_PC/ORDER/国内信用证）
    dict: ""
  - name: biz_module
    type: unknown
    desc: 业务模块标识，实际存在 CFCA_CA_UPGRADE 与中文 CFCA证书升级 两种写法
    dict: ""
  - name: todo_triggered
    type: unknown
    desc: 是否已触发待办/消息 Y/N
    dict: ""
```

关联页面：[[ca_upgrade_auth]]、[[ca_certification_info]]、[[authorized_person]]、[[non_build_success_no_ca]]。

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 客户企业信息表（cust_company_info）
page_key: cust_company_info
domain: CA证书认证
status: draft
aliases: [企业信息, 产融企业主表, cust_company_info]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - code:CaCertificationPreCheckApplication.java
  - code:CfcaOneCertFourStepPackageApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

cust_company_info 在 CA 认证主题中承担"是否要开通、当前开通到哪一步"的主数据角色：need_register_ca 是意愿位，ca_register_status 是 CFCA 数字证书的注册结果位。两者共同构成 [[need_register_ca_judgement|需开通 CFCA 判定口径]]，并直接决定 [[ca_register_status]] 状态机的迁移。

需要注意本表同时承载另一条签章渠道（上上签/BS）的平行字段 need_register_bs / bs_register_status，二者在 isOpenCa 中分别组装 serviceKeys（DATA_SOURCE_CFCA_AUTH / DATA_SOURCE_BS_AUTH），不可互换，详见 [[ca_certificate]]。此外 CA 相关流转还会读取本表的 cust_status、cust_build_status（见 [[company_in_change_forbid_ca]]、[[non_build_success_no_ca]]）。

## 需求背景

CA 开通链路的准入判断大量依赖本表：管理员身份校验取 cust_person_info（见 [[ca_open_operator_must_be_admin]]），存量企业打包取 ca_register_status='Y'（见 [[legacy_package_companies]]），企业变更中则直接阻断。签章中台报失效时，本表的 ca_register_status 会被回写为 N（见 [[sign_center_cert_status]]）。

## 版本演进

- v0：首次沉淀 CA 相关的两个字段语义。bs_register_status 属另一渠道，本主题仅在边界说明中引用。

```ground:table
table: cust_company_info
fields:
  - name: ca_register_status
    type: unknown
    desc: CFCA 数字证书注册状态（Y=已注册/N=未注册/P=处理中），签章中台失效时被回写为 N
    dict: ""
  - name: need_register_ca
    type: unknown
    desc: 是否需要开通 CA 的意愿位，N 时直接判定无需开通
    dict: ""
```

关联页面：[[ca_certificate]]、[[ca_register_status]]、[[need_register_ca_judgement]]、[[legacy_package_companies]]、[[authorized_person]]。

---END FILE---

---FILE: processes/ca_submit_status.md ---
---
type: process
title: CA 签章中台上送状态（ca_certification_info.submit_status）
page_key: ca_submit_status
domain: CA证书认证
status: draft
aliases: [submit_status, 上送状态, 签章中台上送状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - code:CaCertificationIntentSmsApplication.java
  - db:ca_certification_info
contract_version: "0.1"
---

这是本系统到签章中台「一次上送」的状态位，落库为枚举 .name()：PENDING / SUCCESS / FAIL。它只描述一次上送动作的结果，不代表证书生命周期——证书侧的状态是另一套外部态，见 [[sign_center_cert_status]] 与 [[cert_status]]。

状态机有三个关键性质：第一，PENDING 同时是 [[incremental_idempotent_key|增量落库幂等键]] 的一部分，因此"还在 PENDING"的行会被复用而不是新建行；第二，SUCCESS 是终态，再次调用 submitToSignCenter 会短路返回成功（见 [[submit_idempotent_short_circuit]]），协议确认页因此可重复点击；第三，SUCCESS 之后即使再发生意愿落库动作，状态也不回退。

## 需求背景

状态迁移由 writeSubmitResult 统一写入：中台返回 DBaaS code in {0,200} 且业务体 biz.status=SAVED 记为 SUCCESS，其余异常或非 SAVED 记为 FAIL。FAIL 行可被 markFailed 再次置失败（补偿/人工），但不回到 PENDING。AMS 复用数据时按 [[submit_success|上送完成口径]] 取最新一条 SUCCESS 行重新组装上报。

## 版本演进

- v0：首次固化为三态。历史数据中 op_type 的 UPDATE 分支未使用、batch_no 退出幂等键，均与上送状态复用行逻辑（见 [[incremental_idempotent_row]]）相关。

```ground:process
name: CA 签章中台上送状态
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
  - from: PENDING
    event: "cbsSubmitBizData 返回 DBaaS code in {0,200} 且 biz.status=SAVED"
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter/writeSubmitResult"
  - from: PENDING
    event: "cbsSubmitBizData 抛异常或业务体非 SAVED"
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter/writeSubmitResult"
  - from: PENDING
    event: "markFailed 人工/补偿置失败"
    to: FAIL
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#markFailed"
  - from: SUCCESS
    event: "再次 submitToSignCenter（幂等短路，不重复上送）"
    to: SUCCESS
    evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter（CA_CERT_SUBMIT_ALREADY_SUCCESS）"
  - from: SUCCESS
    event: "短信意愿再次落库（拒绝）"
    to: SUCCESS
    evidence: "code_path:CaCertificationIntentSmsApplication.java#persistIntentSmsAfterVerify"
```

关联页面：[[ca_certification_info]]、[[submit_success]]、[[incremental_idempotent_key]]、[[submit_idempotent_short_circuit]]、[[submit_completeness_check]]、[[cert_status]]。

---END FILE---

---FILE: processes/ca_register_status.md ---
---
type: process
title: 企业 CA 注册状态（cust_company_info.ca_register_status）
page_key: ca_register_status
domain: CA证书认证
status: draft
aliases: [ca_register_status, CA注册状态, 证书注册状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - code:CaCertificationConfirmApplication.java
  - code:CaCertificationPreCheckApplication.java
  - code:CaOpenCaApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

企业侧的 CA 注册生命周期位：Y=已注册、N=未注册、P=处理中。它与上送状态 [[ca_submit_status]] 是两件事：本状态描述企业在签章中台的登记/证书有效性，上送状态只描述一条 ca_certification_info 行是否已成功推送给中台。中台证书态到本状态的归一由 [[sign_center_cert_status]] 负责。

## 需求背景

注册成功（custDocFacade.openCa / cbsCompanyRegister）后回写 Y；预检发现证书 CANCELLED/EXPIRED/FAIL 或中台登记企业名与库中不一致时，resetCaRegisterStatusToN 把 Y 回写为 N，从而让企业在下一轮 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 中被重新判定为需开通。需要注意 CaOpenCaApplication.isOpenCa 中还有一条"仅内存视为未开通"的路径（caEval.isInvalid()），不落库，因此库里仍是 Y。

## 版本演进

- v0：首次固化三态与回写规则。存量企业打包口径 [[legacy_package_companies]] 以 ca_register_status='Y' 为筛选起点。

```ground:process
name: 企业 CA 注册状态
field: cust_company_info.ca_register_status
states:
  - value: Y
    label: 已注册
    source: code_enum
  - value: N
    label: 未注册
    source: code_enum
  - value: P
    label: 处理中
    source: code_enum
transitions:
  - from: N
    event: "custDocFacade.openCa / cbsCompanyRegister 注册成功"
    to: Y
    evidence: "code_path:CaActivationApplication.java#activateByOpCompanyId（第 5 步注释）；CaCertificationConfirmApplication.java#confirm"
  - from: P
    event: "注册成功回写"
    to: Y
    evidence: "code_path:CaCertificationConfirmApplication.java#confirm（读取 caRegisterStatus）"
  - from: Y
    event: "pre4Step 预检发现证书 CANCELLED/EXPIRED/FAIL 或中台登记企业名与库中不一致"
    to: N
    evidence: "code_path:CaCertificationPreCheckApplication.java#resetCaRegisterStatusToN"
  - from: Y
    event: "caEval.isInvalid() 时局部视为未开通（仅内存，不落库）"
    to: N
    evidence: "code_path:CaOpenCaApplication.java#isOpenCa"
```

关联页面：[[cust_company_info]]、[[ca_submit_status]]、[[sign_center_cert_status]]、[[cert_status]]、[[ca_certificate]]、[[need_register_ca_judgement]]。

---END FILE---

---FILE: processes/sign_center_cert_status.md ---
---
type: process
title: 签章中台证书状态归一（外部态，非落库字段）
page_key: sign_center_cert_status
domain: CA证书认证
status: draft
aliases: [certStatus, rawCertStatus, 中台证书状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
---

签章中台返回的原始证书态（SUCCESS / NEW_APPLY / INVALID / TIME_OUT 等）由 mapSignCenterStatus 归一为 NORMAL / APPLYING / CANCELLED / EXPIRED / FAIL / UNKNOWN 六类。这是一个**归一化视图**，不落 ca_certification_info 的列：它的用途是驱动 [[ca_register_status]] 的回写（CANCELLED/EXPIRED/FAIL 触发置 N）以及 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的失效判断。

## 需求背景

预检链路把"未注册记录"也按失效处理，因此 CANCELLED 的 label 同时覆盖注销/作废与查无记录两种情况；UNKNOWN 表示查询失败，属于需要人工/重试的分支，不应被当作有效态。该归一结果与本地上送态 [[ca_submit_status]] 不可互换，详见 [[cert_status]]。

## 版本演进

- v0：首次记录归一集合。原始态到归一态的映射表尚未逐值展开，纳入后续版本补充。

```ground:process
name: 签章中台证书状态（外部态归一化，非落库字段）
field: cfca_sign_center.cert_status
states:
  - value: NORMAL
    label: 正常
    source: code_const
  - value: APPLYING
    label: 申请中
    source: code_const
  - value: CANCELLED
    label: 注销/作废（含未注册记录按失效处理）
    source: code_const
  - value: EXPIRED
    label: 到期失效
    source: code_const
  - value: FAIL
    label: 申请失败
    source: code_const
  - value: UNKNOWN
    label: 未知/查询失败
    source: code_const
transitions: []
note: 由 mapSignCenterStatus 把中台 SUCCESS/NEW_APPLY/INVALID/TIME_OUT 等归一到上述集合（CaCertificationPreCheckApplication），不落 ca_certification_info 列
```

关联页面：[[ca_register_status]]、[[cert_status]]、[[ca_submit_status]]、[[cust_company_info]]。

---END FILE---

---FILE: calibers/operation_platform_source.md ---
---
type: caliber
title: 运营中台推送来源口径
page_key: operation_platform_source
domain: CA证书认证
status: draft
aliases: [OPERATION_PLATFORM, 运营中台来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - db:ca_certification_info
contract_version: "0.1"
---

用于圈定由运营中台 notifyActivateCa 主动通知触发的 CA 落库行。该来源的行由 persistActivateData 写入，且在分公司场景下会并行上送 N/Y 两行（与 [[confirm_submit_own_row_only]] 描述的协议确认链路不同）。统计与排障都应以本口径为基础，避免与门户来源混淆。

## 需求背景

运营推送链路标 @Transactional(NOT_SUPPORTED)，中台调用在事务外（见 [[sign_center_call_outside_tx]]），因此该来源的行出现"已建行未上送"属于预期内的中间态。

## 版本演进

- v0：首次固化谓词与分布值。

```ground:caliber
name: 运营中台推送来源口径
predicate: "ca_certification_info.data_source = 'OPERATION_PLATFORM'"
scope: 运营中台 notifyActivateCa 主动通知触发的 CA 落库行（db 分布 453）
evidence: "code_path:CaActivationApplication.java#persistActivateData + db_dist:OPERATION_PLATFORM=453"
```

关联页面：[[ca_certification_info]]、[[fbp_portal_source]]、[[channel_openapi_source]]、[[ca_submit_status]]。

---END FILE---

---FILE: calibers/fbp_portal_source.md ---
---
type: caliber
title: 产融门户一证四步来源口径
page_key: fbp_portal_source
domain: CA证书认证
status: draft
aliases: [FBP_PORTAL, 门户一证四步来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationRealNameApplication.java
  - db:ca_certification_info
contract_version: "0.1"
---

圈定门户 /cust-web/ca/realName/verify 入口落库的 CA 认证行。该来源由 initCertificationRow 建行，是"一证四步"的标准人机链路：协议告知、企业实名、被授权人公安二要素、意愿留痕、附件引用都需要在 [[submit_completeness|一证四步上送完整性口径]] 下齐备后才能上送。

## 需求背景

门户来源是三类来源中体量最大的一类，排查上送失败时通常以本口径先取样，再看 [[ca_submit_status]] 与 sign_platform_result。

## 版本演进

- v0：首次固化谓词与分布值。

```ground:caliber
name: 产融门户一证四步来源口径
predicate: "ca_certification_info.data_source = 'FBP_PORTAL'"
scope: 门户 /cust-web/ca/realName/verify 落库行（db 分布 865）
evidence: "code_path:CaCertificationRealNameApplication.java#initCertificationRow + db_dist:FBP_PORTAL=865"
```

关联页面：[[ca_certification_info]]、[[operation_platform_source]]、[[submit_completeness]]、[[enterprise_four_elements]]。

---END FILE---

---FILE: calibers/channel_openapi_source.md ---
---
type: caliber
title: 开放渠道来源口径（免意愿校验）
page_key: channel_openapi_source
domain: CA证书认证
status: draft
aliases: [CHANNEL_OPENAPI, 开放渠道来源]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

圈定开放渠道 OpenAPI 落库的 CA 认证行，并标记它与门户来源在**校验强度**上的差异：assertCompleteForSubmit 对本来源跳过 intent_sms_json / intent_h_face_json 的必填校验。这意味着渠道侧自行保证意愿，库里可能缺席意愿留痕列，做完整性看板时不能把"意愿列为空"一律判为脏数据。

## 需求背景

上送完整性的其余要求（协议告知 JSON 必填、实名 JSON 至少一项、file_refs_json 非空）对本来源仍然生效，见 [[submit_completeness_check]]。

## 版本演进

- v0：首次固化谓词、豁免范围与分布值。

```ground:caliber
name: 开放渠道来源口径（免意愿校验）
predicate: "ca_certification_info.data_source = 'CHANNEL_OPENAPI'"
scope: assertCompleteForSubmit 对本来源跳过 intent_sms_json/intent_h_face_json 必填校验
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit + db_dist:CHANNEL_OPENAPI=49"
```

关联页面：[[ca_certification_info]]、[[submit_completeness]]、[[submit_completeness_check]]、[[fbp_portal_source]]。

---END FILE---

---FILE: calibers/incremental_idempotent_key.md ---
---
type: caliber
title: 增量落库幂等键
page_key: incremental_idempotent_key
domain: CA证书认证
status: draft
aliases: [幂等键, createOrGetByKey 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

认定"这一行是不是已存在的行"的口径：命中条件为 (cust_id, data_date, head_company_data, submit_status=PENDING)，batch_no 不参与。命中即复用旧行，未命中才新建并生成 batch_no。由此产生两个直接后果：同一企业同日同主体类型重复触发不会产生重复行；跨日重发（data_date 变化）会产生新行。

## 需求背景

本口径与 [[batch_no]] 的边界是历史上最容易误判的地方——batch_no 是新建行时的唯一流水号（INC_ 前缀），但已从幂等键中移除；总/分公司两行各自独立，靠 head_company_data 区分。落地规则见 [[incremental_idempotent_row]]。

## 版本演进

- v0：首次固化幂等键构成，并记录 batch_no 退出幂等键这一变更。

```ground:caliber
name: 增量落库幂等键
predicate: "ca_certification_info.submit_status = 'PENDING'"
scope: "幂等命中条件为 (cust_id, data_date, head_company_data, submit_status=PENDING)；batch_no 不参与；因此跨日重发会产生新行"
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey"
```

关联页面：[[ca_certification_info]]、[[batch_no]]、[[incremental_idempotent_row]]、[[head_company_row]]、[[head_company_data]]。

---END FILE---

---FILE: calibers/head_company_row.md ---
---
type: caliber
title: 总公司主体行口径
page_key: head_company_row
domain: CA证书认证
status: draft
aliases: [headCompanyData=Y, 总公司行]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationHeadCompanySupport.java
  - db:ca_certification_info
contract_version: "0.1"
---

圈定分公司场景下以总公司主体信息落库的独立行：head_company_data='Y'。这类行的 cust_id 是总公司 id（cust_head_company_info.id），不是分公司在 cust_company_info 的 id，因此任何按 cust_id 关联企业主数据的查询都必须显式带上本口径，否则会把总公司行错配到分公司主体上。详见 [[head_company_data]]。

## 需求背景

总/分公司两行各自独立生成 batch_no，且在 [[incremental_idempotent_key|增量落库幂等键]] 中靠 head_company_data 区分。协议确认阶段只有 N 主行会被上送，见 [[confirm_submit_own_row_only]]；运营推送链路才会并行上送 N/Y 两行。

## 版本演进

- v0：首次固化谓词与分布值（Y=101 / 总行数 1367）。

```ground:caliber
name: 总公司主体行口径
predicate: "ca_certification_info.head_company_data = 'Y'"
scope: 分公司场景下以总公司四要素落库的独立行（db 分布 101/1367）
evidence: "code_path:CaCertificationHeadCompanySupport.java + db_dist:Y=101"
```

关联页面：[[ca_certification_info]]、[[head_company_data]]、[[incremental_idempotent_key]]、[[confirm_submit_own_row_only]]。

---END FILE---

---FILE: calibers/legacy_package_companies.md ---
---
type: caliber
title: 存量打包企业口径
page_key: legacy_package_companies
domain: CA证书认证
status: draft
aliases: [存量打包, queryEligibleCompanies 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CfcaOneCertFourStepPackageApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

圈定可以进入一证四步批量打包的存量企业：ca_register_status='Y'，同时要求 enable='Y'、update_time >= since、identify_style != 'SIMPLE'（简易认证不打包）。当请求指定了 custIds 时，改为在内存中过滤，SQL 侧的筛选条件不再全量生效——这是做口径核对时最容易漏掉的一条分支。

## 需求背景

本口径是"已注册企业复用"的入参集合，与 [[need_register_ca_judgement|需开通 CFCA 判定口径]]（面向未注册/处理中企业）互为补集，二者共用 cust_company_info 的 CA 字段但方向相反。

## 版本演进

- v0：首次固化筛选条件与内存过滤分支。

```ground:caliber
name: 存量打包企业口径
predicate: "cust_company_info.ca_register_status = 'Y'"
scope: 同时要求 enable='Y'、update_time >= since、identify_style != 'SIMPLE'（简易认证不打包）；指定 custIds 时改为内存过滤
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java#queryEligibleCompanies"
```

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[need_register_ca_judgement]]、[[simple_auth_forbid_ca]]。

---END FILE---

---FILE: calibers/need_register_ca_judgement.md ---
---
type: caliber
title: 需开通 CFCA 判定口径
page_key: need_register_ca_judgement
domain: CA证书认证
status: draft
aliases: [needOpenCa, 需开通 CA 判定]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

判定一家企业当前是否需要发起 CFCA 开通：意愿位 need_register_ca='Y'，且（ca_register_status in ('N','P') 或签章中台判定 CA 失效）；否则 needOpenCa=N。中台失效判定来自 [[sign_center_cert_status]] 的归一结果，且 isOpenCa 中存在"仅内存视为未开通、不回写库"的分支。

## 需求背景

本口径与 [[legacy_package_companies|存量打包企业口径]] 是互补的两个集合；与 BS（上上签）渠道的判定平行但独立，两者在 isOpenCa 中分别组装 serviceKeys（DATA_SOURCE_CFCA_AUTH / DATA_SOURCE_BS_AUTH），边界见 [[ca_certificate]]。建档未成功时直接判 N，见 [[non_build_success_no_ca]]。

## 版本演进

- v0：首次固化判定表达式与内存分支。

```ground:caliber
name: 需开通 CFCA 判定口径
predicate: "cust_company_info.need_register_ca = 'Y'"
scope: "且 ca_register_status in ('N','P') 或签章中台判定 CA 失效；否则 needOpenCa=N"
evidence: "code_path:CaOpenCaApplication.java#isOpenCa"
```

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[legacy_package_companies]]、[[non_build_success_no_ca]]、[[ca_certificate]]。

---END FILE---

---FILE: calibers/submit_success.md ---
---
type: caliber
title: 上送完成口径
page_key: submit_success
domain: CA证书认证
status: draft
aliases: [SUCCESS 行, findLatestSuccessRow 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

"这单算上送完成"的判定：submit_status='SUCCESS'。AMS 复用数据时并不看最新一行，而是按 findLatestSuccessRow 取最新一条 SUCCESS 行重新组装上报，因此 FAIL/PENDING 行不会污染复用结果。

## 需求背景

本口径直接来自 [[ca_submit_status]] 状态机的终态，并与 [[submit_idempotent_short_circuit]] 互为因果：正因为 SUCCESS 是终态且会短路，取 SUCCESS 行复用才是安全的。

## 版本演进

- v0：首次固化判定与复用语义。

```ground:caliber
name: 上送完成口径
predicate: "ca_certification_info.submit_status = 'SUCCESS'"
scope: AMS 复用数据时取最新一条 SUCCESS 行重新组装上报（findLatestSuccessRow）
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#findLatestSuccessRow"
```

关联页面：[[ca_submit_status]]、[[submit_idempotent_short_circuit]]、[[ca_certification_info]]。

---END FILE---

---FILE: calibers/submit_completeness.md ---
---
type: caliber
title: 一证四步上送完整性口径
page_key: submit_completeness
domain: CA证书认证
status: draft
aliases: [上送完整性, assertCompleteForSubmit 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

判定一行 CA 认证数据是否"材料齐备、可以上送签章中台"：notify_agreement_json 非空，且（enterprise_four_json 或 police_two_json 至少一项），且（intent_sms_json 或 intent_h_face_json 至少一项，CHANNEL_OPENAPI 来源除外），且 file_refs_json 非空。缺项即阻断上送。

## 需求背景

本口径的三处"至少一项"设计，对应真实业务上的可选路径：企业实名四要素/三要素共用 [[enterprise_four_elements|enterprise_four_json]]，意愿可走短信或 H5 刷脸，被授权人核验落 [[ca_certification_info]] 的 police_two_json。开放渠道豁免意愿校验的边界见 [[channel_openapi_source]]。执行侧规则见 [[submit_completeness_check]]。

## 版本演进

- v0：首次固化四项必要条件与一项豁免。

```ground:caliber
name: 一证四步上送完整性口径
predicate: "ca_certification_info.notify_agreement_json != null"
scope: 且（enterprise_four_json 或 police_two_json 至少一项）且（intent_sms_json 或 intent_h_face_json 至少一项，CHANNEL_OPENAPI 除外）且 file_refs_json 非空
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit"
```

关联页面：[[ca_certification_info]]、[[submit_completeness_check]]、[[channel_openapi_source]]、[[notify_agreement]]、[[enterprise_four_elements]]、[[ca_upgrade_auth]]。

---END FILE---

---FILE: concepts/ca_certificate.md ---
---
type: concept
title: CA（数字证书）
page_key: ca_certificate
domain: CA证书认证
status: draft
aliases: [CFCA, 一证四步, 电子签章开通]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - code:CustCompanyCaPolicy.java
contract_version: "0.1"
maps_to: cust_company_info.ca_register_status
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_ca
adjudication: boundary
also_confused_with:
  - cust_company_info.bs_register_status
---

CA（数字证书）在本主题里特指 CFCA 渠道的电子签章开通能力，业务口头语包括"CFCA""一证四步""电子签章开通"。它落到数据上是 cust_company_info 的意愿位与注册状态位两个字段，链路状态由 [[ca_register_status]] 描述，判定口径见 [[need_register_ca_judgement]]。

**边界（boundary）**：need_register_ca / ca_register_status 属 CFCA 数字证书；need_register_bs / bs_register_status（上上签/BS）属另一签章渠道，二者在 isOpenCa 中分别组装 serviceKeys（DATA_SOURCE_CFCA_AUTH / DATA_SOURCE_BS_AUTH），不可互换。凡把 bs_register_status 当作 CFCA 状态统计的结论都应作废。

## 需求背景

"一证四步"指协议告知、企业实名核验、被授权人核验、意愿留痕四类材料齐备后上送签章中台；材料落在 [[ca_certification_info]]，上送结果落 [[ca_submit_status]]，中台证书态归一为 [[sign_center_cert_status]]。简易认证企业被强制不纳入 CA，见 [[simple_auth_forbid_ca]]。

## 版本演进

- v0：首次区分 CFCA 与 BS 两条渠道的字段边界。中台证书态与本地上送态的语义差在 [[cert_status]] 中单独沉淀。

关联页面：[[cust_company_info]]、[[ca_register_status]]、[[need_register_ca_judgement]]、[[sign_center_cert_status]]、[[cert_status]]、[[ca_certification_info]]。

---END FILE---

---FILE: concepts/notify_agreement.md ---
---
type: concept
title: 协议告知
page_key: notify_agreement
domain: CA证书认证
status: draft
aliases: [notifyAgreementList, notify_agreement_json]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.notify_agreement_json
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.file_refs_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.file_refs_json
---

协议告知指用户在上送前逐条确认的协议清单留痕，落库为 notify_agreement_json：CfcaNotifyAgreementItemDto 列表序列化成 JSONArray（固定数组结构）。它是 [[submit_completeness|一证四步上送完整性口径]] 中唯一"必须非空"的前置项。

**边界（boundary）**：协议告知是留痕 JSON 数组；同一条协议的文件路径另有 embeddedFiles 映射进 file_refs_json，两者通过 serviceKey/agreementUrl 关联但不共列。因此"协议告知为空"与"协议文件缺失"是两个独立故障，不能相互推断。

## 需求背景

协议清单中至少包含数字证书服务协议（CFCA_Auth）与 [[ca_upgrade_auth|CA 升级授权书]]（CaUpgradeAuth）等不同 serviceKey 的条目，filterUpgradeAuthContracts 在选择升级授权书时还需排除 CFCA_Auth 文件，详见 [[ca_upgrade_auth]]。

## 版本演进

- v0：首次固化 JSONArray 结构（固定数组，非对象）与 file_refs_json 的分工。

关联页面：[[ca_certification_info]]、[[ca_upgrade_auth]]、[[submit_completeness]]、[[submit_completeness_check]]。

---END FILE---

---FILE: concepts/enterprise_four_elements.md ---
---
type: concept
title: 企业实名四要素
page_key: enterprise_four_elements
domain: CA证书认证
status: draft
aliases: [ENTERPRISE_FOUR, 企业三要素 ENTERPRISE_THREE, 企业实名核验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.enterprise_four_json
field_targets:
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.police_two_json
---

企业实名四要素（ENTERPRISE_FOUR）指企业侧的名称/证件等要素核验，其请求与响应留痕落在 enterprise_four_json。

**边界（boundary）**：四要素与三要素（ENTERPRISE_THREE）在 updateRealNameByMethod 中同样落到 enterprise_four_json（靠 verifyMethod 区分），个人侧公安二要素（POLICE_TWO）落 police_two_json。因此"一列一方法"的直觉是错的：看到 enterprise_four_json 有值不代表走的是四要素核验，需回看 verifyMethod。

## 需求背景

上送时两类实名 JSON 满足"至少一项"即可通过 [[submit_completeness|一证四步上送完整性口径]]；两者都会被 [[submit_data_length_truncate]] 的 1000 字符限制裁剪。

## 版本演进

- v0：首次记录四要素与三要素共列（靠 verifyMethod 区分）这一事实。

关联页面：[[ca_certification_info]]、[[submit_completeness]]、[[submit_data_length_truncate]]、[[authorized_person]]。

---END FILE---

---FILE: concepts/authorized_person.md ---
---
type: concept
title: 被授权人
page_key: authorized_person
domain: CA证书认证
status: draft
aliases: [authPerson, 经办人, 管理员]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
maps_to: cust_person_info.user_type
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
  - cust_company_info.legal_name
adjudication: boundary
also_confused_with:
  - cust_company_info.legal_name
---

被授权人（业务上常称 authPerson、经办人、管理员）取 cust_person_info：user_type=admin + enable=Y + companyType=登录角色，且 ref_cust_company_info 指向本企业 code。

**边界（boundary）**：法人为 cust_company_info 的法人三件套（legal_name 等），二者不可互换。同一次认证中两类人可能同时出现：H5 刷脸意愿优先取法人命中数据，公安二要素取被授权人。因此"意愿留痕里的人"和"二要素核验里的人"未必是同一个自然人，核对数据时需分别取数。

## 需求背景

被授权人身份还会决定能否进入一证四步：CA 开通操作人必须是企业管理员（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），见 [[ca_open_operator_must_be_admin]]。

## 版本演进

- v0：首次沉淀被授权人取数条件与法人边界。

关联页面：[[ca_open_operator_must_be_admin]]、[[enterprise_four_elements]]、[[ca_certification_info]]、[[ca_upgrade_auth]]。

---END FILE---

---FILE: concepts/head_company_data.md ---
---
type: concept
title: 总公司行标识（head_company_data）
page_key: head_company_data
domain: CA证书认证
status: draft
aliases: [headCompanyData=Y, 总公司行标识]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationHeadCompanySupport.java
  - code:CaCertificationConfirmApplication.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.head_company_data
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.cust_id
adjudication: boundary
also_confused_with:
  - ca_certification_info.cust_id
---

head_company_data 标记一行认证数据的主体归属：Y=总公司主体行（来源 head_company_info），N=本企业/分公司自身行，用字面量 'Y'/'N' 写入。

**边界（boundary）**：Y 行 cust_id 是总公司 id（cust_head_company_info.id），不是分公司 cust_company_info.id；N/Y 两行靠 cust_id+data_date+batch_no+head_company_data 共同定位。因此"cust_id 相同"绝不能作为合并两行的依据，反过来也不能因为 cust_id 不同就认为不是同一笔业务。

## 需求背景

口径见 [[head_company_row|总公司主体行口径]]；协议确认阶段只有 N 行会被上送（[[confirm_submit_own_row_only]]），而运营推送链路会并行上送两行（[[operation_platform_source]]）。

## 版本演进

- v0：首次固化字面量写入方式与 cust_id 语义差异。

关联页面：[[ca_certification_info]]、[[head_company_row]]、[[confirm_submit_own_row_only]]、[[incremental_idempotent_key]]。

---END FILE---

---FILE: concepts/ca_upgrade_auth.md ---
---
type: concept
title: CA 升级授权书
page_key: ca_upgrade_auth
domain: CA证书认证
status: draft
aliases: [CaUpgradeAuth, otherAgreementFile1]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaUpgradeAuthApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.file_refs_json
field_targets:
  - ca_certification_info.file_refs_json
  - ca_certification_info.notify_agreement_json
adjudication: boundary
also_confused_with:
  - ca_certification_info.notify_agreement_json
---

CA 升级授权书（serviceKey=CaUpgradeAuth，门户侧字段常写作 otherAgreementFile1）是企业在升级场景下出具的一份授权文件，其文件路径落在 file_refs_json 的 embeddedFiles（multipartField=CaUpgradeAuth），对应协议条目则在 notify_agreement_json 中留痕。

**边界（boundary）**：它与数字证书服务协议 CFCA_Auth（agreementFile1）是两份不同材料——两者 serviceKey 不同，在 notify_agreement_json 的 data.service_key 与 embeddedFiles.multipartField 上分别落位，filterUpgradeAuthContracts 还需排除 CFCA_Auth 文件。把 CFCA_Auth 的文件当成升级授权书，或反之，都会导致上送材料错配。业务事实记录在 [[ca_cfca_upgrade_report]]。

## 需求背景

升级授权书盖章要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)，与 [[non_build_success_no_ca]] 同源；办理入口为 processUpgradeAuthOnOpsNameChange。

## 版本演进

- v0：首次明确 CaUpgradeAuth 与 CFCA_Auth 的 serviceKey 分工与排除逻辑。

关联页面：[[ca_certification_info]]、[[ca_cfca_upgrade_report]]、[[notify_agreement]]、[[non_build_success_no_ca]]。

---END FILE---

---FILE: concepts/cert_status.md ---
---
type: concept
title: 签章中台证书状态
page_key: cert_status
domain: CA证书认证
status: draft
aliases: [certStatus, rawCertStatus]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
maps_to: cust_company_info.ca_register_status
field_targets:
  - cust_company_info.ca_register_status
  - ca_certification_info.submit_status
adjudication: boundary
also_confused_with:
  - ca_certification_info.submit_status
---

签章中台返回的证书生命周期状态，经 mapSignCenterStatus 归一为 NORMAL / APPLYING / CANCELLED / EXPIRED / FAIL / UNKNOWN，详见 [[sign_center_cert_status]]。

**边界（boundary）**：中台 NORMAL/APPLYING 视为产融 ca_register_status 有效；CANCELLED/EXPIRED/FAIL 触发回写 N；submit_status 只描述本系统到中台的一次上送，不代表证书生命周期。因此不能用 [[ca_submit_status]] 的 SUCCESS 推断证书有效，也不能用证书 CANCELLED 推断上送失败——两者是不同维度的事件。

## 需求背景

归一结果是 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的输入之一，也是 [[ca_register_status]] 由 Y 回写 N 的触发源。

## 版本演进

- v0：首次沉淀归一集合与"上送态 ≠ 证书态"的边界。

关联页面：[[sign_center_cert_status]]、[[ca_register_status]]、[[ca_submit_status]]、[[need_register_ca_judgement]]、[[ca_certificate]]。

---END FILE---

---FILE: concepts/batch_no.md ---
---
type: concept
title: 批次号（batch_no）
page_key: batch_no
domain: CA证书认证
status: draft
aliases: [batch_no, 批次流水号]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
maps_to: ca_certification_info.batch_no
field_targets:
  - ca_certification_info.batch_no
  - ca_certification_info.data_date
adjudication: boundary
also_confused_with:
  - ca_certification_info.data_date
---

batch_no 是新建认证行时生成的一次性流水号，格式 INC_<yyyyMMddHHmmssSSS>_<6位hex>，总/分公司两行各自独立。

**边界（boundary）**：batch_no 是每次新建行的唯一流水号（INC_ 前缀），已从幂等键移除；幂等只依赖 cust_id+data_date+head_company_data+PENDING（见 [[incremental_idempotent_key]]）。因此它不能用于判断"是不是同一笔业务"，也不等同于 data_date：同一天可以有多行（两主体类型、状态不同），同一 batch_no 也不会跨日复用。

## 需求背景

定位一行数据的正确姿势是 (cust_id, data_date, head_company_data) 三元组 + [[submit_status]]，batch_no 只作为新建时刻的痕迹参考。

## 版本演进

- v0：首次记录 batch_no 退出幂等键这一变更，及其与 data_date 的语义差异。

关联页面：[[ca_certification_info]]、[[incremental_idempotent_key]]、[[incremental_idempotent_row]]、[[head_company_data]]。

---END FILE---

---FILE: rules/incremental_idempotent_row.md ---
---
type: rule
title: 增量幂等建行
page_key: incremental_idempotent_row
domain: CA证书认证
status: draft
aliases: [createOrGetByKey, 幂等建行规则]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

createOrGetByKey 以 (cust_id, data_date, head_company_data, submit_status='PENDING') 命中即复用已有行，未命中才新建并生成 batch_no；batchNo 不再进入幂等键。

**影响**：重复触发不产生重复行；跨天重发会产生新行。前者保证门户/中台重复通知下数据不膨胀，后者意味着按 data_date 做日切统计时不能把同一业务跨日合并。

## 需求背景

规则依赖 [[incremental_idempotent_key|增量落库幂等键]] 口径；由于 PENDING 同时是幂等条件，一旦行被置为 SUCCESS/FAIL，再次触发就会新建一行，因此"同样材料出现多行"未必是缺陷。

## 版本演进

- v0：首次固化幂等键构成，并记录 batch_no 被移出幂等键的变更。

```ground:rule
name: 增量幂等建行
content: createOrGetByKey 以 (cust_id, data_date, head_company_data, submit_status='PENDING') 命中即复用已有行，未命中才新建并生成 batch_no；batchNo 不再进入幂等键
impact: 重复触发不产生重复行；跨天重发会产生新行
field_targets:
  - ca_certification_info.cust_id
  - ca_certification_info.data_date
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
  - ca_certification_info.batch_no
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#createOrGetByKey"
```

关联页面：[[ca_certification_info]]、[[incremental_idempotent_key]]、[[batch_no]]、[[submit_idempotent_short_circuit]]。

---END FILE---

---FILE: rules/submit_idempotent_short_circuit.md ---
---
type: rule
title: 上送幂等短路
page_key: submit_idempotent_short_circuit
domain: CA证书认证
status: draft
aliases: [CA_CERT_SUBMIT_ALREADY_SUCCESS, 重复上送短路]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

submit_status=SUCCESS 的行再次 submitToSignCenter 直接返回成功，不重复调用 cbsSubmitBizData。

**影响**：协议确认页可重复点击，不会造成中台重复受理；同时也意味着材料在上送成功后再修改，不会自动重推，需要新建行（受 [[incremental_idempotent_row]] 约束）。

## 需求背景

本规则是 [[submit_success|上送完成口径]] 得以安全复用 SUCCESS 行的前提，也是 [[ca_submit_status]] 状态机中 SUCCESS 自指的迁移来源。

## 版本演进

- v0：首次固化短路行为与返回码语义（CA_CERT_SUBMIT_ALREADY_SUCCESS）。

```ground:rule
name: 上送幂等短路
content: submit_status=SUCCESS 的行再次 submitToSignCenter 直接返回成功，不重复调用 cbsSubmitBizData
impact: 协议确认页可重复点击
field_targets:
  - ca_certification_info.submit_status
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#submitToSignCenter"
```

关联页面：[[ca_submit_status]]、[[submit_success]]、[[incremental_idempotent_row]]。

---END FILE---

---FILE: rules/submit_completeness_check.md ---
---
type: rule
title: 上送前完整性校验
page_key: submit_completeness_check
domain: CA证书认证
status: draft
aliases: [assertCompleteForSubmit, CA_CERT_INFO_INCOMPLETE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

上送前校验：notify_agreement_json 必填、实名 JSON 至少一项、意愿 JSON 至少一项（CHANNEL_OPENAPI 免）、file_refs_json 必填。

**影响**：缺项时抛 CA_CERT_INFO_INCOMPLETE 阻断上送，行停留在 [[ca_submit_status|PENDING]] 状态并被后续请求复用。

## 需求背景

校验条件与 [[submit_completeness|一证四步上送完整性口径]] 一一对应；开放渠道豁免的边界见 [[channel_openapi_source]]。若前端提示此错误，通常应先查 [[notify_agreement]] 与 [[ca_upgrade_auth]] 的落位而不是重试。

## 版本演进

- v0：首次固化四项校验与一项豁免。

```ground:rule
name: 上送前完整性校验
content: notify_agreement_json 必填、实名 JSON 至少一项、意愿 JSON 至少一项（CHANNEL_OPENAPI 免）、file_refs_json 必填
impact: 缺项时抛 CA_CERT_INFO_INCOMPLETE 阻断上送
field_targets:
  - ca_certification_info.notify_agreement_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.police_two_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
  - ca_certification_info.file_refs_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#assertCompleteForSubmit"
```

关联页面：[[submit_completeness]]、[[ca_certification_info]]、[[channel_openapi_source]]、[[ca_submit_status]]。

---END FILE---

---FILE: rules/confirm_submit_own_row_only.md ---
---
type: rule
title: 协议确认只上送本企业行
page_key: confirm_submit_own_row_only
domain: CA证书认证
status: draft
aliases: [confirm 上送范围, 只上送 N 行]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationConfirmApplication.java
  - db:ca_certification_info
contract_version: "0.1"
---

CaCertificationConfirmApplication.confirm 中总公司行 submitOrThrow 被注释，仅上送 head_company_data='N' 主行；与类 Javadoc「先总后分」表述不一致。

**影响**：分公司场景总公司行不会在协议确认阶段上送（仅运营推送链路 CaActivationApplication 并行上送 N/Y 两行）。因此"总公司行一直 PENDING"在协议确认入口下是预期现象，不是漏推。

## 需求背景

与 [[head_company_row|总公司主体行口径]]、[[operation_platform_source]] 联读可还原两条链路的上送范围差异。类 Javadoc 与本实现的不一致需后续确认是回退还是有意调整。

## 版本演进

- v0：首次记录被注释代码与文档表述的冲突。

```ground:rule
name: 协议确认只上送本企业行
content: CaCertificationConfirmApplication.confirm 中总公司行 submitOrThrow 被注释，仅上送 head_company_data='N' 主行；与类 Javadoc「先总后分」表述不一致
impact: 分公司场景总公司行不会在协议确认阶段上送（仅运营推送链路 CaActivationApplication 并行上送 N/Y 两行）
field_targets:
  - ca_certification_info.head_company_data
  - ca_certification_info.submit_status
evidence: "code_path:CaCertificationConfirmApplication.java#confirm（//submitOrThrow(ctx.headCertId...) 被注释）"
```

关联页面：[[head_company_row]]、[[head_company_data]]、[[operation_platform_source]]、[[ca_submit_status]]。

---END FILE---

---FILE: rules/submit_data_length_truncate.md ---
---
type: rule
title: 上送 data 字段长度裁剪
page_key: submit_data_length_truncate
domain: CA证书认证
status: draft
aliases: [truncateOversizedDataFieldsInSubmitPayload, 1000 字符裁剪]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationInfoAppServiceImpl.java
  - db:ca_certification_info
contract_version: "0.1"
---

上送前对 authPersonPoliceTwo / authEnterpriseThree / authEnterpriseFour / checkCode / h5Face 的 data 做 1000 字符限制，超长按 JSON 叶子节点从长到短剔除，失败则硬截断。

**影响**：避免签章中台因 data 超长拒收；代价是库内留痕与实际上送内容可能不一致——排查"中台收到的东西和库里不一样"时应先想到本规则。

## 需求背景

被裁剪的字段分别对应 [[enterprise_four_elements]]（authEnterpriseFour/authEnterpriseThree）与意愿留痕（h5Face/checkCode），上送原始报文另存于 sign_platform_result，可用于比对裁剪前后差异。

## 版本演进

- v0：首次固化 1000 字符阈值与"先剔叶、后硬截断"的降级顺序。

```ground:rule
name: 上送 data 字段长度裁剪
content: 上送前对 authPersonPoliceTwo/authEnterpriseThree/authEnterpriseFour/checkCode/h5Face 的 data 做 1000 字符限制，超长按 JSON 叶子节点从长到短剔除，失败则硬截断
impact: 避免签章中台因 data 超长拒收
field_targets:
  - ca_certification_info.police_two_json
  - ca_certification_info.enterprise_four_json
  - ca_certification_info.intent_sms_json
  - ca_certification_info.intent_h_face_json
evidence: "code_path:CaCertificationInfoAppServiceImpl.java#truncateOversizedDataFieldsInSubmitPayload"
```

关联页面：[[ca_certification_info]]、[[enterprise_four_elements]]、[[submit_completeness_check]]。

---END FILE---

---FILE: rules/sign_center_call_outside_tx.md ---
---
type: rule
title: 中台调用置于事务外
page_key: sign_center_call_outside_tx
domain: CA证书认证
status: draft
aliases: [NOT_SUPPORTED, 事务外调用中台]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - code:CaCertificationInfoAppServiceImpl.java
contract_version: "0.1"
---

activateByOpCompanyId 标 @Transactional(NOT_SUPPORTED)，confirm 不加事务，submitToSignCenter/openCa 均跨网络调用。

**影响**：避免长 IO 占用数据库事务。相应地，落库与中台调用不是原子的：可能出现"行已建但未上送"（[[ca_submit_status|PENDING]]）或"中台已成功但本地未回写"的窗口，排障时应以 sign_platform_result 与中台查询为准来对账。

## 需求背景

该规则解释了 [[operation_platform_source]] 来源中 PENDING 行偏多的可能原因，也是 [[incremental_idempotent_row]] 复用 PENDING 行的设计动因。

## 版本演进

- v0：首次固化事务边界。

```ground:rule
name: 中台调用置于事务外
content: activateByOpCompanyId 标 @Transactional(NOT_SUPPORTED)，confirm 不加事务，submitToSignCenter/openCa 均跨网络调用
impact: 避免长 IO 占用数据库事务
field_targets:
  - ca_certification_info.submit_status
evidence: "code_path:CaActivationApplication.java#activateByOpCompanyId"
```

关联页面：[[ca_submit_status]]、[[incremental_idempotent_row]]、[[operation_platform_source]]。

---END FILE---

---FILE: rules/ca_open_operator_must_be_admin.md ---
---
type: rule
title: CA 开通操作人必须是企业管理员
page_key: ca_open_operator_must_be_admin
domain: CA证书认证
status: draft
aliases: [CA_CERT_NOT_ADMIN, 管理员校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
contract_version: "0.1"
---

pre4Step 校验当前登录用户手机号命中 cust_person_info（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），否则抛 CA_CERT_NOT_ADMIN。

**影响**：非管理员无法进入一证四步。取数条件见 [[authorized_person]]。

## 需求背景

该规则是办理链路的准入闸门之一，与 [[company_in_change_forbid_ca]]、[[non_build_success_no_ca]] 共同构成预检（pre4Step）的三大阻断条件。

## 版本演进

- v0：首次固化校验字段组合与错误码。

```ground:rule
name: CA 开通操作人必须是企业管理员
content: pre4Step 校验当前登录用户手机号命中 cust_person_info（user_type=admin、enable=Y、company_type=登录角色、ref_cust_company_info=企业 code），否则抛 CA_CERT_NOT_ADMIN
impact: 非管理员无法进入一证四步
field_targets:
  - cust_person_info.user_type
  - cust_person_info.enable
  - cust_person_info.company_type
  - cust_person_info.ref_cust_company_info
evidence: "code_path:CaCertificationPreCheckApplication.java#assertCurrentUserIsAdmin"
```

关联页面：[[authorized_person]]、[[company_in_change_forbid_ca]]、[[non_build_success_no_ca]]。

---END FILE---

---FILE: rules/company_in_change_forbid_ca.md ---
---
type: rule
title: 企业变更中禁止开通 CA
page_key: company_in_change_forbid_ca
domain: CA证书认证
status: draft
aliases: [变更中禁止开通, cust_status=CHANGE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaCertificationPreCheckApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

cust_status='CHANGE' 或 cust_build_status='CUST_CHANGE' 时抛异常「先走完变更流程再处理 CA 开通」。

**影响**：变更期间阻断 CA 预检与开通。变更完成后企业数据（法人、名称）可能已变，此前留存的核验材料需重新采集，因此不应在变更期间放行。

## 需求背景

规则读的是 [[cust_company_info]] 的变更相关字段；与 [[non_build_success_no_ca]] 的区别在于：本规则拦"正在变更"，后者拦"尚未成功建档"。

## 版本演进

- v0：首次固化两个触发字段与提示语。

```ground:rule
name: 企业变更中禁止开通 CA
content: "cust_status='CHANGE' 或 cust_build_status='CUST_CHANGE' 时抛异常「先走完变更流程再处理 CA 开通」"
impact: 变更期间阻断 CA 预检与开通
field_targets:
  - cust_company_info.cust_status
  - cust_company_info.cust_build_status
evidence: "code_path:CaCertificationPreCheckApplication.java#assertCompanyNotInChange"
```

关联页面：[[cust_company_info]]、[[non_build_success_no_ca]]、[[ca_open_operator_must_be_admin]]。

---END FILE---

---FILE: rules/non_build_success_no_ca.md ---
---
type: rule
title: 非 BUILD_SUCCESS 不判定需开通 CA
page_key: non_build_success_no_ca
domain: CA证书认证
status: draft
aliases: [BUILD_SUCCESS 前置, 建档未完成不开通]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaOpenCaApplication.java
  - code:CaUpgradeAuthApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

cust_build_status != BUILD_SUCCESS 时 needOpenCa=N 并返回变更/未完成提示；升级授权书盖章也要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)。

**影响**：未成功建档企业不生成 CFCA/BS 协议。因此 [[ca_upgrade_auth|CA 升级授权书]] 缺失可能源于建档状态，而非附件上传失败。

## 需求背景

本规则是 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 的前置短路：即便 need_register_ca='Y'，建档未成功也不判定为需开通。

## 版本演进

- v0：首次固化前置状态与两处使用点（isOpenCa、processUpgradeAuthOnOpsNameChange）。

```ground:rule
name: 非 BUILD_SUCCESS 不判定需开通 CA
content: cust_build_status != BUILD_SUCCESS 时 needOpenCa=N 并返回变更/未完成提示；升级授权书盖章也要求 cust_build_status in (BUILD_SUCCESS, CUST_CHANGE)
impact: 未成功建档企业不生成 CFCA/BS 协议
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.need_register_ca
evidence: "code_path:CaOpenCaApplication.java#isOpenCa；CaUpgradeAuthApplication.java#processUpgradeAuthOnOpsNameChange"
```

关联页面：[[need_register_ca_judgement]]、[[cust_company_info]]、[[ca_upgrade_auth]]、[[company_in_change_forbid_ca]]。

---END FILE---

---FILE: rules/simple_auth_forbid_ca.md ---
---
type: rule
title: 简易认证禁止开通电子签章
page_key: simple_auth_forbid_ca
domain: CA证书认证
status: draft
aliases: [enforceMustNotOpenCa, 简易认证不开通 CA]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyCaPolicy.java
  - db:cust_company_info
contract_version: "0.1"
---

简易认证提交时若 need_register_ca='Y'，调用 CustCompanyCaPolicy.enforceMustNotOpenCa 校正并落库 need_register_ca / ca_register_status / need_register_bs / bs_register_status。

**影响**：简易认证企业强制不开通 CA。这条规则解释了为什么存在 need_register_ca='Y' 但 ca_register_status 长期为 N 的企业，也是 [[legacy_package_companies|存量打包企业口径]] 明确排除 identify_style='SIMPLE' 的原因（两份口径互相印证）。

## 需求背景

校正同时覆盖 CFCA 与 BS 两个渠道字段，说明"简易认证不得开通电子签章"是渠道无关的策略，边界参见 [[ca_certificate]]。

## 版本演进

- v0：首次沉淀该策略字段范围（evidence 与 field_targets 在语义分析输入中被截断，本页据 content 中列出的列名推导，待下一版补全逐字证据）。

```ground:rule
name: 简易认证禁止开通电子签章
content: 简易认证提交时若 need_register_ca='Y'，调用 CustCompanyCaPolicy.enforceMustNotOpenCa 校正并落库 need_register_ca/ca_register_status/need_register_bs/bs_register_status
impact: 简易认证企业强制不开通 CA
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.need_register_bs
  - cust_company_info.bs_register_status
evidence: "code_path:CustCompanyCaPolicy.java#enforceMustNotOpenCa"
```

关联页面：[[cust_company_info]]、[[legacy_package_companies]]、[[need_register_ca_judgement]]、[[ca_certificate]]。

---END FILE---

---REVIEW: rule | 简易认证禁止开通电子签章---
语义分析输入在该规则的 field_targets / evidence 处被截断，本页 field_targets 依据 content 中显式列出的列名推导，evidence 仅引用 content 内出现的 CustCompanyCaPolicy.enforceMustNotOpenCa。待补全逐字 evidence 与完整 field_targets 后修订，或确认该规则应降级为非锚定描述。
---END REVIEW---

---REVIEW: table | 物理库名缺失---
语义分析未给出任何物理库名，所有 table / caliber / process / rule 页的 scope.databases 暂填 unknown。待确认 cust_company_info、ca_certification_info、ca_cfca_upgrade_report、cust_person_info 的物理库（或 schema）名后统一回填，并据此校验跨库 JOIN（如 ca_certification_info.cust_id ↔ cust_company_info.id）是否成立。
---END REVIEW---