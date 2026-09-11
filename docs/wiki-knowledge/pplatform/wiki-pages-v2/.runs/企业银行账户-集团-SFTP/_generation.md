---FILE: tables/cust_account_info.md ---
---
type: table
title: cust_account_info 企业银行账户表
page_key: tables/cust_account_info
domain: 企业银行账户
status: draft
aliases: [客户账号信息, 企业银行账户信息]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java
contract_version: "0.1"
---

`cust_account_info` 是企业银行账户主表，承载账号、户名、开户行、认证状态与打款计数等要素，是「企业—银行账户」一对多关系的落地表。账户的真实性通过人行小额打款（CNAPS）验证：先申请打款，再回填金额验证，状态流转见 [[processes/account-cnaps-payment-auth-state]]。其中唯一的默认还款账户口径见 [[calibers/default-repayment-account]]。

## 需求背景

企业完成建档后需绑定银行账户用于资金动作（还款代扣等），因此需要一张账户表同时解决三件事：账户归属（[[concepts/account-owner-company]]）、账户真实性认证（[[calibers/account-payment-auth-passed]]）、默认账户唯一性（[[rules/default-account-unique]]）。打款申请上送的账号/户名/银行名称与联行号存在字段复用，边界见 [[concepts/bank-no]]；账户类型的真实取值集与代码枚举基线不一致，见 [[concepts/account-type]]。新增账户受 [[rules/account-no-unique-per-company]] 约束。

## 版本演进

v0 契约按现状固化：认证状态由 [[processes/account-cnaps-payment-auth-state]] 定义为 APPLY_00 / APPLY_10 / APPLY_20 / APPLY_30 / APPLY_40 五态，DB 默认 APPLY_00；`account_type` 代码枚举基线未覆盖实测存在的 OPERATION_FEE_ACCOUNT，待后续版本补齐；`bank_branch_name` 目前不参与打款申请链路。全表通用逻辑删除口径为 enable = 'Y'（见 [[calibers/valid-record-enable-y]]）。

## 字段语义锚点

```ground:fields
table: cust_account_info
fields:
  - field: account_no
    meaning: 企业银行账户账号（打款验证/默认还款账号载体）
    evidence: db
  - field: account_name
    meaning: 账户名称（户名），打款申请上送 accountName
    evidence: db
  - field: account_type
    meaning: 账户类型，DB 默认 BANK；实测另有 OPERATION_FEE_ACCOUNT（运营费账户），为代码枚举基线外的真实取值
    evidence: db
  - field: bank_no
    meaning: 联行号；代码中同时作为 bankID 与 cnapsCode 上送人行小额打款接口（bankNo 一值两用）
    evidence: code
  - field: bank_code / bank_code_name
    meaning: 银行(总行)代码/名称；申请打款时 bank_code_name 被当作请求 bankName 上送
    evidence: code
  - field: bank_branch_name
    meaning: 开户行网点名称，打款申请链路未使用
    evidence: db
  - field: default_account_flag
    meaning: 是否默认账户，'1'=默认，'0'=非默认；同企业下默认账号需唯一
    evidence: db
  - field: auth_state
    meaning: 小额打款认证状态，DB 默认 APPLY_00，代码取值 APPLY_00/10/20/30/40
    evidence: code
  - field: trans_id
    meaning: 打款申请交易ID（发起时写入银行返回的 OriginalTxSN，查询/验证均以它为准）
    evidence: code
  - field: trace_no
    meaning: 银行系统跟踪号（申请打款返回）
    evidence: code
  - field: payment_remaining_count
    meaning: 剩余打款次数，初始取 cust_setting_config.payment_maximum_number，每次申请 -1
    evidence: code
  - field: error_try_count
    meaning: 打款金额验证失败次数，失败时累加
    evidence: code
  - field: error_try_time
    meaning: 最后一次验证失败时间
    evidence: code
  - field: ref_cust_company_info
    meaning: 账户归属企业标识，存的是 cust_company_info.code（企业编码），不是企业主键 id
    evidence: code
  - field: status
    meaning: 账户状态，实测仅 INIT
    evidence: db
```
---END FILE---

---FILE: tables/cust_group_rel.md ---
---
type: table
title: cust_group_rel 集团成员单位关系表
page_key: tables/cust_group_rel
domain: 企业集团关系
status: draft
aliases: [集团成员单位关系, 集团关系表]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java
contract_version: "0.1"
---

`cust_group_rel` 用一行一关系的方式描述企业集团树：一行代表一个「父/根—成员单位」关系记录，树形结构由 `parent_group_id` / `root_group_id`（关系记录主键）与 `parent_cust_id` / `root_cust_id`（企业 id）两组字段共同定位。成员单位关系的状态流转见 [[processes/cust-group-rel-status-state]]，已生效口径见 [[calibers/effective-group-member]]。

## 需求背景

集团客户场景需要把多个独立企业组织为一棵树，并对成员关系做准入与生命周期管理：新增子级、发送签署待办、签署/拒绝、运营端直接生效、集团解散等。根节点识别口径见 [[calibers/group-root-node]] 与 [[concepts/root-flag]]；企业角色字段的实际存储形态见 [[concepts/cust-type]]；重复关联拦截见 [[rules/group-rel-uniqueness]]；集团解散前置校验见 [[rules/root-group-delete-check]]。待办发送以企业建档成功为前置，见 [[calibers/company-build-success]]。

## 版本演进

v0 契约按现状固化。`cust_type` 的库注释描述为「多企业角色用逗号分隔」，代码实际统一以 JSON 数组字符串存取并追加多角色，库注释已成为历史描述，见 [[concepts/cust-type]]。`level` 实测仅 1（根节点），层级字段尚未被真实使用。

## 字段语义锚点

```ground:fields
table: cust_group_rel
fields:
  - field: cust_id
    meaning: 成员单位企业id（cust_company_info.id）
    evidence: db
  - field: parent_group_id / root_group_id
    meaning: 父/根 关系记录主键（cust_group_rel.id），树形结构靠它组织
    evidence: code
  - field: parent_cust_id / root_cust_id
    meaning: 父/根 企业id（cust_company_info.id）
    evidence: code
  - field: root_flag
    meaning: 是否集团根节点，Y=集团本身，N=成员单位
    evidence: db
  - field: level
    meaning: 层级，实测仅 1（根节点）
    evidence: db
  - field: cust_type
    meaning: 企业角色，实际存 JSON 数组字符串（如 ["SUPPLIER"]），支持追加多角色
    evidence: code
  - field: status
    meaning: 成员单位关系状态 EFFECTIVE/INEFFECTIVE/REJECTED
    evidence: db
```
---END FILE---

