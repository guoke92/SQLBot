---FILE: tables/argeement_migratory_record.md ---
---
type: table
title: argeement_migratory_record（协议迁移记录表）
page_key: table.argeement_migratory_record
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议迁移记录表
  - 协议迁移拉取记录
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
  - code:PlatFormMigratoryApplication.java
contract_version: "0.1"
---

`argeement_migratory_record` 是「协议」主题的落地载体：每个客户 × 每个产品 × 每类协议各生成一条待拉取记录，由迁移初始化写入，再由定时任务消费拉取，直到 `status` 置 `1`（拉取结束）。它同时承载签署模式、协议文件路径与协议编号，因此是 [[concepts/agreement]] 与 [[concepts/authorization-agreement]] 的分界线：本表存协议文本与拉取事实，不记录「谁授过权」的授权关系。

相关的判定口径见 [[calibers/pending-pull-agreement-records]]、[[calibers/migratory-init-five-agreements]]、[[calibers/ams-bs-channel]]；状态流转见 [[processes/agreement-migratory-pull-status]] 与 [[processes/agreement-sign-mode]]。产品维度上，`platform_product_code`（AMS/ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER）既决定拉取哪一产品的协议，也决定产品协议类型映射；AMS 走 [[concepts/ca-cfca|上上签 BS 通道]]，其余产品走 CFCA。

## 需求背景
存量客户的协议分散在旧渠道，需要按客户维度逐产品、逐协议类型向客户端拉取并落库，因此需要一张拉取队列表：既能标记「已结束」避免重复拉取，也能限制失败重试次数（`pull_num` < 配置值 `cust.agreemeent.pull.num`，默认 20）。`is_new` 用于区分新老渠道协议，`agreement_no` 用于合同表判重，避免重复迁移。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张），故无标 (document_claim，未证实) 的条目。

```ground:table
table: argeement_migratory_record
evidence: db
```

```ground:field
table: argeement_migratory_record
fields:
  - field: status
    meaning: "协议迁移拉取状态：'0'（BooleanEnum.no）=待拉取/未处理；'1'（BooleanEnum.yes）=拉取流程已结束（客户端返回了协议，或确认客户端无该协议后置终态，置 1 后不再进入待拉取队列）"
    evidence: db
  - field: pull_num
    meaning: "已拉取尝试次数；pull() 只捞 pull_num < 配置值（cust.agreemeent.pull.num，默认 20）的记录，失败时 +1"
    evidence: code
  - field: is_new
    meaning: "是否新数据：'yes'/'no'（BooleanEnum.name()）；迁移初始化写 isNew，用于区分新老渠道协议"
    evidence: db
  - field: sign_mode
    meaning: "协议签署模式，语义对应 SignModeEnum 三态（NO_SIGN / OFF_LINE / ON_LINE）；DB 实存 '01' / '02' / '03'，代码未给出数值与枚举的显式映射"
    evidence: db
  - field: agreement_type
    meaning: "协议类型 key（AgreementDocType.getAgreementType()）：BS_Auth（AMS 上上签）/CFCA_Auth/ProductProtocol*/CustPersonLicense/UserProtocol/PrivacyPolicy"
    evidence: db
  - field: agreement_path
    meaning: "协议文件在对象存储（COS，FBP_SYSTEM 桶）的存储路径；为空表示未取到文件，createContractInfo 会过滤掉"
    evidence: code
  - field: agreement_no
    meaning: "协议编号（客户端 contractAgreementNo），agreementExist 用它做合同表判重，避免重复迁移"
    evidence: code
  - field: platform_product_code
    meaning: "产品编码（AMS/ACFLOW/BEECREDIT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER），决定拉取哪一产品的协议及产品协议类型映射"
    evidence: db
```

---END FILE---

---FILE: tables/authorization_agreement.md ---
---
type: table
title: authorization_agreement（授权确认书表）
page_key: table.authorization_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权确认书表
  - 授权书记录表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

`authorization_agreement` 存的是「谁授过权」的关系事实：按管理员（`cust_manager_id`，sys/SSO userId）维度记录其对企业（`cust_id`）在各产品上的授权状态。`authed_status='Y'` 即视为已授权，是免补签判定的核心输入（见 [[calibers/platform-level-authed]]）。它与 [[concepts/offline-electronic-auth]] 描述的「授权书这一份文件」生命周期不同，二者通过 `cust_id` 关联。

`platform_product_code='PLATFORM'` 表示平台级授权，是补签判定的唯一依据；具体业务产品行（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的 `Y` 表示存量系统已授权，用于免补签判定（见 [[concepts/platform-product-code]]）。记录的产生场景由 `creation_type` 承载：`AUTO`、`COMPANY_MANAGER_CHANGE_CODE`（管理员变更）、`CUST_BUILD_INIT`（建档）。`act_procinst_id` 为空时（简易认证无流程实例）不落表。

## 需求背景
企业授权按人（userid）维度判定，同一自然人在多家企业任职时只需一份平台级授权；企业管理员变更时，原管理员的全部授权记录需被禁用并同步把 `authed_status` 置 `N`，新管理员重新建/更新平台级授权记录。这要求一张既能表达产品维度、又能表达「授权人—企业」关系的记录表。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: authorization_agreement
evidence: db
```

```ground:field
table: authorization_agreement
fields:
  - field: authed_status
    meaning: "授权书认证状态：'Y'=已授权，'N'=未授权；DDL 默认 '0'，实测仅 N/Y 两值。平台级（platform_product_code='PLATFORM'）为 Y 即视为企业已完成授权"
    evidence: db
  - field: platform_product_code
    meaning: "授权所属产品编码；'PLATFORM' 为平台级授权书（代码常量 PLATFORM_PRODUCT_TYPE），其余为具体业务产品（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的存量授权"
    evidence: db
  - field: creation_type
    meaning: "授权书产生场景/创建类型。DB 实测 AUTO、COMPANY_MANAGER_CHANGE_CODE、CUST_BUILD_INIT；代码在管理员变更场景写入 AuthAgreementCreationTypeEnum.CHANGE_COMPANY_MANAGER.getDictKey()，建档场景写 CUST_BUILD_INIT"
    evidence: db
  - field: enable
    meaning: "记录有效标志；企业管理员发生变更时，原管理员的全部授权记录被置为 'N' 并同时把 authed_status 置 N"
    evidence: db
  - field: cust_manager_id
    meaning: "企业管理员用户 id（sys/SSO userId）；授权按人（userid）维度判定，同人多企业角色只需一份平台级授权"
    evidence: code
  - field: cust_id
    meaning: "产融侧企业 id（cust_company_info.id）"
    evidence: code
  - field: company_type
    meaning: "企业角色，一般单值（SUPPLIER/CORE/FINANCE/PROJECT_COMPANY…）；DB 存在 '[\"CORE\"]' 这类 JSON 数组形态异常值"
    evidence: db
  - field: original_cust_id
    meaning: "源系统 custId，仅存量迁移产生的授权记录有值"
    evidence: db
  - field: act_procinst_id
    meaning: "流程实例 ID；简易认证无流程实例，createAuthorizationAgreement 遇到空 actProcinstId 直接返回不落表"
    evidence: code
