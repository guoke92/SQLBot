---FILE: tables/client_api_sync_error.md ---
---
type: table
title: client_api_sync_error 客户端同步失败记录表
page_key: client_api_sync_error
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户端接口同步失败记录
  - 同步失败登记表
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:AbstractQueueThread.java:464
contract_version: "0.1"
---

本表是平台向客户端（客户、经办人、影像、产品、租户、项目、KA 等）发起同步调用失败时的登记表。每条记录对应一次失败的 RPC 调用，`service_class_name` 标识具体同步链路，`param` 保留请求参数原文，供重试/排查使用。与 [[cust_build_record]] 的差别在于：本表以「调用失败即登记」为粒度，重试次数有独立列 [[retry_count]]；而建档补偿把重试计数塞进 JSON。

## 需求背景

外部同步链路（用户/企业/经办人/影像/产品/租户/项目/KA）在异常时不能让主流程失败，因此统一落到本表，由后台线程池侧（`AbstractQueueThread`）写入并在启用标识为 Y 时继续被重试消费。实测 `name` 与 `remark` 中出现的「直推变更回调连通性」「self-test retry」说明本表同时被用做链路自检的落点。

## 版本演进

- 存量 2227 行 `enable` 全部为 N、`retry_num` 常驻 3，对应「已登记失败/已终止重试」的保留口径，见 [[sync_error_retained_scope]]。
- `service_class_name` 的实测 TopK 以 `ClientCustSyncService`(1453) 与 `ClientOperatorSyncService`(555) 为最多，说明本表当前主要承担客户与经办人同步的失败登记。

```ground:table
table: client_api_sync_error
fields:
  - name: id
    type: unknown
    desc: 表主键
    dict: ""
  - name: service_class_name
    type: unknown
    desc: 失败的客户端同步服务类名，标识具体同步链路（客户/经办人/影像/产品/租户/项目/KA等），实测 TopK 以 ClientCustSyncService(1453) 与 ClientOperatorSyncService(555) 为最多
    dict: ""
  - name: retry_num
    type: unknown
    desc: 已重试次数，实测存量记录常驻 3（达最大重试上限）
    dict: ""
  - name: enable
    type: unknown
    desc: 启用标识，表默认 Y，但实测存量失败记录全为 N（失败记录登记后置 N）
    dict: "EnableEnum"
  - name: param
    type: unknown
    desc: RPC 调用的请求参数原文
    dict: ""
  - name: name
    type: unknown
    desc: 名称/标签，实测出现“直推变更回调连通性”等自检标签
    dict: ""
  - name: remark
    type: unknown
    desc: 备注，实测出现 self-test retry 等自检说明
    dict: ""
  - name: app_tenant_code
    type: unknown
    desc: 逻辑租户标识，实测恒为 base
    dict: ""
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: ""
  - name: act_procinst_id
    type: unknown
    desc: 运营中台流程实例ID
    dict: ""
  - name: act_procinst_no
    type: unknown
    desc: 流程申请编号
    dict: ""
  - name: act_procinst_status
    type: unknown
    desc: 当前审批状态
    dict: ""
  - name: act_procinst_date
    type: unknown
    desc: 审批结束时间
    dict: ""
```

---END FILE---

---FILE: tables/cust_build_record.md ---
---
type: table
title: cust_build_record 客户建档异步补偿记录表
page_key: cust_build_record
domain: 平台事件监听与同步
status: draft
aliases:
  - 建档补偿记录
  - 异步建档补偿表
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:cust_build_record
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
---

本表承载客户建档异步流程失败后的补偿重试登记。与 [[client_api_sync_error]] 不同，本表没有独立的重试次数列，重试计数写在 `returnData` 的 JSON 里；失败类型写在 `remark` 前缀里，由 xxl-job 按前缀筛选后整体重放 `regAsyncService.orchestrateAsync(context)`（`pushData` 即反序列化来源）。

## 需求背景

建档链路中存在「文件推送」与「拉起流程」两个易失败的外部动作，失败时不直接抛出，而是调用 `saveCompensationRecord` 落一条 PENDING 记录，由 `regAsyncCompensationJobHandler` 定时捞取重试。重试状态机见 [[cust_build_compensation_retry]]，重试上限规则见 [[compensation_max_retry]]，失败类型识别见 [[compensation_fail_type]]。

## 版本演进

- 补偿记录以 `remark LIKE 'COMPENSATION_%'` 作为识别口径，见 [[compensation_record_filter]]；job 只扫 PENDING/RETRYING，见 [[compensation_retry_task_filter]]。
- 重试成功在 `remark` 追加 `_RETRY_SUCCESS`，达上限追加 `_FAILED_MAX_RETRY_n`，是判断记录终态最直接的旁证。

