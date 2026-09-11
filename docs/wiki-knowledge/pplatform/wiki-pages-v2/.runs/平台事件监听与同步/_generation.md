---FILE: tables/client_api_sync_error.md ---
---
type: table
title: client_api_sync_error 客户端同步失败记录表
page_key: tables/client_api_sync_error
domain: 平台事件监听与同步
status: draft
aliases:
  - ClientApiSyncErrorDO
  - 客户端同步失败记录
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
  - code:CustSyncService.java:syncByRole
  - "reqdoc:失败数据写入ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
contract_version: "0.1"
---

> 本页 ## 版本演进 收录了未在代码层证实的文档主张（document_claim，未证实）。

client_api_sync_error 是「平台事件监听与同步」主题下的失败留痕表：平台事件经监听回调进入业务系统后，业务系统向客户域发起的 RPC 同步一旦异常，即以入参原文 + 服务类名 + 重试次数落库，形成可排查、可重放的记录。它与 [[tables/cust_build_record]] 的建档异步补偿是两条独立的失败处理链路，口径见 [[concepts/sync-error-record]]。

## 需求背景
平台侧事件触发后构造 `FbpReq<T>` 并回调 `IPlatListener.onEvent`，业务系统消费该事件时需要把数据变动同步到客户/租户等下游系统。同步失败的诉求不是「静默丢弃」而是「留痕」：失败数据写入 ClientApiSyncErrorDO，调用异常 → `error(...)` → 落库（reqdoc 主张，代码层已证实于 `CustSyncService.java:syncByRole` 中的 `custClientSyncService.error`）。因此本表保存了 `service_class_name`（区分失败来源，DB 实测 12 种）、`param`（入参原文）等重放所必需的信息。

## 版本演进
- v0 契约：本表字段语义与失败态口径按 DB 实测沉淀（见 [[calibers/client-sync-error-all-disabled]]、[[calibers/client-sync-error-retry-num-3]]）。
- 启动时重试任务扫描失败记录 → 重放同步请求（StartupSyncRetry）（document_claim，未证实）。
- 服务停止时将队列数据落库，降低消息丢失风险（document_claim，未证实）；现有代码仅见 `CustSyncService.java:shutdownThreadPool` 的 `shutdown/awaitTermination`，未见队列落库实现。

```ground:table
table: client_api_sync_error
business_role: 客户端 RPC 同步调用失败落库记录，承载失败来源、入参原文与关联流程上下文，供排查与重放
fields:
  - name: service_class_name
    meaning: 触发本次失败同步的客户端服务类全名，用于区分失败来源（DB实测12种：ClientCustSyncService 占1453、ClientOperatorSyncService 555等）
    evidence: db
  - name: retry_num
    meaning: 已重试次数/重试上限；DB实测全部为3，即默认重试上限
    evidence: db
  - name: enable
    meaning: 记录启用标识；DB实测2227行全部为'N'，同步失败记录均为停用态
    evidence: db
  - name: param
    meaning: 失败同步请求的入参原文（text）
    evidence: db
  - name: act_procinst_id
    meaning: 关联流程实例ID
    evidence: db
  - name: act_procinst_no
    meaning: 关联流程申请编号
    evidence: db
  - name: act_procinst_status
    meaning: 关联流程当前审批状态
    evidence: db
  - name: act_procinst_date
    meaning: 关联流程审批结束时间
    evidence: db
  - name: organization_id
    meaning: 机构编号
    evidence: db
  - name: app_tenant_code
    meaning: 逻辑租户标识（DB实测仅1个值 base）
    evidence: db
  - name: db_tenant_code
    meaning: 数据租户标识
    evidence: db
write_contract:
  claim: 失败数据写入 ClientApiSyncErrorDO，调用异常 → error(...) → 落库
  evidence: "code_path:CustSyncService.java:syncByRole + reqdoc:失败数据写入ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
related_pages:
  - tables/cust_build_record
  - calibers/client-sync-error-all-disabled
  - calibers/client-sync-error-retry-num-3
```

---REVIEW: table | client_api_sync_error---
1. `scope.databases` 在语义分析中未给出物理库名，本页（及本主题其他页）统一填 `unknown`，待确认。
2. `retry_num` 的语义在分析中同时表述为「已重试次数/重试上限」，二者不可同时成立；DB 实测恒为 3，暂按「默认重试上限」理解（见 [[calibers/client-sync-error-retry-num-3]]），需业务确认。
3. 启动重试（StartupSyncRetry）与服务停止队列落库两条文档主张无代码证据，已在 ## 版本演进 标注。
---END REVIEW---

---END FILE---

---FILE: tables/cust_build_record.md ---
---
type: table
title: cust_build_record 企业建档异步流程补偿记录表
page_key: tables/cust_build_record
domain: 平台事件监听与同步
status: draft
aliases:
  - 建档补偿记录
  - 补偿记录
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
contract_version: "0.1"
---

cust_build_record 记录企业建档异步流程（文件推送 / 流程拉取）失败后的补偿单元。与 [[tables/client_api_sync_error]] 的「同步失败」不同，本表以 `retry_status` 表达重试状态，并用 `remark` 前缀标记记录来源，是 [[processes/build-async-compensation-retry]] 状态机的载体表。

## 需求背景
建档异步流程包含文件推送与流程发起两步，任一步失败都需要可重放：`pushData` 保存序列化后的 `RegAsyncContext`，补偿任务反序列化后重放整个异步流程；`returnData` 保存错误信息 JSON；`remark` 以 `COMPENSATION_` 前缀拼接失败类型（FILE_PUSH_FAIL / START_FLOW_FAIL）与重试结果后缀，使补偿任务可仅凭 remark 识别待处理记录（见 [[calibers/build-compensation-pending-records]]）。

## 版本演进
- v0 契约：字段语义与状态机取自代码枚举与补偿任务实现；`remark` 后缀承载重试终止原因（如 `_FAILED_MAX_RETRY_3`），属隐式格式约定，见 [[rules/compensation-max-retry]]。
- 表内字段在代码层为驼峰命名（retryStatus/returnData），状态机字段引用写作 `cust_build_record.retry_status` / `cust_build_record.return_data`，映射关系待落库脚本阶段固化。

