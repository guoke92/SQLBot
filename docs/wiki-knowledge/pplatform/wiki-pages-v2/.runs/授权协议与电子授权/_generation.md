---FILE: tables/authorization_agreement.md ---
---
type: table
title: authorization_agreement（授权确认书表）
page_key: authorization_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权确认书表
  - 授权书表
  - 客户管理员授权确认书
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

`authorization_agreement` 记录“企业管理员 → 产融平台”的授权确认关系，是企业开通业务前的一道准入凭证。每条记录通过 `cust_id` 指向 [[cust_company_info]]，通过 `cust_manager_id` 指向被授权/签署的企业管理员用户；`authed_status` 表示授权是否达成，`enable` 表示该记录当前是否有效。授权书按 `platform_product_code` 区分归属：`PLATFORM` 为平台级管理员授权书，其余为业务线产品码，口径见 [[platform_level_auth_agreement]]。

必须把它与业务协议文件区分开：产品协议、隐私政策、用户协议、CA 协议等协议实体走 [[argeement_migratory_record]]，二者不可互换，边界见 [[auth_agreement]]。

## 需求背景
平台在放行企业开通业务前，需要确认“当前企业管理员是否有权代表企业签署”。因此建档初始化、补授权、完善资料会写入/更新授权确认记录，状态判定口径为 [[auth_agreement_authed_y]] 与 [[auth_agreement_authed_n]]；管理员换人后旧授权必须整体作废，见 [[manager_change_invalidate_agreement]]。

## 版本演进
`creation_type` 同时存在 `CUST_BUILD_INIT`（建档初始化自动授权）、`AUTO`（自动）与 `COMPANY_MANAGER_CHANGE_CODE`（管理员变更），说明建档链路与管理员变更链路先后接入该表；`original_cust_id` 记录源系统 custId，说明该表承接了存量迁移数据。`company_type` 在 DB 中除标准 dictKey 外还存在 JSON 数组与拼写异常值，属历史写入遗留。

```ground:table
table: authorization_agreement
comment: 授权确认书表
fields:
  - name: authed_status
    type: unknown
    desc: "授权确认书认证状态：Y=已授权，N=未授权/已禁用；DB 分布 Y=11617 / N=19547"
    dict: "Y/N"
  - name: platform_product_code
    type: unknown
    desc: "授权书归属平台产品编码；PLATFORM=产融平台级管理员授权书（代码常量 PLATFORM_PRODUCT_TYPE），其余为业务线产品码（ACFLOW/AMS/ORDER/RVSFACTOR_PC/...）"
    dict: "PLATFORM/ACFLOW/AMS/ORDER/RVSFACTOR_PC"
  - name: company_type
    type: unknown
    desc: "企业角色（CustCompanyTypeEnum.getDictKey()，如 SUPPLIER/CORE/FINANCE/PROJECT_COMPANY）；DB 中另存有 JSON 数组与拼写异常值"
    dict: "CustCompanyTypeEnum"
  - name: creation_type
    type: unknown
    desc: "授权书创建类型：CUST_BUILD_INIT=建档初始化自动授权，AUTO=自动，COMPANY_MANAGER_CHANGE_CODE=管理员变更"
    dict: "CUST_BUILD_INIT/AUTO/COMPANY_MANAGER_CHANGE_CODE"
  - name: cust_id
    type: unknown
    desc: "企业ID，指向 cust_company_info.id（逻辑外键，非物理 FK）"
    dict: ""
  - name: cust_manager_id
    type: unknown
    desc: "签署/被授权企业管理员用户ID（对应 cust_person_info.user_id / sys 用户）"
    dict: ""
  - name: enable
    type: unknown
    desc: "逻辑启用标识，Y/N；管理员变更时原记录置 N"
    dict: "Y/N"
  - name: original_cust_id
    type: unknown
    desc: "源系统 custId（迁移来源企业标识）"
    dict: ""
```
---END FILE---

---FILE: tables/argeement_migratory_record.md ---
---
type: table
title: argeement_migratory_record（协议迁移记录表）
page_key: argeement_migratory_record
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议迁移记录
  - 协议拉取记录表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

`argeement_migratory_record` 承载协议实体从业务系统向产融侧迁移的拉取记录：一条记录 = 一个 `platform_product_code` 产品下的一个 `agreement_type` 协议种类，见 [[agreement_type]]。协议文件本体存在 COS 上（`agreement_path`），记录本身负责“是否已拉取”（`status`）、失败重试次数（`pull_num`）与签署模式（`sign_mode`）。

它与 [[authorization_agreement]]（授权确认记录）语义不同，见 [[auth_agreement]]；状态流转见 [[agreement_migratory_pull_status]]。

## 需求背景
存量客户在业务系统已签署的协议需要迁移到产融侧留存与展示，因此需要一张表记录每个产品、每种协议的拉取进度，并支持有限次重试，口径见 [[agreement_migratory_pending_pull]]、[[agreement_migratory_pulled]]、[[agreement_migratory_enabled]]；签署方式需可追溯，见 [[agreement_sign_mode_offline]] 与 [[sign_mode_mapping]]。

## 版本演进
`is_new` 落库存的是 BooleanEnum 的 java name（yes/no）而非 dictKey，`status` 列为 int 却存字符串数字，`sign_mode` 用两位字典码区分线上/线下/无需签署——这些不一致说明该表是在迁移项目推进中逐步演化出来的，字段写入方式未统一。

```ground:table
table: argeement_migratory_record
fields:
  - name: agreement_type
    type: unknown
    desc: "协议类型（AgreementDocType.getAgreementType()）：PrivacyPolicy/UserProtocol/CustPersonLicense/CFCA_Auth/BS_Auth/ProductProtocol*"
    dict: "AgreementDocType"
  - name: status
    type: int
    desc: "协议拉取状态：0=待拉取（BooleanEnum.no），1=已拉取完成（BooleanEnum.yes）；列为 int 但存字符串数字"
    dict: "0/1"
  - name: sign_mode
    type: unknown
    desc: "协议签署模式：01=线上，02=线下，03=无需签署（SignModeEnum.getDictKey()）"
    dict: "SignModeEnum"
  - name: is_new
    type: unknown
    desc: "是否新数据，存 BooleanEnum 的 java name（yes/no）而非 dictKey"
    dict: "BooleanEnum"
  - name: pull_num
    type: unknown
    desc: "拉取次数，用于失败重试上限（pull_num < 配置的 pullNum）"
    dict: ""
  - name: agreement_path
    type: unknown
    desc: "协议文件在 COS 上的存储路径（协议实体文件）"
    dict: ""
  - name: cust_id
    type: unknown
    desc: "产融客户ID，指向 cust_company_info.id（逻辑外键）"
    dict: ""
```
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（企业建档信息表）
page_key: cust_company_info
domain: 授权协议与电子授权
status: draft
aliases:
  - 企业建档信息表
  - 建档表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