```ground:table
table: cust_build_record
fields:
  - name: retry_status
    type: unknown
    desc: 建档异步流程补偿重试状态（PENDING/RETRYING/SUCCESS/FAILED）
    dict: "CompensationRetryStatus"
  - name: remark
    type: unknown
    desc: 补偿标记：COMPENSATION_FILE_PUSH_FAIL / COMPENSATION_START_FLOW_FAIL，重试成功追加 _RETRY_SUCCESS，达上限追加 _FAILED_MAX_RETRY_n
    dict: ""
  - name: pushData
    type: unknown
    desc: RegAsyncContext 序列化 JSON，供补偿任务反序列化后重放 orchestrateAsync
    dict: ""
  - name: returnData
    type: unknown
    desc: 错误信息 JSON（failType/errorMessage/errorCode/stackTrace/retryCount/lastRetryTime）
    dict: ""
  - name: dbTenantCode
    type: unknown
    desc: 建档企业所属数据租户，补偿任务据此切换租户上下文
    dict: ""
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info 客户企业信息表
page_key: cust_company_info
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户企业信息
  - 建档企业主表
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
contract_version: "0.1"
---

> (document_claim，未证实) 本页「版本演进」含需求文档主张但代码未覆盖的内容。

本表是客户企业的主记录，`cust_build_status` 是平台侧观察企业建档进度的核心字段，其状态机见 [[cust_build_status]]；`need_register_ca` / `ca_register_status` 用于承载电子签章开通决策，见 [[simple_auth_no_ca]]。

## 需求背景

需求文档主张两条主线：一是「用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台」，二是「企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回」。后者在代码侧由 `CustCompanyInfoApplication.updateCustBuildStatus` 承接，对应状态机的审核通过与审核拒绝两条迁移。`enable` 统一由 [[enable_flag]] 描述的 EnableEnum(Y/N) 表达；企业名称/统一社会信用代码的校验在 `importCustCompany` 中存在（“录入统一社会信用代码已存在”），但唯一性是租户维度，非全局唯一——该主张仅作叙述，暂无独立代码证据支撑。

## 版本演进

- 简易认证路径新增 CA 校正逻辑：提交时若 `need_register_ca=Y` 会被 `CustCompanyCaPolicy.enforceMustNotOpenCa` 强制校正为不开通并落库。
- （document_claim，未证实）需求文档提出「企业信息变更流程：创建变更记录（待提交）→审核→生效/驳回」，语义分析未给出对应代码证据，变更流程的落库表与状态字段待补。

```ground:table
table: cust_company_info
fields:
  - name: cust_build_status
    type: unknown
    desc: 客户建档状态（INIT/BUILD_FAIL/CUST_CONFIRM_AWAIT/CUST_BUILDING/BUILD_SUCCESS/AWAIT_CUST_CONFIRM）
    dict: "custBuildStatus 常量类"
  - name: need_register_ca
    type: unknown
    desc: 是否开通电子签章；简易认证提交时若为 Y 会被强制校正为不开通并落库
    dict: ""
  - name: ca_register_status
    type: unknown
    desc: 电子签章开通状态，随 need_register_ca 的校正结果落库
    dict: ""
  - name: enable
    type: unknown
    desc: 企业启用标识，统一由 EnableEnum(Y/N) 表达
    dict: "EnableEnum"
```

---END FILE---

---FILE: tables/cust_person_info.md ---
---
type: table
title: cust_person_info 客户人员信息表
page_key: cust_person_info
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户人员
  - 经办人/管理员信息
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:cust_person_info
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

人员（管理员/经办人/访客）维度记录，是本主题中「用户同步」一侧的落点。冻结、删除、变更等事件最终都体现为 `user_type` 与 `enable` 的组合，见 [[operator_sync_branch]]。

## 需求背景

同步链路的输入来自运营中台事件：管理员与经办人分别以 `UserTypeEnum.admin` / `UserTypeEnum.operator` 的 dictKey 落库，访客为 `guest`。删除经办人时并不物理删除，而是置 `enable=N`，并且只在同手机号既是经办人又是管理员时才这样做，以免误伤管理员权限，见 [[sys_cust_user_rel]]。

## 版本演进

- 冻结口径引入 `UserFreezeEnum.FREEZE.getDictKey()` 写 [[sys_cust_user_rel]] 的 `is_freeze`，人员侧则写 `EnableEnum.N.name()`。
- 存在同一文件内混用 `EnableEnum.N.name()` 与字面量 `'Y'` 的写值方式，见 [[enable_flag]] 与页末 REVIEW。

```ground:table
table: cust_person_info
fields:
  - name: user_type
    type: unknown
    desc: 人员用户类型，取值 admin/operator/guest，落库使用 UserTypeEnum.getDictKey()
    dict: "UserTypeEnum"
  - name: enable
    type: unknown
    desc: 人员启用标识，同步冻结/删除时置 N（EnableEnum.N.name()），另有字面量 'Y' 直写
    dict: "EnableEnum"
```

---END FILE---

---FILE: tables/sys_cust_user_rel.md ---
---
type: table
title: sys_cust_user_rel 系统客户用户角色关联表
page_key: sys_cust_user_rel
domain: 平台事件监听与同步
status: draft
aliases:
  - 用户角色关联
  - 角色冻结记录
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:sys_cust_user_rel
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

> (document_claim，未证实) 本页「版本演进」含需求文档主张但代码未覆盖的内容。

用户与角色（含 accountNormal 等）的关联记录。本主题中它主要出现在「经办人删除」的分支里：不删除关联，而是冻结，见 [[operator_freeze_scope]] 与 [[operator_sync_branch]]。

## 需求背景

DELETE 事件且同手机号既为经办人又为管理员时，仅把经办人记录 `enable=N`，并冻结其对 accountNormal 角色的关联（`is_freeze` 写 `UserFreezeEnum.FREEZE.getDictKey()`）。这样做的业务意图是避免把同一自然人的管理员权限一并冻掉。

## 版本演进

- 冻结用 `getDictKey()` 而非 `name()` 落库，与人员表的 `EnableEnum.N.name()` 写法不一致，跨表比对时需注意。
- （document_claim，未证实）需求文档提出「权限与角色管理：管理员配置角色、分配菜单/数据权限、用户按角色加载」，语义分析未给出对应用代码证据，角色/菜单/数据权限的落点表待补。

```ground:table
table: sys_cust_user_rel
fields:
  - name: is_freeze
    type: unknown
    desc: 角色关联冻结标识，冻结时写 UserFreezeEnum.FREEZE.getDictKey()（Y）
    dict: "UserFreezeEnum"
  - name: enable
    type: unknown
    desc: 记录启用标识；DELETE 且同手机号既是经办人又是管理员时，仅经办人记录置 N
    dict: "EnableEnum"
