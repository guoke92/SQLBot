---FILE: tables/funding_exception_resolution.md ---
---
type: table
title: 资金异常解析表（funding_exception_resolution）
page_key: tables/funding_exception_resolution
domain: funding
status: draft
aliases:
  - funding_exception_resolution
  - 异常解析表
  - 资金异常解析配置表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution"
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication"
  - "code:ExceptionResolutionImportListener"
  - "code:FundingPartyExceptionResolutionProviderImpl"
  - "code:PlatFormOperateAppliaction#getBussinessNo"
contract_version: "0.1"
---

# 资金异常解析表（funding_exception_resolution）

## 业务定位

该表是运营侧维护、外部系统消费的**异常解析配置字典**：把「某产品 + 某对接方」下出现的**报错关键字**映射到**报错原因**与**建议处理方案**，并允许挂附件。一条配置的业务主语由 `product_code + funding_party_code + error_keyword` 三元组确定，对外查询时并不直接按关键字等值取数，而是把该资方该产品下所有 `enable='Y'` 的配置拉回内存，用 `errorMessage.contains(error_keyword)` 做包含匹配，因此一次报错可以命中多条配置并全部返回。

`funding_party_code` 承载的是资方 RPC 返回的 fundingKey，而本表新建主键 `exception_no` 由 `PlatFormOperateAppliaction.getBussinessNo` 按 `fundingPartyCode` 生成，前缀为 `EXCEPTION_NO_<fundingPartyCode>`，即**异常编号与资方绑定**。

## 需求背景

本次语义分析中 `reqdoc_claims` 为空，没有任何需求文档锚点挂载到本表，因此上面的业务定位全部由代码与 DB 证据反推，不含文档声明。

## 版本演进

本表未出现 `action=uncovered` 的需求主张，故无 (document_claim，未证实) 条目。字段层面的可见演进事实：`file_path` 以 JSON 串 `{"files":[{"filePath":...}]}` 形式存储多附件，属后期扩展的结构；`product_code` 在 DB 实测仅出现 `ACFLOW` / `RVSFACTOR_PC` 两个值，说明该表最初可能只服务单一产品，随后扩展到多产品——但这属于推断，未被文档或迁移脚本证实。

```ground:table
table: funding_exception_resolution
fields:
  - name: exception_no
    meaning: "异常编号，新增/导入时由 PlatFormOperateAppliaction.getBussinessNo 按 fundingPartyCode 生成（前缀 EXCEPTION_NO_<fundingPartyCode>）"
    evidence: code
  - name: funding_party_code
    meaning: "对接方标识，取资方 RPC 返回的 fundingKey；导入时支持填写「资金方名称-fundingKey」组合串再映射"
    evidence: code
  - name: funding_party_name
    meaning: "资金方名称；导出时由 funding_party_code 反查映射为「名称(code)」"
    evidence: code
  - name: error_keyword
    meaning: "报错关键字；对外查询时用 errorMessage.contains(error_keyword) 内存匹配命中度"
    evidence: code
  - name: error_reason
    meaning: "报错原因（选填，导入不校验）"
    evidence: code
  - name: suggestion
    meaning: "建议处理方案（导入必填列）"
    evidence: code
  - name: file_path
    meaning: "附件 JSON 串，结构 {\"files\":[{\"filePath\":...}]}，对外查询时逐条 filePathEncrypt 成 URL"
    evidence: code
  - name: product_code
    meaning: "产品code（值来自 ProductCodeEnum），DB 实测为 ACFLOW / RVSFACTOR_PC"
    evidence: db+code
  - name: enable
    meaning: "有效标识，Y=有效；查询/导出均过滤 enable='Y'"
    evidence: db+code
```

## 关联

- 口径：[[calibers/exception_resolution_valid_enable_y]]、[[calibers/exception_resolution_unique_config]]
- 规则：[[rules/exception_import_all_or_nothing]]、[[rules/exception_unique_key_dedup]]、[[rules/exception_upsert_write]]、[[rules/exception_export_limit_50000]]、[[rules/exception_import_row_limit_5000]]、[[rules/exception_export_funding_party_name_acflow]]、[[rules/exception_provider_keyword_contains]]、[[rules/exception_provider_exception_fallback]]
- 概念：[[concepts/funding_party_code]]、[[concepts/funding_key]]、[[concepts/product_code]]
---END FILE---

---FILE: tables/funding_rule_info.md ---
---
type: table
title: 资方规则信息表（funding_rule_info）
page_key: tables/funding_rule_info
domain: funding
status: draft
aliases:
  - funding_rule_info
  - 资方规则主表
  - 资金方规则信息
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_info"
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#activeRule"
  - "code:FundRuleInfoApplication#inActiveRule"
  - "code:FundRuleInfoApplication#exportRecords"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则信息表（funding_rule_info）

## 业务定位

本表是**资方规则的版本化主表**：一个「产品 + 资方」组合对应一条主记录（由 `code` 唯一标识，`DataModelUtils.getUniqueKey()` 生成），其下挂载若干明细（见 [[tables/funding_rule_detail]]）。主表承载三类信息：身份（`product_code` + `funding_party_mark` + `funding_party_name`）、生命周期（`rule_status` + `version`）、有效标识（`enable`）。

规则的**生命周期**是本表的语义核心：新增即落 `PENDING`，需显式生效才变 `ACTIVE`，外部（Dubbo）只能消费 `ACTIVE` 规则；每次更新 `version` 累加 1，明细随之携带同版本。详见 [[processes/funding_rule_status_machine]]。

## 需求背景

语义分析未挂载任何 `reqdoc_claims`，本页背景描述均来自代码证据：`saveRuleInfo` 的新增查重（`productCode + fundingPartyMark`）、`activeRule` / `inActiveRule` 的状态迁移、`FundingPartyRuleProviderImpl#doQuery` 的 `rule_status=ACTIVE` 过滤，共同构成了「先建后生效、外部只见生效版」的设计意图。

## 版本演进

无 `action=uncovered` 的主张，故无 (document_claim，未证实) 条目。字段级演进事实：`version` 从新增时的 1 开始逐次累加，明细表 `funding_rule_detail.version` 会跟随主表版本，DB 实测分布为 1/2/3/4/6/8/9/13/17/23/25，说明同一主记录已被反复更新（非连续值属正常，因为并非每次更新都落明细）。

```ground:table
table: funding_rule_info
fields:
  - name: funding_party_mark
    meaning: "资金方标识（资方标识），取资方 RPC 返回的 fundingKey，与异常解析的 funding_party_code 同源"
    evidence: code
  - name: funding_party_name
    meaning: "资方名称，更新/导入时回写"
    evidence: code
  - name: product_code
    meaning: "产品code（DB 实测 ACFLOW / RVSFACTOR_PC）"
    evidence: db+code
  - name: rule_status
    meaning: "规则状态，枚举 ACTIVE/INACTIVE/PENDING"
    evidence: code
  - name: version
    meaning: "版本号，新增=1，每次更新累加1"
    evidence: code
  - name: code
    meaning: "规则信息唯一编码（DataModelUtils.getUniqueKey），被 funding_rule_detail.fund_rule_code_ref 引用"
    evidence: code
  - name: enable
    meaning: "有效标识，Y=有效"
    evidence: db+code
```

