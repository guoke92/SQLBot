---FILE: tables/funding_exception_resolution.md ---
---
type: table
title: 资金方异常解析表
page_key: funding_exception_resolution
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析表
  - funding_exception_resolution
  - 异常处理配置表
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_exception_resolution
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
contract_version: "0.1"
---

本表沉淀资方侧报错的处理知识：以「产品 code + 对接方标识 + 报错关键字」三元组构成业务唯一键，向上游返回报错原因与建议处理方案。表内同时存在页面手工维护链路与 Excel 导入链路，两条链路共用同一唯一性约束 [[exception_check_before_save_unique]]。资方标识与产品 code 的跨域命名差异见 [[funding_party_mark]]；产品维度的取值分布见 [[exception_resolution_product_scope]]。

## 需求背景

- 导入是全量前置校验型：5 个必填列（产品 code / 对接方标识 / 资金方名称 / 报错关键字 / 建议处理方案）任一不通过即整批不落库，见 [[exception_import_all_or_nothing]] 与 [[exception_import_name_code_translation]]。
- 上游调用场景只按报错关键字做 contains 命中，不做模糊度控制，见 [[exception_provider_contains_match]]。
- 数据可见性统一由 `enable` 口径约束，见 [[exception_resolution_enable_y]]。

## 版本演进

v0 首次建立：字段语义取自语义分析 field_semantics（exception_no / funding_party_code / funding_party_name / error_keyword / error_reason / suggestion / file_path / product_code / enable）。语义分析未提供列类型，type 暂记为 `unknown`，待 v1 从 DDL 校准。删除行为为物理删除，`enable` 不承担软删职责，见 [[batch_delete_physical]]。

```ground:table
table: funding_exception_resolution
fields:
  - name: exception_no
    type: unknown
    desc: 异常编号，系统按 fundingPartyCode 生成的业务流水号，非用户录入
    dict: ""
  - name: funding_party_code
    type: unknown
    desc: 对接方标识（资方标识 code），导入时经 ClientQueryFunderCodeService RPC 校验存在性后可写入；唯一键成员
    dict: ""
  - name: funding_party_name
    type: unknown
    desc: 资金方名称，展示/模糊查询用，非关联键
    dict: ""
  - name: error_keyword
    type: unknown
    desc: 报错关键字，与 errorMessage 做 contains 匹配的命中词；唯一键成员
    dict: ""
  - name: error_reason
    type: unknown
    desc: 报错原因（选填，导入不校验）
    dict: ""
  - name: suggestion
    type: unknown
    desc: 建议处理方案（导入必填列）
    dict: ""
  - name: file_path
    type: unknown
    desc: 附件，存 JSON（files[].filePath），Provider 侧解密为 fileUrl 返回
    dict: ""
  - name: product_code
    type: unknown
    desc: 产品 code，导入时可由产品名称反查映射为 code；唯一键成员
    dict: ""
  - name: enable
    type: unknown
    desc: 有效标识，导入/保存固定写 'Y'，查询固定过滤 'Y'
    dict: ""
```

---END FILE---

---FILE: tables/funding_rule_info.md ---
---
type: table
title: 资方规则信息表
page_key: funding_rule_info
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方规则表
  - funding_rule_info
  - 资金规则主表
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_info
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
contract_version: "0.1"
---

本表是资方规则的头表：以「产品 code + 资方标识」定位一条规则，承载规则状态、版本号与规则编码 `code`，明细行由 [[funding_rule_detail]] 通过 rule_info_id / fund_rule_code_ref 挂靠。资方标识在本域的表达见 [[funding_party_mark]]。

## 需求背景

- 新增规则默认待生效、更新时版本自增，随后与明细联动，见 [[rule_save_version_detail_sync]]。
- 对外只暴露已生效规则，见 [[rule_provider_active_only]]。
- 规则导入的资方合法性校验目前硬编码按 ACFLOW 产品名单执行，与落库产品并存存在语义张力，见 [[rule_import_funding_party_hardcoded]]。
- 列表/导出宣称支持时间区间，实际条件被注释掉，见 [[rule_export_ignore_time_range]]。

## 版本演进

v0 首次建立：核心字段语义取自 field_semantics（funding_party_mark / rule_status / version / code），`enable`、`product_code`、`funding_party_name` 的语义取自 calibers 与 rules 的证据，一并纳入本页。状态取值与流转见 [[funding_rule_status_machine]]，状态枚举审计口径见 [[funding_rule_info_enable_y]]。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_info
fields:
  - name: funding_party_mark
    type: unknown
    desc: 资方标识（规则域的表达，与异常域 funding_party_code 同源不同名）
    dict: ""
  - name: funding_party_name
    type: unknown
    desc: 资金方名称，导入时由资方 RPC 的 mark→name 映射回填，更新时被覆盖写
    dict: ""
  - name: product_code
    type: unknown
    desc: 产品 code，规则导入按产品维度校验并按 (productCode,fundingPartyMark) 分组写入
    dict: ""
  - name: rule_status
    type: unknown
    desc: 规则状态：PENDING(待生效)/ACTIVE(生效中)/INACTIVE(已失效)
    dict: RuleStatusEnum
  - name: version
    type: unknown
    desc: 版本号，新增=1，每次更新明细自增 1
    dict: ""
  - name: code
    type: unknown
    desc: 规则信息唯一编码，DataModelUtils.getUniqueKey() 生成，被 funding_rule_detail.fund_rule_code_ref 引用
    dict: ""
  - name: enable
    type: unknown
    desc: 有效标识，导出查询过滤 'Y'，saveRuleInfo 新增固定写 'Y'
    dict: ""