```

---END FILE---

---FILE: tables/client_cust_event.md ---
---
type: table
title: client_cust_event 客户端客户事件表
page_key: client_cust_event
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户事件
  - 运营中台客户事件
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_cust_event
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

承载运营中台推送给平台的客户事件，`checkStatus` 记录当前审核检查状态，状态机见 [[cust_event_check_status]]。

## 需求背景

外部回调进入 `CustSyncEventProvider.onEvent`：当 `isChangeBroadcast=false` 且 `checkStatus` 为通过/拒绝时，本方法直接返回，交由工作流审核执行器处理，避免双写，见 [[external_callback_skip_pass_reject]]。其余事件经 `processCustEvent → custSyncEventProcessor.doEvent` 按客户事件类型落库。

## 版本演进

- 状态值以 `OperApiConstants.CheckStatus.name()` 落库（`CUST_CHECK_INIT` / `CUST_CHECK_PASS` / `CUST_CHECK_REJECT` / `CUST_CHECK_BACKTOCUSTOM`），与 `cust_info_sync.process_type` 用 `getCode()` 的写法不同，跨表比对需注意。

```ground:table
table: client_cust_event
fields:
  - name: check_status
    type: unknown
    desc: 运营中台客户事件检查状态（CUST_CHECK_INIT/CUST_CHECK_PASS/CUST_CHECK_REJECT/CUST_CHECK_BACKTOCUSTOM），以 OperApiConstants.CheckStatus.name() 落库
    dict: "OperApiConstants.CheckStatus"
```

---END FILE---

---FILE: tables/cust_info_sync.md ---
---
type: table
title: cust_info_sync 客户信息同步记录表
page_key: cust_info_sync
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户信息同步
  - 同步请求记录
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:cust_info_sync
  - code:CustCompanyInfoApplication.java:syncClientForSimple
contract_version: "0.1"
---

记录平台向运营中台发起的客户信息同步请求，`processType` 区分「建档/审核流程」与「变更流程」，是 [[cust_build_status]] 状态迁移的外部触发点。

## 需求背景

需求文档主张「企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回」，其上游即本表所记录的同步请求：`CUST_CHECK_INIT` 由 `operCustFacade.doSyncClient` 发起，变更侧由 `CustSyncService.requestSync(ProcessTy.CHANGE, ...)` 发起。

## 版本演进

- `processType` 落库使用 `ProcessTy.getCode()` 而非 `name()`，同族枚举在本主题内存在三种落库风格（name() / getCode() / getDictKey()），是排查数据时的常见陷阱。

```ground:table
table: cust_info_sync
fields:
  - name: process_type
    type: unknown
    desc: 同步流程类型（CHECK 建档/审核流程、CHANGE 变更流程），以 OperApiConstants.ProcessTy.getCode() 落库
    dict: "OperApiConstants.ProcessTy"
```

---END FILE---

---FILE: enums/cust_build_record_retry_status.md ---
---
type: enum
title: cust_build_record.retry_status 补偿重试状态
page_key: cust_build_record_retry_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 补偿重试状态
  - CompensationRetryStatus
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:handleRetrySuccess
  - code:RegAsyncCompensationJobHandler.java:markAsFailed
contract_version: "0.1"
---

建档异步补偿的重试状态取值，驱动 [[cust_build_compensation_retry]] 的迁移，并被 [[compensation_retry_task_filter]] 用作待重试集合的筛选条件。

## 需求背景

xxl-job 只捞取 PENDING 与 RETRYING 的记录；重试成功落 SUCCESS，重试次数达上限或类型未知落 FAILED，判定逻辑见 [[compensation_max_retry]]。

## 版本演进

- 四个取值均由 `CompensationRetryStatus` 常量以 MyBatis 直写落库，未见历史别名。

```ground:enum
field: cust_build_record.retry_status
java_name: CompensationRetryStatus
stored_as: enum 常量（MyBatis 直写）
values:
  - value: PENDING
    label: 待重试
    java_name: CompensationRetryStatus.PENDING
    stored_as: enum 常量
    note: ""
  - value: RETRYING
    label: 重试中
    java_name: CompensationRetryStatus.RETRYING
    stored_as: enum 常量
    note: ""
  - value: SUCCESS
    label: 重试成功
    java_name: CompensationRetryStatus.SUCCESS
    stored_as: enum 常量
    note: ""
  - value: FAILED
    label: 重试失败
    java_name: CompensationRetryStatus.FAILED
    stored_as: enum 常量
    note: ""
```

---END FILE---

---FILE: enums/client_cust_event_check_status.md ---
---
type: enum
title: client_cust_event.check_status 客户事件检查状态
page_key: client_cust_event_check_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户检查状态
  - OperApiConstants.CheckStatus
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:onEvent
  - code:CustCompanyInfoApplication.java:operCustFacade.doSyncClient
contract_version: "0.1"
---

运营中台客户事件的检查状态取值，驱动 [[cust_event_check_status]] 的迁移。

## 需求背景

`CUST_CHECK_PASS` / `CUST_CHECK_REJECT` 在 `isChangeBroadcast=false` 时由 [[external_callback_skip_pass_reject]] 显式跳过；`CUST_CHECK_INIT` 由平台侧 `operCustFacade.doSyncClient` 发起。

## 版本演进

- 以 `OperApiConstants.CheckStatus.name()` 落库；同一常量类下的 `ProcessTy` 走 `getCode()`，比对时不可想当然互推。

```ground:enum
field: client_cust_event.check_status
java_name: OperApiConstants.CheckStatus
stored_as: .name()
values:
  - value: CUST_CHECK_INIT
    label: 提交审核发起
    java_name: OperApiConstants.CheckStatus.CUST_CHECK_INIT
    stored_as: .name()
    note: ""
  - value: CUST_CHECK_PASS
    label: 审核通过
    java_name: OperApiConstants.CheckStatus.CUST_CHECK_PASS
    stored_as: .name()
    note: 由工作流执行器处理，onEvent 中跳过
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    java_name: OperApiConstants.CheckStatus.CUST_CHECK_REJECT
    stored_as: .name()
    note: 由工作流执行器处理，onEvent 中跳过
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户确认
    java_name: OperApiConstants.CheckStatus.CUST_CHECK_BACKTOCUSTOM
    stored_as: .name()
    note: ""