## 关联

- 口径：[[calibers/funding_rule_info_valid_enable_y]]、[[calibers/funding_rule_info_active_rule]]
- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_create_duplicate_check]]、[[rules/rule_info_update_version_increment]]、[[rules/rule_info_create_initial_pending]]、[[rules/rule_info_provider_active_only]]、[[rules/rule_import_product_code_direct_match]]
- 概念：[[concepts/rule_layer]]、[[concepts/product_code]]、[[concepts/funding_key]]
---END FILE---

---FILE: tables/funding_rule_detail.md ---
---
type: table
title: 资方规则明细表（funding_rule_detail）
page_key: tables/funding_rule_detail
domain: funding
status: draft
aliases:
  - funding_rule_detail
  - 资方规则明细
  - 规则明细表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_detail"
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#getRuleInfoById"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则明细表（funding_rule_detail）

## 业务定位

本表以「键值对 + 规则层」的形式承载资方规则的具体内容：一行即一条 **规则项**，`rule_key` 是机器键（对应前端配置 [[tables/funding_rule_front_cfg]] 的 `front_key`），`rule_value` 是规则值，`rule_layer`（`UNDERLYING` / `FINANCING` / `OTHER`）决定这条规则归属底层/融资/其他哪一层。业务上通过 `rule_info_id` / `fund_rule_code_ref` 双通道回指主表 [[tables/funding_rule_info]]，并冗余 `funding_party_mark` 与 `version` 以便独立查询。

所有明细查询都带 `enable='Y'`（见 [[calibers/funding_rule_detail_valid_enable_y]]）；保存采用「按 `ruleInfoId + ruleKey + enable='Y'` 命中即更新、否则新增」的幂等写法。

## 需求背景

无语义分析挂载的需求文档锚点。当前理解来自 `FundRuleInfoApplication#saveRuleInfo` 与 `FundingPartyRuleProviderImpl#doQuery`：明细以 `ruleKey` 为幂等粒度落库，未在 `ruleMap` 中出现的 `frontKey` 直接跳过而不中断保存。

## 版本演进

无 `action=uncovered` 的主张。DB 实测 `version` 值为 1/2/3/4/6/8/9/13/17/23/25，说明明细跟随主表版本写入但并非逐版留痕；`check_scene` 实测仅 `SUBMIT_VALIDATE`，表明当前明细规则只服务「提交校验」这一场景。

```ground:table
table: funding_rule_detail
fields:
  - name: rule_key
    meaning: "字段key，对应 funding_rule_front_cfg.front_key"
    evidence: db+code
  - name: rule_value
    meaning: "规则值"
    evidence: db+code
  - name: rule_layer
    meaning: "规则层，枚举 UNDERLYING/FINANCING/OTHER"
    evidence: db+code
  - name: rule_info_id
    meaning: "关联 funding_rule_info.id"
    evidence: db+code
  - name: fund_rule_code_ref
    meaning: "关联规则信息 code（funding_rule_info.code）"
    evidence: db+code
  - name: version
    meaning: "版本，跟随 ruleInfo.version；DB 实测分布 1/2/3/4/6/8/9/13/17/23/25"
    evidence: db
  - name: funding_party_mark
    meaning: "资方标识（冗余）"
    evidence: db+code
  - name: check_scene
    meaning: "校验场景，DB 实测值为 SUBMIT_VALIDATE"
    evidence: db
  - name: enable
    meaning: "有效标识，Y=有效；查询 detail 均加 enable='Y'"
    evidence: db+code
```

## 关联

- 口径：[[calibers/funding_rule_detail_valid_enable_y]]
- 规则：[[rules/rule_detail_save_idempotent]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]
- 表：[[tables/funding_rule_info]]、[[tables/funding_rule_front_cfg]]
---END FILE---

---FILE: tables/funding_rule_front_cfg.md ---
---
type: table
title: 前端规则配置表（funding_rule_front_cfg）
page_key: tables/funding_rule_front_cfg
domain: funding
status: draft
aliases:
  - funding_rule_front_cfg
  - 前端字段配置
  - 规则前端配置表
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_rule_front_cfg"
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 前端规则配置表（funding_rule_front_cfg）

## 业务定位

本表是**规则字段的元数据字典**，定义「页面上有哪些可配置字段、字段显示成什么名字、属于哪类业务规则、归在哪个规则层」。它决定了 [[tables/funding_rule_detail]] 中 `rule_key` 的合法取值域（`front_key`），也决定导入模板中「规则名称」列如何匹配（按 `key_name`，配合 `product + rule_layer + key_name` 三元组）。

`key_type` 描述字段受哪一类业务规则约束，DB 实测枚举为 `FIELD_REQUIRED` / `FIELD_LENGTH_LIMIT` / `FILE_TYPE_LIMIT` / `FILE_SIZE_SINGLE_LIMIT` / `FILE_SIZE_TOTAL_LIMIT` / `FILE_SIZE_PACKAGE_LIMIT` / `FILE_COUNT_LIMIT` / `FILE_NAME_SYMBOL` / `INVOICE_COUNT_LIMIT` / `YEARS_CHECK` / `DATE_CHECK_NATURAL` / `DATE_CHECK_WORKDAY`，覆盖必填、长度、附件类型/大小/数量、发票份数、年限与日期（自然日/工作日）校验。

## 需求背景

无语义分析挂载的需求文档锚点。当前理解来自 `FundRuleInfoApplication#validateRuleLayerAndFrontCfg`（校验规则层与前端配置一致性）与 `FundingPartyRuleProviderImpl#doQuery`（对外查询需带 `enable='Y'` 的前端配置）。

## 版本演进

无 `action=uncovered` 的主张。字段级事实：`check_scene` 实测仅 `SUBMIT_VALIDATE`，表明本表配置目前只驱动提交环节校验；`front_key_name` 与 `key_name` 并存，说明展示名存在「名称描述」与「前端展示名」两套，导入匹配使用 `key_name`。

```ground:table
table: funding_rule_front_cfg
fields:
  - name: front_key
    meaning: "前端字段key，被 detail.rule_key 关联"
    evidence: db+code
  - name: key_name
    meaning: "字段名称描述（导入模板「规则名称」按此匹配）"
    evidence: db+code
  - name: key_type
    meaning: "字段业务规则类型，DB 实测枚举：FIELD_REQUIRED/FIELD_LENGTH_LIMIT/FILE_TYPE_LIMIT/FILE_SIZE_SINGLE_LIMIT/FILE_SIZE_TOTAL_LIMIT/FILE_SIZE_PACKAGE_LIMIT/FILE_COUNT_LIMIT/FILE_NAME_SYMBOL/INVOICE_COUNT_LIMIT/YEARS_CHECK/DATE_CHECK_NATURAL/DATE_CHECK_WORKDAY"
    evidence: db
  - name: rule_key
    meaning: "规则字段key"
    evidence: db+code
  - name: rule_layer
    meaning: "规则层 UNDERLYING/FINANCING/OTHER；页面配置按此分组"
    evidence: db+code
  - name: front_key_name
    meaning: "前端展示字段名称"
    evidence: db
  - name: check_scene
    meaning: "校验场景，DB 实测 SUBMIT_VALIDATE"
    evidence: db
  - name: enable
    meaning: "有效标识，Y=有效；导入匹配前端配置时过滤 enable='Y'"
    evidence: db+code
```

