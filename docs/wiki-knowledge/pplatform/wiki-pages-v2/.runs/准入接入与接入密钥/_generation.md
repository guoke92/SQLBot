---FILE: tables/cust_access_secret.md ---
---
type: table
title: 客户接入密钥表 cust_access_secret
page_key: cust_access_secret
domain: 准入接入与接入密钥
status: draft
aliases:
  - 接入密钥表
  - 客户接入秘钥信息
  - 渠道密钥表
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
  - code:CustAccessSecretDO
  - code:CustAccessApplication
contract_version: "0.1"
---

# 客户接入密钥表 cust_access_secret

## 业务定位

`cust_access_secret` 是开放接入侧的渠道主数据表，一行代表一个接入渠道（应用）。它同时承载四类信息：渠道身份（`channel`、`name`、`code`）、落库租户与逻辑租户（`db_tenant_code`、`app_tenant_code`）、加解密材料（`encry_type`、`pub_key`、`pri_key`、`password`、`key_num`）以及渠道开关（`enable`、`status_query_license_enabled`）。

开放 API 按 [[concepts/channel|渠道]] + [[concepts/enable|启用]] 组合定位渠道（见 [[calibers/valid_access_channel|有效接入渠道]]），再由 [[concepts/db_tenant_code|数据租户标识]] 决定接入客户落库到哪个租户，因此本表是「渠道 → 租户」映射的唯一入口。接入密钥这一业务术语的落点即本表（见 [[concepts/access_secret|接入密钥]]）。

## 需求背景

接入方以渠道维度接入，系统需要在请求入口识别渠道、判断渠道可用性并定位数据租户；证书与密钥以文件路径方式挂在渠道上（`pub_key` 为 `-pub.pem` 路径，`pri_key` 为 `-pri.pfx` 路径或空），密钥对数 `key_num` 全量为 2（见 [[calibers/key_num_2|密钥对数2]]），加密类型全量为 `rsa`（见 [[calibers/encry_type_rsa|接入密钥加密类型RSA]]）。

## 版本演进

- `status_query_license_enabled`：DB 实测 N=18、Y=3，但给定代码中 `CustAccessSecretDO` 未定义该字段，本接入链路亦未见读取，疑似后加字段或代码未同步（见 [[calibers/status_query_license_enabled_y|建档状态查询返回营业执照并同步SFTP开启]]）。
- `rel_lls_secret_id`：关联平台密钥记录 id，给定接入链路未见读取。
- `code`：服务层提供 `getByCode`，但给定接入链路未使用。

```ground:table
table: cust_access_secret
fields:
  - name: id
    type: string
    desc: 接入密钥记录标识（术语桥「接入密钥」maps_to 的落点字段）
    dict: null
  - name: channel
    type: string
    desc: 接入渠道/应用ID，开放API按该字段识别渠道并定位租户；DB注释为“应用id”，代码字段语义为渠道
    dict: null
  - name: name
    type: string
    desc: 渠道/接入方名称，如天马、天合光能、怡亚通
    dict: null
  - name: code
    type: string
    desc: 编码；服务层提供getByCode，但给定接入链路未使用
    dict: null
  - name: db_tenant_code
    type: string
    desc: 渠道所属数据租户标识，决定该渠道接入客户落库租户
    dict: null
  - name: app_tenant_code
    type: string
    desc: 逻辑租户标识，与db_tenant_code区分
    dict: null
  - name: enable
    type: string
    desc: 渠道启用标识，Y为有效渠道，N为禁用；接入校验只取Y
    dict: null
  - name: encry_type
    type: string
    desc: 接入密钥加密类型，DB样本全部为rsa
    dict: null
  - name: pub_key
    type: string
    desc: 公钥文件路径，非公钥内容；DB样本多为/qa/FBP_SYSTEM/cert/**-pub.pem
    dict: null
  - name: pri_key
    type: string
    desc: 私钥文件路径，非私钥内容；DB样本多为/qa/FBP_SYSTEM/cert/**-pri.pfx或空
    dict: null
  - name: password
    type: string
    desc: 密钥/证书密码
    dict: null
  - name: key_num
    type: string
    desc: 密钥对数，DB样本全部为2
    dict: null
  - name: rel_lls_secret_id
    type: string
    desc: 关联平台密钥记录id；给定接入链路未见读取该字段
    dict: null
  - name: status_query_license_enabled
    type: string
    desc: 建档状态查询是否返回营业执照并同步SFTP，Y/N；DB实测N=18、Y=3；CustAccessSecretDO给定代码未定义该字段
    dict: null
  - name: act_procinst_status
    type: string
    desc: 流程当前审批状态；接入密钥链路未见读取
    dict: null
  - name: organization_id
    type: string
    desc: 机构编号
    dict: null
```

相关口径：[[calibers/disabled_access_channel|禁用接入渠道]]、[[calibers/channel_tenant_tianma|渠道映射租户示例天马]]、[[calibers/channel_tenant_eascs|渠道映射租户示例怡亚通]]。约束规则见 [[rules/access_channel_must_exist_and_enabled|接入渠道必须存在且启用]]。

---REVIEW: table | 客户接入密钥表 cust_access_secret
- 语义分析未给出物理库名，frontmatter 的 `scope.databases` 暂以 `cust_db` 占位，需人工确认后回填。
- 证据中未出现列物理类型，`fields[].type` 统一记为 string，待 DDL 核对。
- `status_query_license_enabled` 存在于 DB 而 `CustAccessSecretDO` 未定义，需确认代码侧是否已支持该开关。
- `id` 字段由术语桥 maps_to（`cust_access_secret.id`）反推，未在 field_semantics 中单列，需确认是否确为该表主键。
---END REVIEW---
---END FILE---

---FILE: tables/cust_company_info.md ---
---
type: table
title: 企业信息表 cust_company_info
page_key: cust_company_info
domain: 准入接入与接入密钥
status: draft
aliases:
  - 企业信息表
  - 客户企业信息
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_company_info
  - code:CustCompanyInfoApplication
  - code:CustAccessApplication
contract_version: "0.1"
---

# 企业信息表 cust_company_info

## 业务定位

`cust_company_info` 保存接入客户的企业主体信息与其建档过程中的各类状态。剖析出的状态字段共四个，分属三条独立的语义线：