```ground:table
table: cust_build_record
business_role: 建档异步流程失败的补偿单元，序列化保存重放上下文并跟踪重试状态
fields:
  - name: retryStatus
    meaning: 建档异步流程补偿重试状态（PENDING/RETRYING/SUCCESS/FAILED）
    evidence: code
  - name: remark
    meaning: 备注；补偿记录以 'COMPENSATION_' 前缀标记并拼接失败类型（FILE_PUSH_FAIL / START_FLOW_FAIL）及重试结果后缀
    evidence: code
  - name: pushData
    meaning: 序列化的 RegAsyncContext，供补偿任务反序列化后重放整个异步流程
    evidence: code
  - name: returnData
    meaning: 错误信息 JSON（failType/errorMessage/retryCount/lastRetryTime等）
    evidence: code
related_pages:
  - processes/build-async-compensation-retry
  - calibers/build-compensation-pending-records
  - rules/compensation-max-retry
  - rules/compensation-tenant-context-all
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 客户企业信息表
page_key: tables/cust_company_info
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业信息
  - CustCompanyInfoDO
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - "reqdoc:企业准入存在人工审核、驳回后可修改重新提交的流程"
  - "reqdoc:企业信息变更需在途校验，存在在途变更流程时不允许再次变更"
contract_version: "0.1"
---

cust_company_info 是企业认证/准入建档的主表，`custBuildStatus` 承载 [[processes/cust-company-build-status]] 状态机，`custCompanyType` 决定按角色同步的维度。

## 需求背景
企业准入存在人工审核、驳回后可修改重新提交的流程，状态迁移由 `CustCompanyInfoApplication.messageNotify` 驱动；企业信息变更需在途校验，存在在途变更流程时不允许再次变更（`CustPersonApplication.adminChangeSaveOrUpdate` 在 status=CHANGE 时抛出「有在途变更流程」，配合 `CheckBusiOnWayService`）。两条主张均在代码层已证实，且是状态机与同步口径的业务前提。

## 版本演进
- v0 契约：建档状态枚举与迁移取自 `CustCompanyInfoApplication`；产融侧建档状态（CustBuildStatusEnum）与运营中台审核状态（OperApiConstants.CheckStatus：CUST_CHECK_PASS/REJECT/INIT 等）是两套状态体系，通过回调对齐，见 [[concepts/cust-build]]。
- 建档成功企业（[[calibers/build-success-company]]）在存量判定中被直接跳过推送/变更，属口径而非状态机迁移。

```ground:table
table: cust_company_info
business_role: 企业认证与准入建档主表，状态字段驱动推送/审核回调链路
fields:
  - name: custBuildStatus
    meaning: 企业建档状态（CustBuildStatusEnum：INIT/BUILD_FAIL/CUST_CONFIRM_AWAIT/CUST_BUILDING/BUILD_SUCCESS/AWAIT_CUST_CONFIRM）
    evidence: code
  - name: custCompanyType
    meaning: 客户角色JSON数组（如 ["SUPPLIER"]），决定按角色同步的维度
    evidence: code
write_contracts:
  - claim: 企业准入存在人工审核、驳回后可修改重新提交的流程
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify（BUILD_FAIL→重新提交→CUST_CONFIRM_AWAIT） + reqdoc:企业准入存在人工审核、驳回后可修改重新提交的流程"
  - claim: 企业信息变更需在途校验，存在在途变更流程时不允许再次变更
    evidence: "code_path:CustPersonApplication.java:adminChangeSaveOrUpdate（status=CHANGE 抛『有在途变更流程』）+ CheckBusiOnWayService.java + reqdoc:企业信息变更需在途校验，存在在途变更流程时不允许再次变更"
related_pages:
  - processes/cust-company-build-status
  - calibers/build-success-company
  - rules/reject-pass-callback-workflow
```

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info 客户联系人信息表
page_key: tables/cust_person_info
domain: 平台事件监听与同步
status: draft
aliases:
  - 联系人
  - 经办人
  - CustPersonInfoDO
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
  - code:CustPersonApplication.java:insertOrUpdatePerson
contract_version: "0.1"
---

cust_person_info 保存企业下的联系人（经办人 / 管理员），是经办人同步与账号联动（SSO/AMS）的主表。

## 需求背景
企业注册/激活流程中需同步用户到 SSO 与 AMS 运营中台（`CustPersonApplication.insertOrUpdatePerson` 调用 sysUserProvider/ssoFacade，配合 `CustSyncEventProvider.syncOperatorUser`）；联系人删除或冻结时置 `enable='N'`，查询与同步默认过滤有效联系人（[[calibers/valid-contact-person]]），按角色取管理员时叠加 `userType='admin'`（[[calibers/admin-contact-person]]）。

## 版本演进
- v0 契约：`userType` 取值取自 UserTypeEnum（admin/operator/guest）；删除经办人时的冻结边界见 [[rules/operator-delete-freeze-only]]。

```ground:table
table: cust_person_info
business_role: 企业联系人（经办人/管理员）主表，enable 与 userType 共同决定同步与权限判定口径
fields:
  - name: enable
    meaning: 联系人启用标识，Y有效/N禁用（删除或冻结时置N）
    evidence: code
  - name: userType
    meaning: 联系人类型（UserTypeEnum：admin/operator/guest）
    evidence: code
related_pages:
  - calibers/valid-contact-person
  - calibers/admin-contact-person
  - rules/operator-delete-freeze-only
  - tables/sys_cust_user_rel
```

---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel 用户-客户角色关联表
page_key: tables/sys_cust_user_rel
domain: 平台事件监听与同步
status: draft
aliases:
  - 用户客户角色关联
  - SysCustUserRel
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

sys_cust_user_rel 承载用户与客户角色之间的关联关系，`isFreeze` 是权限回收的开关位，删除企业时以「关联是否未冻结」判断用户是否可删（[[calibers/operator-role-rel-not-frozen]]）。

## 需求背景
经办人/管理员删除与冻结涉及账号权限回收：同一手机号既有经办人又有管理员时，DELETE 仅冻结经办人记录及其 accountNormal 角色关联（`is_freeze='Y'`），不动管理员，避免误冻管理员权限（[[rules/operator-delete-freeze-only]]）。

## 版本演进
- v0 契约：`isFreeze` 取值 Y/N；与 [[tables/cust_person_info]] 的 `enable` 构成两级开关（人维度 / 关联维度）。

```ground:table
table: sys_cust_user_rel
business_role: 用户与客户角色的关联关系，冻结位控制权限回收与用户可删判定
fields:
  - name: isFreeze
    meaning: 用户-客户角色关联关系的冻结标识（Y/N）
    evidence: code