`cust_company_info` 是企业建档主表，同时承担授权与签章能力的判定底座：`cust_build_status` 描述建档认证进度（见 [[cust_build_status_flow]]），`need_register_* / *_register_status` 描述电子签章通道的意愿与实际开通情况（见 [[electronic_seal_activation]]），`cust_source / identify_style` 决定该企业走哪条建档与授权链路（见 [[migratory_supplement_exemption]]）。[[authorization_agreement]] 与 [[argeement_migratory_record]] 均以本表 `id` 作为逻辑外键。

## 需求背景
线下授权书要改成线上电子签署，前提是“这家企业已开通 CA、且租户允许”，因此签章意愿/结果与授权补签开关都落在企业建档表上，判定口径见 [[need_register_ca]]、[[cfca_registered]]、[[auth_agreement_supplement_flag]]、[[tenant_electronic_auth_flag]]，触发条件见 [[offline_eauth_sign_trigger]]。

## 版本演进
`migarory_auth_aggrement_flag`（迁移到授权书新渠道标识）字段名保留了历史拼写 `migarory`，未做重命名；`auth_aggrement_supplement_flag` 与 `cust_source=MIGRATORY` 的组合说明新渠道迁移企业被豁免补签，属迁移后期新增口径；`bs_register_status`（上上签）与 `ca_register_status`（CFCA）并存，说明签章通道由单通道扩展为多通道。

```ground:table
table: cust_company_info
fields:
  - name: need_register_ca
    type: unknown
    desc: "是否需要开通电子签章(CFCA)，Y/N"
    dict: "Y/N"
  - name: ca_register_status
    type: unknown
    desc: "CFCA 开通状态（OpenStatus，Y/N）；仅 need_register_ca=Y 且本字段=Y 才算已开通"
    dict: "OpenStatus"
  - name: need_register_bs
    type: unknown
    desc: "是否需要开通上上签(BEST_SIGN)，Y/N；AMS 产品签章通道"
    dict: "Y/N"
  - name: bs_register_status
    type: unknown
    desc: "上上签开通状态 Y/N；迁移开通时与 ca_register_status 同时置 Y"
    dict: "Y/N"
  - name: auth_aggrement_supplement_flag
    type: unknown
    desc: "是否展示/开启授权书补签：Y=需补签；迁移新渠道企业置 N"
    dict: "Y/N"
  - name: migarory_auth_aggrement_flag
    type: unknown
    desc: "迁移到授权书新渠道标识（Y/N，注意字段名拼写为 migarory）"
    dict: "Y/N"
  - name: cust_source
    type: unknown
    desc: "建档数据来源：PLATFORM_PUSH=外部平台推送（无需授权书）、MIGRATORY=存量迁移、其他为产融自建"
    dict: "PLATFORM_PUSH/MIGRATORY"
  - name: identify_style
    type: unknown
    desc: "认证方式：INVITE=邀请客户录入、INVITE_AGW=邀请平台录入、SELF=自主注册、SIMPLE=简易认证"
    dict: "INVITE/INVITE_AGW/SELF/SIMPLE"
  - name: cust_build_status
    type: unknown
    desc: "企业认证/建档状态，取 CustBuildStatusEnum 的 name 落库（代码用 CustBuildStatusEnum.valueOf 反解）"
    dict: "CustBuildStatusEnum"
```
---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config（租户配置表）
page_key: tenant_setting_config
domain: 授权协议与电子授权
status: draft
aliases:
  - 租户配置表
  - 租户设置
oid: 1
scope:
  databases: [unknown]
sources:
  - db:tenant_setting_config
  - code:ElectronicAuthLetterApplication.java
contract_version: "0.1"
---

`tenant_setting_config` 是租户级开关表。在授权场景中，`generate_electronic_auth_flag` 决定该租户是否启用“线下授权书电子签约版”（见 [[electronic_auth_letter]]），它是签署触发链路上的第一道租户级闸门，口径见 [[tenant_electronic_auth_flag]]。

## 需求背景
线下授权书的电子化并非所有租户同时切换，需要按租户灰度：租户开关为 Y 时，企业在满足审核通过、授权模式为 off_auth、企业类型与变更项白名单、CA 已开通等条件后，才自动发起电子签署，完整与门见 [[offline_eauth_sign_trigger]]。

## 版本演进
该字段的语义注记为“是否生成电子版授权书”，与 [[electronic_auth_letter]] 的“线下授权书电子签约版”表述一致，属电子授权书能力上线时新增的租户级配置；查询时另带 `enable='Y'` 条件。

```ground:table
table: tenant_setting_config
fields:
  - name: generate_electronic_auth_flag
    type: unknown
    desc: "租户是否开启线下授权书电子签约版：Y=是（注释「是否生成电子版授权书」）"
    dict: "Y/N"
```
---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: cust_change_record（企业变更记录表）
page_key: cust_change_record
domain: 授权协议与电子授权
status: draft
aliases:
  - 企业变更记录
  - 变更单
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

`cust_change_record` 记录企业信息变更单。在授权场景中，它是“变更流程是否需要重签授权书”的判定依据：`alter_mode` 区分企业自行变更（`SELF_ALTER`）与平台发起变更（`PLAT_ALTER`），`alter_type_id` 是逗号分隔的 [[cust_change_cfg]] 主键列表，用于反查 `item_code` 白名单（如 UN0016/UN0012/UN0013/UN0008/UN0015）。

## 需求背景
企业信息变更可能触发授权书重签或补签：只有企业自行变更、且变更项落在授权书相关白名单内时，才需要走电子授权书签署，见 [[offline_eauth_sign_trigger]] 与 [[manager_change_invalidate_agreement]]。`oper_cust_id` 用于把变更单定位到运营中台客户。

