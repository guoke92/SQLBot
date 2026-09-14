---FILE: tables/ca_fee_company.md ---
---
type: table
title: CA服务费企业主数据表
page_key: ca_fee_company
domain: CA证书收费
status: draft
aliases:
  - ca_fee_company
  - CA服务费企业主数据
  - 企业缴费台账行
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
---

`ca_fee_company` 是「CA证书收费」主题下的**企业维度主数据／台账主表**：以 `certification_no`（统一社会信用代码）为企业唯一键，一行代表一个企业在 CA 服务费语境下的缴费状态、CA 状态与服务周期。订单维度见 [[ca_fee_order]]，项目维度见 [[ca_fee_project_config]]。

表内语义分为四簇：① 身份与租户——`certification_no`、`company_name`、`db_tenant_code`、`enable`；② 状态——`pay_status`（企业级缴费汇总，见 [[ca_fee_company_pay_status]]）、`ca_status`（由签章中台状态归一化后同步，见 [[ca_fee_company_ca_status]]）；③ 服务期——`service_start`／`service_end`，由 [[ca_fee_order]] 的订单服务期快照回写，续费提醒与到期刷新见 [[renewal_remind_expire]]；④ 定价与特殊配置——`source_project_id`／`source_company_type` 记录首次锁定来源，`locked_annual_fee`／`fee_locked` 记录首次缴费成功后锁定的年费标准，`special_annual_fee`／`special_config_flag` 承载生效中的特殊配置快照，`renew_remind_sent` 控制本期续费待办是否已生成。定价优先级见 [[annual_fee_pricing_chain]]，白名单判定见 [[whitelist_exempt]]。

`enable = 'Y'` 是台账查询、规则引擎与快照的有效性前提，口径见 [[company_enable_valid]]。

## 需求背景

CA 服务费按「一企一行」沉淀企业主数据，使同一企业在多个项目、多个角色（`CORE`／`SUPPLIER`／`PROJECT_COMPANY`）下的缴费结论可以汇总为单一状态，避免以订单行替代企业状态导致的重复计费。企业级 `pay_status` 与订单级 `order_status` 的分工见 [[pending_payment]]、[[paid_payment]]。

## 版本演进

- v0（本页）：依据语义分析中 `evidence=db` 的字段清单建立首版字段契约，未引入未证实主张。

```ground:table
table: ca_fee_company
fields:
  - name: certification_no
    type: unknown
    desc: 统一社会信用代码，CA服务费企业主数据唯一键，用于关联订单、企业主数据
    dict: null
  - name: company_name
    type: unknown
    desc: 企业名称
    dict: null
  - name: pay_status
    type: unknown
    desc: 企业维度缴费状态：PAID 已缴费 / UNPAID 未缴费
    dict: null
  - name: ca_status
    type: unknown
    desc: CA签章状态，由签章中台状态归一化后同步，如 NORMAL/CANCELLED/UNKNOWN
    dict: null
  - name: service_start
    type: unknown
    desc: 当前 CA 服务费服务周期起始日
    dict: null
  - name: service_end
    type: unknown
    desc: 当前 CA 服务费服务周期截止日
    dict: null
  - name: source_project_id
    type: unknown
    desc: 首次锁定来源项目 ID
    dict: null
  - name: source_company_type
    type: unknown
    desc: 首次锁定来源企业角色：CORE/SUPPLIER/PROJECT_COMPANY
    dict: null
  - name: locked_annual_fee
    type: unknown
    desc: 首次缴费成功后锁定的年费标准
    dict: null
  - name: special_annual_fee
    type: unknown
    desc: 特殊配置后应缴年费
    dict: null
  - name: special_config_flag
    type: unknown
    desc: 是否存在生效中的特殊配置快照
    dict: null
  - name: fee_locked
    type: unknown
    desc: 是否已锁定年费标准
    dict: null
  - name: renew_remind_sent
    type: unknown
    desc: 本期续费待办是否已生成：Y/N
    dict: null
  - name: enable
    type: unknown
    desc: 有效标识
    dict: null
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: null
```

---END FILE---

---FILE: tables/ca_fee_order.md ---
---
type: table
title: CA服务费订单表
page_key: ca_fee_order
domain: CA证书收费
status: draft
aliases:
  - ca_fee_order
  - CA服务费订单
  - 缴费订单行
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
  - db
contract_version: "0.1"
---

`ca_fee_order` 是**订单维度**的收费单据表，一行代表一次首次缴费、续费或存量补录行为，业务标识为 `order_no`（见 [[fee_order]]）。企业维度的汇总状态在 [[ca_fee_company]]，项目维度的收费开关与费率在 [[ca_fee_project_config]]。

关键分组：① 生命周期——`order_status`（见 [[ca_fee_order_status]]）、`close_reason`、`order_type`（FIRST／RENEW／RENEW_EXPIRED／STOCK）；② 协议——`agreement_signed`（见 [[ca_fee_order_agreement_signed]]、[[fee_agreement]]）、`agreement_version`；③ 金额与支付——`annual_fee`、`pay_amount`、`pay_method`（当前主要支持 `BOCOM` 交e保，见 [[bocom]]）、`pay_time`；④ 服务期快照——`service_start`／`service_end`，是企业主数据当前服务期的来源（见 [[service_period]]）；⑤ 发票——`invoice_status`（见 [[ca_fee_order_invoice_status]]）；⑥ 交e保渠道字段——`bocom_txn_sts`（`00`／`01`／`02`）、`bocom_plfm_ser_no`、`bocom_plfm_bsn_id`、`bocom_req_sn`，幂等与查证逻辑见 [[bocom_idempotent_verify]]；⑦ 归属——`project_id`、`company_id`、`company_type`（`CORE`／`SUPPLIER`／`PROJECT_COMPANY`）。

订单是协议签署、支付、开票、台账编辑等可操作动作的最小载体，因此绝大多数限制性规则（[[agreement_sign_prerequisite]]、[[ledger_edit_limit]]）都落在 `order_status` 与 `bocom_txn_sts` 上。

## 需求背景

订单与企业主数据解耦，使「一次缴费」与「当前服务期」分别可追溯：订单保留签署时的协议版本与年费金额快照，企业主数据只保留当前有效结论。年费标准由 [[annual_fee_pricing_chain]] 解析后写入本表 `annual_fee`。

## 版本演进

- v0（本页）：依据语义分析字段清单建立契约；`EXPIRED` 状态枚举存在但未使用，按订单状态机页标注为「未使用」。

```ground:table
table: ca_fee_order
fields:
  - name: order_no
    type: unknown
    desc: CA服务费订单号
    dict: null
  - name: order_status
    type: unknown
    desc: 订单状态：PENDING 未缴费 / PAID 已缴费 / CLOSED 已关闭；EXPIRED 枚举存在但未使用
    dict: null
  - name: order_type
    type: unknown
    desc: 订单类型：FIRST 首次缴费 / RENEW 即将到期续费 / RENEW_EXPIRED 已到期续费 / STOCK 存量补录
    dict: null
  - name: agreement_signed
    type: unknown
    desc: 是否已签署收费协议：Y/N
    dict: null
  - name: agreement_version
    type: unknown
    desc: 签署时绑定的收费协议版本号
    dict: null
  - name: annual_fee
    type: unknown
    desc: 应缴年费
    dict: null
  - name: pay_amount
    type: unknown
    desc: 实缴金额
    dict: null
  - name: pay_method
    type: unknown
    desc: 支付方式，当前代码主要支持 BOCOM 交e保
    dict: null
  - name: pay_time
    type: unknown
    desc: 支付时间
    dict: null
  - name: service_start
    type: unknown
    desc: 订单服务周期起始日快照
    dict: null
  - name: service_end
    type: unknown
    desc: 订单服务周期截止日快照
    dict: null
  - name: invoice_status
    type: unknown
    desc: 发票状态：NONE/PENDING/ISSUED/FAILED
    dict: null
  - name: bocom_txn_sts
    type: unknown
    desc: 交e保划扣响应状态：00 成功 / 01 明确失败 / 02 待查证
    dict: null
  - name: bocom_plfm_ser_no
    type: unknown
    desc: 交e保平台流水号
    dict: null
  - name: bocom_plfm_bsn_id
    type: unknown
    desc: 交e保平台业务编号
    dict: null
  - name: bocom_req_sn
    type: unknown
    desc: 交e保请求流水号
    dict: null
  - name: close_reason
    type: unknown
    desc: 订单关闭原因
    dict: null
  - name: project_id
    type: unknown
    desc: 订单所属项目 ID
    dict: null
  - name: company_id
    type: unknown
    desc: 企业 ID
    dict: null
  - name: company_type
    type: unknown
    desc: 企业角色：CORE/SUPPLIER/PROJECT_COMPANY
    dict: null
```