```

---END FILE---

---FILE: tables/funding_rule_detail.md ---
---
type: table
title: 资方规则明细表
page_key: funding_rule_detail
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方规则明细
  - funding_rule_detail
  - 资金规则明细表
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
contract_version: "0.1"
---

明细表以「字段 key → 字段值」的 KV 形式存储一条资方规则的具体条目，归属 [[funding_rule_info]]（rule_info_id / fund_rule_code_ref 双挂靠）。字段 key 的跨表匹配语义见 [[rule_key]]，层级语义见 [[rule_layer]]。

## 需求背景

- 明细写入由 saveRuleInfo 与规则导入共同完成：命中已有 enable='Y' 的明细即更新，否则新增，见 [[rule_save_version_detail_sync]] 与 [[rule_import_four_stage_validation]]。
- 对外查询按 ruleLayer 分组为 UNDERLYING / FINANCING / OTHER，见 [[rule_provider_active_only]]。
- 产品维度与层级维度的实际落库分布见 [[funding_rule_detail_product_scope]]、[[funding_rule_detail_rule_layer_scope]]；check_scene 取值分布见 [[funding_rule_detail_check_scene_scope]]。

## 版本演进

v0 首次建立：字段语义取自 field_semantics（rule_key / rule_value / rule_layer / rule_info_id / fund_rule_code_ref / check_scene），`product_code`、`enable` 取自 calibers 证据。check_scene 在本主题 Application / Provider 均未见写值点，来源存疑，见 REVIEW 记录。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_detail
fields:
  - name: rule_key
    type: unknown
    desc: 规则字段 key，语义等于 funding_rule_front_cfg.front_key（应用层匹配，非 SQL JOIN）
    dict: ""
  - name: rule_value
    type: unknown
    desc: 规则值（字符串）
    dict: ""
  - name: rule_layer
    type: unknown
    desc: 规则层，保存时取自 frontCfg.rule_layer，取值为 UNDERLYING/FINANCING/OTHER
    dict: ""
  - name: rule_info_id
    type: unknown
    desc: 关联 funding_rule_info.id
    dict: ""
  - name: fund_rule_code_ref
    type: unknown
    desc: 关联 funding_rule_info.code
    dict: ""
  - name: check_scene
    type: unknown
    desc: 校验场景（DB 实测仅 SUBMIT_VALIDATE，本主题 Application/Provider 写值点均未 setCheckScene，来源在其他链路）
    dict: ""
  - name: product_code
    type: unknown
    desc: 产品 code，DB 实测存在 ACFLOW 与 RVSFACTOR_PC 两值
    dict: ""
  - name: enable
    type: unknown
    desc: 有效标识，详情/Provider 查询过滤 'Y'，saveRuleInfo 固定写 'Y'
    dict: ""
```

---END FILE---

---FILE: tables/funding_rule_front_cfg.md ---
---
type: table
title: 资方规则前端字段配置表
page_key: funding_rule_front_cfg
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则前端配置表
  - funding_rule_front_cfg
  - frontCfg
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_front_cfg
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
---

本表是规则字段的配置字典：定义前端字段 key、字段名称、字段业务规则类型与所属层级，是导入与详情回显时定位字段的权威来源。导入按 (product, rule_layer, key_name) 三元组反查 front_key，规则保存时以 ruleMap.key 匹配 frontKey，见 [[rule_import_four_stage_validation]]、[[rule_save_version_detail_sync]]。

## 需求背景

- 导入阶段 4 需要把规则层级的 displayName 翻译为 dictKey，并借本表拿到 frontKey；产品无前端配置时保存直接抛异常（见 [[rule_save_version_detail_sync]]）。
- 本表的 rule_layer 与明细的 rule_layer 同值但非外键，见 [[rule_layer]]；front_key / rule_key 的三种用法差异见 [[rule_key]]。

## 版本演进

v0 首次建立：字段语义取自 field_semantics（front_key / key_name / key_type / rule_key），`rule_layer` 取自 term_bridges 的边界描述，`enable` 取自 calibers 证据 [[funding_rule_front_cfg_enable_y]]。语义分析未提供列类型，type 暂记为 `unknown`。

```ground:table
table: funding_rule_front_cfg
fields:
  - name: front_key
    type: unknown
    desc: 前端字段 key，detail.rule_key 的匹配目标
    dict: ""
  - name: key_name
    type: unknown
    desc: 字段名称描述，对外展示为 desc；导入按 (product, rule_layer, key_name) 三元组定位 front_key
    dict: ""
  - name: key_type
    type: unknown
    desc: 字段业务规则类型（FIELD_REQUIRED/FILE_TYPE_LIMIT/DATE_CHECK_WORKDAY 等），对外展示为 type
    dict: ""
  - name: rule_key
    type: unknown
    desc: 规则字段 key，对外输出 item.key
    dict: ""
  - name: rule_layer
    type: unknown
    desc: 配置侧定义的规则层级，保存明细时被复制到 funding_rule_detail.rule_layer
    dict: ""
  - name: enable
    type: unknown
    desc: 有效标识，导入校验与 Provider 查询过滤 'Y'
    dict: ""
```

---END FILE---

---FILE: processes/funding_rule_status_machine.md ---
---
type: process
title: 资方规则状态机
page_key: funding_rule_status_machine
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则状态流转
  - rule_status 状态机
  - RuleStatusEnum
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
---

资方规则以 [[funding_rule_info]].rule_status 表达生命周期。新建规则一律落在 PENDING，只有 ACTIVE 才对外可见（[[rule_provider_active_only]]），因此状态流转是「配置完成 → 对外生效」的唯一开关。

## 需求背景

状态仅由 saveRuleInfo 的写入与 activeRule / inActiveRule 两个动作驱动，动作本身不校验前置状态：INACTIVE 可被 activeRule 直接拉回 ACTIVE，PENDING 也可被 inActiveRule 直接置为 INACTIVE。这意味着「失效再启用」不产生新的版本语义，版本号只由 saveRuleInfo 更新路径自增（[[rule_save_version_detail_sync]]）。枚举值审计与 DB 权重校验受数据限制，见 REVIEW 记录。

## 版本演进

v0 首次建立，状态集合与三条流转证据取自 state_machines；新增态以 NEW 表示「尚未落库」，不作为存储取值。

```ground:process
name: 资方规则状态机
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: 待生效
    source: code_enum
  - value: ACTIVE
    label: 生效中
    source: code_enum
  - value: INACTIVE
    label: 已失效
    source: code_enum
transitions:
  - from: NEW
    event: saveRuleInfo 新增（ruleInfoId 为空）
    to: PENDING
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:380
  - from: PENDING
    event: activeRule
    to: ACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:296
  - from: ACTIVE
    event: inActiveRule
    to: INACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:311
  - from: INACTIVE
    event: activeRule（无前置状态校验，可回到生效）
    to: ACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:296
  - from: PENDING
    event: inActiveRule（无前置状态校验，可直接置为失效）
    to: INACTIVE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java:311
```