## 版本演进
`alter_type_id` 采用逗号分隔 ID 列表而非关联表存多项变更，属早期实现方式；白名单 item_code 的集合随授权书电子化推进而扩充。

```ground:table
table: cust_change_record
fields:
  - name: alter_mode
    type: unknown
    desc: "变更方式：SELF_ALTER=企业自行变更、PLAT_ALTER=平台发起变更"
    dict: "SELF_ALTER/PLAT_ALTER"
  - name: alter_type_id
    type: unknown
    desc: "变更项配置ID列表（逗号分隔的 cust_change_cfg.id），用于反查 item_code"
    dict: ""
  - name: cust_id
    type: unknown
    desc: "变更所属企业ID"
    dict: ""
  - name: oper_cust_id
    type: unknown
    desc: "运营中台客户ID，用于定位对应变更单"
    dict: ""
```
---END FILE---

---FILE: tables/cust_change_cfg.md ---
---
type: table
title: cust_change_cfg（变更项配置表）
page_key: cust_change_cfg
domain: 授权协议与电子授权
status: draft
aliases:
  - 变更项配置表
  - 变更项字典
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

`cust_change_cfg` 是变更项配置表，`item_code` 为变更项编码（UN0008/UN0009/UN0012/UN0013/UN0015/UN0016 等）。它通过 `cust_change_record.alter_type_id` 被反查，是判断“本次变更是否需要重签授权书”的白名单依据。

## 需求背景
并非所有企业变更都涉及授权主体或授权要素变化，因此用变更项编码白名单收敛签署范围，减少不必要的电子授权书签署，见 [[offline_eauth_sign_trigger]]。

## 版本演进
UN 系列编码随变更项扩展而增加；授权书签署白名单（UN0016/UN0012/UN0013/UN0008/UN0015）在该表编码体系内被显式引用，说明白名单是在既有变更项体系上追加的语义。

```ground:table
table: cust_change_cfg
fields:
  - name: item_code
    type: unknown
    desc: "变更项编码（UN0008/UN0009/UN0012/UN0013/UN0015/UN0016 等），授权书签署白名单依据"
    dict: "UN0008/UN0009/UN0012/UN0013/UN0015/UN0016"
```
---END FILE---

---FILE: processes/authed_status_state_flow.md ---
---
type: process
title: 授权确认书认证状态流转
page_key: authed_status_state_flow
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权书状态流转
  - authed_status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

该状态机描述 [[authorization_agreement]] 中 `authed_status` 的取值与迁移路径。它决定“这家企业/这个管理员是否已签署授权书”，是 [[auth_agreement_authed_y]] / [[auth_agreement_authed_n]] 两个口径的底层依据。

关键点在于：**N → Y 只在当前操作人是企业管理员（admin）时成立**；非管理员用户被指定授权时，记录保持 N。**Y → N 出现在管理员变更**：换人时原管理员在该企业下的全部授权记录被置为 `enable=N` 且 `authed_status=N`，再由新管理员重新走授权，见 [[manager_change_invalidate_agreement]] 与 [[auth_agreement]]。

## 需求背景
企业管理员授权认证通过（新增企业认证、补授权、完善资料）后授权才生效；管理员换人后原授权必须立即失效，避免“旧人授权、新人操作”。因此状态机需要一条双向通路，且 Y→N 只能由管理员变更触发。

## 版本演进
DB 中 N（19547）显著多于 Y（11617），与“管理员变更即作废、需重新授权”的写入行为一致；`creation_type` 中的 `CUST_BUILD_INIT`（建档初始化自动授权）说明早期授权是在建档时自动产生的。

```ground:process
name: 授权确认书认证状态
field: authorization_agreement.authed_status
states:
  - value: "N"
    label: 未授权/已禁用
    source: db_dist
  - value: "Y"
    label: 已授权
    source: db_dist
transitions:
  - from: "N"
    event: 企业管理员授权认证通过（新增企业认证/补授权/完善资料）
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "N"
    event: 存在未签署记录且当前用户为企业管理员（admin）
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "N"
    event: 非管理员用户被指定授权
    to: "N"
    evidence: "code_path:CustAuthAgreementDomainService.java:passAuthorizationAgreementDirectly"
  - from: "Y"
    event: 企业管理员变更（换人）
    to: "N"
    evidence: "code_path:CustAuthAgreementDomainService.java:disabledAllAuthorizationAgreement"
```
---END FILE---

---FILE: processes/agreement_migratory_pull_status.md ---
---
type: process
title: 协议迁移拉取状态流转
page_key: agreement_migratory_pull_status
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取状态机
  - status 状态流转
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

该状态机描述 [[argeement_migratory_record]] 中 `status` 的推进方式：协议迁移任务取出待拉取记录（口径 [[agreement_migratory_pending_pull]]），成功落库后置 1（口径 [[agreement_migratory_pulled]]）；失败时 `pull_num+1` 等待下一轮重试，超过上限不再拉取，见 [[agreement_pull_retry_limit]]。客户端返回空协议集时直接标记完成，属于终态但无协议文件。

## 需求背景
存量协议不能一次性可靠拉齐，因此需要“待拉取 / 已拉取完成”两态 + 计数重试的组合，保证最终一致性同时避免无限重试。取数一律过滤 `enable='Y'`，见 [[agreement_migratory_enabled]]。

## 版本演进
`status` 列定义为 int 但代码写入的是字符串数字（`BooleanEnum.no/yes`），说明状态取值复用了布尔枚举的字典码而非独立枚举，属迁移初期的实现选择。

```ground:process
name: 协议迁移拉取状态
field: argeement_migratory_record.status
states:
  - value: "0"
    label: 待拉取
    source: db_dist
  - value: "1"
    label: 已拉取完成
    source: db_dist
transitions:
  - from: "0"
    event: 从业务系统拉取到协议并落库
    to: "1"
    evidence: "code_path:AgreementMigratoryService.java:setAgreement"
  - from: "0"
    event: 拉取失败，pull_num+1 后等待重试
    to: "0"
    evidence: "code_path:AgreementMigratoryService.java:updateAgreementPullNum"
  - from: "0"
    event: 客户端返回空协议集，标记为已完成
    to: "1"
    evidence: "code_path:AgreementMigratoryService.java:setAgreement（agreementDocs 为空分支）"
```
---END FILE---

