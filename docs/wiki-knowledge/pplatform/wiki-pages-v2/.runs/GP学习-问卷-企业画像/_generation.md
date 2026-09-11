---FILE: tables/gpt_learn_poster_log.md ---
---
type: table
title: gpt_learn_poster_log（智能审核引流卡片弹出/点击日志）
page_key: tables/gpt_learn_poster_log
domain: GP学习
status: draft
aliases:
  - 引流卡片日志
  - 智能审核引流卡片记录
  - gptlearn 弹出记录
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:gpt_learn_poster_log
  - code:GptLearnService.java
contract_version: "0.1"
---

# gpt_learn_poster_log（智能审核引流卡片弹出/点击日志）

本表是「[[concepts/gptlearn]]」（代码与接口层统一写作 gptlearn、前端与业务口称智能审核引流／GP 学习）的埋点载体。它记录引流卡片对某个企业下的某个用户「是否弹出过」「是否被点击过」两类事实：`popup_time` 由 `checkPosterStatus` 创建弹出记录时写入，`click_time` 由 `recordPosterClick` 记录点击时写入。表同时冗余了企业与用户的名称字段（`company_id`/`company_name`、`user_id`/`user_name`），使投放侧可以在不联表的情况下统计曝光与点击。

该表也是「[[calibers/gptlearn_poster_count_limit]]」的计数依据——弹出次数上限按 `user_id` + `company_id` 聚合本表记录来判定，因此本表的写入时机（而不是卡片实际渲染）决定了限流口径。

表内带有 `db_tenant_code`（数据租户标识）与 `app_tenant_code`（逻辑租户标识）两级租户字段，以及 `enable` 逻辑有效标识（DB 实测均为 Y），与本域其它表保持一致的租户隔离形态。

## 需求背景

本分析未提供针对该表的需求文档（reqdoc_claims）证据，页面内容全部以 DB 字段语义与 `GptLearnService` 代码证据为准。需要业务侧补充：卡片投放的目标人群定义、弹出上限的运营预期值（对应 `gptLearnProperties.maxPosterCount`）以及允许投放的租户白名单（对应 `gptLearnProperties.posterAllowedTenant`）来源。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。该表在当前分析中未被标注为 document_claim（未证实）内容。

```ground:table
table: gpt_learn_poster_log
fields:
  - field: id
    meaning: 表主键
    evidence: db
  - field: code
    meaning: 编码
    evidence: db
  - field: name
    meaning: 名称
    evidence: db
  - field: company_id
    meaning: 企业ID
    evidence: db
  - field: company_name
    meaning: 企业名称
    evidence: db
  - field: user_id
    meaning: 用户ID
    evidence: db
  - field: user_name
    meaning: 用户名
    evidence: db
  - field: popup_time
    meaning: 卡片弹出时间；checkPosterStatus 创建弹出记录时写入
    evidence: db
  - field: click_time
    meaning: 卡片点击时间；recordPosterClick 记录点击时写入
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识
    evidence: db
  - field: app_tenant_code
    meaning: 逻辑租户标识
    evidence: db
  - field: enable
    meaning: 逻辑有效标识；DB 实测均为 Y
    evidence: db
```

相关页面：[[tables/cust_company_info]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[processes/cust_company_info_cust_build_status]]。
---END FILE---

---FILE: tables/cust_survey_answer.md ---
---
type: table
title: cust_survey_answer（调研问卷答案）
page_key: tables/cust_survey_answer
domain: 问卷
status: draft
aliases:
  - 调研问卷答案表
  - 讯易链调研问卷答案
  - CustSurveyAnswer
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
  - code:CustSurveyController
  - code:CustSurveyAnswerService
contract_version: "0.1"
---

# cust_survey_answer（调研问卷答案）