- `cust_build_status`：本地建档/准入状态，驱动 [[processes/cust_build_status_state_machine|企业建档准入状态机]]；
- `check_status`：运营中台审核态，映射 CheckStatus 枚举，由回调更新，驱动 [[processes/cust_check_status_state_machine|运营审核状态机]]；
- `cust_status`：企业主体状态，驱动 [[processes/cust_status_state_machine|企业状态机]]；
- `identify_style`：认证/接入方式，决定建档请求进入哪条分支（见 [[concepts/independent_reg|自主建档]]、[[concepts/dependent_reg|非自主建档]]）。

三条状态线不可互相替代：建档成功（[[concepts/build_success|建档成功]]）与审核通过（[[concepts/check_pass|审核通过]]）是不同字段上的不同状态。

## 需求背景

接入获客后需要为企业建立档案，并由运营中台审核；审核结果通过消息回调落到本地状态字段上，因此本地建档态、本地审核态、企业主体态必须分开存储。重复建档校验依赖 `cust_build_status` 与 `cust_status` 的过滤口径（见 [[calibers/duplicate_build_exclude_build_fail|重复建档排除失败建档]]、[[calibers/tianma_duplicate_exclude_writeoff|天马重复校验排除已注销]]）。

## 版本演进

- `cust_build_status` 同时出现 `CUST_BUILDING` 与 `BUILDING`、`CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM`，前一组为不同代码分支写入，后一组为简易认证分支写入，需核对字典值。
- `check_status` 中 `CUST_BACK` 与 `CUST_CHECK_INIT` 映射同一前端状态，属于过渡期遗留值。

```ground:table
table: cust_company_info
fields:
  - name: cust_build_status
    type: string
    desc: 企业建档/准入状态字段，代码写入INIT、CUST_BUILDING、BUILDING、CUST_CONFIRM_AWAIT、AWAIT_CUST_CONFIRM、BUILD_SUCCESS、BUILD_FAIL
    dict: null
  - name: check_status
    type: string
    desc: 运营中台审核状态字段，映射CheckStatus枚举，回调时更新
    dict: CheckStatus
  - name: cust_status
    type: string
    desc: 企业状态字段，代码出现ADD、EFFECT、FREEZE、WRITEOFF、CHANGE
    dict: null
  - name: identify_style
    type: string
    desc: 认证/接入方式字段，代码出现INVITE、INVITE_AGW、SELF、SIMPLE；自主建档实际落INVITE，非自主建档落INVITE_AGW
    dict: null
```

---REVIEW: table | 企业信息表 cust_company_info
- 语义分析未给出物理库名，frontmatter 的 `scope.databases` 暂以 `cust_db` 占位，需人工确认。
- 证据中未出现列物理类型，`fields[].type` 统一记为 string，待 DDL 核对。
- `cust_build_status` 与 `cust_status` 的字典键名（dictKey）未在证据中出现，暂记 null，需回填。
---END REVIEW---
---END FILE---

---FILE: processes/cust_build_status_state_machine.md ---
---
type: process
title: 企业建档准入状态机（cust_company_info.cust_build_status）
page_key: cust_build_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 建档状态机
  - 准入状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustAuditMsgService.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:messageNotify
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
contract_version: "0.1"
---

# 企业建档准入状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 上 `cust_build_status` 字段的取值与流转，覆盖「提交建档 → 待客户确认 / 审核中 → 建档成功 / 失败 → 修改后重新提交」的完整闭环。

两条分支入口由 [[concepts/independent_reg|自主建档]]（`identify_style=INVITE`/`SELF`）与 [[concepts/dependent_reg|非自主建档]]（`identify_style=INVITE_AGW`）决定：前者先进待客户确认，后者直接进审核中。运营中台回调（`CustAuditMsgService`）负责推进审核通过与拒绝。

## 需求背景

建档结果需要与运营中台审核态解耦（见 [[concepts/await_cust_confirm|待客户确认]]、[[concepts/build_success|建档成功]]），运营中台退回时本地必须回到待客户确认，拒绝时必须落失败态并允许客户修改后重新提交。

## 版本演进

- `CUST_BUILDING` 与 `BUILDING` 并存：查询分支使用 `BUILDING`，回调分支使用 `CUST_BUILDING`，两者关系待核对。
- `CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 并存：邀请/自主流程用前者，简易认证分支用后者，需核对字典键。
- `BUILD_FAIL` 之后的重新提交路径只在 `messageNotify` 中处理，需要确认是否所有入口共用。

```ground:process
name: 企业建档准入状态机
field: cust_company_info.cust_build_status
states:
  - value: INIT
    label: 初始化
    source: code_const
  - value: CUST_CONFIRM_AWAIT
    label: 待客户确认
    source: code_enum
  - value: CUST_BUILDING
    label: 运营中台审核中
    source: code_enum
  - value: BUILDING
    label: 建档中/审核中（查询分支使用，需核对与CUST_BUILDING关系）
    source: code_enum
  - value: BUILD_SUCCESS
    label: 建档成功
    source: code_enum
  - value: BUILD_FAIL
    label: 建档失败
    source: code_enum
  - value: AWAIT_CUST_CONFIRM
    label: 待客户确认（简易认证分支，需核对与CUST_CONFIRM_AWAIT关系）
    source: code_enum
transitions:
  - from: INIT
    event: 提交建档且identify_style为INVITE/SELF
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: INIT
    event: 提交建档且identify_style为INVITE_AGW
    to: CUST_BUILDING
    evidence: "code_path:CustCompanyInfoApplication.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台退回客户确认CUST_CHECK_BACKTOCUSTOM
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 客户确认提交/运营审核中CUST_CHECK_CHECKING
    to: CUST_BUILDING
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核通过CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 运营中台审核通过CUST_CHECK_PASS
    to: BUILD_SUCCESS
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_BUILDING
    event: 运营中台审核拒绝CUST_CHECK_REJECT
    to: BUILD_FAIL
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: CUST_CONFIRM_AWAIT
    event: 运营中台审核拒绝CUST_CHECK_REJECT
    to: BUILD_FAIL
    evidence: "code_path:CustAuditMsgService.java:getCustBuildStatus"
  - from: BUILD_FAIL
    event: 修改后重新提交且identify_style为INVITE/SELF
    to: CUST_CONFIRM_AWAIT
    evidence: "code_path:CustCompanyInfoApplication.java:messageNotify"
  - from: AWAIT_CUST_CONFIRM
    event: 简易认证确认提交
    to: BUILD_SUCCESS
    evidence: "code_path:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth"