---END FILE---

---FILE: calibers/exception_resolution_enable_y.md ---
---
type: caliber
title: 异常解析有效数据口径
page_key: exception_resolution_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 enable 口径
  - funding_exception_resolution enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
contract_version: "0.1"
---

[[funding_exception_resolution]] 的可见性完全由 enable 决定，列表、导出、Provider 查询三处口径一致，避免口径漂移。

## 需求背景

导入与保存固定写 'Y'，查询固定过滤 'Y'，因此本表在业务上不存在「停用但仍保留」的中间态；批量删除走物理删除（[[batch_delete_physical]]），enable 不承担软删职责。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 异常解析有效数据
predicate: funding_exception_resolution.enable = 'Y'
scope: 列表/导出/Provider 查询统一过滤；导入固定写 Y
evidence: code
```

---END FILE---

---FILE: calibers/funding_rule_info_enable_y.md ---
---
type: caliber
title: 资方规则有效数据口径
page_key: funding_rule_info_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方规则 enable 口径
  - funding_rule_info enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
---

[[funding_rule_info]] 的导出查询以 enable='Y' 为口径，saveRuleInfo 新增时固定写 'Y'。

## 需求背景

本口径与状态口径叠加使用：导出看 enable，对外 Provider 看 ruleStatus=ACTIVE（[[rule_provider_active_only]]），两者不可互相替代——规则可能 enable='Y' 但处于 PENDING / INACTIVE（[[funding_rule_status_machine]]）。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 资方规则有效数据
predicate: funding_rule_info.enable = 'Y'
scope: 导出查询过滤；saveRuleInfo 新增固定写 Y
evidence: code
```

---END FILE---

---FILE: calibers/funding_rule_detail_enable_y.md ---
---
type: caliber
title: 资方规则明细有效数据口径
page_key: funding_rule_detail_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则明细 enable 口径
  - funding_rule_detail enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
contract_version: "0.1"
---

[[funding_rule_detail]] 的详情查询与 Provider 查询均以 enable='Y' 为口径，saveRuleInfo 写明细时固定写 'Y'。

## 需求背景