本表承载「[[concepts/cust_survey]]」（调研问卷 / 讯易链调研问卷）的答卷持久化结果。它与「[[concepts/wenjuan]]」（问卷星活动）是两套彼此独立的机制：调研问卷会提交并落库答案，而问卷星活动的完成态不落库（见 [[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]）。

按字段语义，一行代表「某企业某用户对某道题的某个选项」：`survey_code` 标识问卷（DB 实测为 `XYL_2024_Q1`），`question_no` 为题号（DB 实测分布 1~6），`answer_value` 存选项明文，多选题的每个选项单独占一行；当选项为「其他」时，补充文本写入 `other_text`。`company_id`/`user_id` 记录的是当前登录企业与当前登录用户，`submit_time` 为提交时间。

表带 `db_tenant_code`（实测为 `all`）、`app_tenant_code`（实测为 `base`）与 `enable`（实测均为 Y）。这三者的组合构成了本表答案数据的归属口径，见 [[calibers/survey_answer_attribution]]。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。以下问题需要业务侧确认：问卷题的题干与选项字典存放位置（本表只存选项明文，不含题目定义）、多选题拆行后如何还原为一次作答、`other_text` 在导出统计中的取值规则。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。DB 实测 `survey_code` 仅出现 `XYL_2024_Q1`，题号 1~6，可作为当前版本的样本快照，但不代表历史版本。

```ground:table
table: cust_survey_answer
fields:
  - field: id
    meaning: 表主键
    evidence: db
  - field: code
    meaning: 编码
    evidence: db
  - field: name
    meaning: 名称
    evidence: db
  - field: company_id
    meaning: 当前登录企业ID
    evidence: db
  - field: user_id
    meaning: 当前登录用户ID
    evidence: db
  - field: survey_code
    meaning: 问卷code；DB 实测为 XYL_2024_Q1
    evidence: db
  - field: question_no
    meaning: 题号（1~N）；DB 实测分布为 1~6
    evidence: db
  - field: answer_value
    meaning: 选项明文；多选每个选项单独一行
    evidence: db
  - field: other_text
    meaning: 当选项为“其他”时填写的文本内容
    evidence: db
  - field: submit_time
    meaning: 提交时间
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识；DB 实测为 all
    evidence: db
  - field: app_tenant_code
    meaning: 逻辑租户标识；DB 实测为 base
    evidence: db
  - field: enable
    meaning: 逻辑有效标识；DB 实测均为 Y
    evidence: db
```

相关页面：[[concepts/cust_survey]]、[[concepts/wenjuan]]、[[calibers/survey_answer_attribution]]、[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]。
---END FILE---

---FILE: tables/cust_company_survey_state.md ---
---
type: table
title: cust_company_survey_state（企业问卷星活动状态）
page_key: tables/cust_company_survey_state
domain: 问卷
status: draft
aliases:
  - 问卷星活动状态表
  - 企业活动状态
  - first visitor state
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# cust_company_survey_state（企业问卷星活动状态）

本表以「企业」为单位记录[[concepts/wenjuan]]（问卷星活动，入口 `/cust-web/wenjuan`）的活动状态。核心字段是 `first_visit_time`（首个用户首次访问时间）与 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time`（首个用户转盘抽奖是否已展示及其时间，实测均为 Y）。这组字段支撑「[[concepts/first_visitor]]」判定：抽奖、指引与右下角问卷入口只对企业的首个访问用户开放。

`respondent` 字段是问卷星答卷标识，来自代码 `String.valueOf(companyId)`，用于调用问卷星开放接口查询完成态。请注意：本表只保存「谁第一个来、抽奖有没有展示过」这类企业级状态，**不保存答卷内容**——完成态是每次实时查询问卷星得到的，见 [[calibers/wenjuan_no_persist_completion]]。

状态字段的取值组合直接决定首页展示场景，其状态机见 [[processes/wenjuan_home_display_scene]]。表内 `db_tenant_code`（实测为 LN1/all）与 `enable`（实测均为 Y）承担租户与逻辑有效标识。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。需要业务补充：活动结束后 `cust_company_survey_state` 记录是保留还是清理、抽奖已展示后用户重复登录的展示预期。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:table
table: cust_company_survey_state
fields:
  - field: id
    meaning: 表主键
    evidence: db
  - field: company_id
    meaning: 企业ID
    evidence: db
  - field: first_visit_time
    meaning: 首个用户首次访问时间
    evidence: db
  - field: first_visitor_lottery_shown
    meaning: 首个用户转盘抽奖是否已展示 Y/N；DB 实测均为 Y
    evidence: db
  - field: first_visitor_lottery_shown_time
    meaning: 首个用户转盘抽奖展示时间
    evidence: db
  - field: respondent
    meaning: 问卷星答卷标识；代码取 String.valueOf(companyId)
    evidence: code
  - field: db_tenant_code
    meaning: 数据租户标识；DB 实测为 LN1/all
    evidence: db
  - field: enable
    meaning: 逻辑有效标识；DB 实测均为 Y
    evidence: db
```

相关页面：[[tables/cust_company_survey_whitelist]]、[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]。
---END FILE---

---FILE: tables/cust_company_survey_whitelist.md ---
---
type: table
title: cust_company_survey_whitelist（问卷星活动白名单企业）
page_key: tables/cust_company_survey_whitelist
domain: 问卷
status: draft
aliases:
  - 问卷活动白名单
  - 白名单企业
  - wenjuan whitelist
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_whitelist
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# cust_company_survey_whitelist（问卷星活动白名单企业）

本表是[[concepts/wenjuan]]（问卷星活动）的准入名单：只有落在本表中且 `enable = 'Y'`（配合 `isParticipating(company_id)` 判定）的企业，才会在首页看到活动 UI。判定逻辑挂在 `WenjuanDisplayService.resolveHomeDisplay`、`getSurveyUrl`、`shouldStayOnHomeForGotoProduct` 上，口径明细见 [[calibers/wenjuan_whitelist_company]]。

本表字段极简，只有企业名称、逻辑有效标识与数据租户标识（实测为 LN1），说明它是一个运营维护型的名单表，不承载活动过程状态——过程状态在 [[tables/cust_company_survey_state]]。理解两者分工是排查「白名单已加但用户看不到活动」类问题的第一步。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。需要业务确认：白名单维护的操作入口与审批流程、企业名称变更后本表是否同步。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:table
table: cust_company_survey_whitelist
fields:
  - field: company_name
    meaning: 企业名称
    evidence: db
  - field: enable
    meaning: 逻辑有效标识；DB 实测均为 Y
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识；DB 实测为 LN1
    evidence: db
```

相关页面：[[tables/cust_company_survey_state]]、[[concepts/wenjuan]]、[[calibers/wenjuan_whitelist_company]]、[[processes/wenjuan_home_display_scene]]。
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户信息主表／企业画像）
page_key: tables/cust_company_info
domain: 企业画像
status: draft
aliases:
  - 客户信息主表
  - 企业信息主表
  - CustCompanyInfo
  - CustCompanyInfoDO
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# cust_company_info（客户信息主表／企业画像）

本表是「[[concepts/company_profile]]」在代码层的落点：客户信息主表 / CustCompanyInfoDO。它同时承担两类语义：

- **认证流程状态**：`custBuildStatus`（对应 `CustBuildStatusEnum`），状态机见 [[processes/cust_company_info_cust_build_status]]；
- **客户生命周期状态**：`custStatus`（对应 `CustStatusEnum`），状态机见 [[processes/cust_company_info_cust_status]]。

企业「生效」不是单字段判断，而是四个条件的合取：`cust_build_status = 'BUILD_SUCCESS'`、`cust_status = 'EFFECT'`、`data_type = 'MAIN'`、`enable = 'Y'`，见 [[calibers/company_effect]]。因此任何只改其中一个字段的操作都不会让企业进入生效查询结果集。

主数据 / 记录数据由 `dataType`（常量 `DATA_TYPE_MAIN`）与 `mainDataId` 区分，这直接关系到两条唯一性口径：[[calibers/platform_operator_unique]]（平台运营方唯一，按 `custCompanyType` 是否包含 `PLATFORM_OPERATOR_COMPANY` 判定）与 [[calibers/main_data_certification_unique]]（主数据信用代码唯一）。`custCompanyType` 在代码中按 JSON 数组字符串处理（如 `["FINANCE"]`），它同时是[[calibers/gptlearn_finance_user]]（智能审核引流仅金融机构）的判定字段。

其余字段覆盖法人信息（`legalName`/`legalPhone`/`legalCertificationNo`/`legalCertificationType`）、开通状态（`needRegisterCa`/`caRegisterStatus`/`needRegisterBs`/`bsRegisterStatus`）、建档来源与方法（`custFrom`/`custSource`/`custBuildType`）、以及 `headCompany`/`abroadCust`/`outsideOrg` 等属性标记。注意 `enable` 在本表是 Y/N 语义，而部分关联表（如 [[tables/gpt_learn_poster_log]]）的实测值恒为 Y。

## 需求背景

本分析未提供该表的需求文档（reqdoc_claims）证据。待业务补充：企业变更（`CUST_CHANGE`）期间的字段可编辑范围、CA 与上上签开通状态 `Y/N/P` 中「P」的确切业务含义。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:table
table: cust_company_info
fields:
  - field: id
    meaning: 表主键
    evidence: code
  - field: code
    meaning: 编码
    evidence: code
  - field: name
    meaning: 客户名称
    evidence: code
  - field: custCompanyType
    meaning: 企业角色；代码按 JSON 数组字符串处理，如 ["FINANCE"]
    evidence: code
  - field: certificationNo
    meaning: 统一信用代码
    evidence: code
  - field: custBuildStatus
    meaning: 认证状态；对应 CustBuildStatusEnum
    evidence: code
  - field: custStatus
    meaning: 客户状态；对应 CustStatusEnum
    evidence: code
  - field: identifyStyle
    meaning: 认证方式；SELF/INVITE/INVITE_AGW/SIMPLE 等
    evidence: code
  - field: needRegisterCa
    meaning: 开通电子签章；Y/N/P
    evidence: code
  - field: caRegisterStatus
    meaning: CA开通状态；Y/N/P
    evidence: code
  - field: needRegisterBs
    meaning: 是否需要开通上上签；Y/N
    evidence: code
  - field: bsRegisterStatus
    meaning: 上上签开通状态；Y/N/P
    evidence: code
  - field: dataType
    meaning: 数据类型：主数据/记录数据；常量 DATA_TYPE_MAIN
    evidence: code
  - field: mainDataId
    meaning: 主数据id
    evidence: code
  - field: dbTenantCode
    meaning: 数据租户标识
    evidence: code
  - field: enable
    meaning: 逻辑有效标识；Y/N
    evidence: code
  - field: custFrom
    meaning: 客户来源；如“平台邀请”
    evidence: code
  - field: custSource
    meaning: 建档数据来源
    evidence: code
  - field: custBuildType
    meaning: 录入方式；AGW_BUILD/PC_BUILD 等
    evidence: code
  - field: legalName
    meaning: 法人姓名
    evidence: code
  - field: legalPhone
    meaning: 法人手机号
    evidence: code
  - field: legalCertificationNo
    meaning: 法人证件号
    evidence: code
  - field: legalCertificationType
    meaning: 法人证件类型
    evidence: code
  - field: headCompany
    meaning: 是否总公司；Y/N
    evidence: code
  - field: abroadCust
    meaning: 是否境外；Y/N
    evidence: code
  - field: outsideOrg
    meaning: 外部机构；Y/N
    evidence: code
```

相关页面：[[concepts/company_profile]]、[[processes/cust_company_info_cust_build_status]]、[[processes/cust_company_info_cust_status]]、[[calibers/company_effect]]、[[calibers/platform_operator_unique]]、[[calibers/main_data_certification_unique]]、[[calibers/gptlearn_finance_user]]。
---END FILE---

---FILE: processes/cust_company_info_cust_build_status.md ---
---
type: process
title: 企业认证状态机（cust_company_info.cust_build_status）
page_key: processes/cust_company_info_cust_build_status
domain: 企业画像
status: draft
aliases:
  - CustBuildStatusEnum 流程
  - 企业认证状态流转
  - cust_build_status
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 企业认证状态机（cust_company_info.cust_build_status）

该状态机描述[[tables/cust_company_info]]（企业画像 / 客户信息主表）中 `custBuildStatus` 字段（对应 `CustBuildStatusEnum`）的取值与流转。它是「企业从录档到认证成功」的主干流程，共 7 个状态。

流转的主干有两条入口路径：`INIT` 在「邀请认证-客户录入／注册认证提交」下进入 `CUST_CONFIRM_AWAIT`（待客户确认），在「邀请认证-平台录入提交」下直接进入 `CUST_BUILDING`（审核中）。此后 `CUST_CONFIRM_AWAIT` 与 `CUST_BUILDING` 之间可因「客户提交运营中台审核」与「运营中台审核退回」双向往返；审核通过进入 `BUILD_SUCCESS`，审核拒绝进入 `BUILD_FAIL`。被驳回后的「修改后重新提交」会回到 `CUST_CONFIRM_AWAIT`。

简易认证是独立分支：状态停在 `AWAIT_CUST_CONFIRM`（待客户确认，简易认证）时，由 `confirmCustInfoForSimpleAuth` 一次确认直接进入 `BUILD_SUCCESS`。认证成功之后，企业发起变更会进入 `CUST_CHANGE`（企业变更中），该判定来自 `CustCompanyIfoEnchanceService.isNeedMiniAuth`。

需要注意本状态机与[[processes/cust_company_info_cust_status]]的耦合：认证成功是客户状态从 `ADD` 走向 `EFFECT` 的前提，而两者共同参与[[calibers/company_effect]]的四条件合取。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据，状态与迁移均以 `CustCompanyInfoApplication` / `CustCompanyIfoEnchanceService` 代码证据为准。待业务补充：`CUST_CHANGE` 的退出路径（变更完成／失败后的目标状态）在本分析给出的代码证据中尚未出现。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 企业认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始/待提交
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 审核中
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证成功
    source: code_enum
  - value: BUILD_FAIL
    label: 认证失败/驳回
    source: code_enum
  - value: CUST_CHANGE
    label: 企业变更中
    source: code_enum
transitions:
  - from: INIT
    event: 邀请认证-客户录入/注册认证提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:getCustBuildStatus
  - from: INIT
    event: 邀请认证-平台录入提交
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:getCustBuildStatus
  - from: BUILD_FAIL
    event: 修改后重新提交
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: CUST_CONFIRM_AWAIT
    event: 客户提交运营中台审核
    to: CUST_BUILDING
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: CUST_BUILDING
    event: 审核通过
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: CUST_BUILDING
    event: 审核拒绝
    to: BUILD_FAIL
    evidence: code_path:CustCompanyInfoApplication.java:messageNotify
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认
    to: BUILD_SUCCESS
    evidence: code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - from: BUILD_SUCCESS
    event: 企业发起变更
    to: CUST_CHANGE
    evidence: code_path:CustCompanyIfoEnchanceService.java:isNeedMiniAuth
```

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_status]]、[[concepts/company_profile]]、[[calibers/company_effect]]。
---END FILE---

---FILE: processes/cust_company_info_cust_status.md ---
---
type: process
title: 企业客户状态机（cust_company_info.cust_status）
page_key: processes/cust_company_info_cust_status
domain: 企业画像
status: draft
aliases:
  - CustStatusEnum 流程
  - 企业客户状态流转
  - cust_status
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

# 企业客户状态机（cust_company_info.cust_status）

该状态机描述[[tables/cust_company_info]]中 `custStatus` 字段（对应 `CustStatusEnum`）的取值与流转，刻画企业作为「客户」的生命周期：新增 → 生效 → 冻结／解冻 → 注销。

主干是：建档认证成功后由 `ADD`（新增）进入 `EFFECT`（生效），入口方法为 `updateCustBuildStatus`。生效后的运营动作有三类：冻结（`freeze`）与解冻（`unfreeze`）在 `EFFECT` 与 `FREEZE` 之间往返；注销（`diable`）把 `EFFECT` 推向 `WRITEOFF`。`WRITEOFF` 有一条自环迁移：注销时冻结企业下所有用户（`custStatusOperator`），记录在案但不改变企业自身状态。

本状态机是[[calibers/company_effect]]（企业生效口径）的组成条件之一：只有 `cust_status = 'EFFECT'` 且认证成功、主数据、逻辑有效的企业才进入生效查询集合。它与[[processes/cust_company_info_cust_build_status]]的衔接点即 `ADD → EFFECT` 这一步。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据。待业务补充：`FAILURE`（失败）状态由哪些业务动作写入、达到该状态后能否恢复。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 企业客户状态
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增
    source: code_enum
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: FAILURE
    label: 失败
    source: code_enum
transitions:
  - from: ADD
    event: 建档认证成功
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:updateCustBuildStatus
  - from: EFFECT
    event: 冻结企业
    to: FREEZE
    evidence: code_path:CustCompanyInfoApplication.java:freeze
  - from: FREEZE
    event: 解冻企业
    to: EFFECT
    evidence: code_path:CustCompanyInfoApplication.java:unfreeze
  - from: EFFECT
    event: 注销企业
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:diable
  - from: WRITEOFF
    event: 注销时冻结企业下所有用户
    to: WRITEOFF
    evidence: code_path:CustCompanyInfoApplication.java:custStatusOperator
```

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[concepts/company_profile]]、[[calibers/company_effect]]。
---END FILE---