```

关联：[[processes/cust_check_status_state_machine|运营审核状态机]] 的推进事件是本状态机的驱动源；建档成功会联动 [[processes/cust_status_state_machine|企业状态机]] 进入 EFFECT。

---REVIEW: process | 企业建档准入状态机
- `BUILDING` 与 `CUST_BUILDING` 是否为同一状态的两种写法，语义分析未给出结论，需核对字典与查询分支。
- `AWAIT_CUST_CONFIRM` 与 `CUST_CONFIRM_AWAIT` 的关系未确认（是否为同一 dictKey 的不同分支值）。
- 简易认证分支（`confirmCustInfoForSimpleAuth`）只给出到 BUILD_SUCCESS 的迁移，是否存在失败分支未知。
---END REVIEW---
---END FILE---

---FILE: processes/cust_status_state_machine.md ---
---
type: process
title: 企业状态机（cust_company_info.cust_status）
page_key: cust_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 企业主体状态机
  - 客户状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:updateCustBuildStatus
  - code:CustCompanyInfoApplication.java:freeze
  - code:CustCompanyInfoApplication.java:unfreeze
  - code:CustCompanyInfoApplication.java:diable
contract_version: "0.1"
---

# 企业状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 中 `cust_status` 字段的取值与流转，刻画企业主体在平台上的生命周期：新增 → 生效 → 冻结/解冻 → 注销。它与建档状态（[[processes/cust_build_status_state_machine|企业建档准入状态机]]）不是同一维度：建档成功会推动 `cust_status` 从 `ADD` 进入 `EFFECT`，但建档态本身不因冻结而回退。

## 需求背景

企业主体需要独立支持冻结与注销，冻结/解冻不改变建档结果；注销（`WRITEOFF`）作为终态，在天马重复校验中被用作排除条件（见 [[calibers/tianma_duplicate_exclude_writeoff|天马重复校验排除已注销]]）。

## 版本演进

给定证据仅覆盖 ADD→EFFECT、EFFECT↔FREEZE、EFFECT→WRITEOFF 四条迁移，`CHANGE`（变更中）的进入与退出条件未在证据中出现。

```ground:process
name: 企业状态机
field: cust_company_info.cust_status
states:
  - value: ADD
    label: 新增/初始
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: code_enum
  - value: WRITEOFF
    label: 注销
    source: code_enum
  - value: CHANGE
    label: 变更中
    source: code_enum
transitions:
  - from: ADD
    event: 建档成功
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:updateCustBuildStatus"
  - from: EFFECT
    event: 冻结
    to: FREEZE
    evidence: "code_path:CustCompanyInfoApplication.java:freeze"
  - from: FREEZE
    event: 解冻
    to: EFFECT
    evidence: "code_path:CustCompanyInfoApplication.java:unfreeze"
  - from: EFFECT
    event: 注销/禁用
    to: WRITEOFF
    evidence: "code_path:CustCompanyInfoApplication.java:diable"
```

相关联的建档结果语义见 [[concepts/build_success|建档成功]]。

---REVIEW: process | 企业状态机
- `CHANGE`（变更中）的迁移条件未在证据中出现，需补充代码路径。
- FREEZE/WRITEOFF 是否可逆（WRITEOFF 后能否恢复）未确认。
---END REVIEW---
---END FILE---

---FILE: processes/cust_check_status_state_machine.md ---
---
type: process
title: 运营审核状态机（cust_company_info.check_status）
page_key: cust_check_status_state_machine
domain: 准入接入与接入密钥
status: draft
aliases:
  - 运营中台审核状态机
  - CheckStatus 状态流转
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.java:getCheckStatus
contract_version: "0.1"
---

# 运营审核状态机

## 业务定位

该状态机描述 [[tables/cust_company_info|cust_company_info]] 中 `check_status` 字段的取值与流转，是运营中台侧审核结论在本地库的镜像。取值映射 CheckStatus 枚举，由运营中台回调更新，并进一步驱动 [[processes/cust_build_status_state_machine|企业建档准入状态机]]：审核中/退回/通过/拒绝分别对应建档态向 `CUST_BUILDING`、`CUST_CONFIRM_AWAIT`、`BUILD_SUCCESS`、`BUILD_FAIL` 的迁移。

## 需求背景

审核态与本地建档态必须分开存储与展示：`CUST_CHECK_PASS`（见 [[concepts/check_pass|审核通过]]）与 `BUILD_SUCCESS` 虽在同一业务时点联动，但字段与责任人不同，前端展示映射也不同（`CUST_BACK` 与 `CUST_CHECK_INIT` 映射同一前端状态）。

## 版本演进

给定证据只覆盖 `CUST_CHECK_INIT → CUST_CHECK_CHECKING → {BACKTOCUSTOM, PASS, REJECT}` 四条迁移；`CUST_BACK` 与 `CUST_CHECK_INIT` 是否合并待核对。

```ground:process
name: 运营审核状态机
field: cust_company_info.check_status
states:
  - value: CUST_CHECK_INIT
    label: 初始/退回
    source: code_enum
  - value: CUST_CHECK_CHECKING
    label: 审核中
    source: code_enum
  - value: CUST_CHECK_BACKTOCUSTOM
    label: 退回客户
    source: code_enum
  - value: CUST_CHECK_PASS
    label: 审核通过
    source: code_enum
  - value: CUST_CHECK_REJECT
    label: 审核拒绝
    source: code_enum
  - value: CUST_BACK
    label: 退回（与CUST_CHECK_INIT映射同一前端状态）
    source: code_enum
transitions:
  - from: CUST_CHECK_INIT
    event: 运营中台审核中
    to: CUST_CHECK_CHECKING
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 退回客户
    to: CUST_CHECK_BACKTOCUSTOM
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 审核通过
    to: CUST_CHECK_PASS
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
  - from: CUST_CHECK_CHECKING
    event: 审核拒绝
    to: CUST_CHECK_REJECT
    evidence: "code_path:CustAccessApplication.java:getCheckStatus"