---END FILE---

---FILE: tables/ca_fee_project_config.md ---
---
type: table
title: CA收费项目配置表
page_key: ca_fee_project_config
domain: CA证书收费
status: draft
aliases:
  - ca_fee_project_config
  - CA收费配置
  - 项目收费配置
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

`ca_fee_project_config` 是**项目维度**的收费配置表，决定某个项目是否参与 CA 服务费收费、各角色年费标准以及特殊企业名单。它是规则引擎评估的第一道闸门（见 [[project_charge_switch]]），与订单表 [[ca_fee_order]]、企业主数据 [[ca_fee_company]] 构成「项目—订单—企业」三层结构。

`charge_enabled` 是收费总开关（口径见 [[project_charge_enabled]]）；`core_annual_fee`／`supplier_annual_fee` 是角色价，参与 [[annual_fee_pricing_chain]]；`special_company_list` 是特殊企业配置 JSON，承载 `WHITELIST`／`SPECIAL_PRICE`／`DEFER_PAY` 三类语义，其判定见 [[whitelist]]、[[whitelist_exempt]]、[[defer_pay_exempt]]；`pay_channel` 为支付渠道配置 JSON；`agreement_version` 为项目绑定收费协议版本；`enable` 为有效标识。

## 需求背景

收费能力按项目灰度：同一个企业可能在多个项目下有角色，是否收费取决于各项目自身的 `charge_enabled`，因此需要项目级配置源与项目级特殊名单，二者需与企业侧快照交叉校验（企业快照仅用于规则快速判断）。

## 版本演进

- v0（本页）：依据语义分析中 `evidence=code` 的字段清单建立契约。

```ground:table
table: ca_fee_project_config
fields:
  - name: project_id
    type: unknown
    desc: CA收费配置所属项目 ID
    dict: null
  - name: charge_enabled
    type: unknown
    desc: 项目是否开启CA收费：Y/N
    dict: null
  - name: core_annual_fee
    type: unknown
    desc: 项目核企年费标准
    dict: null
  - name: supplier_annual_fee
    type: unknown
    desc: 项目供应商年费标准
    dict: null
  - name: special_company_list
    type: unknown
    desc: 项目特殊企业配置 JSON，承载 WHITELIST/SPECIAL_PRICE/DEFER_PAY
    dict: null
  - name: pay_channel
    type: unknown
    desc: 支付渠道配置 JSON
    dict: null
  - name: agreement_version
    type: unknown
    desc: 项目绑定收费协议版本
    dict: null
  - name: enable
    type: unknown
    desc: 有效标识
    dict: null
```

---END FILE---

---FILE: processes/ca_fee_order_status.md ---
---
type: process
title: CA服务费订单状态机
page_key: ca_fee_order_status
domain: CA证书收费
status: draft
aliases:
  - 订单状态
  - order_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

订单状态机作用于 [[ca_fee_order]] 的 `order_status`，是支付、关闭、台账展示与重新评估建单的共同支点。`PENDING` 是唯一可支付、可签署协议、可人工关闭的状态（口径 [[order_status_pending]]）；`PAID` 表示缴费完成（口径 [[order_status_paid]]）；`CLOSED` 表示订单终止（口径 [[order_status_closed]]）；`EXPIRED` 枚举存在但**未使用**。

进入 `PAID` 的路径是「订单维度支付成功」，同时会回写企业维度 `pay_status`（见 [[ca_fee_company_pay_status]]、[[paid_payment]]）；进入 `CLOSED` 的路径有三类：人工关闭、批量白名单命中时关闭待缴单（见 [[batch_whitelist_defer]]）、以及到期处理流程中的关闭（见 [[renewal_remind_expire]]）。

## 需求背景

订单状态既是操作闸门也是统计口径：待缴费口径用于筛选可操作订单，已缴费口径用于台账展示与编辑限制（[[ledger_edit_limit]]），已关闭口径用于台账历史过滤与重新评估建单。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机；`EXPIRED` 保留为已定义未使用状态。

```ground:process
name: CA服务费订单状态
field: ca_fee_order.order_status
states:
  - value: PENDING
    label: 未缴费
    source: code_enum
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: CLOSED
    label: 已关闭
    source: code_enum
  - value: EXPIRED
    label: 已过期
    source: code_enum
transitions:
  - from: PENDING
    event: 支付成功 markPaid
    to: PAID
    evidence: code_path:CaFeeOrderService.java:279 + CaFeePaymentApplication.java
  - from: PENDING
    event: 关闭订单 closeOrder
    to: CLOSED
    evidence: code_path:CaFeeOrderApplication.java + CaFeeOrderService.java
  - from: PENDING
    event: 批量白名单命中并关闭待缴单
    to: CLOSED
    evidence: code_path:CaFeeLedgerOperateService.java
```

---END FILE---

---FILE: processes/ca_fee_company_pay_status.md ---
---
type: process
title: 企业缴费状态机
page_key: ca_fee_company_pay_status
domain: CA证书收费
status: draft
aliases:
  - 企业缴费状态
  - pay_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

企业缴费状态机作用于 [[ca_fee_company]] 的 `pay_status`，是**企业维度汇总状态**，必须与订单维度 `ca_fee_order.order_status` 区分：订单级未缴是 `PENDING`，企业级未缴汇总是 `UNPAID`（见 [[pending_payment]]、[[paid_payment]]）。

迁移只有两条：订单缴费成功时回写为 `PAID`；服务到期处理（`markServiceExpired`）时回落为 `UNPAID`，后者由续费与到期规则驱动，见 [[renewal_remind_expire]]。`UNPAID` 并不等价于「立刻需要缴费」——多项目放行与豁免规则（[[multi_project_pass]]、[[whitelist_exempt]]、[[defer_pay_exempt]]、[[already_paid_in_service]]）会先于收费结论生效。

## 需求背景

企业级状态的引入使台账统计与「已缴费／未缴费企业筛选」可直接基于一行完成，无需对订单表做聚合；同时作为规则引擎的快速判断依据。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机。

```ground:process
name: 企业缴费状态
field: ca_fee_company.pay_status
states:
  - value: PAID
    label: 已缴费
    source: code_enum
  - value: UNPAID
    label: 未缴费
    source: code_enum
transitions:
  - from: UNPAID
    event: 订单缴费成功回写企业缴费状态
    to: PAID
    evidence: code_path:CaFeeOrderService.java:450
  - from: PAID
    event: 服务到期处理 markServiceExpired
    to: UNPAID
    evidence: code_path:CaFeeRenewalService.java
```

---END FILE---

---FILE: processes/ca_fee_order_agreement_signed.md ---
---
type: process
title: 收费协议签署状态机
page_key: ca_fee_order_agreement_signed
domain: CA证书收费
status: draft
aliases:
  - 协议签署状态
  - agreement_signed
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

收费协议签署状态机作用于 [[ca_fee_order]] 的 `agreement_signed`，是一个**单向开关**：`N` 未签署 → `Y` 已签署，不存在回退迁移。签署时同时绑定 `agreement_version`（签署时的协议版本），二者语义边界见 [[fee_agreement]]。

该状态是支付前置条件：交e保开户与确认打款前必须为 `Y`，否则抛出「请先签署收费协议」，见 [[agreement_sign_prerequisite]]，口径见 [[agreement_signed_y]]。

## 需求背景

CA 服务费属于新增商业模式，需要以订单为粒度留存收费协议的签署事实与版本，供支付前置校验与后续审计使用；协议签署与支付被显式解耦为两步。

## 版本演进