---FILE: processes/wenjuan_home_display_scene.md ---
---
type: process
title: 问卷星首页展示场景（WenjuanHomeDisplayConfigDTO.displayScene）
page_key: processes/wenjuan_home_display_scene
domain: 问卷
status: draft
aliases:
  - displayScene
  - 首页展示场景
  - 转盘指引展示规则
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星首页展示场景（WenjuanHomeDisplayConfigDTO.displayScene）

该状态机描述[[concepts/wenjuan]]（问卷星活动）在首页上「给用户看什么」的三种展示场景，取值承载在 `WenjuanHomeDisplayConfigDTO.displayScene` 上：`NONE`（不展示活动 UI）、`FIRST_VISITOR_LOTTERY`（首个用户首次登入：转盘 + 中奖弹窗 + 右下角入口）、`GUIDE_ONLY`（仅指引弹窗／右下角入口）。

场景解析统一在 `WenjuanDisplayService.resolveHomeDisplay` 中完成。进入 `FIRST_VISITOR_LOTTERY` 的前提是「白名单企业 + 首个访问用户 + 抽奖未展示」，三者缺一不可，其中白名单判定见 [[calibers/wenjuan_whitelist_company]]，首个访问用户定义见 [[concepts/first_visitor]]。抽奖已展示但问卷未完成时降级为 `GUIDE_ONLY`；问卷已完成同样停在 `GUIDE_ONLY`——完成态的判定不落库，而是实时查询问卷星，见 [[calibers/wenjuan_no_persist_completion]] 与 [[concepts/survey_completed]]。企业非首个访问用户时直接落到 `NONE`。