## 关联

- 口径：[[calibers/funding_rule_front_cfg_valid_enable_y]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]
- 表：[[tables/funding_rule_detail]]
---END FILE---

---FILE: processes/funding_rule_status_machine.md ---
---
type: process
title: 资方规则状态机
page_key: processes/funding_rule_status_machine
domain: funding
status: draft
aliases:
  - rule_status 状态机
  - 规则状态流转
  - 资方规则生命周期
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "code:FundRuleInfoApplication#activeRule"
  - "code:FundRuleInfoApplication#inActiveRule"
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则状态机

## 业务定位

资方规则不是一个「保存即生效」的对象，而是带三态的生命周期对象：`PENDING`（待生效）→ `ACTIVE`（已生效）⇄ `INACTIVE`（已失效）。新增入口 `saveRuleInfo` 在 `ruleInfoId` 为空时**强制**落到 `PENDING`，运营必须再调用 `activeRule` 才对外可见；`inActiveRule` 可从 `ACTIVE` 或 `PENDING` 直接落到 `INACTIVE`，但**没有**从 `INACTIVE` 回到 `PENDING` 的路径——`INACTIVE` 只能重新生效为 `ACTIVE`。

外部消费方（Dubbo：[[rules/rule_info_provider_active_only]]）只按 `rule_status='ACTIVE'` 取数，取不到即返回 null，因此「已失效」与「待生效」对外表现一致：都不可见。

## 需求背景

无语义分析挂载的需求文档锚点。状态取值来自代码枚举，迁移路径来自 `saveRuleInfo` / `activeRule` / `inActiveRule` 三个入口方法的证据。

## 版本演进

无 `action=uncovered` 的主张。状态与版本耦合：每次 `saveRuleInfo`（`ruleInfoId` 非空）使 `version` 累加 1（见 [[rules/rule_info_update_version_increment]]），但状态迁移本身不改 `version`，因此同一 `version` 下规则可能经历 `PENDING→ACTIVE→INACTIVE` 的状态变化，版本号并不等于状态轮次。

```ground:process
process: 资方规则状态机
field: funding_rule_info.rule_status
states:
  - value: PENDING
    label: 待生效
    source: code_enum
  - value: ACTIVE
    label: 已生效
    source: code_enum
  - value: INACTIVE
    label: 已失效
    source: code_enum
transitions:
  - from: "(无)"
    event: saveRuleInfo 新增（ruleInfoId 为空）
    to: PENDING
    evidence: "code_path:FundRuleInfoApplication.java#saveRuleInfo"
  - from: PENDING
    event: activeRule 生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#activeRule"
  - from: INACTIVE
    event: activeRule 生效
    to: ACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#activeRule"
  - from: ACTIVE
    event: inActiveRule 失效
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#inActiveRule"
  - from: PENDING
    event: inActiveRule 失效
    to: INACTIVE
    evidence: "code_path:FundRuleInfoApplication.java#inActiveRule"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 口径：[[calibers/funding_rule_info_active_rule]]、[[calibers/funding_rule_info_valid_enable_y]]
- 规则：[[rules/rule_info_create_initial_pending]]、[[rules/rule_info_provider_active_only]]、[[rules/rule_info_update_version_increment]]
---END FILE---

---FILE: calibers/exception_resolution_valid_enable_y.md ---
---
type: caliber
title: 异常解析-有效数据口径
page_key: calibers/exception_resolution_valid_enable_y
domain: funding
status: draft
aliases:
  - 异常解析有效数据
  - exception enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
  - "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
  - "db:funding_exception_resolution"
contract_version: "0.1"
---

# 异常解析-有效数据口径

## 业务定位

凡是从 [[tables/funding_exception_resolution]] 取数的出口——运营导出、列表查询、对外 Provider 查询——一律附加 `enable = 'Y'`。这意味着「软删除」的语义在本表完全由 `enable` 承担：一条被置为非 `Y` 的异常解析配置对任何读取方都不存在。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该口径在三个读取面上表现一致，未发现例外路径。

```ground:caliber
caliber: 异常解析-有效数据
predicate: "funding_exception_resolution.enable = 'Y'"
scope: 导出/列表查询/对外Provider查询
evidence: "code:ExceptionResolutionApplication#exportRecords; FundingPartyExceptionResolutionProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_upsert_write]]、[[rules/exception_provider_keyword_contains]]
---END FILE---

---FILE: calibers/exception_resolution_unique_config.md ---
---
type: caliber
title: 异常解析-唯一配置口径
page_key: calibers/exception_resolution_unique_config
domain: funding
status: draft
aliases:
  - 异常解析唯一键
  - 异常解析三元组唯一
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication#checkBeforeSave"
contract_version: "0.1"
---

# 异常解析-唯一配置口径

## 业务定位

[[tables/funding_exception_resolution]] 的业务唯一性是三元组 `product_code + funding_party_code + error_keyword`，物理上由唯一约束 `funding_exception_resolution_un` 保证。导入去重、保存前校验、upsert 写入全部以此三元组为准：命中已有记录即报「异常解析配置信息已存在」，而不是插入第二条。

注意该口径**不含 `enable`**：`enable` 只影响可读性，不影响唯一性判定。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 唯一索引与代码 `checkBeforeSave` 双保险，属同一口径的两处实现。