明细更新逻辑依赖本口径判存：命中已有 enable='Y' 明细才更新、否则新增，所以 enable 的写入一致性直接决定明细是否会被重复插入，见 [[rule_save_version_detail_sync]]。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 资方规则明细有效数据
predicate: funding_rule_detail.enable = 'Y'
scope: 详情/Provider 查询过滤；saveRuleInfo 固定写 Y
evidence: code
```

---END FILE---

---FILE: calibers/funding_rule_front_cfg_enable_y.md ---
---
type: caliber
title: 前端规则配置有效数据口径
page_key: funding_rule_front_cfg_enable_y
domain: 资金规则与异常处理
status: draft
aliases:
  - frontCfg enable 口径
  - funding_rule_front_cfg enable
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
---

[[funding_rule_front_cfg]] 的有效性口径同时作用于导入校验（按 (product, rule_layer, key_name) 反查 frontKey）与 Provider 查询。

## 需求背景

导入与保存都依赖本口径拿到可用字段集合；若配置被置为非 'Y'，则该字段无法被导入解析，保存时 ruleMap 中多余的 frontKey 会被静默跳过（[[rule_save_version_detail_sync]]）。

## 版本演进

v0 首次建立，口径语句逐字取自 calibers 条目。

```ground:caliber
name: 前端规则配置有效数据
predicate: funding_rule_front_cfg.enable = 'Y'
scope: 导入校验与 Provider 查询过滤
evidence: code
```

---END FILE---

---FILE: calibers/exception_resolution_product_scope.md ---
---
type: caliber
title: 异常解析产品范围（DB 实际落库值）
page_key: exception_resolution_product_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 product_code 分布
  - 异常解析 ACFLOW 占比
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_exception_resolution
contract_version: "0.1"
---

[[funding_exception_resolution]] 的 product_code 在实际库中呈双产品并存：ACFLOW 为主、RVSFACTOR_PC 为次。

## 需求背景

该分布是「产品 code 不写死」的实测依据，与资方规则导入中硬编码 ACFLOW 的做法（[[rule_import_funding_party_hardcoded]]）形成对照。产品名 → code 的翻译链见 [[exception_import_name_code_translation]]。本口径是 DB 实测值，不构成校验规则，不能反向用于限制导入取值。

## 版本演进

v0 首次建立，占比取自 calibers 条目 DB 证据，未做时间切片，未区分 enable 状态。

```ground:caliber
name: 异常解析产品范围（DB 实际落库值）
predicate: funding_exception_resolution.product_code = 'ACFLOW'
scope: DB 实测 58/90；另一取值 RVSFACTOR_PC 32/90
evidence: db
```

---END FILE---

---FILE: calibers/funding_rule_detail_product_scope.md ---
---
type: caliber
title: 资方规则明细产品范围（DB 实际落库值）
page_key: funding_rule_detail_product_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则明细 product_code 分布
  - funding_rule_detail ACFLOW 占比
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
---

[[funding_rule_detail]] 的 product_code 同样双产品并存，ACFLOW 约占七成。

## 需求背景

实测产品分布与导入时资方校验硬编码 ACFLOW 的实现之间存在语义张力：为 RVSFACTOR_PC 导入的明细能够落库，但其资方合法性判断仍以 ACFLOW 名单为准，见 [[rule_import_funding_party_hardcoded]]。

## 版本演进

v0 首次建立，占比取自 calibers 条目 DB 证据，未做时间切片。

```ground:caliber
name: 资方规则明细产品范围（DB 实际落库值）
predicate: funding_rule_detail.product_code = 'ACFLOW'
scope: DB 实测 1062/1530；另一取值 RVSFACTOR_PC 468/1530
evidence: db
```

---END FILE---

---FILE: calibers/funding_rule_detail_rule_layer_scope.md ---
---
type: caliber
title: 规则层枚举（DB 实测）
page_key: funding_rule_detail_rule_layer_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - rule_layer 分布
  - 规则层级分布
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
---

[[funding_rule_detail]].rule_layer 的实测取值分布以 FINANCING 为主，UNDERLYING 次之，OTHER 最少。

## 需求背景

该分布印证了 Provider 对外按 ruleLayer 聚合成「底层（UNDERLYING）/融资（FINANCING）/其他（OTHER）」三组的必要性（[[rule_provider_active_only]]）。层级值在保存时由 [[funding_rule_front_cfg]].rule_layer 复制而来，见 [[rule_layer]]。

## 版本演进

v0 首次建立，计数取自 calibers 条目 DB 证据。

```ground:caliber
name: 规则层枚举（DB 实测）
predicate: funding_rule_detail.rule_layer = 'FINANCING'
scope: DB 925/1530；UNDERLYING 499、OTHER 106
evidence: db
```

---END FILE---

---FILE: calibers/funding_rule_detail_check_scene_scope.md ---
---
type: caliber
title: 校验场景枚举（DB 实测）
page_key: funding_rule_detail_check_scene_scope
domain: 资金规则与异常处理
status: draft
aliases:
  - check_scene 分布
  - 校验场景 SUBMIT_VALIDATE
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - db:funding_rule_detail
contract_version: "0.1"
---

[[funding_rule_detail]].check_scene 在库中只出现 SUBMIT_VALIDATE 一个取值。

## 需求背景

根据字段语义，本主题的 Application / Provider 写值点均未调用 setCheckScene，说明该列的写入方在其他链路（建单/校验链路），本页的取值分布不能推断为「本主题只支持一种场景」。写值点缺失已登记 REVIEW。

## 版本演进

v0 首次建立，计数取自 calibers 条目 DB 证据（实测 50 条）。

```ground:caliber
name: 校验场景枚举（DB 实测）
predicate: funding_rule_detail.check_scene = 'SUBMIT_VALIDATE'
scope: DB 实测 50 条，本主题代码未见写值点
evidence: db
```

---END FILE---

---FILE: concepts/funding_party_mark.md ---
---
type: concept
title: 资方标识（fundingPartyMark / fundingPartyCode）
page_key: funding_party_mark
domain: 资金规则与异常处理
status: draft
aliases:
  - 资金方标识
  - 对接方标识
  - fundingPartyMark
  - fundingPartyCode
  - fundingPartyId
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_rule_info
  - db:funding_exception_resolution
maps_to: funding_rule_info.funding_party_mark
field_targets:
  - funding_rule_info.funding_party_mark
  - funding_rule_detail.funding_party_mark
adjudication: boundary
also_confused_with:
  - funding_exception_resolution.funding_party_code
contract_version: "0.1"
---

「资方标识」是同一业务主体在两个域中的两种列名表达：规则域落 funding_party_mark，异常域落 funding_party_code。二者同源于资方 RPC 的 fundingKey，但列名不同、表不同，**不可互换 join**，跨域取数必须经应用层翻译而非 SQL 关联。

## 需求背景

- 规则域的资方合法性由 ClientQueryFunderMarkService 校验，且产品被硬编码为 ACFLOW（[[rule_import_funding_party_hardcoded]]）。
- 异常域的对接方标识由 ClientQueryFunderCodeService 按 productCode 分组批量校验（[[exception_import_all_or_nothing]]）。
- 上游 Provider 分别以 fundingPartyMark（规则域，[[rule_provider_active_only]]）与 fundingPartyCode（异常域，[[exception_provider_contains_match]]）作为入口参数。

## 版本演进

v0 首次建立，别名集合与判定类型取自 term_bridges：判定为 boundary，边界即「规则域 funding_party_mark / 异常域 funding_party_code 同源不同列」。本页为概念页，锚点信息仅置于 frontmatter（maps_to / field_targets / adjudication / also_confused_with）。

---END FILE---

---FILE: concepts/funding_party_name.md ---
---
type: concept
title: 资金方名称（fundingPartyName）
page_key: funding_party_name
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方名称
  - fundingPartyName
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_exception_resolution
  - db:funding_rule_info
maps_to: funding_exception_resolution.funding_party_name
field_targets:
  - funding_exception_resolution.funding_party_name
  - funding_rule_info.funding_party_name
adjudication: synonym
also_confused_with:
  - funding_rule_info.funding_party_name
contract_version: "0.1"
---

资金方名称在两表中各自冗余存储，**均非关联键**，只服务于展示与模糊查询。查询请勿以名称作为 join 条件，关联一律使用资方标识（[[funding_party_mark]]）。

## 需求背景

- 异常解析导入必填资金方名称列，并参与「资金方名称-标识」→ fundingKey 的翻译（[[exception_import_name_code_translation]]）。
- 规则导入时名称来自资方 RPC 的 mark→name 映射；由于校验产品硬编码为 ACFLOW，落库名称可能取自 ACFLOW 映射（[[rule_import_funding_party_hardcoded]]）；更新规则时名称会被覆盖写（[[rule_save_version_detail_sync]]）。

## 版本演进

v0 首次建立，判定类型 synonym：两表同义字段，取值来源可能不同但语义一致。

---END FILE---

---FILE: concepts/rule_layer.md ---
---
type: concept
title: 规则层级（ruleLayer）
page_key: rule_layer
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则层
  - ruleLayer
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
maps_to: funding_rule_detail.rule_layer
field_targets:
  - funding_rule_detail.rule_layer
  - funding_rule_front_cfg.rule_layer
adjudication: synonym
also_confused_with:
  - funding_rule_front_cfg.rule_layer
contract_version: "0.1"
---

规则层级描述一条规则字段属于底层（UNDERLYING）/ 融资（FINANCING）/ 其他（OTHER）哪一层。配置侧在 [[funding_rule_front_cfg]] 定义，明细侧在 [[funding_rule_detail]] 保存时从 frontCfg 复制，**同值但不是外键关系**。

## 需求背景

- 导入阶段 4 需把规则层级的 displayName 翻译为 dictKey，并参与 (product, rule_layer, key_name) 三元组定位 frontKey（[[rule_import_four_stage_validation]]）。
- 对外 Provider 正是按本字段把明细聚合成三组返回（[[rule_provider_active_only]]）；实测取值分布见 [[funding_rule_detail_rule_layer_scope]]。

## 版本演进

v0 首次建立，判定类型 synonym，边界为「配置侧定义、明细侧复制，非外键」。

---END FILE---

---FILE: concepts/rule_key.md ---
---
type: concept
title: 规则字段 key（ruleKey / frontKey）
page_key: rule_key
domain: 资金规则与异常处理
status: draft
aliases:
  - frontKey
  - front_key
  - rule_key
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
maps_to: funding_rule_detail.rule_key
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_front_cfg.front_key
  - funding_rule_front_cfg.rule_key
adjudication: boundary
also_confused_with:
  - funding_rule_front_cfg.rule_key
  - funding_rule_front_cfg.front_key
contract_version: "0.1"
---

三处 key 语义必须分清：[[funding_rule_detail]].rule_key 在应用层 Map 中与 [[funding_rule_front_cfg]].front_key 匹配（等价，**非 SQL JOIN**）；而 front_cfg.rule_key 是另一个字段，在 Provider 中被写成对外输出的 item.key。三者不可混用。

## 需求背景

- 规则保存：以 ruleMap.key 匹配 frontKey，命中已有 enable='Y' 明细即更新，否则新增；ruleMap 中不存在的 frontKey 静默跳过（[[rule_save_version_detail_sync]]）。
- 规则导入：按 (product, rule_layer, key_name) 反查 front_cfg 拿到 frontKey 作为明细 key（[[rule_import_four_stage_validation]]）。
- 对外输出：Provider 以 front_cfg.rule_key 作为 item.key 返回（[[rule_provider_active_only]]）。

## 版本演进

v0 首次建立，判定类型 boundary，边界为「detail.rule_key ↔ front_cfg.front_key 应用层等价；front_cfg.rule_key 是对外输出字段」。

---END FILE---

---FILE: concepts/error_keyword.md ---
---
type: concept
title: 报错关键字（errorKeyword）
page_key: error_keyword
domain: 资金规则与异常处理
status: draft
aliases:
  - errorKeyword
  - errorMessage
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
  - db:funding_exception_resolution
maps_to: funding_exception_resolution.error_keyword
field_targets:
  - funding_exception_resolution.error_keyword
adjudication: synonym
also_confused_with: []
contract_version: "0.1"
---

报错关键字是 [[funding_exception_resolution]] 的命中词：Provider 用它与上游传入的 errorMessage 做 contains 匹配。代码中局部变量命名为 errorMessage，实际取的是 DTO.errorKeyword，**命名混淆但语义同一字段**。

## 需求背景

- 命中为大小写敏感的 contains，且可命中多条全部返回（[[exception_provider_contains_match]]）。
- 关键字同时是业务唯一键成员，参与导入查重与保存前校验（[[exception_import_all_or_nothing]]、[[exception_check_before_save_unique]]）。

## 版本演进

v0 首次建立，判定类型 synonym，边界即「局部变量名 errorMessage 与字段 errorKeyword 的命名混淆」。

---END FILE---

---FILE: rules/exception_import_all_or_nothing.md ---
---
type: rule
title: 异常解析导入全量校验通过才入库
page_key: exception_import_all_or_nothing
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析导入全量校验
  - 导入不做部分成功
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_exception_resolution
  - reqdoc:import-all-validate-before-save
contract_version: "0.1"
---

导入 [[funding_exception_resolution]] 时，系统先做行级必填校验，再做产品枚举比对，最后按 productCode 分组批量调 RPC 校验对接方标识并做唯一键查重。任一错误直接返回错误列表且不写库，只有全部通过才在单事务内写库。

## 需求背景

需求侧主张与实现一致：资源导入遵循「全量校验通过才入库；任一失败直接返回，不做任何保存/更新」（BR 级主张，code_status: confirmed）。因此导入的失败语义是「整批拒绝」而非「行级忽略」，使用方需按错误列表整批修正后重试。单次导入上限 5000 行。

## 版本演进

v0 首次建立，锚点 evidence 采用双源：代码路径 + 需求文档主张 slug。

```ground:rule
name: 异常解析导入全量校验通过才入库
content: 阶段1 Excel 行级必填校验（产品code/对接方标识/资金方名称/报错关键字/建议处理方案 5 列）→ 阶段2 productCode 枚举比对 → 阶段3 按 productCode 分组各调一次 RPC 校验对接方标识 + 唯一键 (productCode,fundingPartyCode,errorKeyword) 查重；任一错误直接返回错误列表且不写库；全部通过才在单事务内 saveOrUpdateBatch。
impact: 任何一行错误都会导致整批不落库；单次导入上限 5000 行
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: code_path:ExceptionResolutionApplication.java:importRecords/doUpsertAll + DB:funding_exception_resolution_un(funding_party_code,error_keyword,product_code) + reqdoc:import-all-validate-before-save
```

---END FILE---

---FILE: rules/exception_import_name_code_translation.md ---
---
type: rule
title: 异常解析产品名→code 与资金方名→code 二次翻译
page_key: exception_import_name_code_translation
domain: 资金规则与异常处理
status: draft
aliases:
  - 导入翻译规则
  - 产品名转 code
  - 资金方名转标识
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_exception_resolution
contract_version: "0.1"
---

导入允许用户填「产品名称」与「资金方名称-标识」，系统负责翻译成 product_code 与 funding_party_code 后回写，再校验回填值是否落在合法集合内。

## 需求背景

该规则是「全量校验通过才入库」（[[exception_import_all_or_nothing]]）阶段 2 / 阶段 3 的组成部分，翻译失败会以「不在允许范围内 / 不存在」的形式进入错误列表，导致整批拒绝。产品合法集合来自 listPlatformProduct(GENERAL)，与平台产品的维护链路相关。

## 版本演进

v0 首次建立，证据取自异常解析导入链路。

```ground:rule
name: 异常解析产品名→code 与资金方名→code 二次翻译
content: 阶段2 用 listPlatformProduct(GENERAL) 构 productName→productCode 映射回填；阶段3 用 RPC 结果构 "fundingPartyName-fundingKey"→fundingKey 映射回填，再校验回填值是否在合法集合内。
impact: 导入模板允许填产品名称/资金方名称-标识，系统会翻译；翻译失败则报“不在允许范围内/不存在”
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
evidence: code_path:ExceptionResolutionApplication.java:collectProductCodeErrors/collectFundingPartyCodeErrors
```

---END FILE---

---FILE: rules/exception_check_before_save_unique.md ---
---
type: rule
title: 异常解析保存前唯一性校验
page_key: exception_check_before_save_unique
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析唯一键校验
  - 报错关键字已经存在
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - db:funding_exception_resolution
contract_version: "0.1"
---

页面手工新增/编辑与导入链路共用同一唯一键三元组 (productCode, fundingPartyCode, errorKeyword)，命中即抛 BaseException('报错关键字已经存在')。

## 需求背景

保存前校验是 DB 唯一约束（funding_exception_resolution_un）在应用层的等价实现，并被导入查重复用（[[exception_import_all_or_nothing]]）。校验会排除自身 id，因此编辑同一条记录不会误判冲突。

## 版本演进

v0 首次建立。

```ground:rule
name: 异常解析保存前唯一性校验
content: checkBeforeSave 按 productCode + fundingPartyCode + errorKeyword（并排除自身 id）查询，命中即抛 BaseException('报错关键字已经存在')。
impact: 页面手工新增/编辑同样受唯一键约束
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: code_path:ExceptionResolutionApplication.java:checkBeforeSave
```

---END FILE---

---FILE: rules/exception_provider_contains_match.md ---
---
type: rule
title: 异常解析对上游只按关键字 contains 命中
page_key: exception_provider_contains_match
domain: 资金规则与异常处理
status: draft
aliases:
  - 异常解析 Provider 匹配规则
  - errorMessage contains
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyExceptionResolutionProviderImpl.java
  - db:funding_exception_resolution
contract_version: "0.1"
---

对外查询先按 fundingPartyCode + productCode + enable='Y' 批量取数，再在内存中做 errorMessage.contains(errorKeyword) 过滤；命中多条则全部返回。

## 需求背景

上游拿到的结果不带模糊度控制，关键字长度与大小写敏感（实际为大小写敏感 contains），上游需自行处理多命中。参数缺失或系统异常一律返回空列表、不抛错，属于「降级为无结果」的容错约定。调用入口参数即 [[funding_party_mark]] 在异常域的表达 funding_party_code。

## 版本演进

v0 首次建立。

```ground:rule
name: 异常解析对上游只按关键字 contains 命中
content: ProviderImpl 先按 fundingPartyCode + productCode + enable='Y' 批量查，再在内存中过滤 errorMessage.contains(errorKeyword)，可命中多条全部返回；参数缺失或系统异常一律返回空列表不抛错。
impact: 上游拿到的结果不带模糊度控制，关键字长度/大小写敏感（实际为大小写敏感 contains）
field_targets:
  - funding_exception_resolution.error_keyword
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.product_code
evidence: code_path:FundingPartyExceptionResolutionProviderImpl.java:doQuery/queryByFundingPartyId
```

---END FILE---

---FILE: rules/rule_import_funding_party_hardcoded.md ---
---
type: rule
title: 资方规则导入的资方校验产品被硬编码为 ACFLOW
page_key: rule_import_funding_party_hardcoded
domain: 资金规则与异常处理
status: draft
aliases:
  - 资方校验硬编码 ACFLOW
  - collectFundingPartyMarkErrors
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
---

规则导入校验资方标识时，代码固定使用 ProductCodeEnum.ACFLOW 调 ClientQueryFunderMarkService，合法资方集合与 mark→name 映射均以 ACFLOW 为准，而错误文案中拼的却是行自身的 productCode。

## 需求背景

实现与实测数据存在语义张力：DB 中 [[funding_rule_detail]] 与 [[funding_rule_info]] 均存在 RVSFACTOR_PC 产品数据（见 [[funding_rule_detail_product_scope]]、[[exception_resolution_product_scope]]），但为 RVSFACTOR_PC 导入规则时，资方合法性仍按 ACFLOW 名单判断，落库的 fundingPartyName 也可能来自 ACFLOW 映射。这对「名称仅用于展示」的假设（[[funding_party_name]]）构成风险，需业务确认。

## 版本演进

v0 首次建立，按代码现状登记，不做行为修正。

```ground:rule
name: 资方规则导入的资方校验产品被硬编码为 ACFLOW
content: collectFundingPartyMarkErrors 里 dto.setProductCode(ProductCodeEnum.ACFLOW) 后调 ClientQueryFunderMarkService，合法资方集合与 mark→name 映射均以 ACFLOW 为准，但错误文案中拼的是行自身的 productCode。
impact: 为 RVSFACTOR_PC 导入规则时，资方合法性仍按 ACFLOW 名单判断，且落库的 fundingPartyName 可能来自 ACFLOW 映射；与 DB 实测两产品并存存在语义张力
field_targets:
  - funding_rule_info.product_code
  - funding_rule_info.funding_party_mark
  - funding_rule_info.funding_party_name