- v0（本页）：依据语义分析中的状态与迁移证据建立首版状态机。

```ground:process
name: 收费协议签署状态
field: ca_fee_order.agreement_signed
states:
  - value: N
    label: 未签署
    source: code_const
  - value: Y
    label: 已签署
    source: code_const
transitions:
  - from: N
    event: 签署收费协议 markAgreementSigned
    to: Y
    evidence: code_path:CaFeeOrderService.java:337 + CaFeeAgreementApplication.java
```

---END FILE---

---FILE: processes/ca_fee_company_ca_status.md ---
---
type: process
title: CA签章状态机
page_key: ca_fee_company_ca_status
domain: CA证书收费
status: draft
aliases:
  - CA签章状态
  - ca_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code
contract_version: "0.1"
---

CA 签章状态机作用于 [[ca_fee_company]] 的 `ca_status`，**不是**一个由本地业务流驱动的状态机：它是签章中台状态归一化后同步的结果。语义分析中区分了两组取值来源——来自 DB 分布（`db_dist`）的 `NORMAL`／`CANCELLED`／`UNKNOWN`，以及来自代码常量（`code_const`）的 `APPLYING`／`EXPIRED`／`FAIL`；两组的归一化关系在当前证据中缺失，故未给出迁移边。

收费判定只依赖其中三个归一口径：`NORMAL`（[[ca_status_normal]]）、`CANCELLED`（[[ca_status_cancelled]]）、`UNKNOWN`（[[ca_status_unknown]]）。

## 需求背景

CA 状态与收费状态是两条正交语义（见 [[ca_service_fee]] 辨析）：`ca_status` 描述证书有效性，`pay_status` 描述费用缴纳。失效状态会触发提示与重置开通状态，未知状态作为查询失败／未注册的兜底展示。

## 版本演进

- v0（本页）：依据语义分析建立状态清单；`db_dist` 与 `code_const` 两组取值的映射关系未在证据中给出，待补。

```ground:process
name: CA签章状态
field: ca_fee_company.ca_status
states:
  - value: NORMAL
    label: CA正常
    source: db_dist
  - value: CANCELLED
    label: CA注销/作废/失效
    source: db_dist
  - value: UNKNOWN
    label: CA状态未知
    source: db_dist
  - value: APPLYING
    label: CA申请中
    source: code_const
  - value: EXPIRED
    label: CA已过期
    source: code_const
  - value: FAIL
    label: CA申请失败
    source: code_const
transitions: []
```

---END FILE---

---FILE: processes/ca_fee_order_invoice_status.md ---
---
type: process
title: 发票状态机
page_key: ca_fee_order_invoice_status
domain: CA证书收费
status: draft
aliases:
  - 发票状态
  - invoice_status
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
---

发票状态机作用于 [[ca_fee_order]] 的 `invoice_status`，与缴费主流程**异步**：缴费成功后由 `CaFeeInvoiceApplication.requestInvoiceAsync` 将 `invoice_status` 置为 `PENDING`，已存在非 `NONE` 状态则跳过，见 [[invoice_async]]、[[invoice_status_pending]]。

`NONE` 表示无需开票（初始态），`PENDING` 开票中，`ISSUED` 已开票，`FAILED` 开票失败。开票失败后的重试路径在当前证据中未给出。

## 需求背景

开票不阻塞缴费主流程：缴费成功页仅提示「开票中」，开票动作由异步任务承担，因此发票状态与订单状态可以短暂不一致。

## 版本演进

- v0（本页）：依据语义分析建立首版状态机；`FAILED` 之后的恢复路径待补。

```ground:process
name: 发票状态
field: ca_fee_order.invoice_status
states:
  - value: NONE
    label: 无需开票
    source: code_enum
  - value: PENDING
    label: 开票中
    source: code_enum
  - value: ISSUED
    label: 已开票
    source: code_enum
  - value: FAILED
    label: 开票失败
    source: code_enum
transitions:
  - from: NONE
    event: 缴费成功后异步申请开票
    to: PENDING
    evidence: code_path:CaFeeInvoiceApplication.java:49
```

---END FILE---

---FILE: calibers/project_charge_enabled.md ---
---
type: caliber
title: 项目开启CA收费
page_key: project_charge_enabled
domain: CA证书收费
status: draft
aliases:
  - charge_enabled = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

该口径判定一个项目是否进入 CA 服务费收费流程，是规则引擎评估的**前置条件**：项目不存在 [[ca_fee_project_config]] 行或 `charge_enabled <> 'Y'` 时直接豁免（见 [[project_charge_switch]]）。多项目企业按项目逐个通过本口径筛选后再评估（见 [[multi_project_pass]]）。

## 需求背景

收费按项目灰度开放，本口径是「不收费」与「可能收费」的分界线，必须先于定价与豁免判定执行。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 项目开启CA收费
predicate: ca_fee_project_config.charge_enabled = 'Y'
scope: 规则引擎评估收费项目的前置条件
evidence: CaFeeRuleEngineService.java
```

---END FILE---

---FILE: calibers/company_enable_valid.md ---
---
type: caliber
title: 有效企业主数据
page_key: company_enable_valid
domain: CA证书收费
status: draft
aliases:
  - enable = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
---

有效企业主数据口径限定 [[ca_fee_company]] 中 `enable = 'Y'` 的行，用于台账查询、规则引擎评估与企业快照读取。所有企业维度的统计与判定都应先经过本口径，避免把历史失效行纳入计算。

## 需求背景

企业主数据存在失效（关闭／合并等）场景，需要在查询入口统一过滤，保证台账口径与规则结论一致。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 有效企业主数据
predicate: ca_fee_company.enable = 'Y'
scope: 台账查询、规则引擎、企业快照
evidence: CaFeeLedgerQueryService.java
```

---END FILE---

---FILE: calibers/company_pay_status_paid.md ---
---
type: caliber
title: 企业已缴费口径
page_key: company_pay_status_paid
domain: CA证书收费
status: draft
aliases:
  - 企业已缴费
  - PAY_STAUS_PAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
---

企业已缴费口径指 [[ca_fee_company]] 中 `pay_status = 'PAID'` 的行，用于台账统计与已缴费企业筛选。它与订单级「已缴费」是两个层级，辨析见 [[paid_payment]]。

## 需求背景

台账需要以企业为单位给出已缴费名单，而不是按订单行罗列；服务期内不重复收费的判定亦会参考该状态（见 [[already_paid_in_service]]）。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业已缴费口径
predicate: ca_fee_company.pay_status = 'PAID'
scope: 台账统计、已缴费企业筛选
evidence: db + CaFeeLedgerQueryService.java
```

---END FILE---

---FILE: calibers/company_pay_status_unpaid.md ---
---
type: caliber
title: 企业未缴费口径
page_key: company_pay_status_unpaid
domain: CA证书收费
status: draft
aliases:
  - 企业未缴费
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
---

企业未缴费口径指 [[ca_fee_company]] 中 `pay_status = 'UNPAID'` 的行，用于台账统计与未缴费企业筛选。命中本口径不等于必须立即缴费，仍需通过豁免与放行规则（见 [[whitelist_exempt]]、[[defer_pay_exempt]]、[[multi_project_pass]]）。

## 需求背景

企业级未缴是汇总结论，订单级待缴是可操作对象，二者混用会导致运营误操作，故单列口径，辨析见 [[pending_payment]]。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业未缴费口径
predicate: ca_fee_company.pay_status = 'UNPAID'
scope: 台账统计、未缴费企业筛选
evidence: db + CaFeeLedgerQueryService.java
```

---END FILE---

---FILE: calibers/order_status_pending.md ---
---
type: caliber
title: 订单未缴费口径
page_key: order_status_pending
domain: CA证书收费
status: draft
aliases:
  - 待缴订单
  - PENDING
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeOrderApplication.java
contract_version: "0.1"
---

订单未缴费口径指 [[ca_fee_order]] 中 `order_status = 'PENDING'` 的行，界定协议签署、支付、关闭订单的**可操作范围**。台账编辑同样只在此状态（与 `PAID`）下开放，见 [[ledger_edit_limit]]。

## 需求背景