```ground:caliber
caliber: 异常解析-唯一配置
predicate: "funding_exception_resolution.product_code + funding_party_code + error_keyword 唯一"
scope: 导入去重/保存前校验/upsert
evidence: "db:funding_exception_resolution_un; code:ExceptionResolutionApplication#checkBeforeSave"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_unique_key_dedup]]、[[rules/exception_import_all_or_nothing]]
---END FILE---

---FILE: calibers/funding_rule_info_valid_enable_y.md ---
---
type: caliber
title: 资方规则-有效信息口径
page_key: calibers/funding_rule_info_valid_enable_y
domain: funding
status: draft
aliases:
  - 资方规则有效信息
  - rule_info enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#exportRecords"
  - "db:funding_rule_info"
contract_version: "0.1"
---

# 资方规则-有效信息口径

## 业务定位

资方规则主表的读取口径为 `enable = 'Y'`，导出与查询均按此过滤。与异常解析一致，`enable` 是软删除开关，与 `rule_status` 正交：一条 `enable='Y'` 但 `rule_status='INACTIVE'` 的规则对运营可见、对 Dubbo 外部不可见（见 [[calibers/funding_rule_info_active_rule]]）。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 资方规则-有效信息
predicate: "funding_rule_info.enable = 'Y'"
scope: 导出/查询
evidence: "code:FundRuleInfoApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 口径：[[calibers/funding_rule_info_active_rule]]
---END FILE---

---FILE: calibers/funding_rule_info_active_rule.md ---
---
type: caliber
title: 资方规则-生效规则口径
page_key: calibers/funding_rule_info_active_rule
domain: funding
status: draft
aliases:
  - 生效规则口径
  - rule_status=ACTIVE
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "code:FundRuleInfoApplication#activeRule"
contract_version: "0.1"
---

# 资方规则-生效规则口径

## 业务定位

**对外**（Dubbo Provider）查询资方规则时，除 `fundingPartyMark + productCode` 之外必须叠加 `rule_status = 'ACTIVE'`，否则返回 null。这是「内外部可见性分离」的关键口径：运营侧可以查看并维护 `PENDING` / `INACTIVE` 规则，但外部系统永远只能消费已生效版本，从而保证规则变更不会半途泄露给上游。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该口径与状态机 [[processes/funding_rule_status_machine]] 的 `activeRule` 入口共同构成「生效即可见」的语义闭环。

```ground:caliber
caliber: 资方规则-生效规则
predicate: "funding_rule_info.rule_status = 'ACTIVE'"
scope: Dubbo 对外查询资金方规则
evidence: "code:FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_provider_active_only]]
---END FILE---

---FILE: calibers/funding_rule_detail_valid_enable_y.md ---
---
type: caliber
title: 资方规则详情-有效口径
page_key: calibers/funding_rule_detail_valid_enable_y
domain: funding
status: draft
aliases:
  - 规则详情有效口径
  - rule_detail enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "code:FundRuleInfoApplication#getRuleInfoById"
  - "db:funding_rule_detail"
contract_version: "0.1"
---

# 资方规则详情-有效口径

## 业务定位