```

---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: cust_company_info（客户企业信息表）
page_key: table.cust_company_info
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户企业信息表
  - 企业建档信息表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication.java
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

`cust_company_info` 是授权与签署编排的主语表：它同时承载建档/认证状态（见 [[processes/cust-build-status]]）、电子签章开通状态（[[concepts/ca-cfca]]）、数据来源与补签标志位。签署编排的几乎全部硬条件（`check_status`、`need_register_ca`、`ca_register_status`、`identify_style`）都落在这张表上，见 [[calibers/offline-electronic-auth-trigger]] 与 [[rules/electronic-auth-sign-preconditions]]。

免补签判定由 `cust_source` 与 `auth_aggrement_supplement_flag` 决定：`PLATFORM_PUSH` 直接免签（[[calibers/platform-push-no-supplement]]），存量迁移需 `auth_aggrement_supplement_flag='N'` 才免签（[[calibers/migratory-no-supplement]]）。`id` / `app_no` 另被用作签署幂等与分布式锁的键组成部分，见 [[rules/sign-idempotency-and-lock]]。

## 需求背景
企业从建档、认证审核到签署授权书需要一条可追踪的状态链，并需要把「是否需要开证书/电子签章」「数据从哪来」「是否需要补签」这些与签署前置条件相关的标志位就近存放，避免跨系统实时查询。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: cust_company_info
evidence: db
```

```ground:field
table: cust_company_info
fields:
  - field: need_register_ca
    meaning: "是否需要开通电子签章（CFCA）：'Y'=需开通；与 ca_register_status 一起构成 isCaRegistered 判定"
    evidence: code
  - field: ca_register_status
    meaning: "CFCA 开通状态：'Y'=已开通；线下电子授权书签署的前置条件（若正在重开 CA，则等开通成功后链式触发签署）"
    evidence: code
  - field: need_register_bs
    meaning: "是否需要开通上上签（BestSign）：AMS 产品走 BS 通道，setSignRegister 中 AMS 会把 needRegisterBs 置 'Y'"
    evidence: code
  - field: bs_register_status
    meaning: "上上签开通状态：'Y'=已开通；AMS 产品线幂等判断依据"
    evidence: code
  - field: cust_source
    meaning: "建档数据来源（CustSourceEnum）：PLATFORM_PUSH=外部平台推送（免补签授权书）、MIGRATORY=存量迁移等"
    evidence: code
  - field: migarory_auth_aggrement_flag
    meaning: "迁移到授权书新渠道标识：存量迁移走新渠道时置 'Y'"
    evidence: code
  - field: auth_aggrement_supplement_flag
    meaning: "是否需展示/允许授权书补签：旧渠道迁移置 'Y'（需补签），新渠道置 'N'（不需补签）；updateAuthAggrementFlag 可人工翻转"
    evidence: code
  - field: identify_style
    meaning: "认证方式（IdentifyTypeConstant）：INVITE=邀请认证客户录入、INVITE_AGW=邀请认证平台录入、SELF=自主注册、SIMPLE=简易认证"
    evidence: code
  - field: cust_build_status
    meaning: "建档/认证状态（CustBuildStatusEnum）：INIT/CUST_CONFIRM_AWAIT/CUST_BUILDING/BUILD_SUCCESS/BUILD_FAIL 等"
    evidence: code
  - field: check_status
    meaning: "审核（运营中台）状态：'CUST_CHECK_PASS'=审核通过，是电子授权书签署编排的硬条件之一"
    evidence: code
  - field: sign_mode
    meaning: "产品协议签署方式（企业维度）"
    evidence: code
```

---END FILE---

---FILE: tables/tenant_setting_config.md ---
---
type: table
title: tenant_setting_config（租户设置配置表）
page_key: table.tenant_setting_config
domain: 授权协议与电子授权
status: draft
aliases:
  - 租户设置配置表
  - 租户开关表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:tenant_setting_config
  - code:ElectronicAuthLetterApplication.java
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

本表在授权主题中只承担一个职责：提供租户级灰度开关 `generate_electronic_auth_flag`，决定是否启用线下授权书电子签约版能力。开关为 `Y` 才是 [[concepts/offline-electronic-auth]] 的启用前提，也是 [[calibers/offline-electronic-auth-trigger]] 的组成条件之一；非 Y（含配置不存在、为空、查询异常）一律按关闭处理，保持现网跳过签署行为，见 [[rules/tenant-switch-off-legacy-behavior]]。

由于该开关被定义为「灰度/回退的唯一入口」，其取值语义必须是三态的失败安全设计（异常即关闭），而不是简单布尔。

## 需求背景
线下授权书电子化需按租户灰度放量，并且要能在出现问题时快速回退到「线下纸质、跳过签署」的现网行为，因此把能力开关放在租户配置表而非代码常量。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: tenant_setting_config
evidence: db
```

```ground:field
table: tenant_setting_config
fields:
  - field: generate_electronic_auth_flag
    meaning: "租户是否开启线下授权书电子签约版能力：'Y'=开启；未开启/为空/查询异常一律按关闭处理（保持现网跳过签署行为）"
    evidence: code
```

---END FILE---

---FILE: tables/cust_change_record.md ---
---
type: table
title: cust_change_record（客户变更记录表）
page_key: table.cust_change_record
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户变更记录表
  - 企业变更记录表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_record
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

`cust_change_record` 是变更类签署场景的入口证据表：只有 `alter_mode='SELF_ALTER'`（企业自行变更）且本次变更命中的变更项在允许清单内，才可能触发电子授权书签署，见 [[calibers/change-scope-self-alter-items]] 与 [[calibers/offline-electronic-auth-trigger]]。变更项通过 `alter_type_id`（逗号分隔的 `cust_change_cfg.id` 列表）反查 [[tables/cust_change_cfg]] 的 `item_code`。

## 需求背景
平台代变更（`PLAT_ALTER`）与企业自行变更（`SELF_ALTER`）在责任主体上不同，只有后者允许自动发起电子授权签署；同时并非所有变更项都涉及授权，需要通过变更项配置做白名单过滤。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: cust_change_record
evidence: db
```

```ground:field
table: cust_change_record
fields:
  - field: alter_mode
    meaning: "变更方式（AlterModeEnum）：SELF_ALTER=企业自行变更（可触发电子授权签署）、PLAT_ALTER=平台代变更"
    evidence: code
  - field: alter_type_id
    meaning: "变更项配置 id 列表（逗号分隔，对应 cust_change_cfg.id），据此反查 item_code 判断变更项是否在允许签署范围"
    evidence: code
```

---END FILE---