本场景状态与[[tables/cust_company_survey_state]]中的 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time` 直接对应：抽奖展示一旦被写入，后续访问就不可能再回到 `FIRST_VISITOR_LOTTERY`。

## 需求背景

本分析未提供该状态机的需求文档（reqdoc_claims）证据。待业务补充：`GUIDE_ONLY` 在问卷完成后的保留时长、以及 `NONE` 与「非白名单企业」在埋点上的区分方式。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:process
name: 问卷星首页展示场景
field: WenjuanHomeDisplayConfigDTO.displayScene
states:
  - value: NONE
    label: 不展示活动UI
    source: code_enum
  - value: FIRST_VISITOR_LOTTERY
    label: 首个用户首次登入：转盘+中奖弹窗+右下角入口
    source: code_enum
  - value: GUIDE_ONLY
    label: 仅指引弹窗/右下角入口
    source: code_enum
transitions:
  - from: NONE
    event: 白名单企业、首个访问用户、抽奖未展示
    to: FIRST_VISITOR_LOTTERY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: FIRST_VISITOR_LOTTERY
    event: 抽奖已展示且问卷未完成
    to: GUIDE_ONLY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: GUIDE_ONLY
    event: 问卷已完成
    to: GUIDE_ONLY
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
  - from: FIRST_VISITOR_LOTTERY
    event: 非企业首个访问用户
    to: NONE
    evidence: code_path:WenjuanDisplayService.java:resolveHomeDisplay
```

相关页面：[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]、[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[calibers/wenjuan_whitelist_company]]、[[calibers/wenjuan_no_persist_completion]]。
---END FILE---

---FILE: calibers/gptlearn_finance_user.md ---
---
type: caliber
title: 智能审核引流-金融机构用户口径
page_key: calibers/gptlearn_finance_user
domain: GP学习
status: draft
aliases:
  - FINANCE 用户口径
  - validateFinanceUser
  - 金融机构用户校验
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
---

# 智能审核引流-金融机构用户口径

本口径规定「谁能用[[concepts/gptlearn]]」。判定条件是当前登录用户的企业角色为金融机构：`companyType = 'FINANCE'`（字段落点见 [[tables/cust_company_info]] 的 `custCompanyType`，代码按 JSON 数组字符串处理）。

适用范围是 `GptLearnService` 的全部接口：`syncLoginInfo`、`checkPosterStatus`、`recordPosterClick`。实现集中在 `validateFinanceUser`。这是一道前置闸门：用户校验不过，后续的白名单租户口径（[[calibers/gptlearn_tenant_whitelist]]）与弹出次数上限口径（[[calibers/gptlearn_poster_count_limit]]）都不会被评估，也不会向 [[tables/gpt_learn_poster_log]] 写入记录。

与之配套的强制规则见 [[rules/gptlearn_finance_user_only]]。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：企业存在多个角色（`custCompanyType` 为多元素 JSON 数组）时，是否只要包含 `FINANCE` 即通过。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-金融机构用户口径
predicate: "当前登录用户.companyType = 'FINANCE'"
scope: GptLearnService 全部接口：syncLoginInfo、checkPosterStatus、recordPosterClick
evidence: code_path:GptLearnService.java:validateFinanceUser
```

相关页面：[[concepts/gptlearn]]、[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[rules/gptlearn_finance_user_only]]。
---END FILE---

---FILE: calibers/gptlearn_tenant_whitelist.md ---
---
type: caliber
title: 智能审核引流-租户白名单口径
page_key: calibers/gptlearn_tenant_whitelist
domain: GP学习
status: draft
aliases:
  - posterAllowedTenant
  - 引流租户白名单
  - 投放租户口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
---

# 智能审核引流-租户白名单口径

本口径规定哪些租户可以收到[[concepts/gptlearn]]的引流卡片：企业的 `cust_company_info.db_tenant_code` 必须属于 `gptLearnProperties.posterAllowedTenant` 配置的白名单集合。它只作用于 `checkPosterStatus`（引流卡片弹出校验）这一个环节，不覆盖 `syncLoginInfo` 与 `recordPosterClick`。

与它并列的还有两道门：用户侧见 [[calibers/gptlearn_finance_user]]，次数侧见 [[calibers/gptlearn_poster_count_limit]]。三者同时满足时，`checkPosterStatus` 才会创建弹出记录并写入 [[tables/gpt_learn_poster_log]] 的 `popup_time`。

注意本口径使用 `db_tenant_code`（数据租户标识）而非 `app_tenant_code`（逻辑租户标识）；这两个字段在各表中并存，口径选择哪一个直接决定命中范围。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`posterAllowedTenant` 的配置载体与变更流程。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-租户白名单口径
predicate: cust_company_info.db_tenant_code 属于 gptLearnProperties.posterAllowedTenant
scope: checkPosterStatus 引流卡片弹出校验
evidence: code_path:GptLearnService.java:checkPosterStatus
```

相关页面：[[concepts/gptlearn]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_poster_count_limit]]、[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]。
---END FILE---