```

---END FILE---

---FILE: processes/cust_build_compensation_retry.md ---
---
type: process
title: 建档异步补偿重试状态机
page_key: cust_build_compensation_retry
domain: 平台事件监听与同步
status: draft
aliases:
  - 补偿重试流程
  - 建档补偿状态机
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncService.java:saveCompensationRecord
  - code:RegAsyncCompensationJobHandler.java:processCompensationRecord
contract_version: "0.1"
---

用于描述 [[cust_build_record]] 的 `retry_status` 在 xxl-job 驱动下的流转。记录由建档失败时创建为 PENDING，job 捞取后置 RETRYING，成功落 SUCCESS，失败按上限回到 PENDING 或落 FAILED。

## 需求背景

需求侧要求建档不因外部依赖（文件推送、流程拉起）失败而中断：失败即登记补偿记录并重试，重试粒度为整条 `orchestrateAsync(context)` 重放，失败类型仅用于定位，见 [[compensation_fail_type]] 与 [[compensation_max_retry]]。job 只处理 `remark LIKE 'COMPENSATION_%'` 且状态在 PENDING/RETRYING 的记录，见 [[compensation_record_filter]]。

## 版本演进

- 终态标记沿用 `remark` 追加后缀（`_RETRY_SUCCESS`、`_FAILED_MAX_RETRY_n`）的方式，`retry_status` 之外还有一层文本旁证。
- 状态取值见 [[cust_build_record_retry_status]]。

```ground:process
name: 建档异步补偿重试状态
field: cust_build_record.retry_status
states:
  - value: PENDING
    label: 待重试
    source: code_const
  - value: RETRYING
    label: 重试中
    source: code_const
  - value: SUCCESS
    label: 重试成功
    source: code_const
  - value: FAILED
    label: 重试失败/放弃
    source: code_const
transitions:
  - from: "(新建)"
    event: saveCompensationRecord
    to: PENDING
    evidence: "code_path:RegAsyncService.java:saveCompensationRecord"
  - from: PENDING
    event: xxl-job 命中补偿记录
    to: RETRYING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:processCompensationRecord(record.setRetryStatus(RETRYING))"
  - from: RETRYING
    event: retryCompensation 成功
    to: SUCCESS
    evidence: "code_path:RegAsyncCompensationJobHandler.java:handleRetrySuccess"
  - from: RETRYING
    event: 重试失败且 retryCount<maxRetryCount
    to: PENDING
    evidence: "code_path:RegAsyncCompensationJobHandler.java:updateRetryCount(setRetryStatus(PENDING))"
  - from: RETRYING
    event: retryCount>=maxRetryCount 或类型未知
    to: FAILED
    evidence: "code_path:RegAsyncCompensationJobHandler.java:markAsFailed"
```

---END FILE---

---FILE: processes/cust_event_check_status.md ---
---
type: process
title: 运营中台客户事件检查状态机
page_key: cust_event_check_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 客户事件检查流程
  - 回调检查状态机
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:onEvent
  - code:CustSyncEventProvider.java:processCustEvent
contract_version: "0.1"
---

描述 [[client_cust_event]] 的 `checkStatus` 在外部回调与平台处理之间的流转边界。关键点在于：审核通过与拒绝两个状态在本方法内不落库、不处理，交由工作流审核执行器。

## 需求背景

需求文档主张「用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台」，其事件入口即本流程的外部回调；但审核结论类事件（PASS/REJECT）必须由工作流执行器 `CustWorkflowAuditCommitProcessor` 处理，以避免与工作流双写，见 [[external_callback_skip_pass_reject]]。变更广播（`isChangeBroadcast=true`）时仍走本方法。

## 版本演进

- 平台侧发起的检查状态由 `operCustFacade.doSyncClient` 写入 `CUST_CHECK_INIT`，取值见 [[client_cust_event_check_status]]。
- 其余客户事件经 `processCustEvent → custSyncEventProcessor.doEvent` 按事件类型落库，是本流程与用户/企业同步（[[operator_sync_branch]]、[[company_status_sync]]）的分界。

```ground:process
name: 运营中台客户事件检查状态
field: ClientCustEvent.custEnterprise.checkStatus
states:
  - value: CUST_CHECK_INIT
    label: 提交/审核发起
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
transitions:
  - from: CUST_CHECK_PASS
    event: 外部回调 onEvent(isChangeBroadcast=false)
    to: "(跳过/由工作流执行器处理)"
    evidence: "code_path:CustSyncEventProvider.java:onEvent"
  - from: CUST_CHECK_REJECT
    event: 外部回调 onEvent(isChangeBroadcast=false)
    to: "(跳过/由工作流执行器处理)"
    evidence: "code_path:CustSyncEventProvider.java:onEvent"
  - from: "(其它)"
    event: processCustEvent → custSyncEventProcessor.doEvent
    to: 按客户事件类型落库
    evidence: "code_path:CustSyncEventProvider.java:processCustEvent"
```

---END FILE---

---FILE: processes/cust_build_status.md ---
---
type: process
title: 客户建档状态机
page_key: cust_build_status
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业建档状态
  - cust_build_status 流转
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
contract_version: "0.1"
---

描述 [[cust_company_info]] 的 `cust_build_status` 在「邀请录入 → 提交运营中台 → 审核」之间的流转，是平台侧观察建档进度的主视角。

## 需求背景

需求文档主张「企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回」，对应本状态机中 `CUST_BUILDING → BUILD_SUCCESS` 与 `CUST_BUILDING → BUILD_FAIL` 两条迁移，均由 `CustCompanyInfoApplication.updateCustBuildStatus` 承接；上游发起见 [[cust_info_sync]]。同步请求的检查状态与之对应，见 [[cust_event_check_status]]；状态变更后还联动企业/用户冻结口径，见 [[company_status_sync]]。

## 版本演进

- 简易认证路径新增 `AWAIT_CUST_CONFIRM`，且提交时强制不开通电子签章，见 [[simple_auth_no_ca]]。
- 退回（运营中台退回）回落到 `CUST_CONFIRM_AWAIT`，与「待客户确认/待提交审核」共用同一状态值，语义上偏宽。

```ground:process
name: 客户建档状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始
    source: code_const
  - value: BUILD_FAIL
    label: 审核拒绝/建档失败
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认/待提交审核
    source: code_const
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_const
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_const
  - value: AWAIT_CUST_CONFIRM
    label: 简易认证待确认
    source: code_const