支付与签署动作必须以订单为闸门，避免在企业级汇总状态上做状态迁移，从而保证一笔订单一次缴费的可追溯性。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单未缴费口径
predicate: ca_fee_order.order_status = 'PENDING'
scope: 协议签署、支付、关闭订单可操作范围
evidence: CaFeeOrderApplication.java
```

---END FILE---

---FILE: calibers/order_status_paid.md ---
---
type: caliber
title: 订单已缴费口径
page_key: order_status_paid
domain: CA证书收费
status: draft
aliases:
  - 已缴订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeOrderApplication.java
contract_version: "0.1"
---

订单已缴费口径指 [[ca_fee_order]] 中 `order_status = 'PAID'` 的行，用于缴费成功判定、台账展示与编辑限制（已缴费订单不允许改回未缴费，见 [[ledger_edit_limit]]）。服务期内已缴费豁免亦会以「存在 PAID 且服务期覆盖今天的订单」为条件，见 [[already_paid_in_service]]。

## 需求背景

订单级已缴费是金额与协议快照的最终确认态，与 [[company_pay_status_paid]] 的企业级汇总状态分工明确。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单已缴费口径
predicate: ca_fee_order.order_status = 'PAID'
scope: 缴费成功、台账展示、编辑限制
evidence: CaFeeOrderApplication.java
```

---END FILE---

---FILE: calibers/order_status_closed.md ---
---
type: caliber
title: 订单已关闭口径
page_key: order_status_closed
domain: CA证书收费
status: draft
aliases:
  - 已关闭订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerQueryService.java
contract_version: "0.1"
---

订单已关闭口径指 [[ca_fee_order]] 中 `order_status = 'CLOSED'` 的行，用于台账历史过滤与「重新评估建单」的前置判断：已关闭订单不参与可操作订单集合。关闭原因记录在 `close_reason`。

## 需求背景

批量白名单、到期处理与人工关闭都会产生关闭态订单（见 [[batch_whitelist_defer]]、[[renewal_remind_expire]]），需要一个统一口径将其排除在活跃订单之外。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 订单已关闭口径
predicate: ca_fee_order.order_status = 'CLOSED'
scope: 台账历史过滤、重新评估建单
evidence: CaFeeLedgerQueryService.java
```

---END FILE---

---FILE: calibers/agreement_signed_y.md ---
---
type: caliber
title: 收费协议已签署
page_key: agreement_signed_y
domain: CA证书收费
status: draft
aliases:
  - agreement_signed = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
contract_version: "0.1"
---

该口径指 [[ca_fee_order]] 中 `agreement_signed = 'Y'`，是交e保支付的**前置校验**条件，见 [[agreement_sign_prerequisite]]、[[ca_fee_order_agreement_signed]]。签署状态与协议版本字段的边界见 [[fee_agreement]]。

## 需求背景

收费协议签署是合规要求：未签署不允许进入开户与确认打款，故在支付入口以本口径拦截。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 收费协议已签署
predicate: ca_fee_order.agreement_signed = 'Y'
scope: 交e保支付前置校验
evidence: CaFeePaymentApplication.java
```

---END FILE---

---FILE: calibers/company_special_config_flag.md ---
---
type: caliber
title: 企业存在特殊配置快照
page_key: company_special_config_flag
domain: CA证书收费
status: draft
aliases:
  - special_config_flag = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

该口径指 [[ca_fee_company]] 中 `special_config_flag = 'Y'`，用于白名单／定向减免判定。它是企业侧**快照**标记，需与项目配置 `ca_fee_project_config.special_company_list` 交叉校验后才生效，辨析见 [[whitelist]]，落规则见 [[whitelist_exempt]]。

## 需求背景

规则引擎需要在评估时快速判断企业是否处于特殊名单，故在企業主数据上冗余快照标记；配置源仍在项目侧，二者不一致时应以交叉校验结果为准。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业存在特殊配置快照
predicate: ca_fee_company.special_config_flag = 'Y'
scope: 白名单/定向减免判定
evidence: db + CaFeeRuleEngineService.java
```

---END FILE---

---FILE: calibers/company_fee_locked.md ---
---
type: caliber
title: 企业已锁定年费
page_key: company_fee_locked
domain: CA证书收费
status: draft
aliases:
  - fee_locked = Y
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

该口径指 [[ca_fee_company]] 中 `fee_locked = 'Y'`，表示企业已锁定年费标准（`locked_annual_fee`）。在年费定价链中，锁定价优先于项目角色价，见 [[annual_fee_pricing_chain]]。

## 需求背景

首次缴费成功后需要固定价格，避免项目调价影响已购企业的续费金额；因此需要「是否已锁定」的可判定口径。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 企业已锁定年费
predicate: ca_fee_company.fee_locked = 'Y'
scope: 年费定价链锁定价优先
evidence: db + CaFeeRuleEngineService.java
```

---END FILE---

---FILE: calibers/bocom_txn_sts_00.md ---
---
type: caliber
title: 交e保划扣成功
page_key: bocom_txn_sts_00
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 00
  - 划扣成功
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeConstants.java
contract_version: "0.1"
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '00'`，表示交e保划扣成功。它用于**补单**与**幂等拦截**：订单已存在成功流水时不再重复扣款，见 [[bocom_idempotent_verify]]。

## 需求背景

交e保渠道存在回执延迟与重复发起风险，需要以银行响应状态为准做幂等，而非仅依赖本地订单状态。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣成功
predicate: ca_fee_order.bocom_txn_sts = '00'
scope: 补单/幂等拦截
evidence: db + CaFeeConstants.java
```

---END FILE---

---FILE: calibers/bocom_txn_sts_01.md ---
---
type: caliber
title: 交e保划扣明确失败
page_key: bocom_txn_sts_01
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 01
  - 划扣明确失败
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeConstants.java
contract_version: "0.1"
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '01'`，表示银行侧明确失败，用于**禁止重复划扣**。与 `02` 待查证的区别在于：`01` 是确定性结论，`02` 需要向银行查证后才有结论，见 [[bocom_txn_sts_02]]、[[bocom_idempotent_verify]]。

## 需求背景

明确失败若允许再次发起，会导致同一订单反复出金尝试与对账困难，故在支付入口直接拦截。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣明确失败
predicate: ca_fee_order.bocom_txn_sts = '01'
scope: 禁止重复划扣
evidence: CaFeeConstants.java
```

---END FILE---

---FILE: calibers/bocom_txn_sts_02.md ---
---
type: caliber
title: 交e保划扣待查证
page_key: bocom_txn_sts_02
domain: CA证书收费
status: draft
aliases:
  - bocom_txn_sts = 02
  - 划扣待查证
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeConstants.java
contract_version: "0.1"
---

该口径指 [[ca_fee_order]] 中 `bocom_txn_sts = '02'`，表示划扣结果待查证。它同时约束两处：定时补偿任务向银行查证（成功则补 `markPaid`，明确失败则禁止再次划扣），以及**台账编辑拦截**（不允许人工把待查证订单标记为已缴费），见 [[bocom_idempotent_verify]]、[[ledger_edit_limit]]。

## 需求背景

银行响应超时会产生「不确定」，若人工介入可能造成状态与资金不一致，故以中间态冻结人工操作，改由查证任务收敛。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 交e保划扣待查证
predicate: ca_fee_order.bocom_txn_sts = '02'
scope: 定时补偿查证、台账编辑拦截
evidence: CaFeeConstants.java
```

---END FILE---

---FILE: calibers/invoice_status_pending.md ---
---
type: caliber
title: 发票开票中
page_key: invoice_status_pending
domain: CA证书收费
status: draft
aliases:
  - invoice_status = PENDING
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeInvoiceApplication.java
contract_version: "0.1"
---

该口径指 [[ca_fee_order]] 中 `invoice_status = 'PENDING'`，用于缴费成功页提示与异步开票前置判断：已处于非 `NONE` 状态时跳过重复申请，见 [[invoice_async]]、[[ca_fee_order_invoice_status]]。

## 需求背景

开票为异步动作，需要中间状态向用户表达「开票中」，同时作为幂等条件防止重复提交开票请求。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: 发票开票中
predicate: ca_fee_order.invoice_status = 'PENDING'
scope: 缴费成功页提示、异步开票前置
evidence: CaFeeInvoiceApplication.java
```