related_pages:
  - calibers/operator-role-rel-not-frozen
  - rules/operator-delete-freeze-only
```

---END FILE---

---FILE: tables/cust_role_info.md ---
---
type: table
title: cust_role_info 客户角色信息表
page_key: tables/cust_role_info
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户角色
  - CustRoleInfoDO
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:getRoles/syncByRole
contract_version: "0.1"
---

cust_role_info 是「按角色维度同步」的取数表：企业事件到达后，先按 `dbTenantCode + companyCode + (companyType)` 查询有效角色，再逐角色发起同步 RPC（[[rules/sync-by-role]]）。

## 需求背景
一次企业事件可能对应多条按角色的同步调用，角色是否有效由 `enable` 决定（[[calibers/valid-cust-role]]）；`syncByRoleOn` 开关决定是否忽略 companyType 做全角色同步，因此角色维度既影响同步条数，也影响同步范围。

## 版本演进
- v0 契约：本页字段仅来自代码层（`CustSyncService.getRoles/syncByRole`），尚无 DB 实测佐证，落库前需抽样校验。

```ground:table
table: cust_role_info
business_role: 客户角色信息表，作为按角色同步的取数维度
fields:
  - name: enable
    meaning: 角色有效标识；按角色同步时取有效角色（enable='Y'）
    evidence: code
  - name: role_type
    meaning: 角色类型，决定按角色同步的调用维度与 accountNormal 等角色关联
    evidence: code
related_pages:
  - rules/sync-by-role
  - calibers/valid-cust-role
```

---REVIEW: table | cust_role_info---
1. 本表未出现在 `field_semantics` 中，字段（enable / role_type）仅由 `calibers` 与 `rules` 的 field_targets 推断，证据等级为 code，缺 DB 实测；字段完整清单与主键待补。
2. `role_type` 的枚举取值集合未在语义分析中给出，暂不落枚举页。
3. `scope.databases` 同主题其余页，填 `unknown` 待确认。
---END REVIEW---

---END FILE---

---FILE: processes/build-async-compensation-retry.md ---
---
type: process
title: 建档异步流程补偿重试状态机
page_key: processes/build-async-compensation-retry
domain: 平台事件监听与同步
status: draft
aliases:
  - retry_status 状态机
  - 补偿重试状态机
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:handleRetrySuccess
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
  - code:RegAsyncCompensationJobHandler.java:markAsFailed
contract_version: "0.1"
---

该状态机描述建档异步流程失败记录（[[tables/cust_build_record]]）在补偿任务下的生命周期：新建即 PENDING，被扫描后进入 RETRYING，重放成功转 SUCCESS，失败则视重试次数回置 PENDING 或终态 FAILED。它是 [[concepts/compensation]] 的可执行细化。

## 需求背景
建档异步流程（文件推送 / 流程发起）失败不能只留错误日志，需要「可重放 + 有上限 + 有终态」：`saveCompensationRecord` 落 PENDING 并序列化 `RegAsyncContext`；补偿任务 `processCompensationRecord` 反序列化重放 `orchestrateAsync`；重试上限控制见 [[rules/compensation-max-retry]]，扫描可见性控制见 [[rules/compensation-tenant-context-all]]。

## 版本演进
- v0 契约：状态与迁移取自代码枚举与补偿任务实现，未引入 DB 实测；终态失败原因以 remark 后缀承载（如 `_FAILED_MAX_RETRY_3`）。
- 与 [[processes/cust-company-build-status]] 的区分：本状态机关注「失败后的技术重试」，企业建档状态机关注「业务审核推进」，两者通过 custId 关联但不共享状态字段。

```ground:process
name: 建档异步流程补偿重试状态机
field: cust_build_record.retry_status
states:
  - value: PENDING
    label: 待重试
    source: code_enum
  - value: RETRYING
    label: 重试中
    source: code_enum
  - value: SUCCESS
    label: 重试成功
    source: code_enum
  - value: FAILED
    label: 重试失败
    source: code_enum
transitions:
  - from: "(新建)"
    event: 文件推送/流程拉取失败saveCompensationRecord
    to: PENDING
    evidence: "code_path:RegAsyncService.java:saveCompensationRecord"
  - from: PENDING
    event: 补偿任务识别并开始处理processCompensationRecord
    to: RETRYING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:processCompensationRecord"
  - from: RETRYING
    event: retryCompensation重放orchestrateAsync成功handleRetrySuccess
    to: SUCCESS
    evidence: "code_path:RegAsyncCompensationJobHandler.java:handleRetrySuccess"
  - from: RETRYING
    event: 重试失败但未达最大重试次数updateRetryCount
    to: PENDING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount"
  - from: RETRYING
    event: 重试次数>=maxRetryCount markAsFailed(MAX_RETRY_n)
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount"
  - from: RETRYING
    event: 失败类型未知/无法解析markAsFailed
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:markAsFailed"
related_pages:
  - tables/cust_build_record
  - calibers/build-compensation-pending-records
  - rules/compensation-max-retry
```

---END FILE---

---FILE: processes/cust-company-build-status.md ---
---
type: process
title: 企业建档状态机
page_key: processes/cust-company-build-status
domain: 平台事件监听与同步
status: draft
aliases:
  - cust_build_status 状态机
  - CustBuildStatusEnum
  - 企业建档状态
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
---

企业建档状态机描述 `cust_company_info.cust_build_status` 的推进路径：提交建档进入待客户确认或审核中，客户提交后推送运营中台，审核通过转 BUILD_SUCCESS，退回/拒绝转 CUST_CONFIRM_AWAIT 或 BUILD_FAIL；简易认证另走 AWAIT_CUST_CONFIRM 分支。详见 [[concepts/cust-build]]。

## 需求背景
企业准入存在人工审核、驳回后可修改重新提交的流程：`messageNotify` 覆盖提交（INVITE → CUST_CONFIRM_AWAIT）、推送运营中台（CUST_CONFIRM_AWAIT → CUST_BUILDING）、退回（CUST_BUILDING → CUST_CONFIRM_AWAIT）、拒绝（CUST_CONFIRM_AWAIT → BUILD_FAIL）与驳回后重新提交。审核通过由 `updateCustBuildStatus` 落 BUILD_SUCCESS。回调侧的去重策略见 [[rules/reject-pass-callback-workflow]]，终态口径见 [[calibers/build-success-company]]。

## 版本演进
- v0 契约：状态集合取自 CustBuildStatusEnum；产融侧状态与运营中台审核状态（OperApiConstants.CheckStatus：CUST_CHECK_PASS/REJECT/INIT 等）是两套体系，通过回调对齐。
- 运营中台客户数据变动回调产融 CustEventListener 的入站链路（`CustSyncEventProvider.onEvent/custChangeBroadcast/syncOperatorUser`）在代码层已证实，是该状态机的驱动源之一。

```ground:process
name: 企业建档状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_enum
  - value: BUILD_FAIL
    label: 认证驳回/失败
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 客户已提交/运营中台审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证通过/建档成功
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证提交后）
    source: code_enum