transitions:
  - from: INIT/BUILD_FAIL
    event: 邀请认证客户录入提交
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify/updateCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus + reqdoc:企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回"
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus + reqdoc:企业准入审核通过则更新企业状态为已通过，驳回则更新为已驳回"
```

---END FILE---

---FILE: calibers/sync_error_retained_scope.md ---
---
type: caliber
title: 同步失败记录存量口径
page_key: sync_error_retained_scope
domain: 平台事件监听与同步
status: draft
aliases:
  - enable=N 口径
  - 失败记录保留口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
contract_version: "0.1"
---

查询 [[client_api_sync_error]] 时，`enable='N'` 是存量记录的默认观测值，应被理解为「已登记失败/已终止重试」的记录集合，而不是停用配置。

## 需求背景

同步失败需要留痕以便排查与人工重放，因此失败登记后即置 N；表结构默认 Y 只是新增记录的初始值，不代表现存数据分布。统计失败量时若按 `enable='Y'` 过滤会得到空集。

## 版本演进

- 存量 2227 行全部为 N，且 `retry_num` 常驻 3，说明这批记录已不再被重试消费。
- 与 [[cust_build_record]] 的补偿集合不同：后者以状态列（PENDING/RETRYING）而非 `enable` 表达可重试性，见 [[compensation_retry_task_filter]]。

```ground:caliber
name: 同步失败记录存量口径
predicate: "client_api_sync_error.enable = 'N'"
scope: 存量 2227 行全部为 N，作为“已登记失败/已终止重试”记录保留
evidence: db
```

---END FILE---

---FILE: calibers/compensation_record_filter.md ---
---
type: caliber
title: 补偿记录筛选口径
page_key: compensation_record_filter
domain: 平台事件监听与同步
status: draft
aliases:
  - COMPENSATION_ 前缀筛选
  - 补偿记录识别
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
---

xxl-job 从 [[cust_build_record]] 中捞取补偿记录时，以 `remark` 前缀 `COMPENSATION_` 作为唯一识别条件。

## 需求背景

`remark` 同时承载失败标记与终态后缀（`_RETRY_SUCCESS`、`_FAILED_MAX_RETRY_n`），因此只能用前缀匹配而不能用等值匹配；带后缀的历史记录仍会被捞出，是否重试再交给状态口径判断，见 [[compensation_retry_task_filter]]。

## 版本演进

- 失败类型由 `remark` 中的 `FILE_PUSH_FAIL` / `START_FLOW_FAIL` 反推，见 [[compensation_fail_type]]；这意味着新增失败类型必须同步维护该前缀约定。

```ground:caliber
name: 补偿记录筛选
predicate: "cust_build_record.remark LIKE 'COMPENSATION_%'"
scope: xxl-job 只处理 remark 以 COMPENSATION_ 开头的记录
evidence: "code:RegAsyncCompensationJobHandler.java:getCompensationRecords"
```

---END FILE---

---FILE: calibers/compensation_retry_task_filter.md ---
---
type: caliber
title: 补偿重试任务状态筛选口径
page_key: compensation_retry_task_filter
domain: 平台事件监听与同步
status: draft
aliases:
  - 待重试集合
  - PENDING/RETRYING 口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
---

`regAsyncCompensationJobHandler` 的待重试集合 = [[compensation_record_filter]] ∩ `retry_status IN ('PENDING','RETRYING')`。

## 需求背景

状态筛选保证终态（SUCCESS/FAILED）不会被再次重放；状态机见 [[cust_build_compensation_retry]]，取值见 [[cust_build_record_retry_status]]。若人工需要重放一条 FAILED 记录，必须先把状态改回 PENDING，单纯清空 `remark` 后缀无效。

## 版本演进

- 当前筛选为双状态等值集合，未按 `retryCount` 或时间窗口做二次过滤，重试节奏完全由 job 调度周期决定。

```ground:caliber
name: 补偿重试任务状态筛选
predicate: "cust_build_record.retry_status IN ('PENDING','RETRYING')"
scope: xxl-job regAsyncCompensationJobHandler 待重试集合
evidence: "code:RegAsyncCompensationJobHandler.java:getCompensationRecords"
```

---END FILE---

---FILE: calibers/operator_freeze_scope.md ---
---
type: caliber
title: 经办人角色冻结口径
page_key: operator_freeze_scope
domain: 平台事件监听与同步
status: draft
aliases:
  - 经办人冻结范围
  - is_freeze=Y 口径
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

删除经办人时的冻结范围口径：只冻结经办人记录对应的 `accountNormal` 角色关联，即 [[sys_cust_user_rel]].`is_freeze='Y'`，不动管理员。

## 需求背景

同手机号既为经办人又为管理员时，若按用户维度整体冻结会误伤管理员权限；因此改为按记录维度：经办人记录 `enable=N`（见 [[cust_person_info]]），并仅冻结其对 `accountNormal` 的关联。分支细节见 [[operator_sync_branch]]。

## 版本演进

- 冻结值使用 `UserFreezeEnum.FREEZE.getDictKey()`，与人员表 `EnableEnum.N.name()` 的落库风格不同，跨表核对时需按各自风格取值。
- 该口径只覆盖 DELETE 事件；FREEZE/THAW 走独立的冻结/解冻分支。

```ground:caliber
name: 经办人角色冻结口径
predicate: "sys_cust_user_rel.is_freeze = 'Y'"
scope: DELETE 且同手机号既为经办人又为管理员时，仅冻结经办人记录对应 accountNormal 角色关联
evidence: "code:CustSyncEventProvider.java:syncOperatorUser"
```

---END FILE---

---FILE: concepts/retry_count.md ---
---
type: concept
title: 重试次数
page_key: retry_count
domain: 平台事件监听与同步
status: draft
aliases:
  - retryNum
  - retryCount
  - 重试计数
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
maps_to: client_api_sync_error.retry_num
field_targets:
  - client_api_sync_error.retry_num
  - cust_build_record.return_data
adjudication: boundary
also_confused_with:
  - cust_build_record.return_data
---

「重试次数」在本主题内有两个完全不同的落点，同名不同形，是排查时的头号陷阱。

## 需求背景

[[client_api_sync_error]] 用独立列 `retry_num` 记录已重试次数，实测存量常驻 3（达最大重试上限）；[[cust_build_record]] 没有独立列，补偿重试次数塞在 `return_data` JSON 的 `retryCount` 字段里，与 `lastRetryTime` 一起由补偿任务维护。上限判定见 [[compensation_max_retry]]。

## 版本演进

- 两个域各自演化：同步失败表用列 + 启用标识表达终态（见 [[sync_error_retained_scope]]），补偿表用状态列 + JSON 计数表达终态（见 [[cust_build_compensation_retry]]）。
- 口径建议：按代码名 `retryNum` 检索时只查 `client_api_sync_error`，按 `retryCount` 检索时只查 `cust_build_record.return_data`，不要跨表合并统计。

---END FILE---

---FILE: concepts/app_tenant_code.md ---
---
type: concept
title: 逻辑租户
page_key: app_tenant_code
domain: 平台事件监听与同步
status: draft
aliases:
  - appTenantCode
  - AppTenantCode
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
contract_version: "0.1"
maps_to: client_api_sync_error.app_tenant_code
field_targets:
  - client_api_sync_error.app_tenant_code
adjudication: boundary
also_confused_with:
  - client_api_sync_error.db_tenant_code
---

「逻辑租户」指应用层的租户标识，与数据隔离租户是两件事，二者在同一张表上并列存在。

## 需求背景

[[client_api_sync_error]].`app_tenant_code` 为逻辑/应用租户，实测恒为 `base`；`db_tenant_code` 才是数据隔离租户，见 [[db_tenant_code]]。做数据筛选、报表分组时误用前者会得到单一分组。

## 版本演进

- 平台同步场景下逻辑租户长期为 `base`，说明本主题的租户差异主要体现在数据租户维度而非应用维度。
- 代码中命名为 `appTenantCode` / `AppTenantCode`，与列名 `app_tenant_code` 需人工映射。

---END FILE---

---FILE: concepts/db_tenant_code.md ---
---
type: concept
title: 数据租户
page_key: db_tenant_code
domain: 平台事件监听与同步
status: draft
aliases:
  - dbTenantCode
  - db_tenant_code
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:RegAsyncCompensationJobHandler.java:getCompensationRecords
contract_version: "0.1"
maps_to: client_api_sync_error.db_tenant_code
field_targets:
  - client_api_sync_error.db_tenant_code
  - cust_build_record.dbTenantCode
adjudication: boundary
also_confused_with:
  - client_api_sync_error.app_tenant_code
---

「数据租户」是真正的数据隔离维度，代码通过 `MetaDataThreadLocalConfig.setDbTenantCode` 切换上下文。

## 需求背景

同步任务执行前会先 `setDbTenantCode(dbTenantCode)`，见 [[cust_sync_by_role]]；补偿任务则从 [[cust_build_record]].`dbTenantCode` 还原建档企业所属租户后再重放。全量查询使用 `'all'`。与逻辑租户的区别见 [[app_tenant_code]]。

## 版本演进

- 线程上下文方式意味着同步链路对租户上下文有隐式依赖，跨租户批次混跑时需要显式重置。

---END FILE---

---FILE: concepts/enable_flag.md ---
---
type: concept
title: 启用标识
page_key: enable_flag
domain: 平台事件监听与同步
status: draft
aliases:
  - enable
  - EnableEnum
oid: 1
scope:
  databases: ["未确认"]
sources:
  - db:client_api_sync_error
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
maps_to: client_api_sync_error.enable
field_targets:
  - client_api_sync_error.enable
  - cust_company_info.enable
  - cust_person_info.enable
adjudication: synonym
also_confused_with:
  - cust_company_info.enable
---

各表的 `enable` 统一由 `EnableEnum(Y/N)` 表达，但在本主题内落库写法并不统一，是跨表比对的主要噪声来源。

## 需求背景

- [[client_api_sync_error]]：结构默认 Y，但存量失败记录全为 N（失败登记后置 N），见 [[sync_error_retained_scope]]。
- [[cust_person_info]] / [[sys_cust_user_rel]]：经办人删除时写 `EnableEnum.N.name()`，而另有代码路径直接写字面量 `'Y'`。
- [[cust_company_info]]：企业启用标识，同属 EnableEnum 语义。

## 版本演进

- 写值风格从字面量逐步收敛到枚举：`name()`、`getDictKey()`、字面量三者并存，见页末 REVIEW。

---END FILE---

---FILE: rules/external_callback_skip_pass_reject.md ---
---
type: rule
title: 外部回调不处理审核通过与拒绝
page_key: external_callback_skip_pass_reject
domain: 平台事件监听与同步
status: draft
aliases:
  - onEvent 跳过规则
  - PASS/REJECT 不由回调处理
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:onEvent
contract_version: "0.1"
---

外部回调 `onEvent(isChangeBroadcast=false)` 遇到 `CUST_CHECK_PASS` 或 `CUST_CHECK_REJECT` 时直接返回，不做任何处理。

## 需求背景

审核结论类事件必须由工作流审核执行器 `CustWorkflowAuditCommitProcessor` 处理，回调侧再处理一次会造成与企业建档状态机（[[cust_build_status]]）的双写。变更广播（`isChangeBroadcast=true`）时仍走本方法。状态取值见 [[client_cust_event_check_status]]，整体流转见 [[cust_event_check_status]]。

## 版本演进

- 该跳过逻辑与「按事件类型落库」的 `processCustEvent` 分支并存，理解入口时需先看 `isChangeBroadcast` 与 `checkStatus` 两个判别条件。

```ground:rule
name: 外部回调不处理 PASS/REJECT
content: onEvent(isChangeBroadcast=false) 时若 checkStatus 为 CUST_CHECK_PASS 或 CUST_CHECK_REJECT，直接 return，交由工作流审核执行器 CustWorkflowAuditCommitProcessor 处理
impact: 避免与工作流审核双写；变更广播 isChangeBroadcast=true 时仍走本方法
field_targets: []
evidence: "code:CustSyncEventProvider.java:onEvent"
```

---END FILE---

---FILE: rules/compensation_max_retry.md ---
---
type: rule
title: 补偿重试上限规则
page_key: compensation_max_retry
domain: 平台事件监听与同步
status: draft
aliases:
  - maxRetryCount 规则
  - 补偿重试上限
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:updateRetryCount
contract_version: "0.1"
---

重试次数达到上限后记录被标记为 FAILED 并放弃，否则重置为 PENDING 继续排队。

## 需求背景

上限默认 3。与 [[client_api_sync_error]] 的 `retry_num` 常驻 3 相互印证：两个域都采用「3 次即终止」的补偿策略，但一个用列、一个用 JSON，见 [[retry_count]]。判定时机在重试失败分支，成功分支直接落 SUCCESS，见 [[cust_build_compensation_retry]]。

## 版本演进

- 达上限时在 `remark` 追加 `_FAILED_MAX_RETRY_n`，使终态在文本层也可辨识，见 [[compensation_record_filter]]。
- 上限值来源为 `maxRetryCount` 配置，改配置会影响存量尚未终止的记录。

```ground:rule
name: 补偿重试上限规则
content: retryCount>=maxRetryCount(默认3) → markAsFailed；否则 retryStatus 重置 PENDING、retryCount+1 并写 lastRetryTime
impact: 决定补偿记录是否最终放弃
field_targets:
  - cust_build_record.retry_status
  - cust_build_record.return_data