---END FILE---

---FILE: calibers/ca_status_normal.md ---
---
type: caliber
title: CA状态正常
page_key: ca_status_normal
domain: CA证书收费
status: draft
aliases:
  - ca_status = NORMAL
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaCertificationPreCheckApplication.java
contract_version: "0.1"
---

该口径指 [[ca_fee_company]] 中 `ca_status = 'NORMAL'`，用于 CA 有效性判断。`NORMAL` 是签章中台归一化后的正常态，见 [[ca_fee_company_ca_status]]、[[ca_status_cancelled]]、[[ca_status_unknown]]。

## 需求背景

收费与签章是两条链路（辨析见 [[ca_service_fee]]）：收费判定需要知道企业当前 CA 是否可用，故在收费前置检查中读取 CA 归一化状态。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态正常
predicate: ca_fee_company.ca_status = 'NORMAL'
scope: CA有效性判断
evidence: db + CaCertificationPreCheckApplication.java
```

---END FILE---

---FILE: calibers/ca_status_cancelled.md ---
---
type: caliber
title: CA状态失效
page_key: ca_status_cancelled
domain: CA证书收费
status: draft
aliases:
  - ca_status = CANCELLED
  - CA注销
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaCertificationPreCheckApplication.java
contract_version: "0.1"
---

该口径指 [[ca_fee_company]] 中 `ca_status = 'CANCELLED'`，覆盖 CA 注销／作废／失效三种中台语义的归并结果，用于 CA 失效提示与重置开通状态。

## 需求背景

失效态需要显式提示并触发开通状态重置，否则企业会停留在「看似有效」的收费判定上。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态失效
predicate: ca_fee_company.ca_status = 'CANCELLED'
scope: CA失效提示与重置开通状态
evidence: db + CaCertificationPreCheckApplication.java
```

---END FILE---

---FILE: calibers/ca_status_unknown.md ---
---
type: caliber
title: CA状态未知
page_key: ca_status_unknown
domain: CA证书收费
status: draft
aliases:
  - ca_status = UNKNOWN
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaCertificationPreCheckApplication.java
contract_version: "0.1"
---

该口径指 [[ca_fee_company]] 中 `ca_status = 'UNKNOWN'`，作为查询失败或企业未注册时的兜底展示态。它不是业务终态，而是「中台未给出确定结论」的表达。

## 需求背景

中台查询可能失败或企业尚未在签章侧注册，需要与其他状态区分，避免被误判为正常或失效。

## 版本演进

- v0（本页）：依据语义分析口径证据建立。

```ground:caliber
name: CA状态未知
predicate: ca_fee_company.ca_status = 'UNKNOWN'
scope: 查询失败/未注册兜底展示
evidence: db + CaCertificationPreCheckApplication.java
```

---END FILE---

---FILE: concepts/ca_service_fee.md ---
---
type: concept
title: CA服务费
page_key: ca_service_fee
domain: CA证书收费
status: draft
aliases:
  - CA证书收费
  - CA收费
  - 电子认证服务费
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeController.java + reqdoc:ca-fee-mvp-phase1-20260625
  - code_path:CaFeePaymentCheckApplication.java + reqdoc:ca-fee-mvp-phase1-20260625
  - code_path:CaFeeRuleEngineService.java + reqdoc:ca-fee-mvp-phase1-20260625
contract_version: "0.1"
maps_to: ca_fee_order.annual_fee
field_targets:
  - ca_fee_order.annual_fee
adjudication: boundary
boundary: 费用金额字段是 annual_fee；ca_status 是证书状态，不是收费金额
also_confused_with:
  - ca_fee_company.ca_status
---

> (document_claim，未证实)：CA证书收费需求由产品经理张彬伟（Vincent）负责。

「CA服务费」指对使用电子认证服务（CA 证书）的用户开通的收费模式，在数据上落到**费用金额**字段：订单侧的 `ca_fee_order.annual_fee`（应缴年费）与其实际缴纳结果 `pay_amount`。它与管理对象 `ca_fee_company`、配置源 `ca_fee_project_config` 共同构成「项目—订单—企业」三层。

**边界（易混淆）**：`ca_service_fee` 与 [[ca_status_normal]] 等 CA 状态不是一回事——`ca_status` 描述证书是否有效，`annual_fee` 描述要收多少钱。讨论「CA 收费」时若引用了 `ca_fee_company.ca_status`，应校正到费用字段。

## 需求背景

CA 证书收费是产融平台 V1.32 版本推出的全新商业模式／产品功能点，对使用电子认证服务（CA 证书）的用户开通收费模式。这一主张在代码侧有落点：`CaFeeController`（入口）、`CaFeePaymentCheckApplication`（缴费校验）、`CaFeeRuleEngineService`（收费规则引擎），并与需求文档 `CA服务费MVP版本（一期）需求文档-20260625` 对应；该外部文档未内联具体收费规则、计费页面与维护流程，故本主题的规则与页面契约以代码与库表证据为准。

## 版本演进

- v0（本页）：建立术语桥与边界；记录 V1.32 全新商业模式的主张来源（代码 + 需求文档双源）。
- (document_claim，未证实)：CA证书收费需求由产品经理张彬伟（Vincent）负责——代码侧无对应证据，仅作需求侧归属记录。

---END FILE---

---FILE: concepts/fee_order.md ---
---
type: concept
title: 缴费订单
page_key: fee_order
domain: CA证书收费
status: draft
aliases:
  - CA服务费订单
  - 订单
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_order.order_no
field_targets:
  - ca_fee_order.order_no
adjudication: boundary
boundary: 订单维度以 order_no 标识；企业维度以 certification_no 一统码一行
also_confused_with:
  - ca_fee_company.certification_no
---

「缴费订单」在数据上以 `ca_fee_order.order_no` 标识，一行代表一次缴费行为；对应的表页是 [[ca_fee_order]]，状态语义见 [[ca_fee_order_status]]。

**边界（易混淆）**：企业维度以 [[ca_fee_company]] 的 `certification_no` 一行汇总，不能以订单行代替企业状态；统计「有多少企业已缴」应走企业主数据而非订单表。

## 需求背景

订单作为签署、支付、开票与台账编辑的操作载体，需要稳定业务编号；企业主数据则承担跨项目、跨角色的汇总职责，二者分层是收费模型的基础。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/pending_payment.md ---
---
type: concept
title: 待缴费
page_key: pending_payment
domain: CA证书收费
status: draft
aliases:
  - 未缴费
  - PENDING
  - UNPAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_order.order_status
field_targets:
  - ca_fee_order.order_status
adjudication: boundary
boundary: 订单级待缴是 PENDING；企业级未缴汇总是 UNPAID
also_confused_with:
  - ca_fee_company.pay_status
---

「待缴费」是口语化的复合说法，对应两个不同层级的状态字段：订单级 `ca_fee_order.order_status = 'PENDING'`（值 `PENDING`，口径 [[order_status_pending]]），与企业级 `ca_fee_company.pay_status = 'UNPAID'`（值 `UNPAID`，口径 [[company_pay_status_unpaid]]）。

**边界（易混淆）**：订单级待缴是**可操作对象**（可签署协议、可支付、可关闭）；企业级未缴是**汇总结论**（用于统计与筛选）。同一个企业可以「有未缴汇总」但「无可操作待缴订单」。

## 需求背景

三层数据模型（项目—订单—企业）自然会引出同义口语，必须在术语层固定映射，否则运营提问「这单还欠费吗」与「这家企业还欠费吗」会被混为一谈。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/paid_payment.md ---
---
type: concept
title: 已缴费
page_key: paid_payment
domain: CA证书收费
status: draft
aliases:
  - PAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_company.pay_status
field_targets:
  - ca_fee_company.pay_status
adjudication: boundary
boundary: 企业已缴费是汇总状态；订单已缴费是单笔订单状态
also_confused_with:
  - ca_fee_order.order_status
---

「已缴费」主映射取企业维度 `ca_fee_company.pay_status = 'PAID'`（口径 [[company_pay_status_paid]]），订单维度 `ca_fee_order.order_status = 'PAID'` 是其单笔来源（口径 [[order_status_paid]]，状态机见 [[ca_fee_order_status]]）。