evidence: code_path:FundRuleInfoApplication.java:collectFundingPartyMarkErrors
```

---END FILE---

---FILE: rules/rule_import_four_stage_validation.md ---
---
type: rule
title: 资方规则导入四阶段校验
page_key: rule_import_four_stage_validation
domain: 资金规则与异常处理
status: draft
aliases:
  - 规则导入四阶段
  - 规则导入校验链
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_detail
  - db:funding_rule_front_cfg
contract_version: "0.1"
---

规则导入依次经过必填校验、产品枚举校验、资方 RPC 校验、规则层级与前端配置反查四个阶段，任一失败不落库；全部通过后按 (productCode, fundingPartyMark) 分组调用 saveRuleInfo。

## 需求背景

该链路与异常解析导入共享「全量校验通过才入库」的失败语义（[[exception_import_all_or_nothing]]）。阶段 4 要求规则层级能由 displayName 翻译为 dictKey，并按 (product, rule_layer, key_name) 三元组在 [[funding_rule_front_cfg]] 中反查 frontKey；落库时组内 ruleMap.key = frontKey、value = ruleValue，写入 [[funding_rule_detail]]。资方校验阶段的硬编码问题见 [[rule_import_funding_party_hardcoded]]。

## 版本演进

v0 首次建立。

```ground:rule
name: 资方规则导入四阶段校验
content: 阶段1 Excel 必填（产品/资方标识code/规则层级/规则名称/规则值）→ 阶段2 productCode 枚举 → 阶段3 资方标识 RPC 校验 → 阶段4 规则层级 displayName→dictKey 且按 (product,rule_layer,key_name) 反查 funding_rule_front_cfg 拿 frontKey；任一失败不落库；通过后按 (productCode,fundingPartyMark) 分组调 saveRuleInfo。
impact: 导入按组写入，组内 ruleMap.key=frontKey、value=ruleValue
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
  - funding_rule_front_cfg.key_name