evidence: "code:RegAsyncCompensationJobHandler.java:updateRetryCount"
```

---END FILE---

---FILE: rules/compensation_fail_type.md ---
---
type: rule
title: 补偿失败类型识别规则
page_key: compensation_fail_type
domain: 平台事件监听与同步
status: draft
aliases:
  - FILE_PUSH_FAIL/START_FLOW_FAIL 识别
  - 失败类型判定
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:RegAsyncCompensationJobHandler.java:extractFailType
  - code:RegAsyncCompensationJobHandler.java:retryCompensation
contract_version: "0.1"
---

失败类型由 `remark` 是否包含 `FILE_PUSH_FAIL` / `START_FLOW_FAIL` 反推定，但重试时并不按类型分派动作，而是整体重放建档异步流程。

## 需求背景

`saveCompensationRecord` 落库时以字面量拼接成 `COMPENSATION_FILE_PUSH_FAIL` / `COMPENSATION_START_FLOW_FAIL`（并非取枚举 label）。因此 [[cust_build_record]].`remark` 同时承担「筛选键」（见 [[compensation_record_filter]]）与「失败原因」两个职责。

## 版本演进

- 失败类型来自错误码常量 `PlatformEnumsExceptionEnum.FILE_PUSH_FAIL` / `START_FLOW_FAIL`，但落库为字符串拼接，枚举改名不会自动同步存量数据。
- 重试粒度为全流程，意味着类型识别只影响日志与定位，不影响行为；类型未知时直接落 FAILED，见 [[compensation_max_retry]]。

```ground:rule
name: 补偿失败类型识别
content: 按 remark 是否包含 FILE_PUSH_FAIL / START_FLOW_FAIL 判定失败类型，重试时整体重放 regAsyncService.orchestrateAsync(context)
impact: 补偿任务按失败类型定位但重试粒度为全流程
field_targets:
  - cust_build_record.remark