---FILE: tables/cust_change_cfg.md ---
---
type: table
title: cust_change_cfg（客户变更项配置表）
page_key: table.cust_change_cfg
domain: 授权协议与电子授权
status: draft
aliases:
  - 客户变更项配置表
  - 变更项字典表
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_change_cfg
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

`cust_change_cfg` 为 [[tables/cust_change_record]] 的 `alter_type_id` 提供语义：`item_code`（如 `UN0008`/`UN0012`/`UN0013`/`UN0015`/`UN0016`）是「变更项是否允许触发电子授权签署」这个白名单口径的比对值，见 [[calibers/change-scope-self-alter-items]]。

## 需求背景
变更项是配置化字典，授权签署白名单必须以编码而非 id 表达，才能在配置表数据演进时保持判定语义稳定。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的字段语义；本次分析未提供 document_claim（未证实主张）。

```ground:table
table: cust_change_cfg
evidence: db
```

```ground:field
table: cust_change_cfg
fields:
  - field: item_code
    meaning: "变更项编码，如 UN0008/UN0012/UN0013/UN0015/UN0016"
    evidence: code
```

---END FILE---

---FILE: processes/authorization-agreement-authed-status.md ---
---
type: process
title: 授权书认证状态（authorization_agreement.authed_status）
page_key: process.authorization_agreement.authed_status
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权状态机
  - 授权书认证状态流转
oid: 1
scope:
  databases: [unknown]
sources:
  - db:authorization_agreement
  - code:CustAuthAgreementDomainService.java
contract_version: "0.1"
---

该状态机描述「企业管理员—企业—产品」这一授权关系记录的有效性：`authed_status` 只有 `N`/`Y` 两态，但 `N` 有两个来源——从未授权，以及管理员变更后被禁用（`enable='N'` 同时把 `authed_status` 置 `N`）。因此读取授权状态时必须同时看 [[tables/authorization_agreement|enable 标志]]，否则会把「已被替换的旧管理员授权」误判为有效。

平台级授权（`platform_product_code='PLATFORM'`）是免补签判定的唯一依据，见 [[calibers/platform-level-authed]]；与「授权书文件」的区分见 [[concepts/authorization-agreement]]。

## 需求背景
企业授权按管理员自然人维度判定，换人时必须先废止原管理员授权、再为新管理员建立授权，才能保证「一个角色签过即全部免签」的判定既不过严（重复签署）也不过松（离职管理员仍算已授权）。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的状态与迁移；本次分析未提供 document_claim（未证实主张）。

```ground:state_machine
name: 授权书认证状态
field: authorization_agreement.authed_status
states:
  - value: "N"
    label: 未授权/待授权
    source: db_dist
  - value: "Y"
    label: 已授权
    source: db_dist
transitions:
  - from: "N"
    event: 建档通过/完善资料时的管理员认证（含简易认证直接通过）
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java#passAuthorizationAgreementDirectly"
  - from: "N"
    event: 企业管理员变更（换人），为新管理员建/更新平台级授权记录
    to: "Y"
    evidence: "code_path:CustAuthAgreementDomainService.java#changeAuthorizationAgreement"
  - from: "Y"
    event: 企业管理员变更，原管理员所有授权记录被禁用
    to: "N"
    evidence: "code_path:CustAuthAgreementDomainService.java#disabledAllAuthorizationAgreement"
```

---END FILE---

---FILE: processes/agreement-migratory-pull-status.md ---
---
type: process
title: 协议迁移拉取状态（argeement_migratory_record.status）
page_key: process.argeement_migratory_record.status
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取状态机
  - 迁移拉取状态
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
  - code:AgreementMigratoryService.java
contract_version: "0.1"
---

`status` 是布尔语义的终态标志：置 `1` 之后记录不再进入待拉取队列；「客户端确认无该协议」与「成功拉取到协议」在状态上不可区分，都表示拉取流程结束。失败路径不改变状态，而是回置 `no`（`0`）并把 `pull_num + 1`，从而由 [[calibers/pending-pull-agreement-records]] 的重试上限（默认 20）兜底。

判定待拉取记录时还需同时满足 `enable='Y'`，见 [[tables/argeement_migratory_record]]。

## 需求背景
存量协议拉取依赖客户端配合，既可能返回协议、也可能明确表示没有，还可能失败；需要一个「结束即不再打扰客户端」的终态语义，以及一个有限重试机制避免死循环拉取。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的状态与迁移；本次分析未提供 document_claim（未证实主张）。

```ground:state_machine
name: 协议迁移拉取状态
field: argeement_migratory_record.status
states:
  - value: "0"
    label: 待拉取（BooleanEnum.no）
    source: code_enum
  - value: "1"
    label: 拉取结束/不再拉取（BooleanEnum.yes；含客户端确认无此协议）
    source: code_enum
transitions:
  - from: "0"
    event: 拉取到协议并落库，或客户端返回该类型协议缺失
    to: "1"
    evidence: "code_path:AgreementMigratoryService.java#setAgreement"
  - from: "0"
    event: 拉取失败（异常/返回空），主记录回置 no 且 pullNum+1
    to: "0"
    evidence: "code_path:AgreementMigratoryService.java#setStatus"
```

---END FILE---

---FILE: processes/agreement-sign-mode.md ---
---
type: process
title: 协议签署模式（argeement_migratory_record.sign_mode）
page_key: process.argeement_migratory_record.sign_mode
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署模式取值
  - SignModeEnum 取值
oid: 1
scope:
  databases: [unknown]
sources:
  - db:argeement_migratory_record
contract_version: "0.1"
---

`sign_mode` 描述协议以何种方式签署，语义上对应 `SignModeEnum` 的三态（`NO_SIGN` / `OFF_LINE` / `ON_LINE`），DB 实测取值为 `'01'` / `'02'` / `'03'`。语义分析未给出数值与枚举成员的显式映射，因此本页只登记取值分布，不建立「数值→枚举」的确定结论（见文末 REVIEW）。

该字段与企业维度的 [[tables/cust_company_info|sign_mode]]、以及签署编排中的 `authModel=off_auth`（[[concepts/off-auth]]）不是同一层语义：前者是协议迁移记录上的签署方式，后者是企业用户在运营中台的授权模式。

## 需求背景
存量协议迁移需要保留原协议的签署方式，以便在协议重新展示或补签时区分「无需签署」「线下签署」「线上签署」三类处理路径。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的取值；数值与枚举映射待确认。本次分析未提供 document_claim（未证实主张）。

```ground:state_machine
name: 协议签署模式
field: argeement_migratory_record.sign_mode
states:
  - value: "01"
    label: 签署模式取值之一（对应 SignModeEnum 的 NO_SIGN/OFF_LINE/ON_LINE，数值映射代码未显式给出）
    source: db_dist
  - value: "02"
    label: 签署模式取值之一（同上）
    source: db_dist
  - value: "03"
    label: 签署模式取值之一（同上）
    source: db_dist
transitions: []
```