---FILE: processes/cust_build_status_flow.md ---
---
type: process
title: 企业认证/建档状态流转
page_key: cust_build_status_flow
domain: 授权协议与电子授权
status: draft
aliases:
  - 建档状态机
  - cust_build_status 状态流转
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

该状态机描述 [[cust_company_info]] 中 `cust_build_status` 的推进：提交建档后进入待客户确认，客户提交后进入审核中，审核通过则 `BUILD_SUCCESS`，退回回到待客户确认，驳回则 `BUILD_FAIL`，驳回后修改可重新提交。状态值以 `CustBuildStatusEnum` 的 name 落库，代码用 `valueOf` 反解。

这条状态机是电子授权书签署的前置条件之一：只有 `checkStatus=CUST_CHECK_PASS`（审核通过）后才可能触发签署，见 [[offline_eauth_sign_trigger]]；而 `identify_style=SIMPLE`（简易认证）会强制关闭电子签章，见 [[simple_identify_disable_ca]]。

## 需求背景
企业建档需要人机协同（企业录入 → 运营中台审核），因此必须显式建模退回与驳回回路；同时签署与建档分段解耦——签署只在审核通过后的事务提交后触发，任一前置条件不满足仅记日志跳过，不阻断主流程。

## 版本演进
状态集合中同时存在 `CUST_CONFIRM_AWAIT`（待客户确认）与 `AWAIT_CUST_CONFIRM`（待客户确认，简易认证），说明简易认证链路是后加的，与标准链路并存。

```ground:process
name: 企业认证/建档状态
field: cust_company_info.cust_build_status
states:
  - value: "INIT"
    label: 待提交
    source: code_enum
  - value: "CUST_CONFIRM_AWAIT"
    label: 待客户确认
    source: code_enum
  - value: "AWAIT_CUST_CONFIRM"
    label: 待客户确认（简易认证）
    source: code_enum
  - value: "CUST_BUILDING"
    label: 审核中
    source: code_enum
  - value: "BUILD_SUCCESS"
    label: 已通过
    source: code_enum
  - value: "BUILD_FAIL"
    label: 已驳回
    source: code_enum
transitions:
  - from: "INIT"
    event: 提交建档（邀请客户录入/自主注册）
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: "BUILD_FAIL"
    event: 驳回后修改重新提交
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustCompanyInfoApplication.java:appenUpdateCustBulidStatus"
  - from: "CUST_CONFIRM_AWAIT"
    event: 客户提交，运营中台审核
    to: "CUST_BUILDING"
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: "CUST_BUILDING"
    event: 运营中台审核退回
    to: "CUST_CONFIRM_AWAIT"
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: "CUST_BUILDING"
    event: 审核通过（简易/资金方直接生效）
    to: "BUILD_SUCCESS"
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: "CUST_CONFIRM_AWAIT"
    event: 审核驳回
    to: "BUILD_FAIL"
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
```
---END FILE---

---FILE: calibers/platform_level_auth_agreement.md ---
---
type: caliber
title: 平台级授权确认书
page_key: platform_level_auth_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM 授权书
  - 平台授权书口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

用于把「平台级」授权确认书与业务线产品授权书分开。命中该口径的记录代表企业管理员对产融平台的授权，与 `ACFLOW/AMS/ORDER/RVSFACTOR_PC` 等业务线产品码并列存在于同一张 [[authorization_agreement]] 表中。

补签判定中，平台级授权书与存量产品授权是两条并列的检查项，见 [[migratory_supplement_exemption]]；不要把这里的 `PLATFORM` 与协议迁移里的产品协议 [[product_protocol]] 混为一谈。

```ground:caliber
name: 平台级授权确认书
predicate: "authorization_agreement.platform_product_code = 'PLATFORM'"
scope: "产融平台管理员授权书（PLATFORM_PRODUCT_TYPE），与业务线产品码并列"
evidence: "code:CustAuthAgreementDomainService.java:PLATFORM_PRODUCT_TYPE + db:PLATFORM=25156"
```
---END FILE---

---FILE: calibers/auth_agreement_authed_y.md ---
---
type: caliber
title: 授权书已授权
page_key: auth_agreement_authed_y
domain: 授权协议与电子授权
status: draft
aliases:
  - 已签署授权书
  - authed_status=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

判断企业/管理员是否已签署授权书的口径。使用时注意：只有当记录 `enable=Y` 时，`authed_status=Y` 才代表当前有效授权——管理员变更会把原记录置 `enable=N` 并同时置 `authed_status=N`，见 [[manager_change_invalidate_agreement]] 与状态机 [[authed_status_state_flow]]。

```ground:caliber
name: 授权书已授权
predicate: "authorization_agreement.authed_status = 'Y'"
scope: "判断企业/管理员是否已签署授权书（enable=Y 时有效）"
evidence: "code:CustAuthAgreementDomainService.java:hasCompanySignedAuthAggrement + db"
```
---END FILE---

---FILE: calibers/auth_agreement_authed_n.md ---
---
type: caliber
title: 授权书未授权
page_key: auth_agreement_authed_n
domain: 授权协议与电子授权
status: draft
aliases:
  - 未签署授权书
  - authed_status=N
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

需补签授权书的判定口径，与 [[auth_agreement_authed_y]] 互补。DB 中该值占比更高（19547 条），部分来源是管理员变更导致的作废（`enable=N` 且 `authed_status=N`），须结合 `enable` 与 `cust_source` 判断是否真的需要补签，见 [[migratory_supplement_exemption]]、[[auth_agreement_supplement_flag]]。

```ground:caliber
name: 授权书未授权
predicate: "authorization_agreement.authed_status = 'N'"
scope: "需补签授权书的判定口径"
evidence: "code + db"
```
---END FILE---

---FILE: calibers/agreement_migratory_pending_pull.md ---
---
type: caliber
title: 待拉取协议记录
page_key: agreement_migratory_pending_pull
domain: 授权协议与电子授权
status: draft
aliases:
  - status=0
  - 待拉取口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

协议迁移拉取任务的取数口径。实际取数不是单条件，而是复合条件：`status='0'` 且 `enable='Y'` 且 `pull_num < 配置值`，见 [[agreement_migratory_enabled]] 与 [[agreement_pull_retry_limit]]；状态推进见 [[agreement_migratory_pull_status]]。