---FILE: calibers/gptlearn_poster_count_limit.md ---
---
type: caliber
title: 智能审核引流-弹出次数上限口径
page_key: calibers/gptlearn_poster_count_limit
domain: GP学习
status: draft
aliases:
  - maxPosterCount
  - 卡片弹出次数上限
  - 引流限流口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
---

# 智能审核引流-弹出次数上限口径

本口径限制[[concepts/gptlearn]]的引流卡片对同一「用户 + 企业」组合的弹出次数：按 `gpt_learn_poster_log.user_id` 与 `gpt_learn_poster_log.company_id` 聚合计数，结果必须小于 `gptLearnProperties.maxPosterCount`。作用于 `checkPosterStatus`。

因为计数对象是 [[tables/gpt_learn_poster_log]] 中的弹出记录（`popup_time` 由 `checkPosterStatus` 写入），所以「弹出记录已落库」与「用户真的看见了卡片」在本口径下是等价事件。若前端渲染失败但记录已写，额度会被消耗——这是排查「用户反馈没看到卡片但已达上限」时的关键点。

本口径与 [[calibers/gptlearn_finance_user]]（用户资格）、[[calibers/gptlearn_tenant_whitelist]]（租户白名单）串联生效，是三道门中的最后一道。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`maxPosterCount` 的产品预期值、是否按自然日或活动周期重置。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 智能审核引流-弹出次数上限口径
predicate: count(gpt_learn_poster_log.user_id, gpt_learn_poster_log.company_id) < gptLearnProperties.maxPosterCount
scope: checkPosterStatus 引流卡片弹出校验
evidence: code_path:GptLearnService.java:checkPosterStatus
```

相关页面：[[concepts/gptlearn]]、[[tables/gpt_learn_poster_log]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]。
---END FILE---

---FILE: calibers/wenjuan_whitelist_company.md ---
---
type: caliber
title: 问卷星活动-白名单企业口径
page_key: calibers/wenjuan_whitelist_company
domain: 问卷
status: draft
aliases:
  - isParticipating
  - 问卷活动白名单口径
  - 参与企业口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_whitelist
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星活动-白名单企业口径

本口径决定[[concepts/wenjuan]]对哪些企业开放：企业必须出现在 [[tables/cust_company_survey_whitelist]] 中且 `enable = 'Y'`，同时 `isParticipating(company_id)` 为真。判定点有三处：`WenjuanDisplayService.resolveHomeDisplay`（首页展示场景）、`getSurveyUrl`（问卷链接获取）、`shouldStayOnHomeForGotoProduct`（跳转商品页时是否留在首页）。

这是[[processes/wenjuan_home_display_scene]]中进入 `FIRST_VISITOR_LOTTERY` 的前置条件之一；不满足时场景直接落到 `NONE`。它与「首个访问用户」（[[concepts/first_visitor]]）是两个正交条件：白名单是「企业级」准入，首个访问用户是「用户在企业的次序」准入。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：`isParticipating` 除白名单外的判定构成（分析中仅给出该调用名，未展开其内部逻辑）。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 问卷星活动-白名单企业口径
predicate: cust_company_survey_whitelist.enable = 'Y' 且 isParticipating(company_id) 为真
scope: WenjuanDisplayService.resolveHomeDisplay / getSurveyUrl / shouldStayOnHomeForGotoProduct
evidence: db + code_path:WenjuanDisplayService.java:resolveHomeDisplay
```

相关页面：[[concepts/wenjuan]]、[[concepts/first_visitor]]、[[tables/cust_company_survey_whitelist]]、[[tables/cust_company_survey_state]]、[[processes/wenjuan_home_display_scene]]。
---END FILE---

---FILE: calibers/wenjuan_no_persist_completion.md ---
---
type: caliber
title: 问卷星活动-完成态不落库口径
page_key: calibers/wenjuan_no_persist_completion
domain: 问卷
status: draft
aliases:
  - 完成态实时查询口径
  - 不落库口径
  - syncAndResolve
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanDisplayService.java
contract_version: "0.1"
---

# 问卷星活动-完成态不落库口径

本口径规定[[concepts/wenjuan]]（问卷星活动）的「问卷是否已完成」不写入本地库：不写 `cust_survey_answer`（那是[[concepts/cust_survey]]调研问卷的表），而是每次调用 `WenjuanOpenApiClient.isSurveyCompleted(respondent)` 实时获取。作用点是 `WenjuanDisplayService.syncAndDisplayConfig` 与 `resolveHomeDisplay`。

这一设计带来两个直接后果：其一，本地无法通过 SQL 直接统计「谁完成了问卷星活动」，只能依赖问卷星侧数据；其二，完成态每次访问都产生一次外部调用，展示结果（[[processes/wenjuan_home_display_scene]] 中的 `GUIDE_ONLY` 分支）依赖外部接口的可用性。

企业级的本地状态只保存在 [[tables/cust_company_survey_state]]（首个访问时间、抽奖是否已展示）。这一点也是「[[concepts/survey_completed]]」与 [[concepts/cust_survey]] 提交答案最容易被混淆的地方。

## 需求背景