明细的读取一律带 `enable = 'Y'`：无论是对外查询组装规则包，还是运营侧按 id 查看规则详情，都只取有效明细行。保存侧同样以 `enable='Y'` 作为幂等匹配条件（命中即更新、否则新增），因此「失效一条旧明细、新增一条同 `rule_key` 明细」在有 `enable` 过滤的前提下不会互相污染。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 资方规则详情-有效
predicate: "funding_rule_detail.enable = 'Y'"
scope: 规则详情/对外查询
evidence: "code:FundingPartyRuleProviderImpl#doQuery; FundRuleInfoApplication#getRuleInfoById"
```

## 关联

- 表：[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]
---END FILE---

---FILE: calibers/funding_rule_front_cfg_valid_enable_y.md ---
---
type: caliber
title: 前端规则配置-有效口径
page_key: calibers/funding_rule_front_cfg_valid_enable_y
domain: funding
status: draft
aliases:
  - 前端配置有效口径
  - front_cfg enable=Y
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
  - "code:FundingPartyRuleProviderImpl#doQuery"
  - "db:funding_rule_front_cfg"
contract_version: "0.1"
---

# 前端规则配置-有效口径

## 业务定位

[[tables/funding_rule_front_cfg]] 的读取统一带 `enable = 'Y'`：页面按 `rule_layer` 分组渲染配置项、导入时按 `product + rule_layer + key_name` 匹配前端字段、对外查询组装规则包，三处都只认有效配置。这意味着下线一个字段的规范做法是把配置置为非 `Y`，而不是删行——历史明细中的 `rule_key` 仍可追溯。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:caliber
caliber: 前端规则配置-有效
predicate: "funding_rule_front_cfg.enable = 'Y'"
scope: 页面配置/导入匹配/对外查询
evidence: "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg; FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_rule_front_cfg]]
- 概念：[[concepts/rule_key]]、[[concepts/rule_layer]]
---END FILE---

---FILE: concepts/funding_party_code.md ---
---
type: concept
title: 对接方标识（fundingPartyCode）
page_key: concepts/funding_party_code
domain: funding
status: draft
aliases:
  - fundingPartyCode
  - funding_party_code
  - 对接方标识
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication"
  - "code:FundRuleInfoApplication"
contract_version: "0.1"
maps_to: "funding_exception_resolution.funding_party_code = 资方RPC 返回的 fundingKey"
field_targets:
  - funding_exception_resolution.funding_party_code
adjudication: boundary
also_confused_with:
  - 资金方标识(fundingPartyMark)
  - 资金方名称(fundingPartyName)
boundary: "异常解析表用 funding_party_code 承载资方 fundingKey；规则表用 funding_party_mark 承载同一 fundingKey，命名不同但语义同源，禁止跨表混用字段名。异常解析导入还允许填「资金方名称-fundingKey」组合串再映射为 fundingKey"
---

# 对接方标识（fundingPartyCode）

## 业务定位

「对接方标识」= **资方 RPC 返回的 fundingKey**，是资方在系统中的唯一键。它在两处表结构中用**不同字段名**落地：

- [[tables/funding_exception_resolution]] → `funding_party_code`
- [[tables/funding_rule_info]] / [[tables/funding_rule_detail]] → `funding_party_mark`

两者语义同源、命名不同，**跨表不可混用字段名**。此外，异常解析的导入模板允许运营填「资金方名称-fundingKey」组合串，系统先做名称映射再落库为 fundingKey；而规则侧是直接使用 fundingKey。

## 需求背景

无语义分析挂载的需求文档锚点。该术语边界由代码证据裁定：异常解析侧存在组合串映射逻辑，规则侧不存在。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_key]]、[[concepts/funding_party]]、[[concepts/product_code]]
- 表：[[tables/funding_exception_resolution]]、[[tables/funding_rule_info]]
---END FILE---

---FILE: concepts/funding_party.md ---
---
type: concept
title: 资金方 / 资方（fundingParty）
page_key: concepts/funding_party
domain: funding
status: draft
aliases:
  - fundingParty
  - 资方
  - 对接方
  - 资金方
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ClientQueryFunderCodeService"
  - "code:ClientQueryFunderMarkService"
contract_version: "0.1"
maps_to: "资方RPC（ClientQueryFunderCodeService / ClientQueryFunderMarkService）返回的 fundingKey + fundingPartyName"
field_targets:
  - funding_exception_resolution.funding_party_name
  - funding_rule_info.funding_party_name
adjudication: synonym
also_confused_with:
  - 金融机构
  - 产品
boundary: "资金方=资方=对接方，均指某产品下对接的金融/资金机构；仅在字段命名（code/mark）上区分，业务含义一致"
---

# 资金方 / 资方（fundingParty）

## 业务定位

在业务口径上，「资金方」「资方」「对接方」是**同义词**，都指某个产品下对接的金融/资金机构；差异只体现在落字段时的命名（`code` 还是 `mark`），业务含义完全一致。资方信息的来源是资方 RPC（`ClientQueryFunderCodeService` / `ClientQueryFunderMarkService`），返回 `fundingKey`（唯一键）与 `fundingPartyName`（名称）两个值。

资方与「金融机构」不是同一层级概念：资金方是**产品视角**下的合作机构配置，而产品本身（`product_code`，如 `ACFLOW` / `RVSFACTOR_PC`）是更上层的分类维度。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_key]]、[[concepts/funding_party_code]]、[[concepts/product_code]]
---END FILE---

---FILE: concepts/funding_key.md ---
---
type: concept
title: fundingKey（资方唯一键）
page_key: concepts/funding_key
domain: funding
status: draft
aliases:
  - fundingKey
  - fundingPartyCode
  - fundingPartyMark
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:CustFundingPartyResultDto"
contract_version: "0.1"
maps_to: "CustFundingPartyResultDto.fundingKey（资方唯一键）"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_rule_info.funding_party_mark
adjudication: synonym
also_confused_with:
  - fundingPartyName
boundary: "同一资方键：异常解析场景作为 funding_party_code 使用（需先经名称-键组合映射），规则场景作为 funding_party_mark 直接使用；不可与 fundingPartyName 混淆"
---

# fundingKey（资方唯一键）

## 业务定位

`fundingKey` 是 `CustFundingPartyResultDto` 中资方的唯一键，是整个「资金规则与异常处理」主题下**跨表引用资方的唯一锚点**。它有两个使用场景：

| 场景 | 落库字段 | 进入方式 |
| --- | --- | --- |
| 异常解析 | `funding_exception_resolution.funding_party_code` | 需先经「名称-键」组合串映射 |
| 资方规则 | `funding_rule_info.funding_party_mark` | 直接使用 |

**绝不可与 `fundingPartyName` 混淆**：前者是键，后者是展示名。异常解析导出时用 `funding_party_code` 反查映射为「名称(code)」，正是键→名的单向派生。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_party_code]]、[[concepts/funding_party]]
- 规则：[[rules/exception_export_funding_party_name_acflow]]
---END FILE---

---FILE: concepts/product_code.md ---
---
type: concept
title: 产品code（productCode）
page_key: concepts/product_code
domain: funding
status: draft
aliases:
  - productCode
  - product_code
  - 产品code
  - 产品编码
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ProductCodeEnum"
  - "code:ExceptionResolutionApplication#importRecords"
  - "code:FundRuleInfoApplication#collectFundRuleProductCodeErrors"
contract_version: "0.1"
maps_to: "ProductCodeEnum 常量（如 ACFLOW / RVSFACTOR_PC）"
field_targets:
  - funding_exception_resolution.product_code
  - funding_rule_info.product_code
adjudication: boundary
also_confused_with:
  - productName
  - platformProductCode
boundary: "异常解析导入先按 platformProduct.listPlatformProduct 构建 productName→productCode 映射再校验（模板「产品code」列实际可填产品名称）；规则导入直接以 productCode 与 ProductCodeEnum 比对，无名称转换，两者口径不同"
---

# 产品code（productCode）

## 业务定位

`product_code` 的取值来自 `ProductCodeEnum`，DB 实测只有 `ACFLOW` 与 `RVSFACTOR_PC` 两个值。它是异常解析配置与资方规则的共同分类维度：配置与规则都按「产品 + 资方」隔离。

**两条导入链路的校验口径不同**，这是本概念最容易踩坑的边界：

- 异常解析导入：先通过 `platformProduct.listPlatformProduct` 构建 `productName → productCode` 映射再校验——模板「产品code」列**实际可以填产品名称**。
- 资方规则导入：直接拿 `productCode` 与 `ProductCodeEnum` 比对，**没有名称转换**——模板产品列必须填产品 code。

## 需求背景

无语义分析挂载的需求文档锚点。两条链路的口径差异由代码证据裁定。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/funding_party]]、[[concepts/funding_key]]
- 规则：[[rules/rule_import_product_code_direct_match]]、[[rules/exception_export_funding_party_name_acflow]]
---END FILE---

---FILE: concepts/rule_layer.md ---
---
type: concept
title: 规则层（ruleLayer）
page_key: concepts/rule_layer
domain: funding
status: draft
aliases:
  - ruleLayer
  - rule_layer
  - 规则层
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:RuleLayerEnum"
  - "code:FundRuleInfoApplication#validateRuleLayerAndFrontCfg"
contract_version: "0.1"
maps_to: "UNDERLYING / FINANCING / OTHER（RuleLayerEnum）"
field_targets:
  - funding_rule_detail.rule_layer
  - funding_rule_front_cfg.rule_layer
adjudication: boundary
also_confused_with:
  - 规则层级显示名(底层规则/融资规则/其他规则)
boundary: "导入模板填显示名，经 RuleLayerEnum.getDisplayName 反查 dictKey；存储与查询使用 dictKey"
---

# 规则层（ruleLayer）

## 业务定位

规则层是资方规则的**分组维度**，枚举为 `UNDERLYING`（底层）/ `FINANCING`（融资）/ `OTHER`（其他）。页面配置（[[tables/funding_rule_front_cfg]]）按此分组渲染，规则明细（[[tables/funding_rule_detail]]）按此归类；保存前还有专门的 `validateRuleLayerAndFrontCfg` 校验规则层与前端配置是否自洽。

**边界**：导入模板里运营填的是**显示名**（「底层规则 / 融资规则 / 其他规则」），系统经 `RuleLayerEnum.getDisplayName` 反查得到 `dictKey`；存储与查询一律使用 `dictKey`。导入时的字段匹配用三元组 `product + rule_layer + key_name`，此处的 `rule_layer` 同样是 `dictKey`。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/rule_key]]
- 表：[[tables/funding_rule_front_cfg]]、[[tables/funding_rule_detail]]
---END FILE---

---FILE: concepts/rule_key.md ---
---
type: concept
title: 规则键（ruleKey）
page_key: concepts/rule_key
domain: funding
status: draft
aliases:
  - ruleKey
  - rule_key
  - front_key
  - 规则键
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
  - "db:funding_rule_front_cfg"
contract_version: "0.1"
maps_to: "funding_rule_front_cfg.front_key = funding_rule_detail.rule_key"
field_targets:
  - funding_rule_front_cfg.front_key
  - funding_rule_detail.rule_key
adjudication: boundary
also_confused_with:
  - key_name
  - front_key_name
boundary: "detail.rule_key 存 front_cfg.front_key（机器键）；key_name/front_key_name 为展示名，导入匹配用 key_name（product+rule_layer+key_name 三元组）"
---

# 规则键（ruleKey）

## 业务定位

「规则键」串起了资方规则的**定义侧**与**实例侧**：`funding_rule_front_cfg.front_key` 是机器键（定义），`funding_rule_detail.rule_key` 存的就是这个机器键（实例）。明细保存时的幂等粒度正是 `ruleInfoId + ruleKey + enable='Y'`。

**边界**：`key_name` / `front_key_name` 是**展示名**，不是键。导入模板中的「规则名称」列按 `key_name` 匹配，匹配条件为 `product + rule_layer + key_name` 三元组；也就是说，人读的是名称，机器认的是键。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

## 关联

- 概念：[[concepts/rule_layer]]
- 表：[[tables/funding_rule_front_cfg]]、[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]
---END FILE---

---FILE: rules/exception_import_all_or_nothing.md ---
---
type: rule
title: 异常解析导入-全量校验通过才入库
page_key: rules/exception_import_all_or_nothing
domain: funding
status: draft
aliases:
  - 异常解析导入原子性
  - all-or-nothing 导入
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#importRecords"
contract_version: "0.1"
---

# 异常解析导入-全量校验通过才入库

## 业务定位

异常解析导入依次执行四阶段校验——行级必填、`productCode` 枚举、对接方标识存在性、唯一键重复；**任一阶段产生错误即返回错误列表且不写库**。这保证批量导入的原子性，避免「一半成功一半失败」导致运营无法判断最终状态。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与之配套的还有 [[rules/exception_import_row_limit_5000]] 的规模上限。

```ground:rule
rule: 异常解析导入-全量校验通过才入库
content: "导入依次执行行级必填、productCode 枚举、对接方标识存在性、唯一键重复校验；任一阶段产生错误则返回错误列表且不写库（all-or-nothing）"
impact: "保证批量导入原子性，避免半量写入"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: "code:ExceptionResolutionApplication#importRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_import_rpc_group_by_product]]、[[rules/exception_unique_key_dedup]]、[[rules/exception_upsert_write]]
---END FILE---