evidence: "code:RegAsyncCompensationJobHandler.java:extractFailType/retryCompensation"
```

---END FILE---

---FILE: rules/operator_sync_branch.md ---
---
type: rule
title: 经办人同步操作分支规则
page_key: operator_sync_branch
domain: 平台事件监听与同步
status: draft
aliases:
  - syncOperatorUser 分支
  - 经办人增删改冻
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncEventProvider.java:syncOperatorUser
contract_version: "0.1"
---

经办人事件按操作类型分流：INSERT/UPDATE 走新增与编辑，FREEZE/THAW/DELETE 走冻结、解冻与删除。

## 需求背景

需求文档主张「用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台」，代码侧由 `CustSyncEventProvider.syncOperatorUser` 承接并经 `CustSyncService` 广播。DELETE 分支的特别之处在于：同手机号既为经办人又为管理员时，仅将经办人记录 `enable=N` 并冻结其对 `accountNormal` 角色的关联（[[operator_freeze_scope]]、[[sys_cust_user_rel]]），人员侧写法见 [[cust_person_info]]。落库的人员类型使用 `UserTypeEnum.getDictKey()`。

## 版本演进

- 冻结值改用 `UserFreezeEnum.FREEZE.getDictKey()`，与人员表 `EnableEnum.N.name()` 风格不同。
- 同步范围由 `syncByRoleOn` 控制，见 [[cust_sync_by_role]]。

```ground:rule
name: 经办人同步操作分支
content: INSERT/UPDATE→addOperator/editOperator；FREEZE/THAW/DELETE→走冻结/解冻；DELETE 且同手机号既为经办人又为管理员时，仅将经办人记录 enable=N 并冻结其对 accountNormal 角色的 SysCustUserRel
impact: 避免误冻管理员权限
field_targets:
  - cust_person_info.enable
  - sys_cust_user_rel.is_freeze