evidence: code_path:FundRuleInfoApplication.java:importRecords/validateRuleLayerAndFrontCfg/persistFundRuleImportGroups
```

---END FILE---

---FILE: rules/rule_export_ignore_time_range.md ---
---
type: rule
title: 资方规则列表/导出查询条件实际忽略时间区间
page_key: rule_export_ignore_time_range
domain: 资金规则与异常处理
status: draft
aliases:
  - 导出时间区间失效
  - parseTimeRange 死代码
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
contract_version: "0.1"
---

[[funding_rule_info]] 的导出/列表查询中，create_time / update_time 的 ge / le 条件被注释掉，parseTimeRange 成为死代码，而 Controller 的 ApiOperation 注释仍宣称支持时间区间查询。

## 需求背景

行为表现为「静默忽略条件」而非报错，使用方按时间范围导出会得到全量结果，需以其他条件收敛范围。导出上限 50000 行、分页 500。

## 版本演进

v0 首次建立，登记实现与文档不一致的现状。

```ground:rule
name: 资方规则列表/导出查询条件实际忽略时间区间
content: buildExportQueryParam 中 create_time/update_time 的 ge/le 条件被注释掉，parseTimeRange 成为死代码；Controller 的 ApiOperation 注释仍宣称支持时间区间查询。
impact: 按创建/更新时间范围导出无效，只是忽略条件而非报错；导出上限 50000 行、分页 500
field_targets:
  - funding_rule_info.create_time
  - funding_rule_info.update_time