---FILE: rules/exception_import_rpc_group_by_product.md ---
---
type: rule
title: 异常解析导入-按产品分组RPC
page_key: rules/exception_import_rpc_group_by_product
domain: funding
status: draft
aliases:
  - 对接方标识校验按产品分组
  - 分组RPC校验
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#collectFundingPartyCodeErrors"
contract_version: "0.1"
---

# 异常解析导入-按产品分组RPC

## 业务定位

校验导入行中的「对接方标识」是否存在时，**按 `productCode` 分组，每组只发一次 RPC**，禁止逐行循环调用。这是对远程调用次数的硬性约束：一次导入最多产生「产品种类数」次调用，而不是「行数」次，避免批量导入把资方服务打爆。

## 需求背景

无语义分析挂载的需求文档锚点。该方法名 `collectFundingPartyCodeErrors` 表明校验被拆成独立收集步骤，便于与其他阶段解耦。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析导入-按产品分组RPC
content: "对接方标识校验按 productCode 分组，每组一次 RPC，禁止循环调用"
impact: "限制远程调用次数，避免性能问题"
field_targets:
  - funding_exception_resolution.funding_party_code
evidence: "code:ExceptionResolutionApplication#collectFundingPartyCodeErrors"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 概念：[[concepts/product_code]]、[[concepts/funding_party_code]]
- 规则：[[rules/exception_import_all_or_nothing]]
---END FILE---

---FILE: rules/exception_unique_key_dedup.md ---
---
type: rule
title: 异常解析-唯一键去重
page_key: rules/exception_unique_key_dedup
domain: funding
status: draft
aliases:
  - 异常解析重复校验
  - 异常解析配置信息已存在
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "db:funding_exception_resolution_un"
  - "code:ExceptionResolutionApplication#checkBeforeSave"
contract_version: "0.1"
---

# 异常解析-唯一键去重

## 业务定位

当 `(product_code, funding_party_code, error_keyword)` 命中已有记录时，报错「异常解析配置信息已存在」并拒绝写入。该判定与 DB 唯一约束 `funding_exception_resolution_un` 一一对应（口径见 [[calibers/exception_resolution_unique_config]]），代码层提前拦截是为了给出可读的错误提示，而不是把唯一约束异常抛给运营。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析-唯一键去重
content: "(product_code, funding_party_code, error_keyword) 命中原有记录时报「异常解析配置信息已存在」"
impact: "防止重复配置"
field_targets:
  - funding_exception_resolution.product_code
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.error_keyword
evidence: "db:funding_exception_resolution_un; code:ExceptionResolutionApplication#checkBeforeSave"
```

## 关联

- 口径：[[calibers/exception_resolution_unique_config]]
- 规则：[[rules/exception_import_all_or_nothing]]
---END FILE---

---FILE: rules/exception_upsert_write.md ---
---
type: rule
title: 异常解析-upsert写入
page_key: rules/exception_upsert_write
domain: funding
status: draft
aliases:
  - 异常解析写入规则
  - 异常解析 upsert
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#doUpsertAll"
contract_version: "0.1"
---

# 异常解析-upsert写入

## 业务定位

全部校验通过后，在**单个事务**内执行 `saveOrUpdateBatch`，统一置 `enable='Y'`，同时生成 `exception_no` 并回填创建人/更新人。三件事必须同事务：有效标识、编号生成、审计字段——否则会出现「有编号但不可见」或「可见但无编号」的脏数据。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。编号生成规则见 [[tables/funding_exception_resolution]] 的 `exception_no` 字段说明。

```ground:rule
rule: 异常解析-upsert写入
content: "全部校验通过后在单事务内 saveOrUpdateBatch，置 enable='Y'，并生成 exceptionNo、回填创建/更新人"
impact: "保证写入一致性"
field_targets:
  - funding_exception_resolution.enable
  - funding_exception_resolution.exception_no
evidence: "code:ExceptionResolutionApplication#doUpsertAll"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 口径：[[calibers/exception_resolution_valid_enable_y]]
- 规则：[[rules/exception_import_all_or_nothing]]
---END FILE---

---FILE: rules/exception_export_limit_50000.md ---
---
type: rule
title: 异常解析-导出上限50000
page_key: rules/exception_export_limit_50000
domain: funding
status: draft
aliases:
  - 异常解析导出上限
  - 导出50000行限制
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
contract_version: "0.1"
---

# 异常解析-导出上限50000

## 业务定位

单次导出累计行数超过 **50000** 时抛 `BaseException`，提示用户缩小查询范围。该阈值是防止大批量导出导致 OOM 或超时的硬闸门，属**防护性规则**而非业务规则。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与导入侧的行数上限（[[rules/exception_import_row_limit_5000]]）成对出现，读写两侧均有规模约束。