**边界（易混淆）**：企业已缴费是**汇总状态**，可能由服务期内的历史订单支撑；订单已缴费是**单笔事实**，决定该订单不可回退为未缴（见 [[ledger_edit_limit]]）。企业级状态还会因服务到期回落为 `UNPAID`（见 [[renewal_remind_expire]]），此时历史订单仍为 `PAID`。

## 需求背景

台账展示与缴费校验分别需要企业级与订单级结论，混用会造成「已缴企业被要求再缴」或「历史订单被篡改」两类问题。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/service_period.md ---
---
type: concept
title: 服务期
page_key: service_period
domain: CA证书收费
status: draft
aliases:
  - 服务周期
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
contract_version: "0.1"
maps_to: ca_fee_company.service_end
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.service_start
  - ca_fee_order.service_start
  - ca_fee_order.service_end
adjudication: boundary
boundary: 企业主数据保存当前服务期；订单表保存该订单对应的服务期快照
also_confused_with:
  - ca_fee_order.service_end
---

「服务期」由起止两个字段表达（`service_start`／`service_end`）。主映射取企业主数据 [[ca_fee_company]] 的当前服务期截止日，订单 [[ca_fee_order]] 上保存的是该笔订单对应的服务期**快照**。

**边界（易混淆）**：企业主数据随续费滚动为最新一期；订单快照永久保留当时周期。续费提醒（剩余 ≤7 天）、到期刷新（`service_end < today`）与「服务期内已缴费」判定都以企业主数据的当前服务期为准，见 [[renewal_remind_expire]]、[[already_paid_in_service]]；白名单豁免还会使用零元豁免特殊值作为服务期截止。

## 需求背景

需要同时满足「当前有效服务期可查询」与「历史订单可追溯」，因此采用「企业存当前 + 订单存快照」的双写结构。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/whitelist.md ---
---
type: concept
title: 白名单
page_key: whitelist
domain: CA证书收费
status: draft
aliases:
  - WHITELIST
oid: 1
scope:
  databases:
    - unknown
sources:
  - db
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
maps_to: ca_fee_company.special_config_flag
field_targets:
  - ca_fee_company.special_config_flag
  - ca_fee_project_config.special_company_list
adjudication: boundary
boundary: 企业快照用于规则快速判断；项目 JSON 是配置源，二者需交叉校验
also_confused_with:
  - ca_fee_project_config.special_company_list
---

「白名单」在企业侧表现为特殊配置快照标记 `ca_fee_company.special_config_flag = 'Y'`（口径 [[company_special_config_flag]]），在项目侧表现为 `ca_fee_project_config.special_company_list` JSON 中的 `WHITELIST` 条目。

**边界（易混淆）**：企业快照只用于规则引擎的**快速判断**，项目 JSON 才是**配置源**；两者必须交叉校验后才产生豁免结论，见 [[whitelist_exempt]]。仅凭企业快照为 `Y` 不足以豁免。

## 需求背景

规则引擎在缴费校验链路上被高频调用，需要企业级快照降低配置读取成本；同时配置的变更入口在运营后台的项目维度，故保留双写并要求交叉校验。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/bocom.md ---
---
type: concept
title: 交e保
page_key: bocom
domain: CA证书收费
status: draft
aliases:
  - 交e保对公打款
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to: ca_fee_order.pay_method
field_targets:
  - ca_fee_order.pay_method
  - ca_fee_order.bocom_txn_sts
adjudication: boundary
boundary: pay_method 表示支付渠道；bocom_txn_sts 表示该渠道划扣响应状态
also_confused_with:
  - ca_fee_order.bocom_txn_sts
---

「交e保」是当前代码主要支持的支付方式，落到 `ca_fee_order.pay_method = 'BOCOM'`；其划扣结果由同表的 `bocom_txn_sts`（`00`／`01`／`02`）与平台流水 `bocom_plfm_ser_no`、业务编号 `bocom_plfm_bsn_id`、请求流水 `bocom_req_sn` 承载。

**边界（易混淆）**：`pay_method` 回答「走哪个渠道」，`bocom_txn_sts` 回答「这个渠道这次划扣的结果如何」。相关口径见 [[bocom_txn_sts_00]]、[[bocom_txn_sts_01]]、[[bocom_txn_sts_02]]；幂等与查证逻辑见 [[bocom_idempotent_verify]]。

## 需求背景

对公打款需与银行侧对账，故需要独立的渠道响应状态与多组流水号，以便补单、查证与幂等拦截。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: concepts/fee_agreement.md ---
---
type: concept
title: 收费协议
page_key: fee_agreement
domain: CA证书收费
status: draft
aliases:
  - CA服务费收费协议
oid: 1
scope:
  databases:
    - unknown
sources:
  - code
contract_version: "0.1"
maps_to: ca_fee_order.agreement_signed
field_targets:
  - ca_fee_order.agreement_signed
  - ca_fee_order.agreement_version
adjudication: boundary
boundary: agreement_signed 表示是否已签；agreement_version 表示签署时绑定的版本
also_confused_with:
  - ca_fee_order.agreement_version
---

「收费协议」是订单进入支付前的合规前置，签署事实落在 `ca_fee_order.agreement_signed`（状态机见 [[ca_fee_order_agreement_signed]]，口径见 [[agreement_signed_y]]、规则见 [[agreement_sign_prerequisite]]），签署时绑定的版本落在 `agreement_version`；项目侧另有 `ca_fee_project_config.agreement_version` 作为项目绑定的协议版本。

**边界（易混淆）**：`agreement_signed` 表达「是否已签」，`agreement_version` 表达「签的是哪一版」。台账或对外说明中若只写「协议已签署」，不应据此推定版本。

## 需求背景

收费协议需要按版本留痕以支持审计，且必须在交e保开户与确认打款之前完成签署，故在订单上同时保留布尔事实与版本号。

## 版本演进

- v0（本页）：建立术语桥与边界。

---END FILE---

---FILE: rules/project_charge_switch.md ---
---
type: rule
title: 项目收费开关规则
page_key: project_charge_switch
domain: CA证书收费
status: draft
aliases:
  - 收费开关
  - PROJECT_DISABLED
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

项目无 [[ca_fee_project_config]] 行或 `charge_enabled <> 'Y'` 时，规则引擎直接返回 `EXEMPT`，`needPay=false`，`exemptReason=PROJECT_DISABLED`。这是收费流程的**第一道闸门**，口径见 [[project_charge_enabled]]，多项目场景的放行见 [[multi_project_pass]]。

## 需求背景

收费按项目灰度：未开放收费的项目必须完全不产生待缴与拦截，故把「无配置」与「开关关闭」统一收敛为同一豁免结果。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 项目收费开关规则
content: 项目无 ca_fee_project_config 或 charge_enabled<>'Y' 时，规则引擎直接返回 EXEMPT，needPay=false，exemptReason=PROJECT_DISABLED
impact: 决定是否进入CA服务费收费流程
field_targets:
  - ca_fee_project_config.charge_enabled
evidence: CaFeeRuleEngineService.evaluate
```

---END FILE---

---FILE: rules/multi_project_pass.md ---
---
type: rule
title: 多项目放行规则
page_key: multi_project_pass
domain: CA证书收费
status: draft
aliases:
  - 多项目放行
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentCheckApplication.java
contract_version: "0.1"
---

多项目企业遍历所有**已开启收费**的项目分别调用 `evaluate`，只要任一命中白名单、0 元特殊定价、延期豁免或服务期内已缴费，即 `pass=true` 放行。该规则决定企业级缴费校验的最终结论，是各单项豁免规则的**聚合出口**（见 [[whitelist_exempt]]、[[defer_pay_exempt]]、[[already_paid_in_service]]、[[annual_fee_pricing_chain]]）。

## 需求背景

同一企业可能在多个项目下存在角色，若采用「任一项未缴即拦截」的口径，会导致企业因单个未开放或已豁免的项目被误拦；因此采用「任一放行即放行」的宽松聚合。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 多项目放行规则
content: 多项目企业遍历所有已开启收费项目 evaluate，任一命中白名单、0元特殊定价、延期豁免或服务期内已缴费，即 pass=true 放行
impact: 企业有多个项目时避免因单个项目未缴被拦截
field_targets:
  - ca_fee_project_config.charge_enabled
  - ca_fee_company.pay_status
  - ca_fee_company.special_config_flag
evidence: CaFeePaymentCheckApplication.doCheckFeePayment
```