---END FILE---

---FILE: processes/cust-build-status.md ---
---
type: process
title: 客户建档/认证状态（cust_company_info.cust_build_status）
page_key: process.cust_company_info.cust_build_status
domain: 授权协议与电子授权
status: draft
aliases:
  - 建档状态机
  - 认证状态流转
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication.java
contract_version: "0.1"
---

建档状态链是授权签署编排的时序前提：`check_status='CUST_CHECK_PASS'`（审核通过）是 [[calibers/offline-electronic-auth-trigger]] 的硬条件，而审核通过即由 `CUST_BUILDING → BUILD_SUCCESS` 这一迁移产生。入口分支与 `identify_style` 强相关：邀请-客户录入/自主注册先落到待客户确认（`CUST_CONFIRM_AWAIT`），邀请-平台录入（`INVITE_AGW`）直接进入审核中（`CUST_BUILDING`）。

签署编排只接受 `identify_style ∈ {INVITE, SELF}` 的建档流程，见 [[calibers/build-scope-identify-styles]]；本状态机的状态取值与 [[tables/cust_company_info]] 的字段语义一致。

## 需求背景
企业认证需要客户与运营中台两段人工动作，状态机必须能表达「等客户确认」与「等中台审核」两种等待态，以及退回与驳回两种非通过分支，才能驱动后续签署与通知。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的状态与迁移；本次分析未提供 document_claim（未证实主张）。

```ground:state_machine
name: 客户建档/认证状态
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 待提交/初始化
    source: code_enum
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 认证审核中
    source: code_enum
  - value: BUILD_SUCCESS
    label: 认证通过
    source: code_enum
  - value: BUILD_FAIL
    label: 认证驳回
    source: code_enum
transitions:
  - from: INIT
    event: 提交（邀请-客户录入/自主注册）
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#getCustBuildStatus"
  - from: INIT
    event: 提交（邀请-平台录入 INVITE_AGW）
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户在客户端提交，进入运营中台审核
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核退回
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify"
  - from: CUST_BUILDING
    event: 运营中台审核通过
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java#updateCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核驳回
    to: BUILD_FAIL
    evidence: "code_path:CustCompanyInfoApplication.java#messageNotify"
```

---END FILE---

---FILE: calibers/platform-push-no-supplement.md ---
---
type: caliber
title: 外部推送企业免补签授权书
page_key: caliber.platform_push_no_supplement
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM_PUSH 免补签
  - 平台推送企业免签
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
---

数据来源为外部平台推送（`cust_source='PLATFORM_PUSH'`）的企业，视为授权关系已由来源系统保证，判定链路直接返回「不需签约」，不再考察 [[tables/authorization_agreement|平台级授权记录]] 或补签标志位。该口径与 [[calibers/migratory-no-supplement]] 是并列的两条免补签捷径。

## 需求背景
外部平台推送的企业不允许在产融侧再次提示补签授权书，否则会造成来源系统与产融侧授权状态不一致的重复签署。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 外部推送企业免补签授权书
predicate: "cust_company_info.cust_source = 'PLATFORM_PUSH'"
scope: "授权书补签判定（enableCompanyManagerAuthAggrement / hasCompanySignedAuthAggrement 直接返回不需签约）"
evidence: "code_path:CustAuthAgreementDomainService.java#enableCompanyManagerAuthAggrement"
```

---END FILE---

---FILE: calibers/migratory-no-supplement.md ---
---
type: caliber
title: 存量迁移企业免补签授权书
page_key: caliber.migratory_no_supplement
domain: 授权协议与电子授权
status: draft
aliases:
  - MIGRATORY 免补签
  - 存量迁移免签口径
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:cust_company_info
contract_version: "0.1"
---

存量迁移企业只有在 `auth_aggrement_supplement_flag='N'`（走新渠道、不需补签）时才免补签；旧渠道迁移会置 `'Y'` 表示需补签，且该标志可被 `updateAuthAggrementFlag` 人工翻转。因此该口径是「来源 + 标志位」的合取，与来源单一条件的 [[calibers/platform-push-no-supplement]] 不同。

## 需求背景
存量迁移分新旧渠道：走新渠道的协议已在迁移中落库，无需补签；走旧渠道的协议未能完整迁移，必须保留补签入口，故用独立标志位而非来源单一判定。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 存量迁移企业免补签授权书
predicate: "cust_company_info.cust_source = 'MIGRATORY' AND cust_company_info.auth_aggrement_supplement_flag = 'N'"
scope: "授权书补签判定"
evidence: "code_path:CustAuthAgreementDomainService.java#enableCompanyManagerAuthAggrement"
```

---END FILE---

---FILE: calibers/platform-level-authed.md ---
---
type: caliber
title: 平台级授权已完成
page_key: caliber.platform_level_authed
domain: 授权协议与电子授权
status: draft
aliases:
  - PLATFORM 授权已完成
  - 平台授权判定
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
---

判定企业/管理员是否已签署平台授权书时，只取 `platform_product_code='PLATFORM'` 且 `authed_status='Y'` 的行；由于授权按自然人（`cust_manager_id`）维度记录，同一人在多家企业任职时只需一份平台级授权即全部免签。具体产品行（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的 `Y` 表示存量系统已授权，不参与该口径。

相关术语边界见 [[concepts/platform-product-code]]，状态迁移见 [[processes/authorization-agreement-authed-status]]。

## 需求背景
若按产品逐条校验授权，同一管理员在同一企业的多个产品上会被要求重复签署；因此把「平台级」授权作为唯一免签依据，产品级记录只作为存量已授权的事实保留。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 平台级授权已完成
predicate: "authorization_agreement.platform_product_code = 'PLATFORM' AND authorization_agreement.authed_status = 'Y'"
scope: "企业/管理员是否已签署平台授权书（按人维度，一个角色签过即全部免签）"
evidence: "code_path:CustAuthAgreementDomainService.java#hasCompanySignedAuthAggrement"
```

---END FILE---

---FILE: calibers/offline-electronic-auth-trigger.md ---
---
type: caliber
title: 线下电子授权书签署触发条件
page_key: caliber.offline_electronic_auth_trigger
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签署触发条件
  - 签署编排准入门槛
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
  - db:tenant_setting_config
contract_version: "0.1"
---

这是签署编排的准入门槛：审核通过（`check_status='CUST_CHECK_PASS'`）、企业用户授权模式为线下（`auth_model='off_auth'`）、租户开关开启（[[tables/tenant_setting_config|generate_electronic_auth_flag]]='Y'）、且企业已具备 CFCA 电子签章能力（`need_register_ca='Y'` 且 `ca_register_status='Y'`）时必须全满足。企业类型与流程类型还分别有额外口径：[[calibers/allowed-company-types]]、[[calibers/build-scope-identify-styles]]、[[calibers/change-scope-self-alter-items]]。

聚合后的完整规则见 [[rules/electronic-auth-sign-preconditions]]；不满足时仅记日志跳过，不阻断主流程。

## 需求背景
电子授权书签署属于「可选的增强路径」，必须能安全地在前置条件不满足时静默跳过；同时 CA 未开通的企业需等待重开 CA 成功后链式触发签署，因此判定被设计为可重复求值的条件集合而非一次性开关。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 线下电子授权书签署触发条件
predicate: "cust_company_info.check_status = 'CUST_CHECK_PASS' AND <企业用户>.auth_model = 'off_auth' AND tenant_setting_config.generate_electronic_auth_flag = 'Y' AND cust_company_info.need_register_ca = 'Y' AND cust_company_info.ca_register_status = 'Y'"
scope: "审核回调 afterCommit 编排；不满足仅记日志跳过，不阻断主流程"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#evaluateIneligibilityReason"
```