```ground:caliber
name: 待拉取协议记录
predicate: "argeement_migratory_record.status = '0'"
scope: "协议迁移拉取任务取数（复合条件 enable='Y' AND pull_num<配置值）"
evidence: "code:AgreementMigratoryService.java:pull + db"
```
---END FILE---

---FILE: calibers/agreement_migratory_pulled.md ---
---
type: caliber
title: 已拉取协议记录
page_key: agreement_migratory_pulled
domain: 授权协议与电子授权
status: draft
aliases:
  - status=1
  - 已拉取口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

协议迁移的终态口径。注意“已拉取完成”并不必然意味着存在协议文件：客户端返回空协议集时会被标记为已完成，`agreement_path` 可能为空，见 [[agreement_migratory_pull_status]]。

```ground:caliber
name: 已拉取协议记录
predicate: "argeement_migratory_record.status = '1'"
scope: "迁移协议拉取结果终态"
evidence: "code + db"
```
---END FILE---

---FILE: calibers/agreement_migratory_enabled.md ---
---
type: caliber
title: 协议迁移有效记录
page_key: agreement_migratory_enabled
domain: 授权协议与电子授权
status: draft
aliases:
  - enable=Y
  - 协议拉取有效记录
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

协议拉取一律附带的有效性过滤条件，与 [[authorization_agreement]] 中的 `enable` 语义一致（逻辑启用标识）。当前 DB 中该表 `enable` 全为 Y、无 N，因此该口径目前不产生过滤效果，但属于取数必经条件，见 [[agreement_migratory_pending_pull]]。

```ground:caliber
name: 协议迁移有效记录
predicate: "argeement_migratory_record.enable = 'Y'"
scope: "协议拉取一律过滤 enable=Y（DB 中全为 Y，无 N）"
evidence: "code:AgreementMigratoryService.java:pull + db"
```
---END FILE---

---FILE: calibers/tenant_electronic_auth_flag.md ---
---
type: caliber
title: 电子授权书租户开关
page_key: tenant_electronic_auth_flag
domain: 授权协议与电子授权
status: draft
aliases:
  - 租户电子授权书开关
  - generate_electronic_auth_flag=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:tenant_setting_config
  - code:ElectronicAuthLetterApplication.java
contract_version: "0.1"
---

判断某租户是否启用「线下授权书电子签约版」的口径，查询时另带 `enable='Y'`。它是 [[offline_eauth_sign_trigger]] 多重与门中的租户级条件，与 [[electronic_auth_letter]] 概念对应。

```ground:caliber
name: 电子授权书租户开关
predicate: "tenant_setting_config.generate_electronic_auth_flag = 'Y'"
scope: "租户是否开启线下授权书电子签约版；查询另带 enable='Y'"
evidence: "code:ElectronicAuthLetterApplication.java:isGenerateElectronicAuthEnabled"
```
---END FILE---

---FILE: calibers/cfca_registered.md ---
---
type: caliber
title: CFCA 已开通
page_key: cfca_registered
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 已开通
  - ca_register_status=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

电子授权书在线签署的前置校验口径：必须同时满足 [[need_register_ca]]（意愿）与本口径（结果）。它与 `bs_register_status`（上上签）是并列的两个签章通道，见 [[electronic_seal_activation]]。若审核通过时本口径未命中则跳过签署，待 CA 重开成功回调后补偿触发，见 [[ca_delayed_compensation_sign]]。

```ground:caliber
name: CFCA 已开通
predicate: "cust_company_info.ca_register_status = 'Y'"
scope: "电子授权书在线签署前置校验（需同时 need_register_ca='Y'）"
evidence: "code:CustAuthSignOrchestrationApplication.java:isCaRegistered"
```
---END FILE---

---FILE: calibers/need_register_ca.md ---
---
type: caliber
title: 需开通电子签章
page_key: need_register_ca
domain: 授权协议与电子授权
status: draft
aliases:
  - 需要开通电子签章
  - need_register_ca=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

判断企业是否需要 CFCA 电子签章能力的口径，是「意愿」而非「结果」，必须与 [[cfca_registered]] 同时成立才视为已开通，见 [[electronic_seal_activation]]。简易认证场景下即使该字段为 Y 也会被强制校正为不开通，见 [[simple_identify_disable_ca]]。

```ground:caliber
name: 需开通电子签章
predicate: "cust_company_info.need_register_ca = 'Y'"
scope: "判断企业是否需要 CFCA 电子签章能力"
evidence: "code:CustAuthSignOrchestrationApplication.java:isCaRegistered"
```
---END FILE---

---FILE: calibers/auth_agreement_supplement_flag.md ---
---
type: caliber
title: 授权书补签开关
page_key: auth_agreement_supplement_flag
domain: 授权协议与电子授权
status: draft
aliases:
  - 补签开关
  - auth_aggrement_supplement_flag=Y
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

存量迁移企业是否仍需补签平台授权书的口径。它与 `cust_source=MIGRATORY` 组合使用：本字段为 N 且来源为迁移，则视为新渠道迁移企业、免签，见 [[migratory_supplement_exemption]] 与 [[cust_company_info]]。

```ground:caliber
name: 授权书补签开关
predicate: "cust_company_info.auth_aggrement_supplement_flag = 'Y'"
scope: "存量迁移企业是否仍需补签平台授权书；N 且 cust_source=MIGRATORY 则免签"
evidence: "code:CustAuthAgreementDomainService.java:enableCompanyManagerAuthAggrement"
```
---END FILE---

---FILE: calibers/agreement_sign_mode_offline.md ---
---
type: caliber
title: 线下签署协议
page_key: agreement_sign_mode_offline
domain: 授权协议与电子授权
status: draft
aliases:
  - sign_mode=02
  - 线下协议口径
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

标识迁移协议在业务系统中的签署模式为线下（`SignModeEnum.OFF_LINE`）。与之并列的是 01 线上、03 无需签署，映射规则见 [[sign_mode_mapping]]。该口径用于迁移后追溯协议签署方式，与 `cust_company_info.need_register_ca` 等签章能力字段不是同一语义（见 [[electronic_seal_activation]]）。

```ground:caliber
name: 线下签署协议
predicate: "argeement_migratory_record.sign_mode = '02'"
scope: "协议签署模式为线下（SignModeEnum.OFF_LINE）"
evidence: "code:AgreementMigratoryService.java:setMigrateContract + db"
```
---END FILE---