evidence: code_path:FundRuleInfoApplication.java:buildExportQueryParam:237
```

---END FILE---

---FILE: rules/rule_save_version_detail_sync.md ---
---
type: rule
title: 资方规则保存的版本与明细联动
page_key: rule_save_version_detail_sync
domain: 资金规则与异常处理
status: draft
aliases:
  - saveRuleInfo 版本联动
  - 规则明细 upsert
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
  - db:funding_rule_info
  - db:funding_rule_detail
contract_version: "0.1"
---

保存一条资方规则时，头表 [[funding_rule_info]] 与明细 [[funding_rule_detail]] 在同一动作内联动：新增走 PENDING + version=1 + 唯一 code，更新走 version+1 并覆盖资方名称，随后按 frontKey 匹配增改明细。

## 需求背景

- 新增即待生效，对外不可见，直到 activeRule（[[funding_rule_status_machine]]、[[rule_provider_active_only]]）。
- 明细匹配依据 frontKey，多出的 frontKey 静默跳过；产品无前端配置则直接抛异常（[[rule_key]]、[[funding_rule_front_cfg]]）。
- 明细判存依赖 enable='Y' 口径（[[funding_rule_detail_enable_y]]）。

## 版本演进

v0 首次建立。

```ground:rule
name: 资方规则保存的版本与明细联动
content: 新增：查重 (productCode,fundingPartyMark) → 插 funding_rule_info(ruleStatus=PENDING,version=1,code=唯一键,enable=Y)；更新：version+1 并覆盖 fundingPartyName；随后按 productCode 查 front_cfg，用 ruleMap.key 匹配 frontKey，命中已有 enable='Y' 明细则更新否则新增。
impact: ruleMap 中不存在的 frontKey 静默跳过不中断；产品无前端配置直接抛异常
field_targets:
  - funding_rule_info.version
  - funding_rule_info.rule_status
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
evidence: code_path:FundRuleInfoApplication.java:saveRuleInfo
```

---END FILE---

---FILE: rules/rule_provider_active_only.md ---
---
type: rule
title: 对外规则查询只暴露已生效规则
page_key: rule_provider_active_only
domain: 资金规则与异常处理
status: draft
aliases:
  - Provider 只查 ACTIVE
  - 规则三组聚合
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/client/fundingparty/provider/FundingPartyRuleProviderImpl.java
  - db:funding_rule_info
  - db:funding_rule_detail
  - reqdoc:funding-rule-active-only-query
contract_version: "0.1"
---

对外查询按 fundingPartyMark + productCode + ruleStatus=ACTIVE 取头表，无生效规则返回 null；再按 ruleInfoId + enable='Y' 取明细，按 ruleLayer 分组为 UNDERLYING / FINANCING / OTHER 返回。

## 需求背景

需求侧主张与实现一致：资方规则查询按 fundingPartyMark + productCode 只取 ACTIVE 规则并聚合为底层/融资/其他三组（code_status: confirmed）。因此 PENDING / INACTIVE 规则对外不可见，配置完成到对外生效必须显式调用 activeRule（[[funding_rule_status_machine]]）。

## 版本演进

v0 首次建立，锚点 evidence 采用双源：代码路径 + 需求文档主张 slug。

```ground:rule
name: 对外规则查询只暴露已生效规则
content: FundingPartyRuleProviderImpl 按 fundingPartyMark + productCode + ruleStatus=ACTIVE 查询，无生效规则返回 null；再按 ruleInfoId + enable='Y' 查明细，按 ruleLayer 分组为 UNDERLYING/FINANCING/OTHER。
impact: PENDING/INACTIVE 规则对外不可见
field_targets:
  - funding_rule_info.rule_status
  - funding_rule_detail.rule_layer