本分析未提供该口径的需求文档（reqdoc_claims）证据。待业务补充：问卷星接口不可用时的降级展示策略与超时处理。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 问卷星活动-完成态不落库口径
predicate: 不写 cust_survey_answer；每次调 WenjuanOpenApiClient.isSurveyCompleted(respondent)
scope: syncAndDisplayConfig / resolveHomeDisplay
evidence: code_path:WenjuanDisplayService.java:syncAndResolve
```

相关页面：[[concepts/wenjuan]]、[[concepts/survey_completed]]、[[concepts/cust_survey]]、[[tables/cust_company_survey_state]]、[[tables/cust_survey_answer]]、[[processes/wenjuan_home_display_scene]]。
---END FILE---

---FILE: calibers/survey_answer_attribution.md ---
---
type: caliber
title: 调研问卷-答案归属口径
page_key: calibers/survey_answer_attribution
domain: 问卷
status: draft
aliases:
  - XYL_2024_Q1 口径
  - 答案归属三条件
  - 调研问卷有效答案口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
contract_version: "0.1"
---

# 调研问卷-答案归属口径

本口径界定哪些行构成「[[concepts/cust_survey]]（讯易链调研问卷）的有效答案数据」：`survey_code = 'XYL_2024_Q1'`、`db_tenant_code = 'all'`、`enable = 'Y'` 三者同时成立。三者分别锚定问卷身份、租户归属与逻辑有效性。

在 [[tables/cust_survey_answer]] 中，这三列并非总是这个取值——`app_tenant_code` 实测为 `base`、`db_tenant_code` 实测为 `all`，而其它表的 `db_tenant_code` 实测值各不相同（例如 [[tables/cust_company_survey_state]] 为 LN1/all，[[tables/cust_company_survey_whitelist]] 为 LN1）。因此按本口径取数时不应使用统一的租户过滤条件。

本口径是纯 DB 口径（证据来源为 db，不含代码路径），与「完成态不落库」的问卷星活动（[[calibers/wenjuan_no_persist_completion]]）在数据来源上完全不同。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：`survey_code` 未来新增问卷时的命名规范与历史问卷的并存方式。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。DB 实测样本仅覆盖 `XYL_2024_Q1` 与题号 1~6。

```ground:caliber
name: 调研问卷-答案归属口径
predicate: cust_survey_answer.survey_code = 'XYL_2024_Q1' AND cust_survey_answer.db_tenant_code = 'all' AND cust_survey_answer.enable = 'Y'
scope: 讯易链调研问卷答案数据
evidence: db
```

相关页面：[[concepts/cust_survey]]、[[tables/cust_survey_answer]]、[[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]。
---END FILE---

---FILE: calibers/company_effect.md ---
---
type: caliber
title: 企业生效口径
page_key: calibers/company_effect
domain: 企业画像
status: draft
aliases:
  - 生效企业口径
  - listEffectCompany
  - EFFECT 口径
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 企业生效口径

「企业生效」是[[concepts/company_profile]]最常被引用的查询口径，由四个条件合取而成：`cust_build_status = 'BUILD_SUCCESS'`（认证成功，见 [[processes/cust_company_info_cust_build_status]]）、`cust_status = 'EFFECT'`（客户生效，见 [[processes/cust_company_info_cust_status]]）、`data_type = 'MAIN'`（主数据，常量 `DATA_TYPE_MAIN`）、`enable = 'Y'`（逻辑有效）。

适用范围是 `listEffectCompany` / `listEffectCompanyByTenantAndType` 等企业生效查询。因为四条件横跨认证状态、客户状态与数据分层三类字段，任何单字段的运营操作（例如仅冻结企业而不动认证状态）都会即时改变企业是否出现在生效结果集中。

在[[tables/cust_company_info]]中，`data_type` 与 `mainDataId` 一起区分主数据 / 记录数据，这解释了为什么同一家企业在库中可能存在多行而只有主数据行参与生效判定。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：记录数据行（非主数据）在业务上承担的场景。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 企业生效口径
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS' AND cust_company_info.cust_status = 'EFFECT' AND cust_company_info.data_type = 'MAIN' AND cust_company_info.enable = 'Y'
scope: listEffectCompany/listEffectCompanyByTenantAndType 等企业生效查询
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[processes/cust_company_info_cust_status]]、[[calibers/platform_operator_unique]]、[[calibers/main_data_certification_unique]]。
---END FILE---

---FILE: calibers/platform_operator_unique.md ---
---
type: caliber
title: 平台运营方唯一口径
page_key: calibers/platform_operator_unique
domain: 企业画像
status: draft
aliases:
  - PLATFORM_OPERATOR_COMPANY 口径
  - 平台运营企业唯一性
  - checkCustInfoBeforeSave
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 平台运营方唯一口径

本口径约束「每个租户最多只能有一个平台运营方企业」：`cust_company_info.cust_company_type LIKE '%PLATFORM_OPERATOR_COMPANY%'`，且 `enable = 'Y'`、`db_tenant_code` 等于当前租户。校验发生在企业建档保存之前（`checkCustInfoBeforeSave`）。

判定使用 `LIKE '%...%'` 而非等值比较，与 [[tables/cust_company_info]] 中 `custCompanyType` 按 JSON 数组字符串处理（如 `["FINANCE"]`）的存储形态一致——同一个字段可以承载多个角色，因此需要子串匹配。

本口径与 [[calibers/main_data_certification_unique]]（主数据信用代码唯一）同属建档保存前的重复校验，但关注对象不同：本口径约束「角色」，后者约束「主体身份」。两者都以当前租户为范围。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：子串匹配是否会误命中其它包含 `PLATFORM_OPERATOR_COMPANY` 字样的角色值。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 平台运营方唯一口径
predicate: cust_company_info.cust_company_type LIKE '%PLATFORM_OPERATOR_COMPANY%' AND cust_company_info.enable = 'Y' AND cust_company_info.db_tenant_code = 当前租户
scope: 企业建档保存前校验
evidence: code_path:CustCompanyIfoEnchanceService.java:checkCustInfoBeforeSave
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[calibers/main_data_certification_unique]]、[[calibers/company_effect]]。
---END FILE---

---FILE: calibers/main_data_certification_unique.md ---
---
type: caliber
title: 主数据信用代码唯一口径
page_key: calibers/main_data_certification_unique
domain: 企业画像
status: draft
aliases:
  - 统一社会信用代码唯一
  - certificationNo 唯一口径
  - getMainDataByCertification
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
---

# 主数据信用代码唯一口径

本口径用于企业统一社会信用代码的重复校验：`cust_company_info.certification_no` 等于目标信用代码、`db_tenant_code` 等于当前租户、`data_type = 'MAIN'`。实现为 `getMainDataByCertification`。

三个条件缺一不可，其中 `data_type = 'MAIN'` 是本口径与「全局唯一」的差别所在：只有主数据行参与判重，记录数据行可以携带相同信用代码而不冲突。这与 [[calibers/company_effect]] 中对 `data_type = 'MAIN'` 的使用相互印证——主数据行是企业画像的权威行。

字段 `certificationNo`（统一信用代码）在 [[tables/cust_company_info]] 与法人相关字段（`legalCertificationNo`、`legalCertificationType`）并存，取数时注意区分企业主体与法人个人证件。

## 需求背景

本分析未提供本口径的需求文档（reqdoc_claims）证据。待业务补充：跨租户是否存在同一信用代码的合法场景。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:caliber
name: 主数据信用代码唯一口径
predicate: cust_company_info.certification_no = 信用代码 AND cust_company_info.db_tenant_code = 当前租户 AND cust_company_info.data_type = 'MAIN'
scope: 企业统一社会信用代码重复校验
evidence: code_path:CustCompanyIfoEnchanceService.java:getMainDataByCertification
```

相关页面：[[concepts/company_profile]]、[[tables/cust_company_info]]、[[calibers/platform_operator_unique]]、[[calibers/company_effect]]。
---END FILE---

---FILE: concepts/gptlearn.md ---
---
type: concept
title: 智能审核引流
page_key: concepts/gptlearn
domain: GP学习
status: draft
aliases:
  - GP学习
  - gptlearn
  - 引流卡片
  - 智能审核引流卡片
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:gpt_learn_poster_log
  - code:GptLearnService.java
contract_version: "0.1"
maps_to: GptLearnService + gpt_learn_poster_log + /app-web/gptlearn
field_targets:
  - gpt_learn_poster_log.popup_time
  - gpt_learn_poster_log.click_time
adjudication: synonym
also_confused_with: []
---

# 智能审核引流

「智能审核引流」是业务与前端对该功能的称呼，代码、表与接口层统一写作 `gptlearn`（接口前缀 `/app-web/gptlearn`）。同类叫法还包括 GP 学习、引流卡片、智能审核引流卡片——这些在本 wiki 中被判定为同义词（synonym），可以互相替换。参见 [[tables/gpt_learn_poster_log]]。