---FILE: tables/cust_sftp.md ---
---
type: table
title: cust_sftp SFTP 渠道配置表
page_key: tables/cust_sftp
domain: SFTP渠道对接
status: draft
aliases: [SFTP 配置, 渠道 SFTP 配置]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
---

`cust_sftp` 保存各对接渠道的 SFTP 服务器配置与登录账号，是渠道文件交换的接入元数据表：一行对应一个渠道（或渠道的某套测试配置）的 SFTP 账号。启用口径见 [[calibers/enabled-sftp-channel]]，字段混淆边界见 [[concepts/sftp-channel]]。

## 需求背景

不同渠道（如 bgy / tianma / meituan / sny）的文件交互独立开设 SFTP 账号，账号命名形如 `app_<渠道>_<日期/编号>`，服务器以 qa.sftp.lls.com:22 为主、个别为 uat.sftp.lls.com。渠道编码与数据租户标识是两个不同来源的概念，统计与排障时不可互相替代。

## 版本演进

v0 契约按现状固化。本页字段语义均来自 DB 实测，暂无代码侧写值证据；`enable` 实测全部为 'Y'，是否存在失效配置需后续数据核对后再补充演进说明。

## 字段语义锚点

```ground:fields
table: cust_sftp
fields:
  - field: channel
    meaning: SFTP 对接渠道编码（如 bgy/tianma/meituan/sny）
    evidence: db
  - field: user_name
    meaning: SFTP 登录账号，命名形如 app_<渠道>_<日期/编号>
    evidence: db
  - field: host / port
    meaning: SFTP 服务器地址与端口，实测 qa.sftp.lls.com:22 为主、个别 uat.sftp.lls.com
    evidence: db
  - field: db_tenant_code
    meaning: 所属数据租户标识
    evidence: db
```
---END FILE---

---FILE: processes/account-cnaps-payment-auth-state.md ---
---
type: process
title: 银行账户小额打款认证状态机
page_key: processes/account-cnaps-payment-auth-state
domain: 企业银行账户
status: draft
aliases: [CNAPS 打款认证流程, auth_state 状态机]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java
contract_version: "0.1"
---

本流程描述企业银行账户（[[tables/cust_account_info]]）通过人行小额打款完成真实性认证的完整状态流转：申请打款 → 银行受理 → 金额验证。字段 `auth_state` 的五态取值与迁移条件是账户认证能力的核心契约，被 [[calibers/account-payment-auth-passed]]、[[rules/payment-confirm-precondition]]、[[rules/payment-fail-count]] 直接引用。

## 需求背景

账户真实性无法在录入时判断，必须由银行侧发起一笔小额打款、企业侧回填收到的金额来验证账户可用。因此系统需要记录「是否已发起」「银行是否受理」「验证结果」三类事实，并对验证动作施加时序约束（未申请不能验、未受理不能验、受理失败需重新申请）。剩余次数与失败次数用于限制试探，见 [[rules/payment-count-quota]]；金额范围与单位换算见 [[rules/payment-amount-range]]；打款交易标识的取值来源见 [[concepts/trans-id-vs-trace-no]]。

## 版本演进

v0 契约按现状固化，五态基线来自代码枚举。需注意两处与直觉不一致的现行行为：(1) 银行受理失败后可无前置状态校验地直接重新申请，属于覆盖式回退；(2) 金额不匹配或银行库无记录时同样落 APPLY_40 并累加失败次数后抛异常，故 APPLY_40 不能单独作为「验证通过」口径。

## 状态与迁移锚点

```ground:state_machine
name: 银行账户小额打款认证状态机
field: cust_account_info.auth_state
states:
  - value: APPLY_00
    label: 初始/未发起打款
    source: code_enum
  - value: APPLY_10
    label: 打款申请已提交，银行受理中
    source: code_enum
  - value: APPLY_20
    label: 银行受理成功，可进行金额验证
    source: code_enum
  - value: APPLY_30
    label: 申请打款受理失败，需重新申请
    source: code_enum
  - value: APPLY_40
    label: 已完成打款验证（金额一致，或验证不匹配/库无记录时也落该值）
    source: code_enum
transitions:
  - from: APPLY_00
    event: 申请打款 cnapsPaymentApply()
    to: APPLY_10
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply
  - from: APPLY_10
    event: 查询打款结果 paymentResult() 返回 status=20
    to: APPLY_20
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult
  - from: APPLY_10
    event: 查询打款结果 paymentResult() 返回 status=30
    to: APPLY_30
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:paymentResult
  - from: APPLY_20
    event: 打款验证 cnapsPaymentConfirm() 金额一致 result=0
    to: APPLY_40
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm
  - from: APPLY_20
    event: 打款验证 cnapsPaymentConfirm() 金额不匹配/库无记录 result=1|2（同时 error_try_count+1、error_try_time=now 后抛业务异常）
    to: APPLY_40
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentConfirm
  - from: APPLY_30
    event: 重新申请打款 cnapsPaymentApply()（无前置状态校验，直接覆盖）
    to: APPLY_10
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustAccountApplication.java:cnapsPaymentApply
```
---END FILE---

---FILE: processes/cust-group-rel-status-state.md ---
---
type: process
title: 集团成员单位关系状态机
page_key: processes/cust-group-rel-status-state
domain: 企业集团关系
status: draft
aliases: [成员单位生效流程, cust_group_rel.status 状态机]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java
contract_version: "0.1"
---

本流程描述集团成员单位关系（[[tables/cust_group_rel]]）从新建到生效/拒绝的状态流转：新建即 INEFFECTIVE 并发待办，成员单位签署后 EFFECTIVE，拒绝则 REJECTED，运营端亦可直接生效。生效口径被 [[calibers/effective-group-member]] 与 [[rules/effective-member-no-op]] 引用。

## 需求背景

集团树中的成员关系必须经成员单位确认才具备业务效力，因此引入「未生效—已生效—已拒绝」三态与待办通知机制。运营端补录历史集团时允许按企业建档状态直接落生效或未生效。准入校验依赖企业建档成功（[[calibers/company-build-success]]），根节点不可作为被签对象（[[calibers/group-root-node]]）。协议签署与服务端直接生效两条路径并存，见 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化，三态基线来自代码枚举。现行实现中存在两条并存路径：一是成员单位协议签署（accept/reject），二是服务端 effectGroupRel 直接置生效；两者未在状态机层面统一收敛，后续版本可考虑合并为单一入口。新增子级的待办发送范围以企业建档成功为前提，见 [[rules/notice-only-build-success]]。