evidence: "code_path:CustSyncEventProvider.java:syncOperatorUser + reqdoc:用户邀请→激活→同步用户到 SSO、同步用户到 AMS 运营中台"
```

---END FILE---

---FILE: rules/company_status_sync.md ---
---
type: rule
title: 企业状态同步口径规则
page_key: company_status_sync
domain: 平台事件监听与同步
status: draft
aliases:
  - 企业冻结/注销联动
  - custStatusSync/userStatusSync
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:custStatusSync
  - code:CustCompanyInfoApplication.java:userStatusSync
contract_version: "0.1"
---

企业状态变更映射到平台侧状态，并联动该企业下逐联系人（用户）状态同步。

## 需求背景

映射关系：FREEZE→`CustStatusEnum.FREEZE`、UNFREEZE→`EFFECT`、DISABLE→`WRITEOFF`；企业状态经 `clientCustStatusSyncService.call`，随后对每个联系人调用 `clientUserStatusSyncService.call`。这与建档状态机 [[cust_build_status]] 的审核通过与拒绝迁移是两条不同的状态维度，前者是经营状态、后者是建档进度，切勿混用。

## 版本演进

- 企业级与用户级两次调用为串行结构，意味着用户同步失败会直接影响该企业的整体同步结果。

```ground:rule
name: 企业状态同步口径
content: FREEZE→CustStatusEnum.FREEZE；UNFREEZE→EFFECT；DISABLE→WRITEOFF，同时 clientCustStatusSyncService.call 与逐联系人 clientUserStatusSyncService.call
impact: 企业状态变更联动用户冻结/解冻
field_targets: []
evidence: "code:CustCompanyInfoApplication.java:custStatusSync/userStatusSync"
```

---END FILE---

---FILE: rules/simple_auth_no_ca.md ---
---
type: rule
title: 简易认证不支持开通电子签章规则
page_key: simple_auth_no_ca
domain: 平台事件监听与同步
status: draft
aliases:
  - enforceMustNotOpenCa
  - 简易认证 CA 校正
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustCompanyInfoApplication.java:submitForSimpleAuth
contract_version: "0.1"
---

简易认证路径提交时，即使入参 `need_register_ca=Y`，也会被强制校正为不开通并落库。

## 需求背景

由 `CustCompanyCaPolicy.enforceMustNotOpenCa` 执行校正，字段落点为 [[cust_company_info]].`need_register_ca` 与 `ca_register_status`。业务意图是阻断简易认证走电子签章开通流程。该分支与建档状态机的 `AWAIT_CUST_CONFIRM` 状态配套，见 [[cust_build_status]]。

## 版本演进

- 校正发生在提交时而非登记时，失败重试路径（[[compensation_fail_type]]）是否会再次校正需结合重放上下文判断。

```ground:rule
name: 简易认证不支持开通电子签章
content: 简易认证提交时若 needRegisterCa=Y，强制校正为不开通并落库（CustCompanyCaPolicy.enforceMustNotOpenCa）
impact: 阻断简易认证走 CA 开通
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
evidence: "code:CustCompanyInfoApplication.java:submitForSimpleAuth"
```

---END FILE---

---FILE: rules/cust_sync_by_role.md ---
---
type: rule
title: 客户同步按角色维度规则
page_key: cust_sync_by_role
domain: 平台事件监听与同步
status: draft
aliases:
  - syncByRoleOn
  - 按角色同步广播
oid: 1
scope:
  databases: ["未确认"]
sources:
  - code:CustSyncService.java:getRoles
  - code:CustSyncService.java:syncByRole
contract_version: "0.1"
---

同步广播的范围由 `syncByRoleOn` 决定：为 true 时同步企业全部角色，为 false 时只同步指定 `companyType` 对应的角色。

## 需求背景

每次同步前先 `MetaDataThreadLocalConfig.setDbTenantCode(dbTenantCode)` 切换租户上下文，见 [[db_tenant_code]]。角色维度的差异会直接影响经办人/管理员同步的分支走向，见 [[operator_sync_branch]]。

## 版本演进

- 租户上下文以 ThreadLocal 设置，若同一线程连续处理多租户批次，遗漏重置会串数据。

```ground:rule
name: 客户同步按角色维度
content: syncByRoleOn=true 时按企业全部角色同步，false 时仅同步指定 companyType 对应角色；每次同步先 MetaDataThreadLocalConfig.setDbTenantCode(dbTenantCode)
impact: 决定同步广播范围
field_targets: []
evidence: "code:CustSyncService.java:getRoles/syncByRole"
```

---END FILE---

---REVIEW: table | 物理库名未确认---
本次语义分析未给出任何表的物理库名，所有 table 页 frontmatter 的 `scope.databases` 暂填 `"未确认"`。待补：各表所属物理库（疑似按租户分库或单一客户域库），以及分库路由依据（`db_tenant_code` 是否参与库路由）。
---END REVIEW---

---REVIEW: concept | 启用标识---
`EnableEnum` 的落库写法在同一文件内不一致：[[cust_person_info]] 侧有 `EnableEnum.N.name()`（enum_audit 判定 confirm）与字面量 `'Y'` 直写（enum_audit 判定 reject，证据 `CustSyncEventProvider.java:doPushAfterCommit(.enable("Y"))`）并存；`sys_cust_user_rel.is_freeze` 又使用 `getDictKey()`。已按「写值点 + DB」为准记录：枚举页与表页保留各写值点的真实写法，未强行统一。待确认：字面量 `'Y'` 是历史遗留还是有意为之，以及是否有 `EnableEnum.Y.getDictKey()` 与 `'Y'` 取值是否等价（dictKey 是否即 'Y'）。
---END REVIEW---

---REVIEW: concept | 关系（relation_audit）---
语义分析中的 `relation_audit` 在 `{"left":"PlatProductEventListener","right":"IPlatListener","kind":"extends",...}` 处被截断（证据文本止于 `public interface PlatP`），无法确认 `PlatProductEventListener` 与 `IPlatListener` 的继承/实现关系及影响范围，故本次未产出任何关系类页面。待补完整证据后再补 [[cust_event_check_status]] 的上游监听器拓扑。
---END REVIEW---