```

---REVIEW: process | 运营审核状态机
- `CUST_BACK` 与 `CUST_CHECK_INIT` 的差异（是否历史遗留值）未在证据中说明。
- 退回客户（`CUST_CHECK_BACKTOCUSTOM`）之后重新进入审核中的事件未给出。
---END REVIEW---
---END FILE---

---FILE: calibers/valid_access_channel.md ---
---
type: caliber
title: 有效接入渠道
page_key: valid_access_channel
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable=Y 渠道
  - 可用渠道
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
  - code:CustAccessApplication.validateSetValueOfTianma
  - db:cust_access_secret
contract_version: "0.1"
---

# 有效接入渠道

## 业务定位

该口径定义「渠道可用」的判定条件：在 [[tables/cust_access_secret|cust_access_secret]] 中，`enable = 'Y'` 的渠道才被视为有效渠道，可用于开放 API 建档、变更渠道与天马渠道的校验。它是 [[rules/access_channel_must_exist_and_enabled|接入渠道必须存在且启用]] 规则的判定基础，也是 [[concepts/enable|启用]] 术语在接入链路上的具体落地。

## 需求背景

接入请求必须先过渠道校验才能进入租户定位环节；按 `channel + enable='Y'` 查询查不到即拒绝，避免禁用渠道继续接入。对应的反向口径见 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 版本演进

口径条件在给定证据中未发生变化；DB 实测 Y=19、N=2。

```ground:caliber
name: 有效接入渠道
predicate: "cust_access_secret.enable = 'Y'"
scope: 开放API渠道校验、变更渠道校验、天马渠道校验
evidence: "code:CustAccessApplication.validateSetValue/validateChangeChannelAndTenant/validateSetValueOfTianma; db:enable Y=19,N=2"
```
---END FILE---

---FILE: calibers/disabled_access_channel.md ---
---
type: caliber
title: 禁用接入渠道
page_key: disabled_access_channel
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable=N 渠道
  - 停用渠道
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
---

# 禁用接入渠道

## 业务定位

该口径是 [[calibers/valid_access_channel|有效接入渠道]] 的补集：`enable = 'N'` 的渠道在 [[tables/cust_access_secret|cust_access_secret]] 中保留记录但不参与接入。DB 中存在 2 条禁用渠道，接入校验会拒绝。

## 需求背景

渠道停用需要保留历史配置（密钥路径、租户映射）而不物理删除，因此通过 [[concepts/enable|启用]] 开关做软禁用；被禁用渠道的接入请求在校验阶段即被拒绝。

## 版本演进

口径条件在给定证据中未发生变化；仅以 DB 分布作证。

```ground:caliber
name: 禁用接入渠道
predicate: "cust_access_secret.enable = 'N'"
scope: DB中存在2条禁用渠道，接入校验会拒绝
evidence: "db:enable N=2"
```
---END FILE---

---FILE: calibers/encry_type_rsa.md ---
---
type: caliber
title: 接入密钥加密类型RSA
page_key: encry_type_rsa
domain: 准入接入与接入密钥
status: draft
aliases:
  - encry_type=rsa
  - RSA 密钥类型
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
---

# 接入密钥加密类型RSA

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `encry_type` 的取值现状：全量样本的取值唯一，均为 `rsa`。它决定 `pub_key` / `pri_key` 所指向证书文件的加解密方式，是 [[concepts/access_secret|接入密钥]] 配置的一部分。

## 需求背景

接入密钥以文件路径 + 加密类型的方式配置，当前接入方统一使用 RSA，未出现其他加密类型。

## 版本演进

DB 取值为单一值 `rsa`，无历史多值证据；若后续引入国密等其他类型，需重估本口径。

```ground:caliber
name: 接入密钥加密类型RSA
predicate: "cust_access_secret.encry_type = 'rsa'"
scope: cust_access_secret全量样本
evidence: "db:encry_type distinct=1, rsa"
```
---END FILE---

---FILE: calibers/key_num_2.md ---
---
type: caliber
title: 密钥对数2
page_key: key_num_2
domain: 准入接入与接入密钥
status: draft
aliases:
  - key_num=2
  - 密钥对数
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
---

# 密钥对数2

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `key_num` 的取值现状：全量样本取值唯一，均为 2，即每个渠道配置两对密钥材料。

## 需求背景

接入密钥支持多对密钥（便于轮换或双活），当前实际配置统一为两对；与 `pub_key` / `pri_key` 文件路径配置配套使用。

## 版本演进

DB 取值为单一值 2，无历史多值证据。

```ground:caliber
name: 密钥对数2
predicate: "cust_access_secret.key_num = '2'"
scope: cust_access_secret全量样本
evidence: "db:key_num distinct=1, 2"
```
---END FILE---

---FILE: calibers/status_query_license_enabled_y.md ---
---
type: caliber
title: 建档状态查询返回营业执照并同步SFTP开启
page_key: status_query_license_enabled_y
domain: 准入接入与接入密钥
status: draft
aliases:
  - status_query_license_enabled=Y
  - 执照同步开启
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
---

# 建档状态查询返回营业执照并同步SFTP开启

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `status_query_license_enabled = 'Y'` 时，建档状态查询会返回营业执照并同步 SFTP。DB 中 3 条渠道开启该能力。

## 需求背景

不同渠道对执照回传的要求不同，因此按渠道粒度开关该行为，而不是全局开关。

## 版本演进

该字段在 DB 中存在（Y=3、N=18），但给定代码中 `CustAccessSecretDO` 未定义该字段，接入链路亦未见读取，说明代码侧与库结构可能未同步，属未证实项，需 REVIEW 后再引用。对称口径见 [[calibers/status_query_license_enabled_n|建档状态查询返回营业执照并同步SFTP关闭]]。

```ground:caliber
name: 建档状态查询返回营业执照并同步SFTP开启
predicate: "cust_access_secret.status_query_license_enabled = 'Y'"
scope: DB中3条渠道开启，代码链路未读取该字段，需REVIEW
evidence: "db:status_query_license_enabled Y=3,N=18"
```

---REVIEW: caliber | 建档状态查询返回营业执照并同步SFTP开启
- 代码侧 `CustAccessSecretDO` 未定义该字段，无法确认真实生效路径；「返回营业执照并同步SFTP」的行为描述仅有字段名推证，需代码或需求文档佐证。
---END REVIEW---
---END FILE---

---FILE: calibers/status_query_license_enabled_n.md ---
---
type: caliber
title: 建档状态查询返回营业执照并同步SFTP关闭
page_key: status_query_license_enabled_n
domain: 准入接入与接入密钥
status: draft
aliases:
  - status_query_license_enabled=N
  - 执照同步关闭
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
contract_version: "0.1"
---

# 建档状态查询返回营业执照并同步SFTP关闭

## 业务定位

该口径描述 [[tables/cust_access_secret|cust_access_secret]] 中 `status_query_license_enabled = 'N'` 的渠道不返回营业执照、不做 SFTP 同步。DB 中 18 条渠道处于关闭状态，是当前多数渠道的默认配置。

## 需求背景

与开启口径对称，用于按渠道控制执照回传行为；默认关闭可减少不必要的文件同步。

## 版本演进

同 [[calibers/status_query_license_enabled_y|建档状态查询返回营业执照并同步SFTP开启]]，该字段未在给定代码中出现，行为描述待证实。

```ground:caliber
name: 建档状态查询返回营业执照并同步SFTP关闭
predicate: "cust_access_secret.status_query_license_enabled = 'N'"
scope: DB中18条渠道关闭
evidence: "db:status_query_license_enabled N=18"
```
---END FILE---

---FILE: calibers/channel_tenant_tianma.md ---
---
type: caliber
title: 渠道映射租户示例天马
page_key: channel_tenant_tianma
domain: 准入接入与接入密钥
status: draft
aliases:
  - 天马租户
  - tianma 渠道租户
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - db:cust_access_secret
contract_version: "0.1"
---

# 渠道映射租户示例天马

## 业务定位

该口径给出「渠道 → 落库租户」映射的一个实例：天马渠道的 [[concepts/db_tenant_code|数据租户标识]] 为 `tianma.beehive-scf.qhhrly.cn`。开放 API 校验通过渠道定位到该租户后，后续建档数据落入对应租户。

## 需求背景

接入渠道与数据租户是多对一关系，映射由 [[tables/cust_access_secret|cust_access_secret]] 承载，不能由请求方自带租户参数决定。

## 版本演进

天马渠道另有专属校验分支（`validateSetValueOfTianma`），包含重复校验排除已注销（[[calibers/tianma_duplicate_exclude_writeoff|天马重复校验排除已注销]]），说明该渠道存在差异化的接入策略。

```ground:caliber
name: 渠道映射租户示例天马
predicate: "cust_access_secret.db_tenant_code = 'tianma.beehive-scf.qhhrly.cn'"
scope: 天马渠道接入租户
evidence: "db:db_tenant_code值分布; code:CustAccessApplication.validateSetValue"
```
---END FILE---

---FILE: calibers/channel_tenant_eascs.md ---
---
type: caliber
title: 渠道映射租户示例怡亚通
page_key: channel_tenant_eascs
domain: 准入接入与接入密钥
status: draft
aliases:
  - 怡亚通租户
  - eascs 渠道租户
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.setEsassAuthFlag
  - db:cust_access_secret
contract_version: "0.1"
---

# 渠道映射租户示例怡亚通

## 业务定位

该口径给出「渠道 → 落库租户」映射的另一个实例：怡亚通渠道的 [[concepts/db_tenant_code|数据租户标识]] 为 `eascs.beehive-scf.qhhrly.cn`。

## 需求背景

与天马同为接入方示例，用于说明同一张 [[tables/cust_access_secret|cust_access_secret]] 上不同渠道映射到不同数据租户，且可有渠道专属的鉴权开关处理（`setEsassAuthFlag`）。

## 版本演进

怡亚通渠道存在独立的鉴权标记处理逻辑（`setEsassAuthFlag`），属渠道差异化分支。

```ground:caliber
name: 渠道映射租户示例怡亚通
predicate: "cust_access_secret.db_tenant_code = 'eascs.beehive-scf.qhhrly.cn'"
scope: 怡亚通渠道接入租户
evidence: "db:db_tenant_code值分布; code:CustAccessApplication.setEsassAuthFlag"
```
---END FILE---

---FILE: calibers/duplicate_build_exclude_build_fail.md ---
---
type: caliber
title: 重复建档排除失败建档
page_key: duplicate_build_exclude_build_fail
domain: 准入接入与接入密钥
status: draft
aliases:
  - BUILD_FAIL 不参与重复校验
  - 失败建档可重提
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.initCust
contract_version: "0.1"
---

# 重复建档排除失败建档

## 业务定位

该口径规定：同租户同统一社会信用代码的重复建档校验中，[[tables/cust_company_info|cust_company_info]] 里 `cust_build_status = 'BUILD_FAIL'` 的记录被排除，即失败建档不阻塞客户重新提交。

## 需求背景

审核拒绝后客户需要修改并重新发起建档（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]] 中 `BUILD_FAIL → CUST_CONFIRM_AWAIT`），因此失败态不能作为重复拦截依据。

## 版本演进

口径同时出现在校验入口（`validateSetValue`）与建档初始化（`initCust`）两处，未发现分支差异。

```ground:caliber
name: 重复建档排除失败建档
predicate: "cust_company_info.cust_build_status = 'BUILD_FAIL'"
scope: 同租户同统一社会信用代码重复建档校验时排除BUILD_FAIL
evidence: "code:CustAccessApplication.validateSetValue/CustAccessApplication.initCust"
```
---END FILE---

---FILE: calibers/tianma_duplicate_exclude_writeoff.md ---
---
type: caliber
title: 天马重复校验排除已注销
page_key: tianma_duplicate_exclude_writeoff
domain: 准入接入与接入密钥
status: draft
aliases:
  - WRITEOFF 不参与天马重复校验
  - 天马渠道重复放宽
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValueOfTianma
contract_version: "0.1"
---

# 天马重复校验排除已注销

## 业务定位

该口径规定：天马渠道在按企业名称、统一社会信用代码及其组合做重复校验时，[[tables/cust_company_info|cust_company_info]] 中 `cust_status = 'WRITEOFF'`（已注销）的企业被排除，允许同名/同码企业重新接入。

## 需求背景

天马渠道的历史客户可能已注销，注销主体不应阻塞新企业的接入建档，因此该校验分支需要放开注销记录；这与 [[calibers/duplicate_build_exclude_build_fail|重复建档排除失败建档]] 是两条不同维度（主体状态 vs 建档状态）的排除口径。

## 版本演进

仅天马渠道（`validateSetValueOfTianma`）具备该排除逻辑，属渠道差异化策略。

```ground:caliber
name: 天马重复校验排除已注销
predicate: "cust_company_info.cust_status = 'WRITEOFF'"
scope: 天马建档名称/信用代码/组合重复校验时排除WRITEOFF
evidence: "code:CustAccessApplication.validateSetValueOfTianma"
```
---END FILE---

---FILE: concepts/access_secret.md ---
---
type: concept
title: 接入密钥
page_key: access_secret
domain: 准入接入与接入密钥
status: draft
aliases:
  - 客户接入秘钥信息
  - 渠道密钥
  - cust_access_secret
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret
  - code:CustAccessApplication
contract_version: "0.1"
maps_to: cust_access_secret.id
also_confused_with:
  - cust_sftp.channel
  - tenant_setting_config.db_tenant_code
adjudication: boundary
boundary: 接入密钥表存渠道、租户、证书路径；SFTP配置存文件传输账号；租户配置存租户业务配置，三者通过channel/db_tenant_code间接关联。
---

# 接入密钥

## 业务定位

「接入密钥」是业务口语中对渠道接入配置的统称，其权威落点是 [[tables/cust_access_secret|cust_access_secret]] 的一条记录。记录以渠道为粒度，打包了渠道身份、落库租户、证书/密钥文件路径与各类开关；所谓「密钥」在库中存的是文件路径与密码，而不是密钥内容本身。

## 边界与混淆

- 与 `cust_sftp.channel` 的区别：SFTP 配置的 channel 描述文件传输通道，接入密钥的 channel 描述开放 API 接入渠道，二者通过渠道值间接关联但用途不同。
- 与 `tenant_setting_config.db_tenant_code` 的区别：租户配置存租户业务参数，接入密钥存渠道到租户的映射关系，是「用哪个租户」而非「租户怎么配」。

详细口径见 [[calibers/valid_access_channel|有效接入渠道]]、[[calibers/encry_type_rsa|接入密钥加密类型RSA]]、[[calibers/key_num_2|密钥对数2]]。

## 需求背景

接入方需要一套可运维的渠道配置：既能按渠道切换租户、轮换证书，也能在不删数据的前提下停用渠道。相关约束见 [[rules/access_channel_must_exist_and_enabled|接入渠道必须存在且启用]]。

## 版本演进

`status_query_license_enabled`、`rel_lls_secret_id`、`code` 三个字段在给定接入链路中均未见使用，其中前者在代码 DO 中缺失，属配置模型与代码实现不同步的迹象。

---REVIEW: concept | 接入密钥
- 术语桥 maps_to 指向 `cust_access_secret.id`，但 `id` 未在 field_semantics 中单列，需确认主键列名与语义。
---END REVIEW---
---END FILE---

---FILE: concepts/channel.md ---
---
type: concept
title: 渠道
page_key: channel
domain: 准入接入与接入密钥
status: draft
aliases:
  - channel
  - 应用id
  - appId
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret.channel
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_access_secret.channel
also_confused_with:
  - cust_sftp.channel
  - cust_build_record.channel
adjudication: boundary
boundary: cust_access_secret.channel是开放接入渠道；cust_sftp.channel是文件通道；cust_build_record.channel是推送记录渠道。
---

# 渠道

## 业务定位

「渠道」在接入语境下指开放 API 的接入方标识，落在 [[tables/cust_access_secret|cust_access_secret]] 的 `channel` 字段上。DB 注释写作「应用id」，代码字段语义为渠道，二者指向同一列，读表时需按渠道语义理解（该列同时承担渠道识别与租户定位的入口作用）。

## 边界与混淆

- `cust_sftp.channel`：文件传输通道，决定文件收发配置，不参与开放 API 鉴权。
- `cust_build_record.channel`：建档/推送记录上的渠道值，是业务发生后的留痕，不是接入配置。

## 需求背景

渠道是接入校验的第一入口：先按渠道定位配置，再判断 [[concepts/enable|启用]] 状态与 [[concepts/db_tenant_code|数据租户标识]]。

## 版本演进

字段语义在 DB 注释与代码之间存在「应用id / 渠道」的表述差异，暂无版本变更证据。

---REVIEW: concept | 渠道
- DB 注释「应用id」与代码字段语义「渠道」的表述差异是否为历史改名遗留，证据未说明，建议在数据字典中固定一种口径。
---END REVIEW---
---END FILE---

---FILE: concepts/db_tenant_code.md ---
---
type: concept
title: 数据租户标识
page_key: db_tenant_code
domain: 准入接入与接入密钥
status: draft
aliases:
  - db_tenant_code
  - 数据租户
  - 租户编码
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret.db_tenant_code
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_access_secret.db_tenant_code
also_confused_with:
  - cust_access_secret.app_tenant_code
  - tenant_setting_config.db_tenant_code
adjudication: boundary
boundary: db_tenant_code用于数据隔离与落库租户；app_tenant_code为逻辑租户标识，不能混用。
---

# 数据租户标识

## 业务定位

`db_tenant_code` 表示数据租户，决定通过该渠道接入的客户数据落到哪个租户库。它是 [[tables/cust_access_secret|cust_access_secret]] 上「渠道 → 租户」映射的目标值，实例见 [[calibers/channel_tenant_tianma|渠道映射租户示例天马]] 与 [[calibers/channel_tenant_eascs|渠道映射租户示例怡亚通]]。

## 边界与混淆

- 与 [[concepts/app_tenant_code|逻辑租户标识]] 的区别：`app_tenant_code` 是逻辑租户标识，接入定位使用 `db_tenant_code`，不可混用。
- 与 `tenant_setting_config.db_tenant_code` 的区别：后者是租户的业务配置，前者是渠道上的落库归属。

## 需求背景

数据隔离要求接入请求不能自带租户归属，必须由平台侧的渠道配置决定落库租户。

## 版本演进

暂无该字段取值口径变化的证据。

---END FILE---
---END FILE---

---FILE: concepts/app_tenant_code.md ---
---
type: concept
title: 逻辑租户标识
page_key: app_tenant_code
domain: 准入接入与接入密钥
status: draft
aliases:
  - app_tenant_code
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret.app_tenant_code
contract_version: "0.1"
maps_to: cust_access_secret.app_tenant_code
also_confused_with:
  - cust_access_secret.db_tenant_code
adjudication: boundary
boundary: app_tenant_code与db_tenant_code不同，接入定位使用db_tenant_code。
---

# 逻辑租户标识

## 业务定位

`app_tenant_code` 是 [[tables/cust_access_secret|cust_access_secret]] 上的逻辑租户标识，用于应用层面的租户归类，与决定落库归属的 [[concepts/db_tenant_code|数据租户标识]] 并存于同一记录。

## 边界与混淆

两者同表不同义：接入校验与落库定位一律使用 `db_tenant_code`，`app_tenant_code` 不参与接入定位。

## 需求背景

逻辑租户与数据租户分离，使应用层可以在不改动落库归属的前提下调整租户归类。

## 版本演进

暂无版本演进证据。

---REVIEW: concept | 逻辑租户标识
- `app_tenant_code` 的具体消费场景未在给定代码证据中出现，需补充使用方。
---END REVIEW---
---END FILE---

---FILE: concepts/enable.md ---
---
type: concept
title: 启用
page_key: enable
domain: 准入接入与接入密钥
status: draft
aliases:
  - enable
  - Y/N
oid: 1
scope:
  databases:
    - cust_db
sources:
  - db:cust_access_secret.enable
  - code:CustAccessApplication.validateSetValue
contract_version: "0.1"
maps_to: cust_access_secret.enable
also_confused_with:
  - tenant_setting_config.enable
  - cust_company_info.enable
adjudication: boundary
boundary: 不同表的enable是各自独立过滤条件，不能跨表复用。
---

# 启用

## 业务定位

`enable` 是软开关字段，取值 `Y` / `N`。在接入链路上，只有 `cust_access_secret.enable = 'Y'` 的渠道才被认为有效（[[calibers/valid_access_channel|有效接入渠道]]），`N` 即为 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 边界与混淆

同名字段在不同表上语义独立：`tenant_setting_config.enable`、`cust_company_info.enable` 各自是所在表的过滤条件，不能跨表套用；接入校验只认可 `cust_access_secret.enable`。

## 需求背景

渠道停用需要可回退且不删除配置，因此采用 Y/N 软开关，配合校验逻辑在入口拦截。

## 版本演进

DB 实测 Y=19、N=2，取值集合稳定为 Y/N。

---END FILE---
---END FILE---

---FILE: concepts/independent_reg.md ---
---
type: concept
title: 自主建档
page_key: independent_reg
domain: 准入接入与接入密钥
status: draft
aliases:
  - independentReg
  - 自主注册
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style = 'INVITE'
also_confused_with:
  - cust_company_info.identify_style = 'SELF'
  - cust_company_info.identify_style = 'INVITE_AGW'
adjudication: boundary
boundary: 代码independentReg实际setIdentifyStyle=INVITE；SELF是自主认证消息分支；INVITE_AGW是非自主/平台录入。
---

# 自主建档

## 业务定位

「自主建档」指接入客户自行发起并确认建档的流程。在数据上，代码中的 `independentReg` 分支实际把 [[tables/cust_company_info|cust_company_info]] 的 `identify_style` 置为 `INVITE`，因此本术语映射到 `identify_style = 'INVITE'`。

## 边界与混淆

- `SELF`：自主认证消息分支使用的取值，与业务口语「自主」同名但落值不同。
- [[concepts/dependent_reg|非自主建档]]（`INVITE_AGW`）：平台代录，流程不同。

建档状态上的差异见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]：自主分支提交后先进入待客户确认。

## 需求背景

自主与非自主两类来源需要走不同的确认链路，故以 `identify_style` 分流。

## 版本演进

业务词「自主」与代码值 `INVITE` 之间的错位是命名遗留，暂无进一步演进证据。

---REVIEW: concept | 自主建档
- 业务词（independentReg / 自主注册）与落值 `INVITE` 不一致，`SELF` 的实际消费分支未在证据中明确，建议核对字典与前端文案。
---END REVIEW---
---END FILE---

---FILE: concepts/dependent_reg.md ---
---
type: concept
title: 非自主建档
page_key: dependent_reg
domain: 准入接入与接入密钥
status: draft
aliases:
  - dependentReg
  - 平台录入
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - db:cust_company_info.identify_style
contract_version: "0.1"
maps_to: cust_company_info.identify_style = 'INVITE_AGW'
also_confused_with:
  - cust_company_info.identify_style = 'INVITE'
adjudication: boundary
boundary: dependentReg落INVITE_AGW，与自主建档INVITE不同。
---

# 非自主建档

## 业务定位

「非自主建档」指由平台/运营侧录入而非客户自主确认的建档流程，代码 `dependentReg` 分支把 [[tables/cust_company_info|cust_company_info]] 的 `identify_style` 置为 `INVITE_AGW`。

## 边界与混淆

与 [[concepts/independent_reg|自主建档]]（`INVITE`）是并列的两条流程入口；同一字段不同取值决定建档提交后直接进审核中还是先进待客户确认（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]）。

## 需求背景

平台代录场景无需客户确认，需缩短流程，因此与自主建档分成两条链路。

## 版本演进

暂无进一步版本演进证据。

---END FILE---
---END FILE---

---FILE: concepts/check_pass.md ---
---
type: concept
title: 审核通过
page_key: check_pass
domain: 准入接入与接入密钥
status: draft
aliases:
  - CUST_CHECK_PASS
  - 已通过
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAuditMsgService.java:getCustBuildStatus
  - db:cust_company_info.check_status
contract_version: "0.1"
maps_to: cust_company_info.check_status = 'CUST_CHECK_PASS'
also_confused_with:
  - cust_company_info.cust_build_status = 'BUILD_SUCCESS'
adjudication: boundary
boundary: check_status是运营中台审核态；cust_build_status是本地建档态，审核通过时联动BUILD_SUCCESS。
---

# 审核通过

## 业务定位

「审核通过」是运营中台给出的审核结论，落在 [[tables/cust_company_info|cust_company_info]] 的 `check_status = 'CUST_CHECK_PASS'`，由回调（`CustAuditMsgService`）更新。

## 边界与混淆

- 与 [[concepts/build_success|建档成功]]（`cust_build_status = 'BUILD_SUCCESS'`）的区别：前者是外部审核态，后者是本地建档态；审核通过会联动本地建档态变为 `BUILD_SUCCESS`，但两者字段、责任方不同。

状态流转见 [[processes/cust_check_status_state_machine|运营审核状态机]]。

## 需求背景

对外展示与内部推进依赖不同的状态字段，需同时保留审核结论与本地推进结果。

## 版本演进

暂无该值变更的证据。

---END FILE---
---END FILE---

---FILE: concepts/build_success.md ---
---
type: concept
title: 建档成功
page_key: build_success
domain: 准入接入与接入密钥
status: draft
aliases:
  - BUILD_SUCCESS
  - 已通过
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAuditMsgService.java:getCustBuildStatus
  - code:CustCompanyInfoApplication.java:confirmCustInfoForSimpleAuth
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status = 'BUILD_SUCCESS'
also_confused_with:
  - cust_company_info.cust_status = 'EFFECT'
adjudication: boundary
boundary: 建档成功同时可能将cust_status置EFFECT。
---

# 建档成功

## 业务定位

「建档成功」是本地建档流程的终态，落在 [[tables/cust_company_info|cust_company_info]] 的 `cust_build_status = 'BUILD_SUCCESS'`。审核通过回调与简易认证确认提交都会迁移到该状态（见 [[processes/cust_build_status_state_machine|企业建档准入状态机]]）。

## 边界与混淆

- 与 [[concepts/check_pass|审核通过]]（`check_status = 'CUST_CHECK_PASS'`）的区别：前者为本地结果，后者为运营中台结论。
- 与 `cust_status = 'EFFECT'` 的区别：建档成功可能同时推动企业主体状态置为 `EFFECT`（[[processes/cust_status_state_machine|企业状态机]]），但企业主体的冻结/注销不改变建档成功这一事实。

## 需求背景

建档结果是重复建档校验、后续业务开通的依据，需要与主体生命周期状态解耦保存。

## 版本演进

暂无该值变更的证据。

---END FILE---
---END FILE---

---FILE: concepts/await_cust_confirm.md ---
---
type: concept
title: 待客户确认
page_key: await_cust_confirm
domain: 准入接入与接入密钥
status: draft
aliases:
  - CUST_CONFIRM_AWAIT
  - AWAIT_CUST_CONFIRM
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustCompanyInfoApplication.java:getCustBuildStatus
  - code:CustAuditMsgService.java:getCustBuildStatus
  - db:cust_company_info.cust_build_status
contract_version: "0.1"
maps_to: cust_company_info.cust_build_status = 'CUST_CONFIRM_AWAIT'
also_confused_with:
  - cust_company_info.cust_build_status = 'AWAIT_CUST_CONFIRM'
adjudication: boundary
boundary: 邀请/自主流程用CUST_CONFIRM_AWAIT；简易认证代码用AWAIT_CUST_CONFIRM，需核对dictKey。
---

# 待客户确认

## 业务定位

「待客户确认」表示建档申请已提交、等待客户侧确认的状态，落在 [[tables/cust_company_info|cust_company_info]] 的 `cust_build_status = 'CUST_CONFIRM_AWAIT'`。运营中台退回客户（`CUST_CHECK_BACKTOCUSTOM`）时，本地建档态也会回到该值。

## 边界与混淆

代码中同时存在 `AWAIT_CUST_CONFIRM`（简易认证分支 `confirmCustInfoForSimpleAuth` 使用）。两者是否同一字典键下的两种写法尚未确认，读库时不可默认等价。

## 需求背景

自主/邀请流程需要客户确认这一中间环节；简易认证流程的确认语义与之接近，因此出现命名近似的两个值。

## 版本演进

`CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 并存，属历史分支遗留，需核对字典键后收敛。