该概念的服务入口是 `GptLearnService`，三个接口分别是 `syncLoginInfo`（同步登录信息）、`checkPosterStatus`（检查卡片状态并写入弹出记录）、`recordPosterClick`（记录点击）。它对用户开放的前置条件是「用户为金融机构」，见 [[calibers/gptlearn_finance_user]] 与 [[rules/gptlearn_finance_user_only]]；卡片弹出还受租户白名单（[[calibers/gptlearn_tenant_whitelist]]）与弹出次数上限（[[calibers/gptlearn_poster_count_limit]]）约束。

注意本概念与问卷域的两个概念（[[concepts/cust_survey]]、[[concepts/wenjuan]]）没有业务交集，不要因为都叫「引流／问卷」而混淆。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：引流卡片指向的具体业务动作与转化目标。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/gpt_learn_poster_log]]、[[tables/cust_company_info]]、[[calibers/gptlearn_finance_user]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]、[[rules/gptlearn_finance_user_only]]。
---END FILE---

---FILE: concepts/cust_survey.md ---
---
type: concept
title: 调研问卷
page_key: concepts/cust_survey
domain: 问卷
status: draft
aliases:
  - 讯易链调研问卷
  - CustSurvey
  - survey
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_survey_answer
  - code:CustSurveyController
  - code:CustSurveyAnswerService
contract_version: "0.1"
maps_to: CustSurveyController + CustSurveyAnswerService + cust_survey_answer
field_targets:
  - cust_survey_answer.answer_value
  - cust_survey_answer.other_text
  - cust_survey_answer.submit_time
adjudication: boundary
also_confused_with:
  - 问卷星活动
---

# 调研问卷

「调研问卷」指讯易链调研问卷（代码层称 `CustSurvey` / `survey`），入口为 `/cust-web/survey`，由 `CustSurveyController` 与 `CustSurveyAnswerService` 提供服务。

它与 [[concepts/wenjuan]]（问卷星活动）的最主要边界是**是否落库**：调研问卷会提交并持久化答案到 [[tables/cust_survey_answer]]，DB 中 `survey_code` 为 `XYL_2024_Q1`；而问卷星活动不落答卷状态。因此在本 wiki 中二者是 boundary 关系而非同义词。

答案取数的归属口径见 [[calibers/survey_answer_attribution]]。答案形态上，一道多选题会拆成多行（`answer_value` 每个选项单独一行），「其他」选项的补充文本进 `other_text`。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：问卷题干的配置位置、调研结果的统计与导出路径。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_survey_answer]]、[[concepts/wenjuan]]、[[concepts/survey_completed]]、[[calibers/survey_answer_attribution]]。
---END FILE---

---FILE: concepts/wenjuan.md ---
---
type: concept
title: 问卷星活动
page_key: concepts/wenjuan
domain: 问卷
status: draft
aliases:
  - Wenjuan
  - 产融首页问卷活动
  - 抽奖问卷
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - db:cust_company_survey_whitelist
  - code:WenjuanController
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: WenjuanController + WenjuanDisplayService + cust_company_survey_state + cust_company_survey_whitelist
field_targets:
  - cust_company_survey_state.first_visitor_lottery_shown
  - cust_company_survey_state.first_visit_time
  - cust_company_survey_whitelist.enable
adjudication: boundary
also_confused_with:
  - 调研问卷
---

# 问卷星活动

「问卷星活动」指产融首页的问卷抽奖活动（代码层称 `Wenjuan`），入口 `/cust-web/wenjuan`，由 `WenjuanController` 与 `WenjuanDisplayService` 承载，本地状态落在 [[tables/cust_company_survey_state]] 与 [[tables/cust_company_survey_whitelist]]。

与 [[concepts/cust_survey]]（调研问卷）的边界有两条：其一，**问卷星活动不落答卷状态**，完成态每次实时调用问卷星（见 [[calibers/wenjuan_no_persist_completion]]、[[concepts/survey_completed]]）；其二，**展示范围受白名单与首个访问用户双重限制**，仅白名单企业（[[calibers/wenjuan_whitelist_company]]）且企业首个访问用户（[[concepts/first_visitor]]）能看到 UI。首页展示什么由 [[processes/wenjuan_home_display_scene]] 描述。

因此在本 wiki 中二者是 boundary 关系：看到「问卷」字样时必须先确认指的是哪一套机制，再决定去查答案表还是查活动状态表。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：活动的起止时间配置与抽奖奖品的发放链路。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_survey_state]]、[[tables/cust_company_survey_whitelist]]、[[concepts/cust_survey]]、[[concepts/first_visitor]]、[[concepts/survey_completed]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]、[[calibers/wenjuan_no_persist_completion]]。
---END FILE---

---FILE: concepts/company_profile.md ---
---
type: concept
title: 企业画像
page_key: concepts/company_profile
domain: 企业画像
status: draft
aliases:
  - 客户信息
  - 企业信息主表
  - CustCompanyInfo
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:CustCompanyInfoApplication.java
  - code:CustCompanyIfoEnchanceService.java
contract_version: "0.1"
maps_to: cust_company_info / CustCompanyInfoDO
field_targets:
  - cust_company_info.custBuildStatus
  - cust_company_info.custStatus
  - cust_company_info.custCompanyType
  - cust_company_info.certificationNo
  - cust_company_info.dataType
adjudication: synonym
also_confused_with:
  - 企业认证状态
  - 企业客户状态
---

# 企业画像

「企业画像」在本 wiki 中是同义词集合：企业画像 = 客户信息 = 企业信息主表 = `CustCompanyInfo`，代码层落点为 [[tables/cust_company_info]] / `CustCompanyInfoDO`。同义判定的依据是这些叫法在代码与表中指向同一实体，而非不同的视图或聚合。

需要与之划清界限的是两个**字段级状态**概念：企业认证状态（[[processes/cust_company_info_cust_build_status]]，字段 `custBuildStatus`）与企业客户状态（[[processes/cust_company_info_cust_status]]，字段 `custStatus`）。它们是企业画像上的两个属性，不是企业画像本身。说「企业画像变了」时，应进一步确认变的是哪个属性。

企业画像的常用派生口径有三条：生效企业（[[calibers/company_effect]]）、平台运营方唯一（[[calibers/platform_operator_unique]]）、主数据信用代码唯一（[[calibers/main_data_certification_unique]]）。其中 `custCompanyType` 字段还被 GP 学习域引用，用于判定金融机构用户（[[calibers/gptlearn_finance_user]]）。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：企业画像是否对外提供只读视图、是否存在缓存副本。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_info]]、[[processes/cust_company_info_cust_build_status]]、[[processes/cust_company_info_cust_status]]、[[calibers/company_effect]]、[[calibers/platform_operator_unique]]、[[calibers/main_data_certification_unique]]、[[calibers/gptlearn_finance_user]]。
---END FILE---