---END FILE---

---FILE: calibers/allowed-company-types.md ---
---
type: caliber
title: 可触发电子授权签署的企业类型
page_key: caliber.allowed_company_types
domain: 授权协议与电子授权
status: draft
aliases:
  - 允许签署的企业类型
  - ALLOWED_COMPANY_TYPE_KEYS
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

签署编排只对企业角色为供应商（`SUPPLIER`）、核心企业（`CORE`）、金融机构（`FINANCE`）、项目公司（`PROJECT_COMPANY`）的企业开放。该口径与 [[calibers/offline-electronic-auth-trigger]] 是合取关系，同时使用 [[tables/cust_change_record|company_type]] 相关的角色语义。

## 需求背景
电子授权书目前只覆盖参与授信/融资主链路的四类企业角色，其余角色保持原线下流程，避免一次性扩大灰度范围。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 可触发电子授权签署的企业类型
predicate: "cust_company_info.cust_company_type ∈ {'SUPPLIER','CORE','FINANCE','PROJECT_COMPANY'}"
scope: "电子授权书签署编排"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#ALLOWED_COMPANY_TYPE_KEYS"
```

---END FILE---

---FILE: calibers/build-scope-identify-styles.md ---
---
type: caliber
title: 建档类签署仅限邀请/自主录入
page_key: caliber.build_scope_identify_styles
domain: 授权协议与电子授权
status: draft
aliases:
  - CHECK 分支认证方式白名单
  - ALLOWED_BUILD_IDENTIFY_STYLES
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_company_info
contract_version: "0.1"
---

在 `processType=CHECK`（建档类）分支中，只有认证方式为 `INVITE`（邀请认证-客户录入）或 `SELF`（自主注册）才允许发起电子授权签署；`INVITE_AGW`（平台录入）与 `SIMPLE`（简易认证）不进入该分支。该口径与 [[calibers/offline-electronic-auth-trigger]] 共同作用，状态来源见 [[processes/cust_build_status]]。

## 需求背景
邀请-平台录入在企业侧天然对应线下签署流程，简易认证则无流程实例（`act_procinst_id` 为空不落授权记录），二者均不适合走线上电子签署编排。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 建档类签署仅限邀请/自主录入
predicate: "cust_company_info.identify_style ∈ {'INVITE','SELF'}"
scope: "processType=CHECK 分支"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#ALLOWED_BUILD_IDENTIFY_STYLES"
```

---END FILE---

---FILE: calibers/change-scope-self-alter-items.md ---
---
type: caliber
title: 变更类签署仅限企业自行变更且变更项命中
page_key: caliber.change_scope_self_alter_items
domain: 授权协议与电子授权
status: draft
aliases:
  - CHANGE 分支准入
  - 变更项白名单
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
  - db:cust_change_record
  - db:cust_change_cfg
contract_version: "0.1"
---

`processType=CHANGE` 分支要求变更方式为企业自行变更（`alter_mode='SELF_ALTER'`），且 `alter_type_id` 反查 [[tables/cust_change_cfg|item_code]] 命中 `UN0016`/`UN0012`/`UN0013`/`UN0008`/`UN0015` 之一。平台代变更（`PLAT_ALTER`）与未命中的变更项不触发签署，见 [[calibers/offline-electronic-auth-trigger]]。

## 需求背景
只有企业自行发起的、且涉及授权要件的变更项才需要重新出具电子授权书；平台代变更与不涉及授权的变更项重复签署无业务意义。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 变更类签署仅限企业自行变更且变更项命中
predicate: "cust_change_record.alter_mode = 'SELF_ALTER' AND cust_change_cfg.item_code ∈ {'UN0016','UN0012','UN0013','UN0008','UN0015'}"
scope: "processType=CHANGE 分支"
evidence: "code_path:CustAuthSignOrchestrationApplication.java#isAllowedChangeScenario"
```

---END FILE---

---FILE: calibers/pending-pull-agreement-records.md ---
---
type: caliber
title: 待拉取协议记录
page_key: caliber.pending_pull_agreement_records
domain: 授权协议与电子授权
status: draft
aliases:
  - 协议拉取扫描口径
  - pull 捞取条件
oid: 1
scope:
  databases: [unknown]
sources:
  - code:AgreementMigratoryService.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

定时任务捞取待拉取记录的条件是「未结束 + 有效 + 未超重试上限」：`status='0'`、`enable='Y'`、`pull_num < 20`（20 为配置 `cust.agreemeent.pull.num` 默认值）。失败一次 `pull_num` 自增 1，因此记录在有限次尝试后自然退出扫描集合。状态语义见 [[processes/agreement-migratory-pull-status]]，字段释义见 [[tables/argeement_migratory_record]]。

## 需求背景
客户端可能长期无法返回某类协议，若无限重试会持续占用定时任务容量；用次数上限把「一直失败」的记录自然淘汰，同时用 `status` 终态区分「已确认无此协议」。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 待拉取协议记录
predicate: "argeement_migratory_record.status = '0' AND argeement_migratory_record.enable = 'Y' AND argeement_migratory_record.pull_num < 20"
scope: "协议拉取定时任务（20 为 cust.agreemeent.pull.num 默认值）"
evidence: "code_path:AgreementMigratoryService.java#pull"
```

---END FILE---

---FILE: calibers/ams-bs-channel.md ---
---
type: caliber
title: AMS 走 BS/上上签通道
page_key: caliber.ams_bs_channel
domain: 授权协议与电子授权
status: draft
aliases:
  - AMS 走上上签
  - BS_Auth 与 CFCA_Auth 分流
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
  - db:cust_company_info
contract_version: "0.1"
---

协议类型与签署机构按产品分流：`platform_product_code='AMS'` 时 `agreement_type='BS_Auth'`、签署机构取 `BEST_SIGN`；其他产品取 `CFCA_Auth`，签署机构为 `PAPER_LESS`。这与开通状态字段相呼应——AMS 用 `need_register_bs`/`bs_register_status`，其余产品用 `need_register_ca`/`ca_register_status`，两者在 `openCa` 中互斥判断，术语边界见 [[concepts/ca-cfca]]。