---REVIEW: concept | 待客户确认
- `CUST_CONFIRM_AWAIT` 与 `AWAIT_CUST_CONFIRM` 是否为同一 dictKey 的两个值，语义分析未给出结论，需核对数据字典与简易认证分支代码。
---END REVIEW---
---END FILE---
---END FILE---

---FILE: rules/access_channel_must_exist_and_enabled.md ---
---
type: rule
title: 接入渠道必须存在且启用
page_key: access_channel_must_exist_and_enabled
domain: 准入接入与接入密钥
status: draft
aliases:
  - 渠道校验规则
  - 渠道不存在
oid: 1
scope:
  databases:
    - cust_db
sources:
  - code:CustAccessApplication.validateSetValue
  - code:CustAccessApplication.validateChangeChannelAndTenant
contract_version: "0.1"
---

# 接入渠道必须存在且启用

## 业务定位

该规则是开放接入的第一道门禁：建档、变更渠道、天马建档三条链路均以 `channel + enable='Y'` 查询 [[tables/cust_access_secret|cust_access_secret]]，查不到即拒绝，不再进行租户定位。

## 需求背景

渠道是租户定位与数据隔离的前提，若渠道不存在或已禁用仍允许接入，会出现落库归属不明或已停用渠道继续写入的问题。因此校验在链路入口统一执行，判定条件见 [[calibers/valid_access_channel|有效接入渠道]] 与 [[calibers/disabled_access_channel|禁用接入渠道]]。

## 版本演进

规则在三条链路上被重复实现（建档校验、变更渠道校验、天马渠道校验），暂未见统一抽取的证据。

```ground:rule
name: 接入渠道必须存在且启用
content: 开放API建档、变更、天马建档均按channel + enable=Y查询cust_access_secret，查不到即抛“渠道不存在”。
impact: 接入请求拒绝，后续租户定位无法进行。
field_targets:
  - cust_access_secret.channel
  - cust_access_secret.enable
evidence: "code:CustAccessApplication.validateSetValue/validateChangeChannelAndTenant/validate"
```

---REVIEW: rule | 接入渠道必须存在且启用
- 语义分析中 rules 数组的证据串被截断（止于 `.../validate`），完整代码文件与行号缺失，需补齐 validateSetValueOfTianma 等路径后回填 evidence。
- rules 数组可能还存在其他规则条目但未在本次语义分析中给出，需确认是否遗漏。
---END REVIEW---
---END FILE---