---FILE: concepts/survey_completed.md ---
---
type: concept
title: 问卷完成态
page_key: concepts/survey_completed
domain: 问卷
status: draft
aliases:
  - 答卷状态
  - surveyCompleted
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:WenjuanOpenApiClient
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: WenjuanOpenApiClient.isSurveyCompleted(respondent)
field_targets: []
adjudication: boundary
also_confused_with:
  - cust_survey_answer 提交答案
---

# 问卷完成态

「问卷完成态」特指[[concepts/wenjuan]]（问卷星活动）中的「该企业是否已完成问卷」这一实时判定，来源是 `WenjuanOpenApiClient.isSurveyCompleted(respondent)`，其中 `respondent` 是 [[tables/cust_company_survey_state]] 中的问卷星答卷标识（代码取 `String.valueOf(companyId)`）。

它与「[[tables/cust_survey_answer]] 提交答案」是 boundary 关系：后者是[[concepts/cust_survey]]调研问卷的落库行为，前者**不落库**，每次访问都实时查询问卷星（见 [[calibers/wenjuan_no_persist_completion]]）。因此不能用一条 SQL 在本地统计问卷星活动的完成人数。

完成态参与首页展示场景的判定：抽奖已展示且问卷未完成 → `GUIDE_ONLY`；问卷已完成 → 亦停在 `GUIDE_ONLY`，细节见 [[processes/wenjuan_home_display_scene]]。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：问卷星接口的可用性 SLA 与失败重试策略。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[concepts/wenjuan]]、[[concepts/cust_survey]]、[[tables/cust_company_survey_state]]、[[tables/cust_survey_answer]]、[[calibers/wenjuan_no_persist_completion]]、[[processes/wenjuan_home_display_scene]]。
---END FILE---

---FILE: concepts/first_visitor.md ---
---
type: concept
title: 首个访问用户
page_key: concepts/first_visitor
domain: 问卷
status: draft
aliases:
  - firstVisitor
  - first_visitor
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - db:cust_company_survey_state
  - code:WenjuanDisplayService.java
contract_version: "0.1"
maps_to: cust_company_survey_state.claimFirstVisitor / first_visitor_lottery_shown
field_targets:
  - cust_company_survey_state.first_visit_time
  - cust_company_survey_state.first_visitor_lottery_shown
  - cust_company_survey_state.first_visitor_lottery_shown_time
adjudication: synonym
also_confused_with: []
---

# 首个访问用户

「首个访问用户」（代码层 `firstVisitor` / `first_visitor`）是[[concepts/wenjuan]]（问卷星活动）的准入角色之一，判定**以企业为单位**：只有该企业的第一名访问用户可以看到转盘抽奖、指引弹窗与右下角问卷入口。同义词 `firstVisitor`、`first_visitor` 与中文叫法在本 wiki 中等价。

状态载体是 [[tables/cust_company_survey_state]] 的 `first_visit_time`（首个用户首次访问时间）与 `first_visitor_lottery_shown` / `first_visitor_lottery_shown_time`（抽奖是否/何时已展示，DB 实测均为 Y）。抽奖一旦展示过，后续访问落在 `GUIDE_ONLY` 或 `NONE` 分支，见 [[processes/wenjuan_home_display_scene]]。

它与白名单口径（[[calibers/wenjuan_whitelist_company]]）是两个正交条件：白名单决定「哪些企业有活动」，本概念决定「企业里的哪个用户看得到」。非首个访问用户直接落到 `NONE`。

## 需求背景

本分析未提供该概念的需求文档（reqdoc_claims）证据。待业务补充：首个访问用户判定是否受企业内用户注销／离职影响。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

相关页面：[[tables/cust_company_survey_state]]、[[concepts/wenjuan]]、[[processes/wenjuan_home_display_scene]]、[[calibers/wenjuan_whitelist_company]]。
---END FILE---

---FILE: rules/gptlearn_finance_user_only.md ---
---
type: rule
title: 智能审核引流仅金融机构用户可用
page_key: rules/gptlearn_finance_user_only
domain: GP学习
status: draft
aliases:
  - validateFinanceUser 规则
  - FINANCE 前置校验
  - 引流接口准入规则
oid: 1
scope:
  databases: ["(待确认)"]
sources:
  - code:GptLearnService.java
contract_version: "0.1"
---

# 智能审核引流仅金融机构用户可用

这是一条强制的接口准入规则：`validateFinanceUser` 校验当前登录用户非空、`companyType` 为 `FINANCE`、且企业信息存在，任一不满足即抛异常。它保护的是 [[concepts/gptlearn]] 的全部三个接口。

规则的影响面是明确的：非金融机构用户无法调用 `/app-web/gptlearn/**` 下的同步登录、检查卡片、记录点击接口，因而也不会在 [[tables/gpt_learn_poster_log]] 中产生任何记录。字段落点为 [[tables/cust_company_info]] 的 `custCompanyType`，口径表述见 [[calibers/gptlearn_finance_user]]。

需要区分「规则」与「口径」：规则描述的是校验行为与失败后果（抛异常、接口不可用），口径描述的是判定谓词本身。两者证据同源，但使用场景不同——排查接口报错看本页，统计投放范围看口径页。

## 需求背景

本分析未提供本规则的需求文档（reqdoc_claims）证据。待业务补充：异常抛出后的前端提示话术与埋点。

## 版本演进

当前契约版本 0.1，暂无版本演进证据。

```ground:rule
name: 智能审核引流仅金融机构用户可用
content: validateFinanceUser 校验当前登录用户非空、companyType 为 FINANCE、企业信息存在，否则抛异常。
impact: 非金融机构用户无法调用 /app-web/gptlearn/** 下同步登录、检查卡片、记录点击接口。
field_targets:
  - cust_company_info.custCompanyType
evidence: code_path:GptLearnService.
```

相关页面：[[concepts/gptlearn]]、[[calibers/gptlearn_finance_user]]、[[tables/cust_company_info]]、[[tables/gpt_learn_poster_log]]、[[calibers/gptlearn_tenant_whitelist]]、[[calibers/gptlearn_poster_count_limit]]。
---END FILE---

---REVIEW: rule | 智能审核引流仅金融机构用户可用---
语义分析给出的该规则 evidence 字符串在 `code_path:GptLearnService.` 处被截断（缺少文件名后缀与行号），因此本页 `ground:rule` 块中的 `evidence` 只能逐字保留截断值，无法补齐到 `文件:行` 粒度。需要重新提取该规则的代码证据（`GptLearnService.validateFinanceUser`）后更新。
---END REVIEW---

---REVIEW: table | 全局-物理库名未证实---
本次语义分析的 `field_semantics` 证据仅标注 `db` / `code`，未给出承载这些表的物理库名。因此所有页面的 `scope.databases` 只能写占位值 `"(待确认)"`，未做任何推断。需要数据源清单（表 → 物理库）后统一回填 5 个 table 页及其引用页。此外，分析输入在 `rules` 第一条处结束，未见 doc_claims / reqdoc_claims 段（anchor 或 uncovered），故本期无 `## 版本演进` 的 document_claim（未证实）内容可写。
---END REVIEW---