## 需求背景
AMS 产品线使用上上签（BestSign）作为签署渠道，其余产品线使用 CFCA，因此协议迁移初始化与签署机构选择必须按产品分派。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: AMS 走 BS/上上签通道
predicate: "argeement_migratory_record.platform_product_code = 'AMS' → agreement_type = 'BS_Auth'；其他产品 → agreement_type = 'CFCA_Auth'"
scope: "协议迁移初始化与签署机构选择（BEST_SIGN vs PAPER_LESS）"
evidence: "code_path:PlatFormMigratoryApplication.java#getCaAgreement"
```

---END FILE---

---FILE: calibers/migratory-init-five-agreements.md ---
---
type: caliber
title: 迁移初始化五类协议
page_key: caliber.migratory_init_five_agreements
domain: 授权协议与电子授权
status: draft
aliases:
  - 迁移初始化协议类型清单
  - setAgreementMigratory
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
contract_version: "0.1"
---

迁移初始化会为每个客户 × 每个产品生成五类待拉取协议记录：认证类协议（`CFCA_Auth` 或 `BS_Auth`，按 [[calibers/ams-bs-channel]] 分流）、产品协议、`CustPersonLicense`、`UserProtocol`、`PrivacyPolicy`。去重以「该 custId + productCode + type 的记录计数为 0」为条件，避免重复插入；写入后进入 [[calibers/pending-pull-agreement-records]] 描述的拉取流程。

## 需求背景
协议在客户端侧按类型分散存放，迁移必须按类型逐项拉取才能完整还原客户已签署的协议集合，去重条件保证初始化可重入。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的口径；本次分析未提供 document_claim（未证实主张）。

```ground:caliber
name: 迁移初始化五类协议
predicate: "argeement_migratory_record.agreement_type IN ('CFCA_Auth'|'BS_Auth', 产品协议, 'CustPersonLicense', 'UserProtocol', 'PrivacyPolicy')"
scope: "每个客户×每个产品各生成一条待拉取记录（按 custId+productCode+type 计数为 0 才插入）"
evidence: "code_path:PlatFormMigratoryApplication.java#setAgreementMigratory"
```

---END FILE---

---FILE: concepts/authorization-agreement.md ---
---
type: concept
title: 授权书
page_key: concept.authorization_agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 授权确认书
  - 授权协议
  - 客户管理员授权认证
  - 企业授权书
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
maps_to: "authorization_agreement（表注释：授权确认书表）——记录企业管理员是否完成平台/产品级授权，authed_status=Y 视为已授权"
field_targets:
  - authorization_agreement.authed_status
  - authorization_agreement.platform_product_code
  - authorization_agreement.cust_manager_id
adjudication: boundary
also_confused_with:
  - 线下电子授权书（OfflineElectronicAuth 协议文件）
  - 平台协议文本（用户协议/隐私政策）
boundary: "authorization_agreement 是「谁授过权」的关系记录；线下电子授权书是「授权书这一份文件」的生成与签章，二者通过 cust_id 关联但生命周期不同"
---

「授权书」在业务对话中指关系事实而非文件：它回答「某管理员是否已代表某企业完成授权」，落在 [[tables/authorization_agreement]]，以 `authed_status='Y'` 表达已授权，判定口径见 [[calibers/platform-level-authed]]，状态流转见 [[processes/authorization-agreement-authed-status]]。

最常见的混淆是把「授权书」等同于 [[concepts/offline-electronic-auth]]（一份被签署并上传影像的合同文件），或者等同于 [[concepts/agreement]]（用户协议/隐私政策这类平台协议文本）。二者的边界是：本术语不含文件落库、不含签署模式，只有授权关系与生效标志；文件的生命周期、开关控制与签署动作在电子授权书术语下描述。

## 需求背景
企业授权按人（userid）维度判定，同一自然人的多企业角色只需一份平台级授权；为避免与「授权书文件」「平台协议文本」混用，需要把关系记录这一层语义单独命名。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: concepts/agreement.md ---
---
type: concept
title: 协议
page_key: concept.agreement
domain: 授权协议与电子授权
status: draft
aliases:
  - 用户协议
  - 隐私政策
  - 产品协议
  - CA 协议
  - BS 协议
oid: 1
scope:
  databases: [unknown]
sources:
  - code:PlatFormMigratoryApplication.java
  - db:argeement_migratory_record
contract_version: "0.1"
maps_to: "argeement_migratory_record（协议迁移记录）+ 底层 BaseContractProvider/IContractInfoProvider 维护的合同表；agreement_type 取 AgreementDocType"
field_targets:
  - argeement_migratory_record.agreement_type
  - argeement_migratory_record.sign_mode
  - argeement_migratory_record.agreement_path
  - argeement_migratory_record.agreement_no
adjudication: boundary
also_confused_with:
  - 授权书
boundary: "协议是文本文件与签署事实（含 sign_mode、agreement_path、agreement_no）；授权书是管理员授权状态记录，不含文件落库"
---

「协议」指客户与平台/机构之间签署的文本及其签署事实：类型由 `AgreementDocType` 给出（`BS_Auth`/`CFCA_Auth`/产品协议/`CustPersonLicense`/`UserProtocol`/`PrivacyPolicy`），迁移记录落在 [[tables/argeement_migratory_record]]，文件路径与编号由 `agreement_path`/`agreement_no` 承载，清单见 [[calibers/migratory_init_five_agreements]]，签署方式取值见 [[processes/agreement_sign_mode]]。

与 [[concepts/authorization-agreement]] 的边界是：协议有文件、有签署模式、有拉取与判重；授权书只有「谁授过权」的关系状态。日常称为「CA 协议」「BS 协议」时指的是签署机构维度上的协议类型，仍属本术语。

## 需求背景
协议集合按产品与类型分散存放于客户端，迁移与展示都需要一个统一的「协议」概念来承载类型、文件与签署事实，故与授权关系记录分离命名。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: concepts/offline-electronic-auth.md ---
---
type: concept
title: 线下电子授权书
page_key: concept.offline_electronic_auth
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签约版授权书
  - OfflineElectronicAuth
oid: 1
scope:
  databases: [unknown]
sources:
  - code:ElectronicAuthLetterApplication.java
  - code:CustAuthSignOrchestrationApplication.java
  - db:tenant_setting_config
contract_version: "0.1"
maps_to: "预览接口生成的 OfflineElectronicAuth ON_LINE 合同，由 custDocFacade.signOfflineElectronicAuthAndUpload 签署并上传影像 A0050；是否启用由 tenant_setting_config.generate_electronic_auth_flag 控制"
field_targets:
  - tenant_setting_config.generate_electronic_auth_flag
adjudication: boundary
also_confused_with:
  - authorization_agreement 授权记录
  - 线下纸质授权书（现网 OFF_AUTH 直接跳过签署）
boundary: "开关为 N 时该方法直接返回 true（保持现网线下纸质行为），不会产生电子合同"
---

「线下电子授权书」指线下授权场景中由系统生成、电子签章并上传影像的那份文件（`OfflineElectronicAuth`，`ON_LINE` 合同）。启用前提是租户开关 `generate_electronic_auth_flag='Y'`，见 [[rules/tenant-switch-off-legacy-behavior]]；触发条件见 [[calibers/offline-electronic-auth-trigger]]，幂等控制见 [[rules/sign-idempotency-and-lock]]。

与 [[concepts/authorization-agreement]] 的边界：本术语关注文件的生成、签署与影像上传；授权记录只表达授权状态。与「线下纸质授权书」的边界在于开关未开启时流程直接返回成功、不产生任何电子合同，即保持现网行为。

## 需求背景
线下签署的授权书需要电子化，以便留痕与归档；但电子化必须可灰度、可回退，因此文件生成与签署被包裹在租户开关与前置条件判定之后。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: concepts/off-auth.md ---
---
type: concept
title: 线下授权（off_auth）
page_key: concept.off_auth
domain: 授权协议与电子授权
status: draft
aliases:
  - OFF_AUTH
  - 线下签署模式
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
maps_to: "CustEnterpriseUserDTO.authModel = AuthModel.OFF_AUTH.getCode()（代码注释与日志字面为 off_auth），签署编排的硬条件之一"
field_targets: []
adjudication: boundary
also_confused_with:
  - 线上签署（on_auth）
  - 邀请认证-平台录入（业务上必然线下签署）
boundary: "authModel 是企业用户在运营中台的授权模式；与企业建档方式 identify_style 正交"
---

`off_auth` 是企业用户在运营中台的授权模式取值，作为 [[calibers/offline-electronic-auth-trigger]] 的硬条件之一出现在签署编排中（代码注释与日志字面为 `off_auth`）。

它与 [[tables/cust_company_info|identify_style]]（建档方式）正交：即使业务上「邀请认证-平台录入」往往伴随线下签署，也仍然是两个不同维度，不能互相替代判定；建档分支的白名单见 [[calibers/build-scope-identify-styles]]。

## 需求背景
只有线下授权模式的企业才需要线下授权书的电子化替代方案，线上签署企业走各自既有通道，故编排以 `authModel` 作为分流条件。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: concepts/ca-cfca.md ---
---
type: concept
title: CA / CFCA
page_key: concept.ca_cfca
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子签章
  - 数字证书
  - PAPER_LESS
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustCompanyInfoApplication.java
  - db:cust_company_info
  - db:argeement_migratory_record
contract_version: "0.1"
maps_to: "cust_company_info.need_register_ca / ca_register_status；非 AMS 产品走 CFCA（SignAgencyTransferEnum.PAPER_LESS），协议类型 DATA_SOURCE_CFCA_AUTH"
field_targets:
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
adjudication: boundary
also_confused_with:
  - 上上签 / BS（BEST_SIGN）
boundary: "AMS 产品走 BS：need_register_bs / bs_register_status、协议类型 BS_Auth、签署机构 BEST_SIGN；两者开通过程在 openCa 中互斥判断"
---

「CA / CFCA」指产融侧为线下授权书签署准备的电子签章能力：是否需开通由 `need_register_ca` 表达，是否已开通由 `ca_register_status` 表达，二者同时为 `'Y'` 才满足 [[calibers/offline-electronic-auth-trigger]] 的证书前置条件。若企业正在重开 CA，则等开通成功后链式触发签署。

与「上上签 / BS」的边界见 [[calibers/ams-bs-channel]]：AMS 产品走 `BS_Auth`/`BEST_SIGN`，其余产品走 `CFCA_Auth`/`PAPER_LESS`，开通过程在 `openCa` 中互斥判断，因此两个术语不能混用。

## 需求背景
不同产品线的签署渠道不同，电子签章能力的开通状态必须逐渠道记录，才能保证签署编排在「渠道开通中」时安全等待而非误判为不具备条件。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: concepts/platform-product-code.md ---
---
type: concept
title: 平台产品编码 PLATFORM
page_key: concept.platform_product_code
domain: 授权协议与电子授权
status: draft
aliases:
  - 平台级授权书
  - PLATFORM_PRODUCT_TYPE
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthAgreementDomainService.java
  - db:authorization_agreement
contract_version: "0.1"
maps_to: "authorization_agreement.platform_product_code = 'PLATFORM'，表示平台级授权而非某个业务产品的存量授权"
field_targets:
  - authorization_agreement.platform_product_code
adjudication: boundary
also_confused_with:
  - 业务产品编码（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）
boundary: "是否补签只看 PLATFORM 行；具体产品行的 Y 表示存量系统已授权，用于免补签判定"
---

`PLATFORM`（代码常量 `PLATFORM_PRODUCT_TYPE`）是 [[tables/authorization_agreement]] 中 `platform_product_code` 的一个特殊取值，标记该行为平台级授权。是否已授权、是否需要补签只考察该行，见 [[calibers/platform-level-authed]]。

与业务产品编码（ACFLOW/AMS/ORDER/RVSFACTOR_PC…）的边界：产品行的 `authed_status='Y'` 表示存量系统已授权，用于免补签判定，但不代表平台级授权已完成。混用两者会导致对企业重复要求签署。

## 需求背景
存量系统的授权记录按产品分散，而平台级授权是唯一免签依据，因此需要用同一字段上的特殊取值区分两个层级，避免新增冗余字段。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的术语桥接；本次分析未提供 document_claim（未证实主张）。

---END FILE---

---FILE: rules/electronic-auth-sign-preconditions.md ---
---
type: rule
title: 电子授权书签署编排前置条件（全满足才签署）
page_key: rule.electronic_auth_sign_preconditions
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署准入规则
  - evaluateIneligibilityReason
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

该规则把分散的准入口径聚合为一次求值：审核通过、线下授权模式、租户开关开启、企业类型在白名单、流程类型命中（建档的邀请/自主录入，或企业自行变更且变更项命中）、且 CFCA 已开通。任一不满足仅记日志跳过，不阻断 `CustSyncEventProcessor` 主流程；CA 未开通时等待重开 CA 成功后链式触发。

引用的口径页：[[calibers/offline-electronic-auth-trigger]]、[[calibers/allowed-company-types]]、[[calibers/build-scope-identify-styles]]、[[calibers/change-scope-self-alter-items]]；幂等与并发见 [[rules/sign-idempotency-and-lock]]。

## 需求背景
电子签署是增强路径，必须在任何前置条件缺失时安全跳过，并允许在 CA 开通等异步条件补齐后重新求值，因此被设计为「条件集合 + 不阻断主流程」的规则。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则；本次分析未提供 document_claim（未证实主张）。

```ground:rule
name: 电子授权书签署编排前置条件（全满足才签署）
content: "checkStatus=CUST_CHECK_PASS；企业用户 authModel=off_auth；租户 generate_electronic_auth_flag=Y；企业类型 ∈{SUPPLIER,CORE,FINANCE,PROJECT_COMPANY}；流程为建档（identifyStyle ∈{INVITE,SELF}）或企业自行变更（alterMode=SELF_ALTER 且变更项命中 UN0016/UN0012/UN0013/UN0008/UN0015）；need_register_ca=Y 且 ca_register_status=Y。任一不满足仅记日志跳过。"
impact: "不阻断 CustSyncEventProcessor 主流程；CA 未开通时等待重开 CA 成功后链式触发"
field_targets:
  - cust_company_info.check_status
  - cust_company_info.need_register_ca
  - cust_company_info.ca_register_status
  - cust_company_info.identify_style
  - cust_change_record.alter_mode
  - cust_change_cfg.item_code
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code_path:CustAuthSignOrchestrationApplication.java#evaluateIneligibilityReason"
```

---END FILE---

---FILE: rules/sign-idempotency-and-lock.md ---
---
type: rule
title: 签署幂等与并发控制
page_key: rule.sign_idempotency_and_lock
domain: 授权协议与电子授权
status: draft
aliases:
  - 签署幂等规则
  - executeOfflineElectronicAuthSignSafely
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CustAuthSignOrchestrationApplication.java
contract_version: "0.1"
---

签署动作以已完成标记 + 分布式锁双重保护：`cust_auth_sign_done:{sourceMainId}:{appNo}` 表示该单据已签署完成，`cust_auth_sign_after_audit:{sourceMainId}:{appNo}` 为审核后签署的 Redis 分布式锁（获取超时默认 1000ms、锁超时默认 120000ms）。签署成功才写 done 标记，失败仅记日志。键来源见 [[tables/cust_company_info]]（`id` / `app_no`）。

## 需求背景
审核回调可能重复或并发触发，签署是不可逆的对外动作（[[concepts/offline-electronic-auth]]），因此必须幂等；同时签署失败不得回滚审核主流程，故失败只记日志而不抛出。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则；本次分析未提供 document_claim（未证实主张）。

```ground:rule
name: 签署幂等与并发控制
content: "以 cust_auth_sign_done:{sourceMainId}:{appNo} 作为已完成标记，以 cust_auth_sign_after_audit:{sourceMainId}:{appNo} 做 Redis 分布式锁（默认获取超时 1000ms、锁超时 120000ms）；签署成功才写 done 标记，失败仅记日志。"
impact: "重复回调/并发回调不会重复签署；签署失败不回滚审核主流程"
field_targets:
  - cust_company_info.id
  - cust_company_info.app_no