---FILE: concepts/auth_agreement.md ---
---
type: concept
title: 授权书（授权确认书）
page_key: auth_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户管理员授权确认书
  - 平台授权书
  - 授权协议
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
maps_to:
  - authorization_agreement.authed_status
field_targets:
  - authorization_agreement.authed_status
  - authorization_agreement.enable
  - authorization_agreement.cust_manager_id
adjudication: boundary
also_confused_with:
  - argeement_migratory_record.agreement_type
  - contract_info
---

业务上说“授权书”，指的是企业管理员对产融平台的授权确认关系，落在 [[authorization_agreement]] 上，以 `authed_status`、`enable`、`cust_manager_id` 为关键字段，口径见 [[auth_agreement_authed_y]] 与 [[auth_agreement_authed_n]]。

它与业务协议文件是两件事：产品协议/隐私政策/用户协议/CA 协议等文件实体走 [[argeement_migratory_record]]（协议类型见 [[agreement_type]]），底层由协议组件合同表承载。做需求或排查时若把两者互换，会出现“授权书状态为 Y 但协议文件缺失”之类的误判。

## 需求背景
企业与平台之间的“授权”关系与“协议文件”关系在业务上被反复混用，本页用于固定词汇边界：凡是讨论“企业管理员是否已授权 / 是否需补签”“授权书签署触发条件”的，一律走本概念；凡是讨论“协议文件是否已拉取/存储路径/签署模式”的，一律走协议迁移记录。

## 版本演进
该词的别名随产品演进增加（客户管理员授权确认书、平台授权书、授权协议）；管理员变更作废、迁移企业免签等新规则都作用在本概念所指的记录上，见 [[manager_change_invalidate_agreement]]、[[migratory_supplement_exemption]]。
---END FILE---

---FILE: concepts/electronic_auth_letter.md ---
---
type: concept
title: 电子授权书（电子签约版授权书）
page_key: electronic_auth_letter
domain: 授权协议与电子授权
status: draft
aliases:
  - 线下电子授权书
  - off_auth 授权书
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - db:tenant_setting_config
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - tenant_setting_config.generate_electronic_auth_flag
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - tenant_setting_config.generate_electronic_auth_flag
adjudication: boundary
also_confused_with:
  - authorization_agreement.authed_status
---

「电子授权书」指线下授权（off_auth）场景下把纸质授权书改为 CFCA 在线签署的方案，其存在性由租户开关 + 企业签章能力共同定义：[[tenant_electronic_auth_flag]]、[[need_register_ca]]、[[cfca_registered]]。它不是一个独立的授权状态字段，因此**不能**用 `authorization_agreement.authed_status` 来代替描述。

## 需求背景
线下授权书需要人工签署与回收，效率低且难追溯，因此引入电子签约版：租户开关打开、企业已开通 CA、且本次业务满足审核通过与变更项白名单时，系统自动发起签署，完整触发条件见 [[offline_eauth_sign_trigger]]；签署幂等见 [[auth_sign_idempotent]]。

## 版本演进
该能力上线时同时引入了租户级开关（[[tenant_setting_config]] 的 `generate_electronic_auth_flag`）与企业级签章字段；后续又加入“CA 未开通时延迟补偿签署”的补签链路，见 [[ca_delayed_compensation_sign]]，以及简易认证强制不开通 CA 的约束，见 [[simple_identify_disable_ca]]。
---END FILE---

---FILE: concepts/electronic_seal_activation.md ---
---
type: concept
title: 电子签章开通
page_key: electronic_seal_activation
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 开通
  - CFCA 注册
  - 上上签开通
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
field_targets:
  - cust_company_info.ca_register_status
  - cust_company_info.bs_register_status
adjudication: boundary
also_confused_with:
  - cust_company_info.need_register_ca
  - cust_company_info.need_register_bs
---

必须区分两组字段：`need_register_*` 是“要不要开”的意愿标识，`*_register_status` 是“已经开了”的落库结果；签署判定要求两者同时为 Y（见 [[need_register_ca]]、[[cfca_registered]]）。另外 CFCA（PAPER_LESS）与上上签（BEST_SIGN，AMS 使用）是两个并列的签章通道，不能只检查其中一个。

## 需求背景
电子授权书签署要求企业具备可用签章能力，因此产品侧先采集意愿（`need_register_ca` / `need_register_bs`），再由签章开通流程回写结果状态；两者不同步是“签署被跳过”的常见原因，对应的补偿逻辑见 [[ca_delayed_compensation_sign]]。

## 版本演进
上上签字段（`need_register_bs` / `bs_register_status`）说明签章通道由单一 CFCA 扩展为多通道，且迁移开通时会同时把 `bs_register_status` 与 `ca_register_status` 置 Y；简易认证链路则禁止开通 CA，见 [[simple_identify_disable_ca]]。
---END FILE---

---FILE: concepts/agreement_type.md ---
---
type: concept
title: 协议类型（agreementType）
page_key: agreement_type
domain: 授权协议与电子授权
status: draft
aliases:
  - AgreementDocType
  - serviceKey
  - 协议 code
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
maps_to:
  - argeement_migratory_record.agreement_type
field_targets:
  - argeement_migratory_record.agreement_type
adjudication: boundary
also_confused_with:
  - authorization_agreement.platform_product_code
---

协议类型区分“协议的种类”：PrivacyPolicy / UserProtocol / CustPersonLicense / CFCA_Auth / BS_Auth / ProductProtocol*，对应 [[argeement_migratory_record]] 的 `agreement_type`。而 `platform_product_code` 区分“业务线产品”（ACFLOW/AMS/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER）。同一协议类型在每个产品码下各有一条迁移记录——两个维度是交叉关系，不是同义。

## 需求背景
协议拉取需要按“产品 × 协议类型”的粒度记录进度与文件路径，才能支持不同业务线各自回溯，见 [[agreement_migratory_pending_pull]]、[[agreement_migratory_pulled]]，产品协议的具体取值见 [[product_protocol]]。

## 版本演进
`ProductProtocol*` 是一族按产品码派生的协议类型，说明早期只有平台级协议（隐私政策、用户协议、CA 协议等），后续随业务线接入扩展出按产品的协议类型。
---END FILE---

---FILE: concepts/product_protocol.md ---
---
type: concept
title: 产品协议
page_key: product_protocol
domain: 授权协议与电子授权
status: draft
aliases:
  - ProductProtocol
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
maps_to:
  - argeement_migratory_record.agreement_type