## 状态与迁移锚点

```ground:state_machine
name: 集团成员单位关系状态机
field: cust_group_rel.status
states:
  - value: INEFFECTIVE
    label: 未生效（待成员单位签署/处理待办）
    source: code_enum
  - value: EFFECTIVE
    label: 已生效
    source: code_enum
  - value: REJECTED
    label: 已拒绝
    source: code_enum
transitions:
  - from: "（新建）"
    event: 新增成员单位子级且企业认证成功，发送待办 sendCustGroupRelNotice(groupId)
    to: INEFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:sendCustGroupRelNotice
  - from: "（新建）"
    event: 运营端新增集团根节点 addExistRootGroupRel()：企业 cust_build_status=BUILD_SUCCESS 时直接置 EFFECTIVE，否则 INEFFECTIVE
    to: "EFFECTIVE | INEFFECTIVE"
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:addExistRootGroupRel
  - from: INEFFECTIVE
    event: 签署协议 accept()（校验非 EFFECTIVE、rootFlag!=Y）
    to: EFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:accept
  - from: INEFFECTIVE
    event: 拒绝协议 reject()
    to: REJECTED
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupLicenseApplication.java:reject
  - from: INEFFECTIVE
    event: effectGroupRel(custId,custType) 直接生效
    to: EFFECTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/CustGroupRelApplication.java:effectGroupRel
```
---END FILE---

---FILE: calibers/default-repayment-account.md ---
---
type: caliber
title: 默认还款账户口径
page_key: calibers/default-repayment-account
domain: 企业银行账户
status: draft
aliases: [默认账户, default_account_flag=1]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:setDefaultFlag/afterSave
contract_version: "0.1"
---

默认还款账户指企业名下被标记为默认的资金账户，是代扣/还款类业务的取数入口。判定条件为 `cust_account_info.default_account_flag = '1'`，作用域为同一归属企业；维护规则见 [[rules/default-account-unique]]。

## 需求背景

一个企业可绑定多个银行账户（[[tables/cust_account_info]]），但资金动作只能落到一个账户上，因此需要「默认标记 + 同企业唯一」的显式口径，避免下游按时间或主键取到不确定账户。企业名下无默认账户时，系统按 afterSave 逻辑自动把首个账户置为默认，保证口径恒有取值。

## 版本演进

v0 契约按现状固化。该口径同时被写入路径（setDefaultFlag 先清零再置一）与兜底路径（afterSave）维护，两条路径共同保证同企业唯一性。

## 口径锚点

```ground:caliber
name: 默认还款账户
predicate: cust_account_info.default_account_flag = '1'
scope: 同一 ref_cust_company_info 企业下唯一
evidence: code_path:CustAccountApplication.java:setDefaultFlag/afterSave
```
---END FILE---

---FILE: calibers/account-payment-auth-passed.md ---
---
type: caliber
title: 账户打款认证通过口径
page_key: calibers/account-payment-auth-passed
domain: 企业银行账户
status: draft
aliases: [认证通过账户, APPLY_40]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
---

账户打款认证通过指该银行账户已走完人行小额打款验证流程，判定条件为 `cust_account_info.auth_state = 'APPLY_40'`，作用域为账户维度。

## 需求背景

资金类业务只能使用经验证的真实账户，因此需要以认证状态作为准入口径。但现行实现中 APPLY_40 是「验证动作已终态」的标记，而非严格意义的「验证成功」，见 [[processes/account-cnaps-payment-auth-state]] 与 [[rules/payment-fail-count]]。

## 版本演进

v0 契约按现状固化。该口径当前不足以单独作为「验证通过」的过滤条件：建议配合 error_try_count 与 trans_id 组合判断，后续版本再决定是否拆出独立的成功状态。

## 口径锚点

```ground:caliber
name: 账户打款认证通过
predicate: cust_account_info.auth_state = 'APPLY_40'
scope: 账户维度
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```
---END FILE---