evidence: "code_path:CustAuthSignOrchestrationApplication.java#executeOfflineElectronicAuthSignSafely"
```

---END FILE---

---FILE: rules/tenant-switch-off-legacy-behavior.md ---
---
type: rule
title: 租户开关关闭时保持现网行为
page_key: rule.tenant_switch_off_legacy_behavior
domain: 授权协议与电子授权
status: draft
aliases:
  - 电子授权开关回退规则
  - isGenerateElectronicAuth
oid: 1
scope:
  databases: [unknown]
sources:
  - code:ElectronicAuthLetterApplication.java
  - db:tenant_setting_config
contract_version: "0.1"
---

当租户开关 `generate_electronic_auth_flag` 非 `Y`——包括配置不存在、值为空、以及查询异常——`signOfflineElectronicAuthOnLine` 直接返回 `true`，既不做 CFCA 校验也不发起签署，从而保持现网线下纸质授权行为。该规则是 [[concepts/offline-electronic-auth]] 的失败安全设计，同时构成 [[calibers/offline-electronic-auth-trigger]] 的一部分。

## 需求背景
电子签署能力需要可灰度、可一键回退；把「配置缺失/查询异常」与「显式关闭」归为同一结果，避免依赖故障导致误发起签署。

## 版本演进
v0 初稿：仅收录语义分析中已有证据的规则。该条证据在语义分析中被截断（`code_path:ElectronicAuthLetterApplication.java#isGenerateElectronicA`），精确方法名待补全，见文末 REVIEW。