```ground:rule
rule: 异常解析-导出上限50000
content: "单次导出累计行数超过 50000 抛 BaseException，提示缩小查询范围"
impact: "防 OOM/超时"
field_targets: []
evidence: "code:ExceptionResolutionApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_import_row_limit_5000]]、[[rules/exception_export_funding_party_name_acflow]]
---END FILE---

---FILE: rules/exception_import_row_limit_5000.md ---
---
type: rule
title: 异常解析导入-行数上限5000
page_key: rules/exception_import_row_limit_5000
domain: funding
status: draft
aliases:
  - 导入行数超过上限
  - 导入5000行限制
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionImportListener"
contract_version: "0.1"
---

# 异常解析导入-行数上限5000

## 业务定位

单次导入数据行超过 **5000** 时直接抛「导入行数超过上限」，在文件解析阶段就终止，不进入后续校验。与导出上限一起构成异常解析的规模护栏。

## 需求背景

无语义分析挂载的需求文档锚点。该限制在 `ExceptionResolutionImportListener`（EasyExcel 监听器）中生效，说明是按行累计触发的。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析导入-行数上限5000
content: "单次导入数据行超过 5000 抛「导入行数超过上限」"
impact: "控制单批导入规模"
field_targets: []
evidence: "code:ExceptionResolutionImportListener"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_export_limit_50000]]、[[rules/exception_import_all_or_nothing]]
---END FILE---

---FILE: rules/exception_export_funding_party_name_acflow.md ---
---
type: rule
title: 异常解析-导出资金方名称映射固定ACFLOW
page_key: rules/exception_export_funding_party_name_acflow
domain: funding
status: draft
aliases:
  - 导出资金方名称映射
  - mapFundingPartyCode ACFLOW
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:ExceptionResolutionApplication#exportRecords"
contract_version: "0.1"
---

# 异常解析-导出资金方名称映射固定ACFLOW

## 业务定位

导出时使用 `mapFundingPartyCode(ProductCodeEnum.ACFLOW)` 把 `funding_party_code` 反查为「名称(code)」写入 `funding_party_name` 列。**映射被硬编码为 ACFLOW 产品**：当导出的记录属于其他产品（如 `RVSFACTOR_PC`）时，映射结果可能为空，导致跨产品导出时资金方名称展示缺失。

这是本主题下最需要关注的实现约束——它把「按产品维度的资方映射」错误地固定到了单一产品。详见 REVIEW 待确认项。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该行为是否为缺陷、是否已有后续修复，分析中无证据。

```ground:rule
rule: 异常解析-导出资金方名称映射固定ACFLOW
content: "导出时使用 mapFundingPartyCode(ProductCodeEnum.ACFLOW) 将 funding_party_code 映射为「名称(code)」；非 ACFLOW 产品（如 RVSFACTOR_PC）记录映射结果可能为空"
impact: "跨产品导出时资金方名称展示可能缺失"
field_targets:
  - funding_exception_resolution.funding_party_code
  - funding_exception_resolution.funding_party_name
evidence: "code:ExceptionResolutionApplication#exportRecords"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 概念：[[concepts/product_code]]、[[concepts/funding_party_code]]、[[concepts/funding_key]]
---END FILE---

---FILE: rules/rule_info_create_duplicate_check.md ---
---
type: rule
title: 资方规则-新增查重
page_key: rules/rule_info_create_duplicate_check
domain: funding
status: draft
aliases:
  - 资方规则重复新增校验
  - 不允许重复新增
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则-新增查重

## 业务定位

当 `ruleInfoId` 为空（即新增）时，按 `productCode + fundingPartyMark` 查重，已存在则抛「不允许重复新增」。这确立了「**同一产品下同一资方只有一条规则主记录**」的模型——后续修改必须走更新路径（`ruleInfoId` 非空）以累加版本，而不是新建第二条。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。该查重与 [[rules/rule_info_update_version_increment]] 的版本累加共同构成「一资方一规则、版本留痕」的设计。

```ground:rule
rule: 资方规则-新增查重
content: "ruleInfoId 为空时按 productCode + fundingPartyMark 查重，已存在则抛「不允许重复新增」"
impact: "同产品下同一资方唯一规则"
field_targets:
  - funding_rule_info.product_code
  - funding_rule_info.funding_party_mark
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_info]]
- 规则：[[rules/rule_info_update_version_increment]]、[[rules/rule_info_create_initial_pending]]
---END FILE---

---FILE: rules/rule_info_update_version_increment.md ---
---
type: rule
title: 资方规则-更新version+1
page_key: rules/rule_info_update_version_increment
domain: funding
status: draft
aliases:
  - 规则版本累加
  - version+1
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则-更新version+1

## 业务定位

`ruleInfoId` 不为空时视为更新：`version` 在原有基础上累加 1，并回写 `funding_party_name`。明细行随主表写入同一 `version`（见 [[tables/funding_rule_detail]]），因此版本号是「规则内容快照」的标识，可用于追溯某一版规则的具体取值。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 实测明细 `version` 分布为 1/2/3/4/6/8/9/13/17/23/25，说明版本累加是连续的，而明细并非每版都写（跳号来自未落明细的更新）。

```ground:rule
rule: 资方规则-更新version+1
content: "ruleInfoId 不为空时 version 累加 1，并回写 funding_party_name"
impact: "规则版本可追溯，明细携带版本"
field_targets:
  - funding_rule_info.version
  - funding_rule_detail.version
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_info]]、[[tables/funding_rule_detail]]
- 规则：[[rules/rule_detail_save_idempotent]]
---END FILE---

---FILE: rules/rule_info_create_initial_pending.md ---
---
type: rule
title: 资方规则-新增初始PENDING
page_key: rules/rule_info_create_initial_pending
domain: funding
status: draft
aliases:
  - 新增规则默认待生效
  - 初始PENDING
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则-新增初始PENDING

## 业务定位