transitions:
  - from: "(新建)"
    event: 提交建档getCustBuildStatus(INVITE_AGW→CUST_BUILDING, INVITE/SELF→CUST_CONFIRM_AWAIT)
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 信息提交 (INVITE)
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: BUILD_FAIL
    event: 驳回后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交推送运营中台completeSpAdminNotice
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: CUST_BUILDING
    event: 认证审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: "(简易认证)"
    event: submitForSimpleAuth提交且非变更
    to: AWAIT_CUST_CONFIRM
    evidence: "code_path:CustCompanyInfoApplication.java:submitForSimpleAuth"
related_pages:
  - tables/cust_company_info
  - concepts/cust-build
  - calibers/build-success-company
  - rules/reject-pass-callback-workflow
```

---END FILE---

---FILE: calibers/client-sync-error-all-disabled.md ---
---
type: caliber
title: 客户端同步失败记录（全部停用态）
page_key: calibers/client-sync-error-all-disabled
domain: 平台事件监听与同步
status: draft
aliases:
  - enable='N' 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
contract_version: "0.1"
---

该口径用于识别 [[tables/client_api_sync_error]] 中的失败记录集合：同步失败记录落库后均为停用态，因此按 `enable='N'` 取数即可覆盖全部失败留痕，无需额外状态过滤。

## 需求背景
同步失败不是业务对象生命周期中的「有效记录」，而是留痕记录。DB 实测 2227 行全部为 `'N'`，说明写入即停用，业务侧不会把失败记录当作有效数据参与后续查询。该口径是 [[concepts/sync-error-record]] 的判定标准，与 [[calibers/build-compensation-pending-records]]（补偿扫描口径）分属两条链路。

## 版本演进
- v0 契约：按 DB 实测沉淀；样本量 2227 行。

```ground:caliber
name: 客户端同步失败记录（全部停用态）
predicate: "client_api_sync_error.enable = 'N'"
scope: DB实测2227行全部为N
evidence: db
related_pages:
  - tables/client_api_sync_error
  - concepts/sync-error-record
```

---END FILE---

---FILE: calibers/client-sync-error-retry-num-3.md ---
---
type: caliber
title: 客户端同步失败默认重试上限
page_key: calibers/client-sync-error-retry-num-3
domain: 平台事件监听与同步
status: draft
aliases:
  - retry_num=3 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
contract_version: "0.1"
---

该口径描述客户端同步失败记录的重试次数取值特征：DB 实测全部为 3，与补偿链路的默认重试上限（默认 3，见 [[rules/compensation-max-retry]]）数值一致。

## 需求背景
失败重试需要可预期上限。`retry_num` 在 DB 中恒定，说明当前实现不区分单条记录的实际重试次数，而是以固定值表达上限；因此取数时不能据 `retry_num` 做「重试进度」分析。字段语义的歧义见本页 REVIEW。

## 版本演进
- v0 契约：按 DB 实测沉淀，全部为 3。

```ground:caliber
name: 客户端同步失败默认重试上限
predicate: "client_api_sync_error.retry_num = 3"
scope: DB实测全部为3
evidence: db
related_pages:
  - tables/client_api_sync_error
  - rules/compensation-max-retry
```

---REVIEW: caliber | 客户端同步失败默认重试上限---
`retry_num` 的语义在被测数据中无法区分「已重试次数」与「重试上限」（恒为 3）；本页按「默认重试上限」口径沉淀，与 [[rules/compensation-max-retry]] 的 maxRetryCount=3 是否同一配置项待确认。
---END REVIEW---

---END FILE---

---FILE: calibers/build-compensation-pending-records.md ---
---
type: caliber
title: 建档异步补偿待处理记录
page_key: calibers/build-compensation-pending-records
domain: 平台事件监听与同步
status: draft
aliases:
  - 补偿扫描口径
  - COMPENSATION_ 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
---

补偿任务的取数口径：仅扫描 remark 以 `COMPENSATION_` 开头且 retry_status 处于 PENDING/RETRYING 的 [[tables/cust_build_record]] 记录。

## 需求背景
建档异步流程失败记录与普通建档记录同表存放，靠 `remark` 前缀区分身份；再叠加未终态过滤，避免把 SUCCESS/FAILED 记录重复拉入重试。任务侧另按 custId / failType / 时间范围做附加过滤，并按 [[rules/compensation-tenant-context-all]] 以 `dbTenantCode='all'` 全量扫描。

## 版本演进
- v0 契约：口径取自 `RegAsyncCompensationJobHandler.getCompensationRecords`；`remark` 后缀格式（失败类型与重试结果）属隐式约定。

```ground:caliber
name: 建档异步补偿待处理记录
predicate: "cust_build_record.remark LIKE 'COMPENSATION_%' AND cust_build_record.retry_status IN ('PENDING','RETRYING')"
scope: 补偿任务扫描口径；additional过滤 custId/failType/时间范围
evidence: code
related_pages:
  - tables/cust_build_record
  - processes/build-async-compensation-retry
  - rules/compensation-tenant-context-all
```

---END FILE---

---FILE: calibers/valid-contact-person.md ---
---
type: caliber
title: 有效联系人
page_key: calibers/valid-contact-person
domain: 平台事件监听与同步
status: draft
aliases:
  - enable='Y' 联系人
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustPersonApplication.java:insertOrUpdatePerson
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

有效联系人口径：[[tables/cust_person_info]] 中 `enable='Y'` 的联系人，为同步与查询经办人/管理员时的默认过滤条件。

## 需求背景
联系人被删除或冻结时置 `enable='N'`，因此有效态是同步（SSO/AMS 账号联动）与查询的公共前置条件；在此之上按 `userType` 再细分（[[calibers/admin-contact-person]]）。人维度的 enable 与关联维度的冻结位（[[calibers/operator-role-rel-not-frozen]]）构成两级开关。

## 版本演进
- v0 契约：口径取自代码层同步/查询实现，无 DB 实测。

```ground:caliber
name: 有效联系人
predicate: "cust_person_info.enable = 'Y'"
scope: 同步/查询经办人与管理员时默认过滤
evidence: code
related_pages:
  - tables/cust_person_info
  - calibers/admin-contact-person
  - rules/operator-delete-freeze-only