```ground:rule
name: 租户开关关闭时保持现网行为
content: "tenant_setting_config.generate_electronic_auth_flag 非 Y（含配置不存在、为空、查询异常）时，signOfflineElectronicAuthOnLine 直接返回 true，不做 CFCA 校验也不发起签署。"
impact: "开关是灰度/回退的唯一入口"
field_targets:
  - tenant_setting_config.generate_electronic_auth_flag
evidence: "code_path:ElectronicAuthLetterApplication.java#isGenerateElectronicA"
```

---END FILE---

---REVIEW: process | 协议签署模式（argeement_migratory_record.sign_mode）---
语义分析只给出「`sign_mode` 语义对应 `SignModeEnum` 三态（NO_SIGN / OFF_LINE / ON_LINE）」与「DB 实存 `'01'`/`'02'`/`'03'`」，未给出数值与枚举成员的显式映射。当前页面仅登记取值分布，未建立 01→? 的确定结论。
待确认项：
1. `'01'` / `'02'` / `'03'` 分别对应 NO_SIGN / OFF_LINE / ON_LINE 的哪一项（需代码中的映射常量或字典配置证据）。
2. 该字段与企业维度 `cust_company_info.sign_mode` 是否使用同一枚举、取值域是否一致。
3. 是否存在 `'00'` 或其他历史取值（当前证据只覆盖 db_dist 的三个值）。
---END REVIEW---

---REVIEW: rule | 租户开关关闭时保持现网行为---
语义分析中该规则的 evidence 字符串被截断为 `code_path:ElectronicAuthLetterApplication.java#isGenerateElectronicA`，方法名不完整；但 content / impact / field_targets 三项内容完整且相互一致，故仍按原样登记，不做补全。
待确认项：
1. `isGenerateElectronicA…` 的完整方法名（推测为 `isGenerateElectronicAuth` 一类，未证实）。
2. 该「非 Y 一律按关闭」逻辑是否也覆盖 `cust_company_info` 侧的读取路径。
---END REVIEW---

---REVIEW: table | scope.databases 物理库名---
语义分析未提供任何表所属的物理库名（仅给出逻辑表名），因此所有 table 页的 `scope.databases` 暂填 `unknown`。若契约流水线要求真实物理库名，需要在语义分析阶段补充 `db: <物理库名>` 证据后再回填，避免凭业务命名推断。
待确认项：
1. `argeement_migratory_record` / `authorization_agreement` / `cust_company_info` / `tenant_setting_config` / `cust_change_record` / `cust_change_cfg` 的物理库名与是否同库。
2. `cust_change_record`、`cust_change_cfg` 是否与 `cust_company_info` 同库（影响跨库 JOIN 的可行性描述）。
---END REVIEW---