新增规则时同时落四个初始值：`rule_status=PENDING`、`version=1`、`enable='Y'`、`code=DataModelUtils.getUniqueKey()`。核心语义是「**新增规则默认未生效，必须显式生效**」——新配置不会自动对外可见，给了运营一个检视窗口。参见状态机 [[processes/funding_rule_status_machine]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 资方规则-新增初始PENDING
content: "新增时 rule_status=PENDING、version=1、enable='Y'、code=DataModelUtils.getUniqueKey()"
impact: "新增规则默认未生效，需显式生效"
field_targets:
  - funding_rule_info.rule_status
  - funding_rule_info.version
  - funding_rule_info.enable
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 流程：[[processes/funding_rule_status_machine]]
- 规则：[[rules/rule_info_create_duplicate_check]]、[[rules/rule_info_provider_active_only]]
---END FILE---

---FILE: rules/rule_info_provider_active_only.md ---
---
type: rule
title: 资方规则-对外仅返回ACTIVE
page_key: rules/rule_info_provider_active_only
domain: funding
status: draft
aliases:
  - 对外只返回生效规则
  - Dubbo 仅 ACTIVE
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyRuleProviderImpl#doQuery"
contract_version: "0.1"
---

# 资方规则-对外仅返回ACTIVE

## 业务定位

Dubbo 查询按 `fundingPartyMark + productCode + rule_status='ACTIVE'` 取规则，取不到则**返回 null**（而非空对象或异常）。这是内外可见性的分界线：外部系统只能消费已生效规则，`PENDING` 与 `INACTIVE` 对外均不可见。对应口径 [[calibers/funding_rule_info_active_rule]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。返回 null 的约定要求调用方必须做空值判断。

```ground:rule
rule: 资方规则-对外仅返回ACTIVE
content: "Dubbo 查询按 fundingPartyMark + productCode + rule_status=ACTIVE 取规则，否则返回 null"
impact: "外部只能消费已生效规则"
field_targets:
  - funding_rule_info.rule_status
evidence: "code:FundingPartyRuleProviderImpl#doQuery"
```

## 关联

- 口径：[[calibers/funding_rule_info_active_rule]]、[[calibers/funding_rule_detail_valid_enable_y]]
- 流程：[[processes/funding_rule_status_machine]]
---END FILE---

---FILE: rules/exception_provider_keyword_contains.md ---
---
type: rule
title: 异常解析对外查询-关键字包含匹配
page_key: rules/exception_provider_keyword_contains
domain: funding
status: draft
aliases:
  - 报错关键字包含匹配
  - errorMessage.contains
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
contract_version: "0.1"
---

# 异常解析对外查询-关键字包含匹配

## 业务定位

对外查询先按 `fundingPartyCode + productCode + enable='Y'` 把候选配置全部拉回，再在**内存中**用 `errorMessage.contains(error_keyword)` 过滤，可命中多条并全部返回。因此 `error_keyword` 不是等值键而是**匹配模式**：一条配置的关键字可以是另一条的父串，两条都可能被命中，调用方需按返回顺序自行取舍。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。DB 中的三元组唯一约束（见 [[calibers/exception_resolution_unique_config]]）保证了「同一资方同一产品下关键字不重复」，但**不保证关键字之间不互为子串**。

```ground:rule
rule: 异常解析对外查询-关键字包含匹配
content: "按 fundingPartyCode + productCode + enable='Y' 拉取后，内存过滤 errorMessage.contains(error_keyword)，可命中多条全部返回"
impact: "对外按报错信息匹配异常解析"
field_targets:
  - funding_exception_resolution.error_keyword
  - funding_exception_resolution.enable
evidence: "code:FundingPartyExceptionResolutionProviderImpl#doQuery"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 口径：[[calibers/exception_resolution_valid_enable_y]]
- 规则：[[rules/exception_provider_exception_fallback]]
---END FILE---

---FILE: rules/exception_provider_exception_fallback.md ---
---
type: rule
title: 异常解析对外查询-异常兜底
page_key: rules/exception_provider_exception_fallback
domain: funding
status: draft
aliases:
  - 对外接口异常兜底
  - 返回空列表不抛异常
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundingPartyExceptionResolutionProviderImpl#queryByFundingPartyId"
contract_version: "0.1"
---

# 异常解析对外查询-异常兜底

## 业务定位

对外查询入口 `queryByFundingPartyId` 对**参数校验失败**与**系统异常**一视同仁：记日志后返回空列表，绝不向 Dubbo 上游抛异常。这是可用性优先的取舍——异常解析是辅助性能力，宁可返回「没找到」也不能让主流程因它失败。代价是上游无法区分「无匹配配置」与「查询出错」，需要靠日志排查。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。

```ground:rule
rule: 异常解析对外查询-异常兜底
content: "参数校验失败或系统异常均记日志并返回空列表，不向 Dubbo 上游抛异常"
impact: "保证对外接口稳定"
field_targets: []
evidence: "code:FundingPartyExceptionResolutionProviderImpl#queryByFundingPartyId"
```

## 关联

- 表：[[tables/funding_exception_resolution]]
- 规则：[[rules/exception_provider_keyword_contains]]
---END FILE---

---FILE: rules/rule_import_product_code_direct_match.md ---
---
type: rule
title: 资方规则导入-产品校验直接比对productCode
page_key: rules/rule_import_product_code_direct_match
domain: funding
status: draft
aliases:
  - 规则导入产品校验
  - 无名称转换的产品校验
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#collectFundRuleProductCodeErrors"
contract_version: "0.1"
---

# 资方规则导入-产品校验直接比对productCode

## 业务定位

资方规则导入时，`productCode` 直接与 `ProductCodeEnum` 枚举比对，**没有名称转换**。这与异常解析导入的口径不同——后者会先用 `platformProduct.listPlatformProduct` 把产品名称映射为 code，因此异常解析模板的「产品code」列实际可以填产品名称，而**规则导入模板的产品列必须填产品 code**。两者的差异详见 [[concepts/product_code]]。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。两条导入链路口径不一致，是本主题下最容易导致运营填错的边界。

```ground:rule
rule: 资方规则导入-产品校验直接比对productCode
content: "规则导入 productCode 直接与 ProductCodeEnum 枚举比对（无名称转换），与异常解析导入的名称映射口径不同"
impact: "规则导入模板产品列必须填产品code"
field_targets:
  - funding_rule_info.product_code
evidence: "code:FundRuleInfoApplication#collectFundRuleProductCodeErrors"
```

## 关联

- 概念：[[concepts/product_code]]
- 表：[[tables/funding_rule_info]]
---END FILE---

---FILE: rules/rule_detail_save_idempotent.md ---
---
type: rule
title: 资方规则详情保存-幂等更新
page_key: rules/rule_detail_save_idempotent
domain: funding
status: draft
aliases:
  - 明细幂等落库
  - ruleKey 幂等更新
oid: 1
scope:
  databases:
    - funding_rule
sources:
  - "code:FundRuleInfoApplication#saveRuleInfo"
contract_version: "0.1"
---

# 资方规则详情保存-幂等更新

## 业务定位

明细保存以 `ruleInfoId + ruleKey + enable='Y'` 为幂等键：命中即更新，未命中即新增。**关键细节**：不在 `ruleMap` 中出现的 `frontKey` 直接跳过，不中断保存——即「本次没提交的字段」保持原样，而不是被置空或删除。这让前端可以只提交变更字段。

## 需求背景

无语义分析挂载的需求文档锚点。

## 版本演进

无 `action=uncovered` 的主张。与主表版本累加（[[rules/rule_info_update_version_increment]]）配合：每次保存主表 version+1，明细带新版本写入。

```ground:rule
rule: 资方规则详情保存-幂等更新
content: "按 ruleInfoId + ruleKey + enable='Y' 命中则更新，否则新增；ruleMap 中不存在的 frontKey 跳过（不中断）"
impact: "明细按 key 幂等落库"
field_targets:
  - funding_rule_detail.rule_key
  - funding_rule_detail.rule_value
  - funding_rule_detail.enable
evidence: "code:FundRuleInfoApplication#saveRuleInfo"
```

## 关联

- 表：[[tables/funding_rule_detail]]
- 概念：[[concepts/rule_key]]
- 口径：[[calibers/funding_rule_detail_valid_enable_y]]
---END FILE---

---REVIEW: table | 全部 table 页的 scope.databases ---
语义分析中所有证据均以表名给出（db:funding_exception_resolution、db:funding_rule_detail 等），**未出现物理库名/模式名**。本批次所有页面的 `scope.databases: [funding_rule]` 为占位值，需人工确认真实物理库名后统一替换。
---END REVIEW---

---REVIEW: rule | 异常解析-导出资金方名称映射固定ACFLOW ---
`mapFundingPartyCode(ProductCodeEnum.ACFLOW)` 在导出时被硬编码为单一产品，而 `product_code` 实测存在 `RVSFACTOR_PC`，二者组合会导致非 ACFLOW 记录的资金方名称映射为空。此处仅按代码证据记录现状，**是否为已知缺陷、是否已有修正计划，分析中无证据**，需业务确认预期行为（是按记录所属产品动态映射，还是明确只支持 ACFLOW 导出）。
---END REVIEW---