---FILE: calibers/valid-record-enable-y.md ---
---
type: caliber
title: 有效账户/有效记录口径
page_key: calibers/valid-record-enable-y
domain: 企业银行账户
status: draft
aliases: [逻辑删除口径, enable=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
---

有效记录指未被逻辑删除的数据行，判定条件为 `cust_account_info.enable = 'Y'`，作用域为该表通用逻辑删除口径。

## 需求背景

账户数据涉及历史与失效记录，物理删除会破坏认证与打款审计链路，因此统一以 enable 标记做逻辑删除，所有列表与取数默认叠加该过滤条件。与之相邻的状态字段（如 `status`，实测仅 INIT）不可替代本口径。

## 版本演进

v0 契约按现状固化，该口径适用于 [[tables/cust_account_info]] 全表查询。

## 口径锚点

```ground:caliber
name: 有效账户/有效记录
predicate: cust_account_info.enable = 'Y'
scope: 全表通用逻辑删除口径
evidence: db
```
---END FILE---

---FILE: calibers/effective-group-member.md ---
---
type: caliber
title: 已生效集团成员单位口径
page_key: calibers/effective-group-member
domain: 企业集团关系
status: draft
aliases: [生效成员单位, status=EFFECTIVE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:listSubCust
contract_version: "0.1"
---

已生效集团成员单位指成员关系已完成确认的节点，判定条件为 `cust_group_rel.status = 'EFFECTIVE'`，作用域为平铺列表 / 子级列表（listSubCust）的过滤口径。

## 需求背景

集团树中包含未生效与已拒绝的关系记录（[[tables/cust_group_rel]]），对外展示与统计只应包含生效节点。状态的产生与流转见 [[processes/cust-group-rel-status-state]]，重复操作拦截见 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化，该口径与状态机三态基线一致。

## 口径锚点

```ground:caliber
name: 已生效集团成员单位
predicate: cust_group_rel.status = 'EFFECTIVE'
scope: 平铺/子级列表 listSubCust 过滤口径
evidence: code_path:CustGroupRelApplication.java:listSubCust
```
---END FILE---

---FILE: calibers/group-root-node.md ---
---
type: caliber
title: 集团根节点口径
page_key: calibers/group-root-node
domain: 企业集团关系
status: draft
aliases: [集团本身, root_flag=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
contract_version: "0.1"
---

集团根节点指代表集团本身的关系记录，判定条件为 `cust_group_rel.root_flag = 'Y'`；root_flag = 'Y' 的企业不可签署成员单位协议，也不可作为子级被关联。字段边界见 [[concepts/root-flag]]。

## 需求背景

集团树必须有一个根来承载集团角色，根节点与成员单位在权限上互斥：根不能成为别人的子级，也不能以成员身份签署协议。相关准入校验见 [[rules/effective-member-no-op]] 与 [[rules/corp-company-cannot-be-child]]。

## 版本演进

v0 契约按现状固化；`level` 字段实测仅 1（根节点），层级能力尚未展开使用。

## 口径锚点

```ground:caliber
name: 集团根节点
predicate: cust_group_rel.root_flag = 'Y'
scope: 根节点识别；root_flag=Y 的企业不可签成员单位协议
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```
---END FILE---

---FILE: calibers/company-build-success.md ---
---
type: caliber
title: 企业建档成功口径
page_key: calibers/company-build-success
domain: 企业集团关系
status: draft
aliases: [建档成功, BUILD_SUCCESS]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
contract_version: "0.1"
---

企业建档成功指企业主数据已完成认证建档，判定条件为 `cust_company_info.cust_build_status = 'BUILD_SUCCESS'`，是发送集团待办、CA 开通、集团类操作的前置条件。

## 需求背景

未建档完成的企业不具备签署与业务承接能力，若提前发送待办或允许操作会产生无效流程与脏状态，因此把建档成功作为一系列动作的统一闸门，见 [[rules/notice-only-build-success]] 与 [[rules/effective-member-no-op]]。

## 版本演进

v0 契约按现状固化。该口径同时被协议签署侧（CustGroupLicenseApplication.checkCustGroup）与关系新增/导入侧（CustGroupRelApplication）引用，是跨模块共享口径。

## 口径锚点

```ground:caliber
name: 企业建档成功
predicate: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
scope: 发送集团待办、CA 开通、集团操作的前置条件
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup / CustGroupRelApplication.java:addExistSubCustGroupRel
```
---END FILE---

---FILE: calibers/master-data-company.md ---
---
type: caliber
title: 主数据企业口径
page_key: calibers/master-data-company
domain: 企业集团关系
status: draft
aliases: [主数据企业, data_type=DATA_TYPE_MAIN]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
contract_version: "0.1"
---

主数据企业指以企业主数据身份存在、可对外参与集团与业务关系的企业记录，判定条件为 `cust_company_info.data_type = DATA_TYPE_MAIN`，用于把企业主数据与记录数据区分开。

## 需求背景

同一套企业信息表中同时承载主数据与业务记录数据，若不显式区分，集团关系与列表类查询会把非主数据记录纳入结果集，造成同企业多行、统计重复。该口径与 [[calibers/real-operator-exclude-test-data]] 共同用于结果集净化。

## 版本演进

v0 契约按现状固化，作为企业维度查询的基础过滤条件。

## 口径锚点

```ground:caliber
name: 主数据企业
predicate: cust_company_info.data_type = DATA_TYPE_MAIN
scope: 企业主数据与记录数据区分
evidence: code_path:CustCompanyIfoEnchanceService.java:listEffectCompany
```
---END FILE---

---FILE: calibers/real-operator-exclude-test-data.md ---
---
type: caliber
title: 真实运营方（排除测试数据）口径
page_key: calibers/real-operator-exclude-test-data
domain: 企业集团关系
status: draft
aliases: [真实运营方, test_data != Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:queryTenantOperatorCompany
contract_version: "0.1"
---

真实运营方指租户下真正承担运营主体角色的企业，判定条件为 `cust_company_info.test_data != 'Y'`（排除测试数据），使用场景为：租户存在多个 PLATFORM_OPERATOR_COMPANY 时仅保留非测试运营方。

## 需求背景

测试租户中常并存多个运营方企业（PLATFORM_OPERATOR_COMPANY），若不做剔除会导致运营主体识别歧义（取到测试企业），因此对运营方查询追加 test_data 过滤。注意 `!= 'Y'` 对 NULL 值的处理需按各库比较语义核对，见文末 REVIEW。

## 版本演进

v0 契约按现状固化，该口径仅作用于运营方识别链路。

## 口径锚点

```ground:caliber
name: 真实运营方（排除测试数据）
predicate: cust_company_info.test_data != 'Y'
scope: 租户存在多个 PLATFORM_OPERATOR_COMPANY 时仅保留非测试运营方
evidence: code_path:CustGroupRelApplication.java:queryTenantOperatorCompany
```
---END FILE---

---FILE: calibers/enabled-sftp-channel.md ---
---
type: caliber
title: 启用的 SFTP 渠道口径
page_key: calibers/enabled-sftp-channel
domain: SFTP渠道对接
status: draft
aliases: [启用渠道, cust_sftp.enable=Y]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
---

启用的 SFTP 渠道指当前可参与文件交互的渠道配置，判定条件为 `cust_sftp.enable = 'Y'`，作用域为 SFTP 渠道配置表（[[tables/cust_sftp]]）。

## 需求背景

渠道 SFTP 账号会随对接上下线增删，需要启停标记区分在用的配置；同时同名渠道可能存在 -test 后缀的测试配置，统计时需一并排除，字段边界见 [[concepts/sftp-channel]]。

## 版本演进

v0 契约按现状固化：该字段实测全部为 'Y'，目前无代码写值证据，启停是否由运营端维护待后续核实。

## 口径锚点

```ground:caliber
name: 启用的 SFTP 渠道
predicate: cust_sftp.enable = 'Y'
scope: SFTP 渠道配置表（实测全部为 Y，无代码写值证据）
evidence: db
```
---END FILE---

---FILE: concepts/account-owner-company.md ---
---
type: concept
title: 账户归属企业（ref_cust_company_info）
page_key: concepts/account-owner-company
domain: 企业银行账户
status: draft
aliases: [ref_cust_company_info, 客户账号信息]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: cust_account_info.ref_cust_company_info = cust_company_info.code
field_targets:
  - cust_account_info.ref_cust_company_info
  - cust_company_info.code
adjudication: boundary
also_confused_with:
  - cust_company_info.id
  - cust_id
boundary: 字段名与注释像“账号信息”，实际存企业编码；代码统一用 company.getCode() 赋值/查询，用企业主键 id 过滤会查不到数据。
---

「账户归属企业」是账户表与企业的关联语义：`cust_account_info.ref_cust_company_info` 存的是 `cust_company_info.code`（企业编码），不是企业主键 id。相关表见 [[tables/cust_account_info]]。

## 需求背景

账户的所有校验与口径（重复账户校验、默认账户唯一、企业维度统计）都依赖这个关联字段，因此它的取值语义必须唯一确定，否则会同时影响 [[rules/account-no-unique-per-company]] 与 [[calibers/default-repayment-account]] 的正确性。

## 版本演进

v0 契约按现状固化：关联值为企业编码，`cust_id` 语义仅属于集团关系表，两者不可互换。

## 判定边界

字段名与注释像「账号信息」，实际存企业编码；代码统一用 company.getCode() 赋值/查询，用企业主键 id 过滤会查不到数据。
---END FILE---

---FILE: concepts/bank-no.md ---
---
type: concept
title: 联行号（bank_no）
page_key: concepts/bank-no
domain: 企业银行账户
status: draft
aliases: [bank_no, bankID, cnapsCode]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: cust_account_info.bank_no
field_targets:
  - cust_account_info.bank_no
  - cust_account_info.bank_code
  - cust_account_info.bank_code_name
  - cust_account_info.bank_branch_name
adjudication: boundary
also_confused_with:
  - bank_code（银行总行代码）
  - bank_id（银行ID）
  - bank_code_name（上送 bankName）
boundary: 代码把 bank_no 同时当作 bankID 与 cnapsCode 上送人行接口，bankName 取的是 bank_code_name（总行名称）而非开户行 branch 名称。
---

联行号是账户开户行的清算行号，落库字段为 `cust_account_info.bank_no`。在打款申请链路中，代码把该字段同时作为 `bankID` 与 `cnapsCode` 上送人行小额打款接口，即「一值两用」。账户表见 [[tables/cust_account_info]]，流程见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

银行侧接口需要清算行标识与银行名称；现有实现用 bank_no 顶替两个入参、用总行名称顶替开户行名称，任何按字段名直觉推断的口径（如认为 bankName 来自 bank_branch_name）都会与实际上送不一致。

## 版本演进

v0 契约按现状固化；`bank_branch_name` 未参与打款申请链路，后续版本若接入分支行维度需重新厘清三个字段的分工。

## 判定边界

代码把 bank_no 同时当作 bankID 与 cnapsCode 上送人行接口，bankName 取的是 bank_code_name（总行名称）而非开户行 branch 名称。
---END FILE---

---FILE: concepts/cust-type.md ---
---
type: concept
title: 企业角色（cust_type）
page_key: concepts/cust-type
domain: 企业集团关系
status: draft
aliases: [cust_type, 公司类型, companyType]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java
contract_version: "0.1"
maps_to: 'cust_group_rel.cust_type = JSON 数组字符串（如 ["SUPPLIER"]）'
field_targets:
  - cust_group_rel.cust_type
  - cust_company_info.cust_company_type
adjudication: boundary
also_confused_with:
  - DB 注释“多企业角色用逗号分隔”
  - CustCompanyInfoDO.cust_company_type
boundary: 库注释写逗号分隔，代码实际统一 JSONArray.toJSONString() 存取与 like '%"FINANCE"%' 精确匹配；多角色通过 addRoleToRoot 追加数组元素，不能按逗号切分解析。
---

企业角色描述成员单位在集团中承担的身份（如 SUPPLIER、FINANCE），落库字段为 `cust_group_rel.cust_type`，实际以 JSON 数组字符串存储。所属表见 [[tables/cust_group_rel]]，相关唯一性校验见 [[rules/group-rel-uniqueness]]。

## 需求背景

同一成员单位可承担多个角色，代码通过 addRoleToRoot 向数组追加角色，并按 like 精确匹配单个角色做筛选；若按库注释的「逗号分隔」解析，将无法正确拆出角色集合。

## 版本演进

v0 契约按现状固化：存储形态已从注释描述的逗号分隔演进为 JSON 数组，库注释成为历史描述，以代码为准。

## 判定边界

库注释写逗号分隔，代码实际统一 JSONArray.toJSONString() 存取与 like '%"FINANCE"%' 精确匹配；多角色通过 addRoleToRoot 追加数组元素，不能按逗号切分解析。
---END FILE---

---FILE: concepts/root-flag.md ---
---
type: concept
title: 集团根标识（root_flag）
page_key: concepts/root-flag
domain: 企业集团关系
status: draft
aliases: [root_flag, rootFlag]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java
contract_version: "0.1"
maps_to: "cust_group_rel.root_flag = 'Y'（集团本身）/ 'N'（成员单位）"
field_targets:
  - cust_group_rel.root_flag
  - cust_group_rel.root_group_id
  - cust_group_rel.root_cust_id
adjudication: boundary
also_confused_with:
  - root_group_id（根关系记录主键）
  - root_cust_id（根企业id）
boundary: root_flag=Y 的节点不允许再作为子级关联、也不允许签署成员单位协议；root_group_id/root_cust_id 是树定位字段，与布尔标识无关。
---

集团根标识用于区分一行关系记录代表的是集团本身（Y）还是成员单位（N），是权限与树结构的判定基础，口径见 [[calibers/group-root-node]]，表见 [[tables/cust_group_rel]]。

## 需求背景

根节点与成员单位在操作权限上互斥：根节点不能再作为其他集团的子级，也不能签署成员单位协议，因此必须有一个明确的布尔标识承载该判定；树定位则另由 root_group_id / root_cust_id 承担，见 [[processes/cust-group-rel-status-state]]。

## 版本演进

v0 契约按现状固化，标识与树定位字段职责分离。

## 判定边界

root_flag=Y 的节点不允许再作为子级关联、也不允许签署成员单位协议；root_group_id/root_cust_id 是树定位字段，与布尔标识无关。
---END FILE---

---FILE: concepts/trans-id-vs-trace-no.md ---
---
type: concept
title: 打款交易标识（trans_id 与 trace_no）
page_key: concepts/trans-id-vs-trace-no
domain: 企业银行账户
status: draft
aliases: [trans_id, trace_no, OriginalTxSN]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java
contract_version: "0.1"
maps_to: trans_id=我方发起打款后写入的银行 OriginalTxSN；trace_no=银行返回的系统跟踪号
field_targets:
  - cust_account_info.trans_id
  - cust_account_info.trace_no
adjudication: boundary
also_confused_with:
  - 两者互相混用
boundary: 查询打款结果与打款验证都以 trans_id（OriginalTxSN）为入参；trace_no 仅落库留痕，不参与后续调用。
---

打款链路中存在两个容易混淆的标识：`trans_id` 是我方发起打款后写入的银行 OriginalTxSN，`trace_no` 是银行返回的系统跟踪号。两者均落库于 [[tables/cust_account_info]]，流程语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

查询打款结果与打款验证都需要一个与银行侧一致的请求标识，现行实现统一以 trans_id 为入参，并在申请阶段就把它写入账户记录；trace_no 仅用于留痕排查，不参与后续调用。验证前置约束见 [[rules/payment-confirm-precondition]]。

## 版本演进

v0 契约按现状固化：两标识职责分离，混用会导致银行侧查不到记录。

## 判定边界

查询打款结果与打款验证都以 trans_id（OriginalTxSN）为入参；trace_no 仅落库留痕，不参与后续调用。
---END FILE---

---FILE: concepts/account-type.md ---
---
type: concept
title: 账户类型（account_type）
page_key: concepts/account-type
domain: 企业银行账户
status: draft
aliases: [account_type, BANK, OPERATION_FEE_ACCOUNT]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
maps_to: 账户类型值（代码枚举基线缺失，取自 DB 实测）
field_targets:
  - cust_account_info.account_type
adjudication: boundary
also_confused_with:
  - "'1'、'received' 等脏值"
boundary: DB 默认值 BANK；OPERATION_FEE_ACCOUNT 为代码中未声明的真实类型，另存在 '1'/'received' 低量异常值，统计口径需排除或归并。
---

账户类型用于区分账户用途，落库字段为 `cust_account_info.account_type`（见 [[tables/cust_account_info]]），DB 默认值为 BANK。

## 需求背景

账户表同时承载还款账户与运营费账户等不同用途，按类型分流的统计与筛选需要一个稳定的取值集合；但代码枚举基线未声明 OPERATION_FEE_ACCOUNT，且存在 '1' / 'received' 等低量异常值，直接按枚举过滤会漏数。

## 版本演进

v0 契约按现状固化，取值集来自 DB 实测而非代码枚举；后续版本建议将 OPERATION_FEE_ACCOUNT 补入枚举并清理异常值。

## 判定边界

DB 默认值 BANK；OPERATION_FEE_ACCOUNT 为代码中未声明的真实类型，另存在 '1'/'received' 低量异常值，统计口径需排除或归并。
---END FILE---

---FILE: concepts/sftp-channel.md ---
---
type: concept
title: SFTP 渠道（channel）
page_key: concepts/sftp-channel
domain: SFTP渠道对接
status: draft
aliases: [channel, name, user_name]
oid: 1
scope:
  databases: [unknown]
sources:
  - db
contract_version: "0.1"
maps_to: cust_sftp.channel = 渠道编码（英文），cust_sftp.name = 渠道中文名，cust_sftp.user_name = 登录账号
field_targets:
  - cust_sftp.channel
  - cust_sftp.name
  - cust_sftp.user_name
  - cust_sftp.db_tenant_code
adjudication: boundary
also_confused_with:
  - db_tenant_code（租户标识）
boundary: channel 与 db_tenant_code 不同源（如 ZTSJ 既是 channel 也是 tenant，但多数渠道的 tenant 是域名形式）；同名渠道存在 -test 后缀的测试配置，统计需排除。
---

SFTP 渠道指文件交互的对接方，表 [[tables/cust_sftp]] 中用 `channel` 存渠道编码、`name` 存渠道中文名、`user_name` 存登录账号。

## 需求背景

渠道维度的排障与统计需要在「渠道编码」「账号」「租户」之间建立正确映射：账号命名形如 app_<渠道>_<日期/编号>，而租户标识多数为域名形式，与渠道编码并非同源。启用口径见 [[calibers/enabled-sftp-channel]]。

## 版本演进

v0 契约按现状固化；同名渠道的 -test 后缀测试配置属历史遗留，建议后续版本统一清理或以字段标注。

## 判定边界

channel 与 db_tenant_code 不同源（如 ZTSJ 既是 channel 也是 tenant，但多数渠道的 tenant 是域名形式）；同名渠道存在 -test 后缀的测试配置，统计需排除。
---END FILE---

---FILE: rules/account-no-unique-per-company.md ---
---
type: rule
title: 企业账户不可重复
page_key: rules/account-no-unique-per-company
domain: 企业银行账户
status: draft
aliases: [账户重复校验, 账户不能重复添加]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:checkBefore
contract_version: "0.1"
---

新增企业银行账户时的前置唯一性校验：同一企业下 `account_no` 已存在则阻断新增。涉及表见 [[tables/cust_account_info]]，企业关联语义见 [[concepts/account-owner-company]]。

## 需求背景

重复账号会导致打款认证与默认账户口径出现歧义（同一账号多行、默认标记分散），因此在写入前按企业维度判重。

## 版本演进

v0 契约按现状固化，校验在 checkBefore 中前置执行。

## 规则锚点

```ground:rule
name: 企业账户不可重复
content: 同一企业（ref_cust_company_info）下 account_no 已存在时抛“账户不能重复添加”，阻断新增。
impact: 新增账户前置校验
field_targets:
  - cust_account_info.account_no
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:checkBefore
```
---END FILE---

---FILE: rules/default-account-unique.md ---
---
type: rule
title: 默认账户唯一
page_key: rules/default-account-unique
domain: 企业银行账户
status: draft
aliases: [默认账号唯一, setDefaultFlag]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:setDefaultFlag
  - code_path:CustAccountApplication.java:afterSave
contract_version: "0.1"
---

设置默认账号时的排他性规则：先把该企业已有默认账户置为非默认，再置目标账户为默认；企业无默认账户时由 afterSave 兜底。对应口径见 [[calibers/default-repayment-account]]。

## 需求背景

下游资金动作按「默认账户」取单条记录，若同企业出现多条默认会导致取数不确定，故在写入路径与保存后路径双重保证唯一性。企业判定基于 [[concepts/account-owner-company]]。

## 版本演进

v0 契约按现状固化，写路径与兜底路径并存。

## 规则锚点

```ground:rule
name: 默认账户唯一
content: 设置默认账号时先查询该企业下 default_account_flag='1' 的记录并置为 '0'，再把目标账户置 '1'；保存后 afterSave 会在企业无默认账户时自动把首个账户置为默认。
impact: 企业默认还款账号口径
field_targets:
  - cust_account_info.default_account_flag
  - cust_account_info.ref_cust_company_info
evidence: code_path:CustAccountApplication.java:setDefaultFlag / afterSave
```
---END FILE---

---FILE: rules/payment-count-quota.md ---
---
type: rule
title: 打款次数配额
page_key: rules/payment-count-quota
domain: 企业银行账户
status: draft
aliases: [剩余打款次数, payment_remaining_count]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentApply
  - code_path:CustAccountApplication.java:updatePayCount
contract_version: "0.1"
---

限制单个账户发起小额打款频次的规则：剩余次数初始取自配置、每次申请成功后扣减、为 0 时阻断。语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

打款涉及真实资金与银行接口调用，需要频次刹车防止滥用与重复试探；配置项 `cust_setting_config.payment_maximum_number` 提供上限来源，账户侧记录剩余量。

## 版本演进

v0 契约按现状固化；剩余次数按账户维度维护，配置变更不影响已初始化账户的剩余值。

## 规则锚点

```ground:rule
name: 打款次数配额
content: 剩余打款次数初始值取自 cust_setting_config.payment_maximum_number（updatePayCount）；每次申请打款成功后 -1；为 0 时抛“今天打款次数已用完，请明天再试”。
impact: 限制账户验证频率
field_targets:
  - cust_account_info.payment_remaining_count
  - cust_setting_config.payment_maximum_number
evidence: code_path:CustAccountApplication.java:cnapsPaymentApply / updatePayCount
```
---END FILE---

---FILE: rules/payment-amount-range.md ---
---
type: rule
title: 打款验证金额范围与单位
page_key: rules/payment-amount-range
domain: 企业银行账户
status: draft
aliases: [验证金额0.01-0.99, checkAmount]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountController.java:checkAmount
  - code_path:CustAccountController.java:cnapsPaymentConfirm
contract_version: "0.1"
---

打款金额验证的输入口径规则：金额必填、格式合法且严格落在 0 与 1 之间，上送银行前换算为「分」。语境见 [[processes/account-cnaps-payment-auth-state]]。

## 需求背景

小额打款金额以元为单位录入、以分为单位上送，若不做范围与单位约束，会出现「1 元打款」或单位不一致导致银行侧比对失败，进而污染失败次数（[[rules/payment-fail-count]]）。

## 版本演进

v0 契约按现状固化，控制器层统一承担范围与格式校验。

## 规则锚点

```ground:rule
name: 打款验证金额范围与单位
content: 控制器校验金额为空/格式错误即抛错，且必须 0 < amount < 1（提示“输入验证金额需要在0.01～0.99”）；上送银行前金额 *100 转为“分”。
impact: 小额打款验证输入口径
field_targets:
  - cust_account_info.auth_state
evidence: code_path:CustAccountController.java:checkAmount / cnapsPaymentConfirm
```
---END FILE---

---FILE: rules/payment-confirm-precondition.md ---
---
type: rule
title: 验证前置状态约束
page_key: rules/payment-confirm-precondition
domain: 企业银行账户
status: draft
aliases: [打款验证时序约束, cnapsPaymentConfirm 前置校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
---

金额验证动作的时序约束规则：必须先申请打款、必须等银行受理成功，受理失败则需重新申请。状态取值见 [[processes/account-cnaps-payment-auth-state]]，交易标识要求见 [[concepts/trans-id-vs-trace-no]]。

## 需求背景

验证是与银行侧的一次比对动作，缺少 trans_id 或处于未受理/受理失败状态时调用必然失败并消耗配额，因此在服务层前置拦截并给出可操作提示。

## 版本演进

v0 契约按现状固化，三条前置条件共用同一入口校验。

## 规则锚点

```ground:rule
name: 验证前置状态约束
content: 无 trans_id 抛“请先发起申请打款”；auth_state=APPLY_10 抛“还未受理成功，请在账户收到打款金额后再验证”；auth_state=APPLY_30 抛“申请打款受理失败，请重新申请打款”。
impact: 打款验证时序约束
field_targets:
  - cust_account_info.trans_id
  - cust_account_info.auth_state
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```
---END FILE---

---FILE: rules/payment-fail-count.md ---
---
type: rule
title: 验证失败计数口径
page_key: rules/payment-fail-count
domain: 企业银行账户
status: draft
aliases: [error_try_count, 验证失败累加]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustAccountApplication.java:cnapsPaymentConfirm
contract_version: "0.1"
---

打款金额验证失败时的记录规则：金额不匹配或银行库无记录时，先落状态再累加失败次数与时间，最后抛业务异常。直接决定 [[calibers/account-payment-auth-passed]] 的可用性。

## 需求背景

失败需要留痕以支持人工排查与风控（疑似恶意试探），同时失败请求本身也需要把账户推进到终态避免重复卡在 APPLY_20。

## 版本演进

v0 契约按现状固化，并由此产生一个已知口径缺陷：失败请求同样落 APPLY_40，故该状态不等于验证通过，需结合 error_try_count 判读。

## 规则锚点

```ground:rule
name: 验证失败计数口径
content: 金额不匹配（result=1）或银行库无记录（result=2）时，先置 auth_state=APPLY_40，再 error_try_count+1、error_try_time=now，然后抛业务异常——失败请求也会留下 APPLY_40 状态。
impact: auth_state=APPLY_40 不能单独作为“验证通过”口径，需结合 error_try_count 判断
field_targets:
  - cust_account_info.auth_state
  - cust_account_info.error_try_count
  - cust_account_info.error_try_time
evidence: code_path:CustAccountApplication.java:cnapsPaymentConfirm
```
---END FILE---

---FILE: rules/group-rel-uniqueness.md ---
---
type: rule
title: 集团成员单位关联唯一性
page_key: rules/group-rel-uniqueness
domain: 企业集团关系
status: draft
aliases: [成员单位重复校验, 已存在]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:addNewSubCustGroupRel
contract_version: "0.1"
---

新增成员单位关系时的唯一性规则：以企业 + 租户 + 父/根企业 + 角色为组合键计数，命中即阻断。涉及表见 [[tables/cust_group_rel]]，角色字段语义见 [[concepts/cust-type]]。

## 需求背景

同一企业在同一集团树下承担同一角色只能有一条关系记录，否则生效状态、待办与统计都会重复。组合键中包含 cust_type，意味着同一企业可在不同角色下被重复关联。

## 版本演进

v0 契约按现状固化，新增（addNewSubCustGroupRel）与既有企业关联（addExistSubCustGroupRel）共用同一唯一性判定。

## 规则锚点

```ground:rule
name: 集团成员单位关联唯一性
content: 按 cust_id + db_tenant_code + parent_cust_id + root_cust_id + cust_type 计数，>=1 即抛“该企业{名称} - {角色}已存在”。
impact: 重复关联拦截
field_targets:
  - cust_group_rel.cust_id
  - cust_group_rel.cust_type
  - cust_group_rel.parent_cust_id
  - cust_group_rel.root_cust_id
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / addNewSubCustGroupRel
```
---END FILE---

---FILE: rules/corp-company-cannot-be-child.md ---
---
type: rule
title: 集团公司不可作为子级
page_key: rules/corp-company-cannot-be-child
domain: 企业集团关系
status: draft
aliases: [集团角色互斥, CORPORATION_COMPANY]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:processCompany
contract_version: "0.1"
---

角色互斥规则：已经是集团公司的企业不能被设置为其他公司的子级；导入场景中根企业必须是集团角色。相关口径见 [[calibers/group-root-node]] 与 [[processes/cust-group-rel-status-state]]。

## 需求背景

集团树是一棵有向树，若允许集团企业再成为别人的子级会产生跨集团的环与权限冲突；导入场景下根节点角色不符时无法自动创建，只能提示联系运营补建。

## 版本演进

v0 契约按现状固化，判断依据为企业角色字段（含 CORPORATION_COMPANY）。

## 规则锚点

```ground:rule
name: 集团公司不可作为子级
content: 目标企业 cust_company_type 含 CORPORATION_COMPANY 时抛“该企业已是集团公司，无法设置为其他公司的子级企业”；导入时根企业必须是集团角色，否则提示联系运营添加。
impact: 集团角色互斥
field_targets:
  - cust_company_info.cust_company_type
  - cust_group_rel.cust_type
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / processCompany
```
---END FILE---

---FILE: rules/effective-member-no-op.md ---
---
type: rule
title: 已生效成员单位不可重复操作
page_key: rules/effective-member-no-op
domain: 企业集团关系
status: draft
aliases: [checkCustGroup, 成员单位准入校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupLicenseApplication.java:checkCustGroup
contract_version: "0.1"
---

成员单位协议操作的准入规则：已生效记录、根节点、未认证成功企业三类情形均被拒。口径见 [[calibers/effective-group-member]]、[[calibers/group-root-node]]、[[calibers/company-build-success]]。

## 需求背景

重复签署会破坏生效时间与协议一致性，根节点不具备成员身份，未建档完成的企业无承接能力，因此三类场景需要在操作入口一并拦截。

## 版本演进

v0 契约按现状固化；AGW 端登录企业在非 BUILD_SUCCESS 时同样纳入拦截。

## 规则锚点

```ground:rule
name: 已生效成员单位不可重复操作
content: checkCustGroup：groupId 对应记录 status=EFFECTIVE 时抛“集团成员单位已生效，不支持该操作”；root_flag=Y 时抛“集团公司不支持该操作”；非 AGW 端登录企业 cust_build_status 非 BUILD_SUCCESS 时抛“企业未认证成功，不能执行当前操作”。
impact: 成员单位协议签署准入
field_targets:
  - cust_group_rel.status
  - cust_group_rel.root_flag
  - cust_company_info.cust_build_status
evidence: code_path:CustGroupLicenseApplication.java:checkCustGroup
```
---END FILE---

---FILE: rules/notice-only-build-success.md ---
---
type: rule
title: 新增子级仅认证成功才发待办
page_key: rules/notice-only-build-success
domain: 企业集团关系
status: draft
aliases: [待办发送范围, sendCustGroupRelNotice]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:addExistSubCustGroupRel
  - code_path:CustGroupRelApplication.java:processChildCompany
contract_version: "0.1"
---

待办发送范围规则：仅对建档成功（BUILD_SUCCESS）的企业发送集团关系待办，导入场景同理。前置口径见 [[calibers/company-build-success]]，状态语义见 [[processes/cust-group-rel-status-state]]。

## 需求背景

建档未完成的企业尚未接入系统，此时推送待办既无人处理也会产生悬挂任务，因此以待办发送范围收敛为「建档成功节点」。

## 版本演进

v0 契约按现状固化；导入链路通过把 BUILD_SUCCESS 节点加入 needSends 复用同一规则。

## 规则锚点

```ground:rule
name: 新增子级仅认证成功才发待办
content: addExistSubCustGroupRel 中仅当企业 cust_build_status=BUILD_SUCCESS 才 sendCustGroupRelNotice；导入场景同样只对 BUILD_SUCCESS 的节点加入 needSends。
impact: 待办发送范围
field_targets:
  - cust_company_info.cust_build_status
  - cust_group_rel.status
evidence: code_path:CustGroupRelApplication.java:addExistSubCustGroupRel / processChildCompany
```
---END FILE---

---FILE: rules/root-group-delete-check.md ---
---
type: rule
title: 集团删除前在途业务校验
page_key: rules/root-group-delete-check
domain: 企业集团关系
status: draft
aliases: [removeRootGroup, 集团解散校验]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:CustGroupRelApplication.java:removeRootGroup
contract_version: "0.1"
---

集团解散/移除成员前的约束规则：先扁平化整棵集团树做在途业务校验，通过后批量删除关系、释放额度并回收待办。相关表见 [[tables/cust_group_rel]]。

## 需求背景

集团关系中可能挂有额度等业务，直接删除会产生孤儿额度与在途业务，因此删除前必须逐节点校验。未生效且认证成功的子节点同时消除待办，避免遗留悬挂任务（参见 [[rules/notice-only-build-success]]）。

## 版本演进

v0 契约按现状固化，删除流程包含「校验—删关系—取消额度—消待办」四步。

## 规则锚点

```ground:rule
name: 集团删除前在途业务校验
content: removeRootGroup 先扁平化整棵集团树，调用 CheckGroupMemberDeleteService：额度模块 custWithActiveLimit 非空即抛 HAS_BUSINESS_PROCESS(有在途业务不允许删除)，再批量按主键删除关系并调用 limitFacade.cancelCustLimit；未生效且认证成功的子节点同时消除待办。
impact: 集团解散/成员移除约束
field_targets:
  - cust_group_rel.id
  - cust_group_rel.status
  - cust_company_info.cust_build_status
evidence: code_path:CustGroupRelApplication.java:removeRo
```
---END FILE---

---REVIEW: meta | 物理库名缺失---
全部分析证据仅标注为 `db` 或 `code_path`，未给出任何物理库名，故本批次所有页面的 `scope.databases` 暂填 `unknown`。待补充物理库名后统一回填。
---END REVIEW---

---REVIEW: rule | 集团删除前在途业务校验---
该规则的 evidence 字符串在语义分析结果中被截断（原文止于 "...CustGroupRelApplication.java:removeRo"），本页按逐字原则保留原样。校准后的方法名锚点需在下一轮语义分析中确认后再更新。
---END REVIEW---