---END FILE---

---FILE: rules/whitelist_exempt.md ---
---
type: rule
title: 白名单豁免规则
page_key: whitelist_exempt
domain: CA证书收费
status: draft
aliases:
  - WHITELIST 豁免
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

企业快照 `special_config_flag=Y` 且 `special_annual_fee=0`，并与项目 `special_company_list` 中**生效的** `WHITELIST` 交叉校验后，`needPay=false`，`exemptReason=WHITELIST`，服务期截止取零元豁免特殊值。相关口径见 [[company_special_config_flag]]，术语边界见 [[whitelist]]，服务期语义见 [[service_period]]。

## 需求背景

白名单企业免缴 CA 服务费，但配置源在项目侧、判定在规则引擎侧，因此必须交叉校验，避免快照过期导致误免。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 白名单豁免规则
content: 企业快照 special_config_flag=Y 且 special_annual_fee=0，并与项目 special_company_list 中生效 WHITELIST 交叉校验后，needPay=false，exemptReason=WHITELIST，服务期截止取零元豁免特殊值
impact: 白名单企业免缴CA服务费
field_targets:
  - ca_fee_company.special_config_flag
  - ca_fee_company.special_annual_fee
  - ca_fee_project_config.special_company_list
evidence: CaFeeRuleEngineService.isWhitelistExempt
```

---END FILE---

---FILE: rules/defer_pay_exempt.md ---
---
type: rule
title: 延期支付豁免规则
page_key: defer_pay_exempt
domain: CA证书收费
status: draft
aliases:
  - DEFER_PAY 豁免
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

在**无生效定向减免**的前提下，若项目 `special_company_list` 中存在 `DEFER_PAY` 且 `today <= deferServiceEnd`，则 `needPay=false`，`exemptReason=DEFER_PAY`。批量写入延期名单的运营动作见 [[batch_whitelist_defer]]。

## 需求背景

部分企业需要延期缴纳（非免除），需要在延期到期前不产生缴费拦截，同时保留到期后恢复收费的能力；因此以服务结束日作为延期窗口边界。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 延期支付豁免规则
content: 无生效定向减免时，项目 special_company_list 中存在 DEFER_PAY 且 today<=deferServiceEnd，则 needPay=false，exemptReason=DEFER_PAY
impact: 延期企业暂不缴费
field_targets:
  - ca_fee_project_config.special_company_list
evidence: CaFeeRuleEngineService.resolveDeferPay
```

---END FILE---

---FILE: rules/already_paid_in_service.md ---
---
type: rule
title: 服务期内已缴费规则
page_key: already_paid_in_service
domain: CA证书收费
status: draft
aliases:
  - ALREADY_PAID
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

`ca_fee_company.service_end >= today`，或存在 `PAID` 且服务期覆盖今天的订单时，`feeStatus=PAID`，`needPay=false`，`exemptReason=ALREADY_PAID`。判定依据是 [[ca_fee_company]] 的当前服务期与 [[ca_fee_order]] 的服务期快照，口径见 [[order_status_paid]]、[[company_pay_status_paid]]，术语见 [[service_period]]。

## 需求背景

服务期内不得重复收费；企业级服务期可能因数据同步滞后，故补充「订单快照覆盖今天」的兜底判断。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 服务期内已缴费规则
content: ca_fee_company.service_end>=today，或存在 PAID 且服务期覆盖今天的订单，则 feeStatus=PAID，needPay=false，exemptReason=ALREADY_PAID
impact: 服务期内不重复收费
field_targets:
  - ca_fee_company.service_end
  - ca_fee_order.order_status
  - ca_fee_order.service_end
evidence: CaFeeRuleEngineService.evaluate
```

---END FILE---

---FILE: rules/annual_fee_pricing_chain.md ---
---
type: rule
title: 年费定价链规则
page_key: annual_fee_pricing_chain
domain: CA证书收费
status: draft
aliases:
  - 定价链
  - resolveAnnualFee
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeRuleEngineService.java
contract_version: "0.1"
---

应缴年费按优先级解析：`special_annual_fee` → `locked_annual_fee`（仅当 `fee_locked=Y`）→ 项目角色价 `core_annual_fee`／`supplier_annual_fee`；角色价解析为 0 元时视同豁免（对多项目放行与豁免判定产生影响）。相关口径见 [[company_fee_locked]]、[[company_special_config_flag]]。

## 需求背景

同一企业可能同时存在特殊定价、锁定价与项目角色价，必须固定优先级才能保证订单金额可复现；锁定价的存在是为了让首次缴费成功后的价格不随项目调价而变。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 年费定价链规则
content: 应缴年费按 special_annual_fee -> locked_annual_fee（fee_locked=Y） -> 项目角色价 core_annual_fee/supplier_annual_fee 解析；角色价0元时视同豁免
impact: 决定订单 annual_fee 和是否需缴费
field_targets:
  - ca_fee_company.special_annual_fee
  - ca_fee_company.locked_annual_fee
  - ca_fee_company.fee_locked
  - ca_fee_project_config.core_annual_fee
  - ca_fee_project_config.supplier_annual_fee
evidence: CaFeeRuleEngineService.resolveAnnualFee
```

---END FILE---

---FILE: rules/agreement_sign_prerequisite.md ---
---
type: rule
title: 协议签署前置规则
page_key: agreement_sign_prerequisite
domain: CA证书收费
status: draft
aliases:
  - 请先签署收费协议
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
contract_version: "0.1"
---

交e保开户与确认打款前，订单必须 `agreement_signed=Y`；否则抛出「请先签署收费协议」。这是支付入口的硬前置，口径见 [[agreement_signed_y]]，状态机见 [[ca_fee_order_agreement_signed]]，术语边界见 [[fee_agreement]]。

## 需求背景

收费协议属于合规材料，不能在支付完成后补签；因此把签署作为支付的前置条件而非并行步骤。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 协议签署前置规则
content: 交e保开户和确认打款前，订单必须 agreement_signed=Y；否则抛出“请先签署收费协议”
impact: 收费协议是支付前置条件
field_targets:
  - ca_fee_order.agreement_signed
evidence: CaFeePaymentApplication.requirePendingSignedOrder
```

---END FILE---

---FILE: rules/bocom_idempotent_verify.md ---
---
type: rule
title: 交e保划扣幂等与查证规则
page_key: bocom_idempotent_verify
domain: CA证书收费
status: draft
aliases:
  - 划扣幂等
  - 待查证补偿
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeePaymentApplication.java
  - code_path:CaFeeBocomPayReconcileService.java
contract_version: "0.1"
---

订单已有 `txnSts=00/01/02` 时拦截重复扣款；`02` 待查证由定时任务向银行查证，成功则补 `markPaid`，明确失败则禁止再次划扣。三个状态的口径见 [[bocom_txn_sts_00]]、[[bocom_txn_sts_01]]、[[bocom_txn_sts_02]]，并联动订单状态 [[ca_fee_order_status]]。

## 需求背景

渠道响应超时会产生资金状态不确定，若不冻结重试会造成重复出金；因此以「先查证、后收敛」替代「直接重试」。台账侧同时冻结人工编辑，见 [[ledger_edit_limit]]。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 交e保划扣幂等与查证规则
content: 订单已有 txnSts=00/01/02 时拦截重复扣款；02 待查证由定时任务向银行查证，成功则补 markPaid，明确失败则禁止再次划扣
impact: 防止重复支付和状态不一致
field_targets:
  - ca_fee_order.bocom_txn_sts
  - ca_fee_order.order_status
evidence: CaFeePaymentApplication.tryResolveByBocomVerify + CaFeeBocomPayReconcileService
```

---END FILE---