field_targets:
  - argeement_migratory_record.agreement_type
adjudication: synonym
also_confused_with:
  - authorization_agreement.platform_product_code
---

「产品协议」是 [[agreement_type]] 的一个取值族（`ProductProtocol*`）：按产品码返回不同的协议类型（AMS/BEECREDIT/RVSFACTOR_PC/ACFLOW/ORDER/DEALER/STORAGE/VOUCHER）。它与“平台级协议”并列，但**不同于** `PLATFORM_PRODUCT_TYPE`（平台级管理员授权书）——后者属于 [[authorization_agreement]] 的产品码维度，见 [[platform_level_auth_agreement]]。

## 需求背景
每个业务线在开通时都需要客户签署对应的产品协议，迁移时按产品码逐条拉取，因此在迁移记录中表现为“同协议类型、不同产品码各一条”。

## 版本演进
产品协议的类型数量随业务线增加而扩张（AMS/BEECREDIT/RVSFACTOR_PC/ACFLOW/ORDER/DEALER/STORAGE/VOUCHER），是协议迁移需求长期演进的主要驱动之一。
---END FILE---

---FILE: rules/offline_eauth_sign_trigger.md ---
---
type: rule
title: 线下电子授权书签署触发条件（多重与门）
page_key: offline_eauth_sign_trigger
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子授权书触发条件
  - off_auth 签署与门
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
  - db:cust_change_record
  - db:tenant_setting_config
contract_version: "0.1"
---

这是本主题最核心的规则：电子授权书签署不是单条件触发，而是六个与门同时成立。任一条件不满足时**仅记日志跳过**，不阻断主流程——这一点决定了线上问题往往表现为“没有签”，而不是“报错”。

涉及口径：[[tenant_electronic_auth_flag]]、[[need_register_ca]]、[[cfca_registered]]、[[auth_agreement_supplement_flag]]；相关表 [[cust_company_info]]、[[cust_change_record]]、[[cust_change_cfg]]、[[tenant_setting_config]]。

```ground:rule
name: 线下电子授权书签署触发条件（多重与门）
content: "仅当 ①审核通过(checkStatus=CUST_CHECK_PASS) ②授权模式为 off_auth ③租户 generate_electronic_auth_flag=Y ④企业类型∈{供应商,核心企业,金融机构,项目公司} ⑤建档流程且建档方式∈{INVITE客户录入,SELF自主注册} 或 变更流程且 alterMode=SELF_ALTER 且变更项∈{UN0016,UN0012,UN0013,UN0008,UN0015} ⑥need_register_ca=Y 且 ca_register_status=Y 时，才在事务提交后触发签署；任一不满足仅记日志跳过，不阻断主流程"
impact: "决定线下授权书是否自动发起电子签署"
field_targets:
  - cust_company_info.cust_build_status
  - cust_company_info.identify_style
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_change_record.alter_mode
  - cust_change_record.alter_type_id
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code:CustAuthSignOrchestrationApplication.java:evaluateIneligibilityReason + isCaRegistered"
```
---END FILE---

---FILE: rules/ca_delayed_compensation_sign.md ---
---
type: rule
title: CFCA 未开通时的延迟补偿签署
page_key: ca_delayed_compensation_sign
domain: 授权协议与电子授权
status: draft
aliases:
  - CA 回调补偿签署
  - 延迟补签规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

解决“审核通过时 CA 还没开好”的时序问题：审核通过时若 [[cfca_registered]] 不成立则本轮跳过；待 CA 重开成功回调（`CaActivateResult.activateSuccess=true`）后再链式触发一次签署，此时即便本地状态仍非 Y 也继续尝试，由签章层做二次校验。与 [[offline_eauth_sign_trigger]] 配合，保证不永久漏签。

```ground:rule
name: CFCA 未开通时的延迟补偿签署
content: "审核通过时若本地 ca_register_status≠Y 则跳过签署；待 CA 重开成功回调（CaActivateResult.activateSuccess=true）后再链式触发一次签署，此时即使本地状态仍非 Y 也继续尝试（由签章层二次校验）"
impact: "保证 CA 开通后授权书能补签，避免永久漏签"
field_targets:
  - cust_company_info.ca_register_status
evidence: "code:CustAuthSignOrchestrationApplication.java:tryOfflineElectronicAuthSignAfterCaSuccess"
```
---END FILE---

---FILE: rules/auth_sign_idempotent.md ---
---
type: rule
title: 授权书签署幂等（Redis 锁 + 完成标记）
page_key: auth_sign_idempotent
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署幂等
  - 授权书签署防重
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

签署动作必须幂等：先用完成标记判重，再用分布式锁抢执行权，成功后写完成标记；签署失败只记日志、不回滚主流程。这让 [[ca_delayed_compensation_sign]] 的补偿触发与正常触发可以安全并存。

```ground:rule
name: 授权书签署幂等（Redis 锁 + 完成标记）
content: "签署前用 cust_auth_sign_done:{sourceMainId}:{appNo} 判重，再用 cust_auth_sign_after_audit:{sourceMainId}:{appNo} 抢锁（acquire-timeout 1000ms / lock-timeout 120000ms）执行，成功后写 done 标记；签署失败仅记日志不回滚主流程"
impact: "避免重复签署与并发重复提交"
field_targets: []
evidence: "code:CustAuthSignOrchestrationApplication.java:executeOfflineElectronicAuthSignSafely"
```
---END FILE---

---FILE: rules/manager_change_invalidate_agreement.md ---
---
type: rule
title: 企业管理员变更即作废原授权书
page_key: manager_change_invalidate_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 管理员变更作废授权
  - 授权主体切换规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
---

管理员换人时“先作废、后重建”：先把原管理员在该企业下的全部授权记录置 `enable=N`、`authed_status=N`（remark 记录 to|新管理员|原因），再为新管理员按企业各角色创建/更新 `authed_status=Y` 的授权记录。这是 [[authed_status_state_flow]] 中 Y→N 迁移的唯一来源，也解释了 [[auth_agreement_authed_n]] 记录偏多的现象。