```

---END FILE---

---FILE: calibers/admin-contact-person.md ---
---
type: caliber
title: 管理员联系人
page_key: calibers/admin-contact-person
domain: 平台事件监听与同步
status: draft
aliases:
  - userType=admin 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

管理员联系人口径：在 [[calibers/valid-contact-person]] 基础上叠加 `user_type='admin'`，用于按角色取管理员做同步与待办。

## 需求背景
同一手机号可能同时是经办人与管理员，两类身份在权限与同步目标上不同；取管理员时必须显式限定 `userType='admin'`，否则会误取经办人。删除场景的对称约束见 [[rules/operator-delete-freeze-only]]。

## 版本演进
- v0 契约：口径取自代码层同步实现；`userType` 取值域为 UserTypeEnum（admin/operator/guest）。

```ground:caliber
name: 管理员联系人
predicate: "cust_person_info.enable = 'Y' AND cust_person_info.user_type = 'admin'"
scope: 按角色取管理员用于同步/待办
evidence: code
related_pages:
  - tables/cust_person_info
  - calibers/valid-contact-person
  - rules/operator-delete-freeze-only
```

---END FILE---

---FILE: calibers/valid-cust-role.md ---
---
type: caliber
title: 有效客户角色
page_key: calibers/valid-cust-role
domain: 平台事件监听与同步
status: draft
aliases:
  - cust_role_info.enable='Y'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:getRoles/syncByRole
contract_version: "0.1"
---

有效客户角色口径：按角色同步时仅取 [[tables/cust_role_info]] 中 `enable='Y'` 的角色作为同步维度。

## 需求背景
一次企业事件会产生多条按角色的同步 RPC，若把停用角色纳入，会造成无效调用与下游脏数据；因此同步前先按 `dbTenantCode + companyCode + (companyType)` 过滤有效角色（[[rules/sync-by-role]]）。

## 版本演进
- v0 契约：口径取自代码层 `CustSyncService.getRoles/syncByRole`，无 DB 实测。

```ground:caliber
name: 有效客户角色
predicate: "cust_role_info.enable = 'Y'"
scope: 按角色同步时取角色维度
evidence: code
related_pages:
  - tables/cust_role_info
  - rules/sync-by-role
```

---END FILE---

---FILE: calibers/operator-role-rel-not-frozen.md ---
---
type: caliber
title: 经办人角色关联未冻结
page_key: calibers/operator-role-rel-not-frozen
domain: 平台事件监听与同步
status: draft
aliases:
  - is_freeze='N'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

未冻结口径：[[tables/sys_cust_user_rel]] 中 `is_freeze='N'` 的用户-客户角色关联，用于删除企业时判断该用户是否仍被占用、是否可删。

## 需求背景
删除企业需要判断用户是否可回收：只要还存在未冻结的角色关联，就不能直接删除用户；冻结是回收权限的软手段（[[rules/operator-delete-freeze-only]]）。

## 版本演进
- v0 契约：口径取自代码层删除判定实现，无 DB 实测。

```ground:caliber
name: 经办人角色关联未冻结
predicate: "sys_cust_user_rel.is_freeze = 'N'"
scope: 删除企业时判断是否可删用户
evidence: code
related_pages:
  - tables/sys_cust_user_rel
  - rules/operator-delete-freeze-only
```

---END FILE---

---FILE: calibers/build-success-company.md ---
---
type: caliber
title: 建档成功企业
page_key: calibers/build-success-company
domain: 平台事件监听与同步
status: draft
aliases:
  - BUILD_SUCCESS 口径
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

建档成功企业口径：`cust_company_info.cust_build_status = 'BUILD_SUCCESS'` 的企业，在存量判定中直接跳过推送/变更。

## 需求背景
存量企业已经完成过推送与审核，事件回调到达时无需再次推送；用建档终态做幂等短路，可避免重复同步与重复回调。终态的写入路径见 [[processes/cust-company-build-status]] 的 `updateCustBuildStatus` 迁移。

## 版本演进
- v0 契约：口径取自代码层增量/存量判定逻辑，无 DB 实测。

```ground:caliber
name: 建档成功企业
predicate: "cust_company_info.cust_build_status = 'BUILD_SUCCESS'"
scope: 存量企业直接跳过推送/变更判定
evidence: code
related_pages:
  - tables/cust_company_info
  - processes/cust-company-build-status