---FILE: rules/renewal_remind_expire.md ---
---
type: rule
title: 续费提醒与到期规则
page_key: renewal_remind_expire
domain: CA证书收费
status: draft
aliases:
  - 续费待办
  - 服务到期
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeScheduledJobHandler.java
  - code_path:CaFeeRenewalService.java
contract_version: "0.1"
---

`service_end` 剩余 ≤7 天且 `renew_remind_sent=N` 时生成续费待办；`service_end < today` 时完结「即将到期」待办、关闭 `RENEW` 待缴单、企业 `pay_status` 置 `UNPAID`，并按需创建 `RENEW_EXPIRED` 订单并发已过期待办。相关口径见 [[order_status_closed]]、[[company_pay_status_unpaid]]，状态机见 [[ca_fee_company_pay_status]]。

## 需求背景

续费是收费模型的持续收入来源：需要在到期前提醒、到期后刷新企业状态并生成补缴入口，同时避免旧待缴单与新周期订单并存。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 续费提醒与到期规则
content: service_end 剩余≤7天且 renew_remind_sent=N 时生成续费待办；service_end<today 时完结即将到期待办、关闭 RENEW 待缴单、企业 pay_status 置 UNPAID，并按需创建 RENEW_EXPIRED 订单发已过期待办
impact: 到期续费提醒和服务状态刷新
field_targets:
  - ca_fee_company.service_end
  - ca_fee_company.renew_remind_sent
  - ca_fee_company.pay_status
  - ca_fee_order.order_type
evidence: CaFeeScheduledJobHandler + CaFeeRenewalService
```

---END FILE---

---FILE: rules/dubbo_biz_node_check.md ---
---
type: rule
title: Dubbo业务节点校验规则
page_key: dubbo_biz_node_check
domain: CA证书收费
status: draft
aliases:
  - dualCheck
  - 业务节点校验
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeBizNodeCheckApplication.java
contract_version: "0.1"
---

统码维度若不存在**生效主数据的**供应商／核企角色，Dubbo `dualCheck` 直接放行；只有存在收费角色才进入缴费校验。该规则决定了讯易链签章前的拦截只针对收费对象，挂钩的字段为 `cust_company_info.certification_no` 与 `cust_company_info.cust_company_type`（该表未在本主题字段语义清单中展开，见页末 REVIEW）。

## 需求背景

签章链路被多个业务复用，若不先判断「该统码下是否存在收费角色」，会对非收费对象产生误拦截；因此把角色存在性作为放行条件。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: Dubbo业务节点校验规则
content: 统码维度若不存在生效主数据的供应商/核企角色，Dubbo dualCheck 直接放行；存在收费角色才进入缴费校验
impact: 讯易链签章前拦截只针对收费对象
field_targets:
  - cust_company_info.certification_no
  - cust_company_info.cust_company_type
evidence: CaFeeBizNodeCheckApplication.check
```

---END FILE---

---FILE: rules/ledger_edit_limit.md ---
---
type: rule
title: 台账编辑限制规则
page_key: ledger_edit_limit
domain: CA证书收费
status: draft
aliases:
  - 编辑限制
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerOperateService.java
contract_version: "0.1"
---

台账订单编辑仅支持 `PENDING`／`PAID`；已缴费订单不允许改为未缴费；交e保 `bocom_txn_sts=02`（待查证）不允许人工标记已缴费。涉及口径 [[order_status_pending]]、[[order_status_paid]]、[[bocom_txn_sts_02]]，与自动收敛逻辑的关系见 [[bocom_idempotent_verify]]。

## 需求背景

台账是运营人工介入的入口，但人工修改不能破坏支付事实：已缴订单回退会造成重复收费风险，待查证订单改价会造成状态与资金不一致。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 台账编辑限制规则
content: 台账订单编辑仅支持 PENDING/PAID；已缴费订单不允许改为未缴费；交e保查证中 bocom_txn_sts=02 不允许人工标记已缴费
impact: 保障台账状态与支付状态一致
field_targets:
  - ca_fee_order.order_status
  - ca_fee_order.bocom_txn_sts
evidence: CaFeeLedgerOperateService.editOrder
```

---END FILE---

---FILE: rules/batch_whitelist_defer.md ---
---
type: rule
title: 批量白名单与延期规则
page_key: batch_whitelist_defer
domain: CA证书收费
status: draft
aliases:
  - 批量豁免
  - batchWhitelist
  - batchDefer
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeLedgerOperateService.java
contract_version: "0.1"
---

批量白名单写入项目 `WHITELIST`，同时**关闭 PENDING 订单**并创建 0 元已缴订单；批量延期写入 `DEFER_PAY`，并记录操作日志。该规则把运营决策转化为可追溯的订单事实，涉及 [[order_status_closed]]、[[whitelist]]、[[defer_pay_exempt]]。

## 需求背景

线下审批通过的白名单与延期必须落到系统且可审计，因此除了写配置，还要关闭既有待缴单并留痕，避免配置与订单状态不一致。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 批量白名单与延期规则
content: 批量白名单写入项目 WHITELIST，关闭 PENDING 订单并创建0元已缴订单；批量延期写入 DEFER_PAY，记录操作日志
impact: 运营后台批量豁免与延期
field_targets:
  - ca_fee_project_config.special_company_list
  - ca_fee_order.order_status
evidence: CaFeeLedgerOperateService.batchWhitelist/batchDefer
```

---END FILE---

---FILE: rules/invoice_async.md ---
---
type: rule
title: 发票异步规则
page_key: invoice_async
domain: CA证书收费
status: draft
aliases:
  - requestInvoiceAsync
oid: 1
scope:
  databases:
    - unknown
sources:
  - code_path:CaFeeInvoiceApplication.java
contract_version: "0.1"
---

缴费成功后异步 `requestInvoiceAsync`：先将订单 `invoice_status` 置 `PENDING`，已存在非 `NONE` 状态则跳过。相关口径见 [[invoice_status_pending]]，状态机见 [[ca_fee_order_invoice_status]]。

## 需求背景

开票链路涉及外部系统，若同步执行会阻塞缴费主流程；因此异步化并以状态判断做幂等，保证同一订单不重复申请开票。

## 版本演进

- v0（本页）：依据语义分析规则证据建立。

```ground:rule
name: 发票异步规则
content: 缴费成功后异步 requestInvoiceAsync，先将订单 invoice_status 置 PENDING，已存在非 NONE 状态则跳过
impact: 开票不阻塞缴费主流程
field_targets:
  - ca_fee_order.invoice_status
evidence: CaFeeInvoiceApplication.requestInvoiceAsync
```

---END FILE---

---REVIEW: table | cust_company_info---
语义分析在「Dubbo业务节点校验规则」中引用了 `cust_company_info.certification_no` 与 `cust_company_info.cust_company_type` 作为 field_targets，但 `field_semantics` 中没有任何 `cust_company_info` 的字段条目，也没有该表的完整字段清单与物理库名。因此未产出 tables/cust_company_info.md 的 ground:table 块——缺少字段证据时不应发明。待补：该表字段清单、字段含义与 `cust_company_type` 取值域后，再建表页，并把 [[dubbo_biz_node_check]] 的 field_targets 指向该页。
---END REVIEW---

---REVIEW: caliber | 全主题 scope.databases---
所有页面的 frontmatter `scope.databases` 依赖「物理库名」，但语义分析未给出任何物理库名（仅出现逻辑表名与 `db_tenant_code` 字段）。本次统一以 `unknown` 占位，未做任何推测映射。待补真实库名后批量回填。
---END REVIEW---

---REVIEW: concept | CA服务费（reqdoc 双源与截断主张）---
`reqdoc_claims` 第三条在语义分析中于 `code_evidence` 处被截断（结尾为 "CaFeeRuleEngineS"），其 `action` 字段缺失；第二条 `action=review` 且 `code_status=uncovered`（产品经理归属），已在 [[ca_service_fee]] 页首与「版本演进」中以 (document_claim，未证实) 标注。此外，`reqdoc` 的 slug 未在语义分析中显式给出，本页暂以需求文档标题推出的 `ca-fee-mvp-phase1-20260625` 作为 slug，并把它与 `code_path` 以 " + " 连接写入 sources（双源形式）。待确认：第三条 claim 的完整 action 与正式 reqdoc slug。
---END REVIEW---