evidence: code_path:FundingPartyRuleProviderImpl.java:doQuery + reqdoc:funding-rule-active-only-query
```

---END FILE---

---FILE: rules/batch_delete_physical.md ---
---
type: rule
title: 批量删除为物理删除
page_key: batch_delete_physical
domain: 资金规则与异常处理
status: draft
aliases:
  - 物理删除
  - removeByIds / removeBatchByIds
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/ExceptionResolutionApplication.java
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/application/FundRuleInfoApplication.java
contract_version: "0.1"
---

[[funding_exception_resolution]] 与 [[funding_rule_info]] 的批量删除均走 MyBatis-Plus 物理删除（removeByIds / removeBatchByIds），并非 enable='N' 的逻辑删除。

## 需求背景

该行为澄清了 enable 字段的职责边界：enable 只是有效数据口径（[[exception_resolution_enable_y]]、[[funding_rule_info_enable_y]]），不承担软删；删除不可恢复，且删除 `code` 被 [[funding_rule_detail]].fund_rule_code_ref 引用的规则头时需自行评估悬挂引用风险。

## 版本演进

v0 首次建立。

```ground:rule
name: 批量删除为物理删除
content: 异常解析 batchDelete 用 removeByIds、规则 batchDelete 用 removeBatchByIds，均非 enable='N' 逻辑删除。
impact: 删除不可恢复，且 enable 字段并不承担软删职责
field_targets:
  - funding_exception_resolution.enable
  - funding_rule_info.enable
evidence: code_path:ExceptionResolutionApplication.java:batchDelete / FundRuleInfoApplication.java:batchDelete
```

---END FILE---

---FILE: rules/platform_product_check_before_save.md ---
---
type: rule
title: 平台产品保存前置校验
page_key: platform_product_check_before_save
domain: 资金规则与异常处理
status: draft
aliases:
  - BR-001
  - PlatformProductApplication.checkBeforeSave
oid: 1
scope:
  databases:
    - lowcode_pplatform_customer_management
sources:
  - code:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/PlatformProductApplication.java
  - reqdoc:BR-001
contract_version: "0.1"
---

平台产品保存前调用 checkBeforeSave，校验产品 code 唯一性与类型枚举等，失败抛 BaseException 阻断保存。该规则是异常解析与规则导入中「产品 code 合法集合」的上游来源（[[exception_import_name_code_translation]]，listPlatformProduct(GENERAL)）。

## 需求背景

本主题需求文档中仅有产品与项目管理文档提及平台产品校验与列表过滤，**未对资金规则与异常处理主题给出独立业务规则章节**（document_claim，未证实）。与产品列表过滤相关的主张（BR-002）在代码中未见实现，见 REVIEW 记录。

## 版本演进

v0 首次建立，来源为需求文档主张 action=anchor（code_status: confirmed），锚点 evidence 写双源。

```ground:rule
name: 平台产品保存前置校验
content: 调用 PlatformProductApplication.checkBeforeSave 校验产品 code 唯一性、类型枚举等，失败抛 BaseException 阻断保存（BR-001）。
impact: 产品 code 重复或类型不合法时保存被阻断；产品合法集合是下游导入校验（异常解析、资方规则）的前置依赖
field_targets: []
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/product/application/PlatformProductApplication.java:checkBeforeSave + reqdoc:BR-001
```

---END FILE---

---REVIEW: rules | 平台产品列表过滤（BR-002，未覆盖主张）---
主张「非 AGW 端按当前租户已开通 tenant_product 列表过滤，并通过 Nacos 白名单进一步过滤」在代码侧未覆盖：PlatformProductApplication 仅有 listPlatformProduct(type) 直连 domainService，本主题代码中未见 listTenantProduct / filterLimitProduct 实现。当前只在语义分析中标注 action=review，未落为任何页面的 ground:rule 锚点；需确认该过滤逻辑是否在其他模块/其他服务实现，再决定是否升级为规则页。
---END REVIEW---

---REVIEW: calibers | 校验场景（check_scene）写值点缺失---
funding_rule_detail.check_scene 在 DB 实测仅 SUBMIT_VALIDATE（50 条），但本主题 Application / Provider 的写值点均未调用 setCheckScene。字段语义明确指向「来源在其他链路」，因此本页只登记取值分布口径（[[funding_rule_detail_check_scene_scope]]），不推断枚举全集，也不据此外推业务含义。需补查建单/校验链路后回填写值点。
---END REVIEW---

---REVIEW: enums | 资方规则状态枚举（enum_audit 数据被截断）---
语义分析的 enum_audit 数组在 funding_rule_info.rule_status=PENDING 一条之后被截断，仅可见：value=PENDING、java_name=PENDING、stored_as=same、label=待生效、verdict=confirm、evidence=FundRuleInfoApplication.java:saveRuleInfo 写 setRuleStatus(RuleStatusEnum.PENDING.getDictKey())。ACTIVE / INACTIVE 两条的 java_name、stored_as、note 未获取，故本批次未单独产出 enum 页，状态取值与流转暂由 [[funding_rule_status_machine]] 承载。另附注：DB 未提供 funding_rule_info 的值分布，无法用 TopK 校验权重。待 enum_audit 补全后建立 enums 页并回链。
---END REVIEW---

---REVIEW: rules | reqdoc 主张 slug 缺失---
reqdoc_claims 中两条 action=anchor 的主张（「资源导入遵循全量校验通过才入库」「资方规则查询按 fundingPartyMark + productCode 只取 ACTIVE 规则」）在语义分析里只有 claim 文本与 code_evidence，未给出文档 slug。本批次按主张摘要自拟 slug（reqdoc:import-all-validate-before-save、reqdoc:funding-rule-active-only-query），仅 BR-001 为文档原文自带编号。待需求文档编号体系确认后统一替换 slug，并同步 [[exception_import_all_or_nothing]]、[[rule_provider_active_only]] 两页锚点。
---END REVIEW---

---REVIEW: tables | 物理库名未在语义分析中给出---
各页 frontmatter 的 scope.databases 暂用模块名推导值 lowcode_pplatform_customer_management，语义分析仅以 [DB] 标注证据来源，未给出物理库（schema）名。表页锚点字段不受影响，但跨库/跨服务引用与 SQL 复现需以真实库名校准，建议 v1 统一回填。
---END REVIEW---