```

---END FILE---

---FILE: concepts/event-listener-onevent.md ---
---
type: concept
title: 事件监听 / onEvent
page_key: concepts/event-listener-onevent
domain: 平台事件监听与同步
status: draft
aliases:
  - IPlatListener.onEvent
  - PlatFormCustEventListener.onEvent
  - IPlatListener<T extends IFlatEvent>
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:lowcode-pplatform-client/.../base/IPlatListener.java
  - code:PlatTenantEventListener.java
  - code:PlatProjectEventListener.java
  - code:PlatProductEventListener.java
  - code:PlatFormCustEventListener.java
  - code:CustSyncEventProvider.java:onEvent
  - "reqdoc:事件回调：平台触发事件 → 构造 FbpReq<T> → 回调 IPlatListener.onEvent"
  - "reqdoc:监听器子接口：租户、项目、产品、角色、协议等扩展监听器（PlatTenantEventListener/PlatProjectEventListener/PlatProductEventListener等）均继承基接口"
  - "reqdoc:PlatProjectEventListener 提供 queryProject/importProject/queryProjectLandTime 等查询与导入契约"
  - "reqdoc:客户域监听器 PlatFormCustEventListener 覆盖企业信息同步/状态同步/经办人/在途校验/站内信等（含默认实现的 syncCustManager/syncDeleteCustInfo）"
  - "reqdoc:回调链路：平台触发事件 → 构造 FbpReq<T> → 回调 IPlatListener.onEvent → 业务系统消费并记录处理结果"
contract_version: "0.1"
maps_to: "产融平台→业务系统的数据变动回调契约（业务系统实现子接口）"
adjudication:
  kind: boundary
  boundary: "两者方向相反：IPlatListener/PlatFormCustEventListener 是产融侧对外提供的回调接口（@Api 信息变动事件），由业务系统实现；CustSyncEventProvider.onEvent 是产融侧实现运营中台 CustEventListener 的入站回调，同名字段但属对立方向。"
also_confused_with:
  - CustSyncEventProvider.onEvent（运营中台→产融平台的回调入口）
---

> 本页 ## 版本演进 收录了未在代码层证实的文档主张（document_claim，未证实）。

「事件监听 / onEvent」是一个被同名复用的契约概念，指代产融侧对外提供的、由业务系统实现的数据变动回调接口族（IPlatListener 及其扩展子接口），与产融侧作为消费方的入站回调 `CustSyncEventProvider.onEvent` 方向相反。二者同名不同向，是阅读同步链路时最容易混淆的一处。

## 需求背景
回调链路为：平台触发事件 → 构造 `FbpReq<T>` → 回调 `IPlatListener.onEvent` → 业务系统消费并记录处理结果。子接口按域扩展，租户、项目、产品、角色、协议等扩展监听器（PlatTenantEventListener / PlatProjectEventListener / PlatProductEventListener 等）均继承基接口；其中 PlatProjectEventListener 提供 queryProject / importProject / queryProjectLandTime 等查询与导入契约。客户域的 PlatFormCustEventListener 覆盖企业信息同步 / 状态同步 / 经办人 / 在途校验 / 站内信等，并含默认实现的 syncCustManager / syncDeleteCustInfo。以上四项 reqdoc 主张均已由代码层证实，锚点证据（code_path + reqdoc:slug）记于 frontmatter sources。

## 版本演进
- v0 契约：产融侧接口族以「基接口 + 分域子接口」组织；客户域实现对象见 [[concepts/cust-build]] 与 [[processes/cust-company-build-status]] 的驱动链路。
- 接口矩阵：PlatFormAmsProvider.addEnterpriseContact（AMS 联系人同步）/ PlatFormTenantProvider.queryTenant·syncProject / PlatFormAgreementProvider.syncAgreementDoc（document_claim，未证实）。
- MigratoryPointService 提供 push（异步）与 call（同步）接口用于迁移点数据推送（document_claim，未证实）。

---REVIEW: concept | 事件监听 / onEvent---
1. 本页为 concept 页，按 v0 §3.9 不设 ground 块；reqdoc_claims 中 action=anchor 的双源证据写入 frontmatter `sources`（code_path + reqdoc:slug 形式），如与团队约定的锚点承载方式不一致请统一。
2. PlatFormCustEventListener 的默认实现方法（syncCustManager/syncDeleteCustInfo）与 `CustSyncEventProvider.syncOperatorUser` 是否职责重叠，语义分析未给结论。
3. 两条 action=review 的接口主张（Provider 矩阵、MigratoryPointService）无代码证据，已按规约仅置于 ## 版本演进。
---END REVIEW---

---END FILE---

---FILE: concepts/cust-build.md ---
---
type: concept
title: 建档
page_key: concepts/cust-build
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业建档
  - build
  - custBuildStatus
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
  - "reqdoc:企业注册/激活流程中同步用户到SSO与AMS运营中台"
  - "reqdoc:企业准入存在人工审核、驳回后可修改重新提交的流程"
contract_version: "0.1"
maps_to: "企业认证/准入的建档流程与 cust_company_info.cust_build_status"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.cust_company_type
adjudication:
  kind: synonym
  boundary: "产融侧建档状态（CustBuildStatusEnum）与运营中台审核状态（OperApiConstants.CheckStatus：CUST_CHECK_PASS/REJECT/INIT等）是两套状态体系，通过回调对齐。"
also_confused_with:
  - 运营中台建档审核回调
---

「建档」在业务口径中指企业认证/准入的完整流程（提交、审核、退回、驳回重提、通过），在数据口径上落为 `cust_company_info.cust_build_status`。它与运营中台的「建档审核」不同源：产融侧用 CustBuildStatusEnum，运营中台用 OperApiConstants.CheckStatus，二者通过回调对齐，不能直接比等。

## 需求背景
企业准入存在人工审核、驳回后可修改重新提交的流程，状态迁移由 `CustCompanyInfoApplication.messageNotify` 驱动；审核通过由 `updateCustBuildStatus` 落终态；简易认证经 `submitForSimpleAuth` 走 AWAIT_CUST_CONFIRM 分支。企业注册/激活流程中还需同步用户到 SSO 与 AMS 运营中台（`CustPersonApplication.insertOrUpdatePerson` + `CustSyncEventProvider.syncOperatorUser`），因此建档不是单系统内部状态，而是跨系统回调收敛的结果。

## 版本演进
- v0 契约：状态与迁移见 [[processes/cust-company-build-status]]；终态口径见 [[calibers/build-success-company]]；回调侧去重见 [[rules/reject-pass-callback-workflow]]。

---REVIEW: concept | 建档---
产融侧 CustBuildStatusEnum 与运营中台 CheckStatus 的对齐关系（逐一映射还是仅里程碑对齐）在语义分析中未给出逐项映射表，本页仅保留「两套体系」的边界结论，待补映射关系。
---END REVIEW---

---END FILE---

---FILE: concepts/sync-error-record.md ---
---
type: concept
title: 同步失败记录
page_key: concepts/sync-error-record
domain: 平台事件监听与同步
status: draft
aliases:
  - client_api_sync_error
  - ClientApiSyncErrorDO
oid: 1
scope:
  databases:
    - unknown
sources:
  - db:client_api_sync_error
  - code:CustSyncService.java:syncByRole
contract_version: "0.1"
maps_to: "客户端RPC同步调用失败落库记录（service_class_name + param + retry_num）"
field_targets:
  - client_api_sync_error.service_class_name
  - client_api_sync_error.param
  - client_api_sync_error.retry_num
  - client_api_sync_error.enable
adjudication:
  kind: boundary
  boundary: "client_api_sync_error 记录通用客户端同步失败（CustSyncService 用 error() 写入，重试上限以 retry_num 表达，DB实测恒为3）；cust_build_record 记录建档异步流程（pushFile/startProcess）补偿，用 retry_status 表达重试状态。二者表、状态字段均不同。"
also_confused_with:
  - cust_build_record 建档异步补偿记录
---

「同步失败记录」特指客户端 RPC 同步调用失败的落库留痕，以服务类名 + 入参原文 + 重试次数刻画一次失败，落表 [[tables/client_api_sync_error]]。它常被与 [[concepts/compensation]] 混为一谈，但后者是建档异步流程的重放补偿，二者的表、状态字段、识别口径都不同。

## 需求背景
同步失败的诉求是「不吞异常、可追溯、可重试」：同步失败经 `custClientSyncService.error(e, rpcSync)` 落库后抛出（见 [[rules/sync-exception-retain-context]]），因此记录写入路径本身是异常处理链的一环。失败记录均为停用态（[[calibers/client-sync-error-all-disabled]]），重试上限以 `retry_num` 表达（[[calibers/client-sync-error-retry-num-3]]）。

## 版本演进
- v0 契约：区分口径以表与状态字段为准；重放任务相关文档主张未证实，见 [[tables/client_api_sync_error]] 的 ## 版本演进。

---END FILE---

---FILE: concepts/compensation.md ---
---
type: concept
title: 补偿
page_key: concepts/compensation
domain: 平台事件监听与同步
status: draft
aliases:
  - COMPENSATION_
  - regAsyncCompensationJobHandler
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
maps_to: "建档异步流程失败后的重放补偿（RegAsyncCompensationJobHandler + RegAsyncService.saveCompensationRecord）"
field_targets:
  - cust_build_record.remark
  - cust_build_record.retry_status
  - cust_build_record.return_data
adjudication:
  kind: boundary
  boundary: "补偿以 cust_build_record.remark='COMPENSATION_'+failType 识别，状态为 retry_status；同步失败以 client_api_sync_error.enable='N' 识别。"
also_confused_with:
  - ClientApiSyncErrorDO 的同步失败重试
---

「补偿」指建档异步流程（文件推送 / 流程发起）失败后的重放机制：失败时 `RegAsyncService.saveCompensationRecord` 落一条带 `COMPENSATION_` 前缀的 [[tables/cust_build_record]] 记录并序列化重放上下文，补偿任务 `processCompensationRecord` 反序列化后重放整个异步流程。

## 需求背景
补偿需要三个要素：识别（remark 前缀 + retry_status 未终态，见 [[calibers/build-compensation-pending-records]]）、上下文（pushData 中的 RegAsyncContext）、上限（[[rules/compensation-max-retry]]）。跨租户可见性由 [[rules/compensation-tenant-context-all]] 保证。与同步失败重试的边界见 [[concepts/sync-error-record]]。

## 版本演进
- v0 契约：状态机见 [[processes/build-async-compensation-retry]]；当前 retry_status 为代码枚举，尚无 DB 实测分布。

---END FILE---

---FILE: rules/compensation-max-retry.md ---
---
type: rule
title: 补偿重试上限
page_key: rules/compensation-max-retry
domain: 平台事件监听与同步
status: draft
aliases:
  - maxRetryCount
  - MAX_RETRY_n
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
  - db:client_api_sync_error
contract_version: "0.1"
---

补偿重试有硬上限：retryCount 从 `returnData.retryCount` 读取，达到 maxRetryCount（默认 3）时标记 FAILED（remark 追加 `_FAILED_MAX_RETRY_3`），否则重试次数 +1 并回置 PENDING。

## 需求背景
无限重放会放大下游故障；因此补偿任务必须在「重试次数」与「终态」之间做取舍。该规则决定 [[processes/build-async-compensation-retry]] 的终态收敛，并与 [[calibers/client-sync-error-retry-num-3]] 中 DB 实测 `retry_num` 恒为 3 相互印证（默认上限一致）。

## 版本演进
- v0 契约：上限默认值 3，失败原因以 remark 后缀承载；终态后不再被 [[calibers/build-compensation-pending-records]] 扫描。

```ground:rule
name: 补偿重试上限
content: "retryCount 从 returnData.retryCount 读取，达到 maxRetryCount（默认3）时标记 FAILED（remark 追加 _FAILED_MAX_RETRY_3），否则重试次数+1并回置 PENDING"
impact: 决定补偿记录终态；DB中 retry_num 恒为3与默认上限一致
field_targets:
  - cust_build_record.retry_status
  - cust_build_record.return_data