```ground:rule
name: 企业管理员变更即作废原授权书
content: "管理员换人时先把原管理员在该企业下的全部授权记录 enable=N、authed_status=N（remark 记录 to|新管理员|原因），再为新管理员按企业各角色创建/更新 authed_status=Y 的授权记录"
impact: "保证授权主体与当前管理员一致"
field_targets:
  - authorization_agreement.enable
  - authorization_agreement.authed_status
  - authorization_agreement.cust_manager_id
  - authorization_agreement.creation_type
evidence: "code:CustAuthAgreementDomainService.java:changeCompanyAuthorizationAgreement + disabledAllAuthorizationAgreement"
```
---END FILE---

---FILE: rules/migratory_supplement_exemption.md ---
---
type: rule
title: 存量迁移企业授权书补签的豁免
page_key: migratory_supplement_exemption
domain: 授权协议与电子授权
status: draft
aliases:
  - 迁移企业免补签
  - 补签豁免规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
---

决定迁移/外部企业在开通产品时是否弹补签授权书：`cust_source=PLATFORM_PUSH`（外部平台推送）一律视为已授权；`cust_source=MIGRATORY` 且 [[auth_agreement_supplement_flag]] 为 N（新渠道迁移）无需签署；其余情况仍需检查平台授权（[[platform_level_auth_agreement]]）或存量产品授权。

```ground:rule
name: 存量迁移企业授权书补签的豁免
content: "cust_source=PLATFORM_PUSH（外部平台推送）一律视为已授权；cust_source=MIGRATORY 且 auth_aggrement_supplement_flag=N（新渠道迁移）不需要签署；其余情况需检查平台授权(PLATFORM)或存量产品授权"
impact: "决定迁移/外部企业在开通产品时是否弹补签授权书"
field_targets:
  - cust_company_info.cust_source
  - cust_company_info.auth_aggrement_supplement_flag
  - cust_company_info.migarory_auth_aggrement_flag
evidence: "code:CustAuthAgreementDomainService.java:enableCompanyManagerAuthAggrement"
```
---END FILE---

---FILE: rules/agreement_pull_retry_limit.md ---
---
type: rule
title: 协议迁移拉取的重试与上限
page_key: agreement_pull_retry_limit
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取重试
  - pull_num 上限
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

协议迁移任务的调度与重试约束：定时执行 + Redis 锁防重；只取待拉取且有效的记录，失败则 `pull_num+1`，超过配置上限不再拉取。状态含义见 [[agreement_migratory_pending_pull]]、[[agreement_migratory_pulled]]、[[agreement_migratory_pull_status]]。

```ground:rule
name: 协议迁移拉取的重试与上限
content: "协议迁移任务每 30 秒执行，用 Redis 锁 cust_argeement_pull 防重；取 status=0 且 enable=Y、pull_num<配置值 的记录按产品/客户分组拉取，失败时 pull_num+1 后重试，超过上限不再拉取"
impact: "保证协议迁移的最终一致性与有限重试"
field_targets:
  - argeement_migratory_record.status
  - argeement_migratory_record.pull_num
  - argeement_migratory_record.enable
evidence: "code:AgreementMigratoryService.java:pull + AreementPullTask"
```
---END FILE---

---FILE: rules/sign_mode_mapping.md ---
---
type: rule
title: 协议签署模式映射
page_key: sign_mode_mapping
domain: 授权协议与电子授权
status: draft
aliases:
  - signMode 映射
  - 签署模式落库规则
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

迁移时把业务系统的 `signMode` 归一化为产融侧的 [[argeement_migratory_record]] 字典码，并补齐 `sign_type=SIGNED`、`business_type=cust_company_info`，使迁移后协议在产融侧的签署方式可追溯。线下口径见 [[agreement_sign_mode_offline]]。

```ground:rule
name: 协议签署模式映射
content: "迁移协议将业务系统 signMode 映射为 SignModeEnum：NO_SIGN=03 无需签署、OFF_LINE=02 线下、ON_LINE=01 线上；并落 sign_type=SIGNED、business_type=cust_company_info"
impact: "迁移后协议在产融侧的签署方式可追溯"
field_targets:
  - argeement_migratory_record.sign_mode
evidence: "code:AgreementMigratoryService.java:setMigrateContract"
```
---END FILE---

---FILE: rules/simple_identify_disable_ca.md ---
---
type: rule
title: 简易认证强制关闭电子签章
page_key: simple_identify_disable_ca
domain: 授权协议与电子授权
status: draft
aliases:
  - SIMPLE 不开 CA
  - 简易认证签章约束
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyCaPolicy.java
  - db:cust_company_info
contract_version: "0.1"
---

简易认证（`identify_style=SIMPLE`）链路不支持开通电子签章：提交时若 [[need_register_ca]] 为 Y，会被策略强制校正为不开通并落库。这直接影响 [[offline_eauth_sign_trigger]] 的第 ⑥ 个与门——简易认证企业不会走电子授权书签署。

```ground:rule
name: 简易认证强制关闭电子签章
content: "简易认证提交时如 need_register_ca=Y 则通过 CustCompanyCaPolicy.enforceMustNotOpenCa 强制校正为不开通并落库"
impact: "简易建档不支持开通电子签章"
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.identify_style
evidence: "code:CustCompanyCaPolicy.java:enforceMustNotOpenCa"
```
---END FILE---

---REVIEW: table | authorization_agreement---
语义分析未给出各表所属的物理库名，本批页面 `scope.databases` 统一写 `unknown`，待补充真实物理库名（如多租户分库需按租户标注分片规则）。
---END REVIEW---

---REVIEW: rule | 简易认证强制关闭电子签章---
源语义分析在第八条规则处被截断（`field_targets` 与 `evidence` 不完整）。本页 `field_targets` 中的 `cust_company_info.need_register_ca`、`cust_company_info.identify_style` 与 `evidence` 的 `code:CustCompanyCaPolicy.java:enforceMustNotOpenCa` 系依据 rule content 中逐字出现的字段名与类名补全，需与 extract 结果核对确认。
---END REVIEW---

---REVIEW: process | 企业认证/建档状态流转---
状态集合中同时存在 `CUST_CONFIRM_AWAIT`（待客户确认）与 `AWAIT_CUST_CONFIRM`（待客户确认，简易认证），两者是否为同一状态的不同拼写、抑或分属标准链路与简易认证链路，语义分析未给出判定；转移动线未覆盖 `AWAIT_CUST_CONFIRM` 的出边，暂按原文保留，待确认。
---END REVIEW---