evidence: "RegAsyncCompensationJobHandler.java:updateRetryCount + db:client_api_sync_error.retry_num=3"
related_pages:
  - processes/build-async-compensation-retry
  - calibers/client-sync-error-retry-num-3
```

---REVIEW: rule | 补偿重试上限---
本规则的证据跨两处：补偿侧 `updateRetryCount`（code）与 `client_api_sync_error.retry_num`（db）。后者属另一张表、另一条链路，语义分析以「默认上限一致」将二者关联；该等价性未经直接证据确认，标记待确认。
---END REVIEW---

---END FILE---

---FILE: rules/reject-pass-callback-workflow.md ---
---
type: rule
title: 拒绝/通过回调由工作流处理
page_key: rules/reject-pass-callback-workflow
domain: 平台事件监听与同步
status: draft
aliases:
  - onEvent 审核状态短路
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

回调路由去重规则：`onEvent` 非变更广播时，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的记录直接跳过，仅处理审核中，避免与 CustWorkflowAuditCommitProcessor 重复处理。

## 需求背景
运营中台的审核终态既会通过事件回调到达产融，也会由工作流提交处理器处理；若两条路径都消费终态，会造成 [[tables/cust_company_info]] 建档状态的重复推进。因此回调侧只处理「审核中」这一中间态，终态交由工作流处理。

## 版本演进
- v0 契约：短路条件取自 `CustSyncEventProvider.onEvent`；与 [[processes/cust-company-build-status]] 中 CUST_BUILDING → BUILD_SUCCESS / CUST_CONFIRM_AWAIT 的迁移路径互补。

```ground:rule
name: 拒绝/通过回调由工作流处理
content: "onEvent 非变更广播时，checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT 的记录直接跳过，仅处理审核中，避免与 CustWorkflowAuditCommitProcessor 重复处理"
impact: 回调路由去重，防止重复消费
field_targets:
  - cust_company_info.cust_build_status
evidence: "CustSyncEventProvider.java:onEvent"
related_pages:
  - tables/cust_company_info
  - processes/cust-company-build-status
```

---END FILE---

---FILE: rules/sync-by-role.md ---
---
type: rule
title: 按角色维度同步
page_key: rules/sync-by-role
domain: 平台事件监听与同步
status: draft
aliases:
  - syncByRole
  - syncByRoleOn
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:getRoles/syncByRole
contract_version: "0.1"
---

同步维度规则：同步前按 `dbTenantCode + companyCode + (companyType)` 查有效 CustRoleInfoDO，逐角色调用 custClientSyncService；`syncByRoleOn` 开关决定是否忽略 companyType 做全角色同步。

## 需求背景
企业在不同角色下（如 SUPPLIER）对下游系统的可见性不同，因此一次企业事件需要展开为多条按角色同步的 RPC。取数口径见 [[calibers/valid-cust-role]]，角色来源见 [[tables/cust_role_info]]；每条同步 RPC 失败即落 [[tables/client_api_sync_error]]。

## 版本演进
- v0 契约：开关名为 `syncByRoleOn`，默认行为未在语义分析中给出，需配置面确认。

```ground:rule
name: 按角色维度同步
content: "同步前按 dbTenantCode+companyCode+(companyType) 查有效 CustRoleInfoDO，逐角色调用 custClientSyncService；syncByRoleOn 开关决定是否忽略 companyType 全角色同步"
impact: 控制一次企业事件产生多条按角色同步的RPC
field_targets:
  - cust_role_info.role_type
  - cust_role_info.enable
evidence: "CustSyncService.java:getRoles/syncByRole"
related_pages:
  - tables/cust_role_info
  - calibers/valid-cust-role
  - tables/client_api_sync_error
```

---END FILE---

---FILE: rules/operator-delete-freeze-only.md ---
---
type: rule
title: 经办人DELETE仅冻结经办人角色
page_key: rules/operator-delete-freeze-only
domain: 平台事件监听与同步
status: draft
aliases:
  - syncOperatorUser 删除规则
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

删除规则：同一手机号既有经办人又有管理员时，DELETE 仅将经办人记录 `enable` 置 N 并冻结其 accountNormal 角色关联（`is_freeze='Y'`），不动管理员。

## 需求背景
手机号是联系人的自然标识，一人多角色常见。若删除经办人时连同管理员一并冻结，会误伤管理员权限；因此删除必须限定在经办人记录与其 accountNormal 关联上。涉及的过滤口径见 [[calibers/valid-contact-person]] 与 [[calibers/operator-role-rel-not-frozen]]。

## 版本演进
- v0 契约：规则取自 `CustSyncEventProvider.syncOperatorUser`；「accountNormal」角色关联的冻结范围未在语义分析中进一步展开。

```ground:rule
name: 经办人DELETE仅冻结经办人角色
content: "同一手机号既有经办人又有管理员时，DELETE 仅将经办人记录 enable 置N并冻结其 accountNormal 角色关联（is_freeze=Y），不动管理员"
impact: 避免误冻管理员权限
field_targets:
  - cust_person_info.enable
  - sys_cust_user_rel.is_freeze
evidence: "CustSyncEventProvider.java:syncOperatorUser"
related_pages:
  - tables/cust_person_info
  - tables/sys_cust_user_rel
  - calibers/operator-role-rel-not-frozen
```

---END FILE---

---FILE: rules/compensation-tenant-context-all.md ---
---
type: rule
title: 补偿任务租户上下文全量查询
page_key: rules/compensation-tenant-context-all
domain: 平台事件监听与同步
status: draft
aliases:
  - dbTenantCode='all'
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords/processCompensationRecord
contract_version: "0.1"
---

租户上下文规则：补偿任务查询时设置 `dbTenantCode='all'` 全量扫描，处理单条时再按 `record.dbTenantCode` 还原租户上下文。

## 需求背景
补偿任务是后台任务，不承载具体请求的租户上下文；若按当前租户过滤，会漏扫其他租户沉积的失败记录。因此查询阶段放开租户过滤，处理阶段再切回记录自身的租户，保证重放时数据源指向正确。扫描口径见 [[calibers/build-compensation-pending-records]]。

## 版本演进
- v0 契约：规则取自 `getCompensationRecords/processCompensationRecord`；「all」的取值约定属实现细节，未在语义分析中展开。

```ground:rule
name: 补偿任务租户上下文全量查询
content: "补偿任务查询时设置 dbTenantCode='all' 全量扫描，处理单条时再按 record.dbTenantCode 还原租户上下文"
impact: 跨租户补偿记录可见性
field_targets:
  - cust_build_record.db_tenant_code
evidence: "RegAsyncCompensationJobHandler.java:getCompensationRecords/processCompensationRecord"
related_pages:
  - tables/cust_build_record
  - calibers/build-compensation-pending-records
```

---END FILE---

---FILE: rules/sync-exception-retain-context.md ---
---
type: rule
title: 同步异常保留上下文不吞
page_key: rules/sync-exception-retain-context
domain: 平台事件监听与同步
status: draft
aliases:
  - custClientSyncService.error
oid: 1
scope:
  databases:
    - unknown
sources:
  - code:CustSyncService.java:syncByRole
  - db:client_api_sync_error
  - "reqdoc:失败数据写入 ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
contract_version: "0.1"
---

异常处理规则：同步失败经 `custClientSyncService.error(e, rpcSync)` 落库 [[tables/client_api_sync_error]] 后抛出，保留上下文用于后续重放与排查。

## 需求背景
同步失败若被静默吞掉，上游无法感知、下游无法重放。落库保留 `service_class_name` 与 `param`（入参原文）使失败可追溯、可重放；「失败数据写入 ClientApiSyncErrorDO，调用异常 → error(...) → 落库」这一文档主张已在代码层证实（`CustSyncService.java:syncByRole`），双源锚点见 frontmatter sources。

## 版本演进
- v0 契约：规则取自 `CustSyncService.syncByRole`；失败记录后续如何被重放，见 [[tables/client_api_sync_error]] 的 ## 版本演进（含未证实主张）。

```ground:rule
name: 同步异常保留上下文不吞
content: "同步失败经 custClientSyncService.error(e, rpcSync) 落库 client_api_sync_error 后抛出，用于后续重放与排查"
impact: 同步失败可追溯、可重试
field_targets:
  - client_api_sync_error.service_class_name
  - client_api_sync_error.param
evidence: "CustSyncService.java:syncByRole + reqdoc:失败数据写入ClientApiSyncErrorDO，调用异常 → error(...) → 落库"
related_pages:
  - tables/client_api_sync_error
  - concepts/sync-error-record
  - calibers/client-sync-error-all-disabled
```

---END FILE---