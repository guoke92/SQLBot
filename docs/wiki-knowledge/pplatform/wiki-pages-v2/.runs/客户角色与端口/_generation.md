---FILE: tables/cust_role_info.md ---
---
type: table
title: 客户角色表（cust_role_info）
page_key: cust_role_info
domain: 客户角色与端口
status: draft
aliases:
  - cust_role_info
  - 客户角色
  - 企业角色绑定
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java
  - code_path:CustCompanyIfoEnchanceService.java
  - code_path:RoleFacade.java
  - db_dist:cust_role_info
contract_version: "0.1"
---

cust_role_info 是「客户角色与端口」主题的事实表：一条记录表示某个客户企业在某产品下持有的一个企业角色（端口）。角色编码 role_type 与平台产品端口表 [[platform_product_cust_role]] 的 company_type_code 共用值域，术语解释见 [[company_role]] 与 [[port]]。

## 需求背景

客户开通产品后需要被赋予相应的企业角色，平台据此决定其可见菜单与可执行业务。角色以“全量覆盖”的方式维护（见 [[role_full_overwrite]]）：先按企业 code 删除旧角色，再按 roleType 数组逐个插入，新增记录状态为 ADD，需要后续激活。角色的可用性由 status 生命周期（见 [[cust_role_status_machine]]）与 enable 逻辑标识共同决定，常用口径见 [[valid_cust_role]]、[[effect_cust_role]]。

## 字段说明

- id：表主键。
- code：角色编码，新增时通过 DataModelUtils.uuid() 生成，每次覆盖都会重新生成。
- role_type：企业角色编码，如 CORE、SUPPLIER、FINANCE；写入前会去除 JSON 引号。
- status：角色状态，取值与流转见 [[cust_role_status]] 与 [[cust_role_status_machine]]。
- ref_cust_company_info：关联客户企业编码，指向 cust_company_info.code，用于反查企业信息（relation_audit 判定 confirm）。
- ref_cust_auth_application：应用客户角色（关联客户开通产品），当前代码未直接使用，未发现实现级关联（reject，待确认）。
- platform_cust_id：关联平台企业 ID。
- db_tenant_code：数据租户标识，全量覆盖写入时取自关联企业。
- enable：逻辑启用标识（Y/N），查询时常用 enable='Y' 过滤。

与其他表的关联：ref_cust_company_info 与 cust_person_info.ref_cust_company_info 为共享键（同为企业的 code 值，derived，非直接外键 JOIN）；与 cust_change_record 的关联无直接查询证据（reject）。

## 版本演进

- v0（draft）：基于 db 字段语义与代码路径首次成页；列类型、role_type 带引号历史值均待后续核实与清洗。

```ground:table
name: cust_role_info
comment: 客户角色表，记录客户企业在产品下的企业角色（端口）绑定
fields:
  - name: id
    type: unknown
    desc: 表主键
    dict: null
  - name: code
    type: unknown
    desc: 编码，新增角色时通过 DataModelUtils.uuid() 生成
    dict: null
  - name: role_type
    type: unknown
    desc: 企业角色编码，如 CORE、SUPPLIER、FINANCE 等；写入时去除 JSON 引号
    dict: platform_product_cust_role.company_type_code
  - name: status
    type: unknown
    desc: 角色状态：ADD-未激活/新增，EFFECT-已激活/生效，FREEZE-冻结，WRITEOFF-注销
    dict: CustRoleStatusConstant
  - name: ref_cust_company_info
    type: unknown
    desc: 关联客户企业编码，指向 cust_company_info.code
    dict: null
  - name: ref_cust_auth_application
    type: unknown
    desc: 应用客户角色（关联客户开通产品），当前代码未直接使用
    dict: null
  - name: platform_cust_id
    type: unknown
    desc: 关联平台企业ID
    dict: null
  - name: db_tenant_code
    type: unknown
    desc: 数据租户标识
    dict: null
  - name: enable
    type: unknown
    desc: 逻辑启用标识（Y/N），查询时常用 enable=Y 过滤
    dict: Y/N
```

---REVIEW: table | cust_role_info 列类型与 role_type 脏数据待核实---
- 语义分析仅提供字段含义（db/code 证据），未提供建表 DDL，故上方 fields 的 type 一律记为 unknown，待补充建表语句后回填。
- enum_audit 显示 role_type 存在字面量带引号的历史值（"CORE" 1 条、"SUPPLIER" 1 条），代码 addRoleInfo 中的 role.replace("\"","") 可去引号；需确认清洗范围与责任方。
- ref_cust_auth_application 的关联被 relation_audit 判为 reject（无 .eq / mapper JOIN 证据），字段是否废弃未确认。
---END REVIEW---
---END FILE---

---FILE: tables/platform_product_cust_role.md ---
---
type: table
title: 平台产品客户角色表（platform_product_cust_role）
page_key: platform_product_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - platform_product_cust_role
  - 产品端口
  - 企业角色端口
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - db_dist:platform_product_cust_role
  - code_path:LocalTypeMenuService.java
contract_version: "0.1"
---

platform_product_cust_role 定义某个产品下支持哪些企业角色，即业务口语中的“端口”。company_type_code 与 [[cust_role_info]].role_type 共用编码（CORE、SUPPLIER、FINANCE 等），二者为逻辑关联（derived，无外键约束）。术语见 [[port]]、[[company_role]]。

## 需求背景

产品开通时，产品下可支持的企业角色决定了客户能选择的端口集合；菜单配置需要按端口逐个勾选，形成 tenant_product_menu 配置（见 [[menu_port_filter]]）。因此本表是「客户角色」与「菜单可见性」之间的桥接表，也是 [[valid_product_cust_role]] 口径的事实来源。

## 版本演进

- v0（draft）：基于 db 字段语义与 LocalTypeMenuService 代码路径首次成页。

```ground:table
name: platform_product_cust_role
comment: 平台产品下支持的企业角色（端口）配置
fields:
  - name: company_type_code
    type: unknown
    desc: 企业角色编码，产品下支持的企业角色（端口）
    dict: cust_role_info.role_type
  - name: company_type_name
    type: unknown
    desc: 企业角色名称，如核心企业、供应商等
    dict: null
  - name: product_code
    type: unknown
    desc: 产品编码，如 ACCOUNT_PRODUCT、ACFLOW、AMS 等
    dict: null
  - name: enable
    type: unknown
    desc: 逻辑启用标识（Y/N）
    dict: Y/N
```
---END FILE---

---FILE: tables/cust_project_rel.md ---
---
type: table
title: 客户项目关系表（cust_project_rel）
page_key: cust_project_rel
domain: 客户角色与端口
status: draft
aliases:
  - cust_project_rel
  - 客户项目关系
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:addRoleInfo
contract_version: "0.1"
---

cust_project_rel 记录客户与项目的关系，其中 company_type 承载该客户在项目中的企业角色。该字段与 [[cust_role_info]].role_type 为业务同步关系（derived，无外键约束）。

## 需求背景

为客户添加角色后，需要把该企业所有项目关系记录的 companyType 统一更新为第一个角色值，使项目维度也能识别客户身份，规则见 [[project_rel_role_sync]]。

## 版本演进

- v0（draft）：本页仅依据 addRoleInfo 代码路径成页，字段清单不完整，待补 DDL 后扩充。

```ground:table
name: cust_project_rel
comment: 客户项目关系表（仅 company_type 字段有语义证据）
fields:
  - name: company_type
    type: unknown
    desc: 客户在项目中的企业角色，添加角色后同步为第一个角色值
    dict: cust_role_info.role_type
```
---END FILE---

---FILE: enums/cust_role_status.md ---
---
type: enum
title: 客户角色状态（cust_role_info.status）
page_key: cust_role_status
domain: 客户角色与端口
status: draft
aliases:
  - 角色状态
  - CustRoleStatusConstant
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleStatusConstant.java
  - code_path:CustStatusEnum.java
  - db_dist:cust_role_info.status
contract_version: "0.1"
---

cust_role_info.status 描述客户角色在生命周期中的位置，取值由 CustRoleStatusConstant 定义，与库内分布一致。状态之间的流转见 [[cust_role_status_machine]]，按状态切分的查询口径见 [[effect_cust_role]]、[[freeze_cust_role]]、[[writeoff_cust_role]]。

## 需求背景

角色新增时默认进入 ADD（未激活），业务激活后为 EFFECT；EFFECT 可被冻结为 FREEZE，解冻回到 EFFECT，注销则进入 WRITEOFF。批量更新企业角色状态时会跳过已注销记录，见 [[role_status_freeze_logout]]。

## 版本演进

- v0（draft）：4 个取值经 code_enum + db_dist 双向确认；CustStatusEnum 中的 FAILURE、CHANGE 未用于本字段（见 REVIEW）。

```ground:enum
name: 客户角色状态
field: cust_role_info.status
java_name: CustRoleStatusConstant
stored_as: same
values:
  - value: ADD
    java_name: ADD
    stored_as: same
    label: 未激活
    verdict: confirm
    evidence: "CustRoleStatusConstant.java + db_dist: ADD 34867"
  - value: EFFECT
    java_name: EFFECT
    stored_as: same
    label: 已激活
    verdict: confirm
    evidence: "CustRoleStatusConstant.java + db_dist: EFFECT 19791"
  - value: FREEZE
    java_name: FREEZE
    stored_as: same
    label: 冻结
    verdict: confirm
    evidence: "CustRoleStatusConstant.java + db_dist: FREEZE 11"
  - value: WRITEOFF
    java_name: WRITEOFF
    stored_as: same
    label: 注销
    verdict: confirm
    evidence: "CustRoleStatusConstant.java + db_dist: WRITEOFF 44"
```

---REVIEW: enum | CustStatusEnum 中 FAILURE/CHANGE 未用于 cust_role_info.status---
enum_audit 将 FAILURE（失效）与 CHANGE（变更）判为 reject：二者在 CustStatusEnum.java 中定义，但 cust_role_info.status 的 db_dist 中无此值，实际用于 cust_company_info.cust_status。若后续出现同名状态混用，需按字段区分而非按常量类区分。
---END REVIEW---
---END FILE---

---FILE: processes/cust_role_status_machine.md ---
---
type: process
title: 客户角色状态机（cust_role_info.status）
page_key: cust_role_status_machine
domain: 客户角色与端口
status: draft
aliases:
  - 角色状态流转
  - 角色冻结解冻注销
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:freeze
  - code_path:CustRoleApplication.java:unFreeze
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
  - code_path:CustCompanyIfoEnchanceService.java:setCustCompany
contract_version: "0.1"
---

客户角色状态机描述 ADD / EFFECT / FREEZE / WRITEOFF 之间的迁移路径，状态取值见 [[cust_role_status]]，载体表见 [[cust_role_info]]。

## 需求背景

角色创建（addRoleInfo）后落在 ADD，等待业务激活；冻结、解冻、注销分别把状态置为 FREEZE、EFFECT、WRITEOFF。批量按企业更新状态时跳过已 WRITEOFF 的记录，避免“复活”已注销角色（见 [[role_status_freeze_logout]]）。已安装状态的存量分布显示业务上绝大多数角色处于 ADD（34867）与 EFFECT（19791），FREEZE/WRITEOFF 为少数态。

## 版本演进

- v0（draft）：依据代码路径 + db_dist 首次成页；updateStatusByCustCompany 的目标状态为“传入状态”，属于参数化迁移，未在锚点块中枚举具体目标值。

```ground:process
name: 客户角色状态机
field: cust_role_info.status
states:
  - value: ADD
    label: 未激活
    source: code_enum
  - value: EFFECT
    label: 已激活
    source: code_enum
  - value: FREEZE
    label: 冻结
    source: db_dist
  - value: WRITEOFF
    label: 注销
    source: db_dist
transitions:
  - from: "*"
    event: freeze
    to: FREEZE
    evidence: "code_path:CustRoleApplication.java:freeze -> operatorCustRoleStatus(role, CustRoleStatusConstant.FREEZE)"
  - from: FREEZE
    event: unFreeze
    to: EFFECT
    evidence: "code_path:CustRoleApplication.java:unFreeze -> operatorCustRoleStatus(role, CustRoleStatusConstant.EFFECT)"
  - from: "*"
    event: logout
    to: WRITEOFF
    evidence: "code_path:CustRoleApplication.java:logout -> operatorCustRoleStatus(role, CustRoleStatusConstant.WRITEOFF)"
  - from: "*"
    event: updateStatusByCustCompany
    to: 传入状态
    evidence: "code_path:CustRoleApplication.java:updateStatusByCustCompany，跳过已有 WRITEOFF 的记录"
  - from: 无
    event: addRoleInfo
    to: ADD
    evidence: "code_path:CustCompanyIfoEnchanceService.java:setCustCompany 中 custRoleInfoDO.setStatus(CustStatusEnum.ADD.getDictKey())"
```
---END FILE---

---FILE: calibers/valid_cust_role.md ---
---
type: caliber
title: 有效客户角色
page_key: valid_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - enable=Y 客户角色
  - 有效角色
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:getCompanyTypeByCompanyCode
contract_version: "0.1"
---

口径「有效客户角色」用于查询当前企业已存在的企业角色，事实表见 [[cust_role_info]]，与状态维度口径 [[effect_cust_role]] 可组合使用。

## 需求背景

查询企业的角色集合时以 enable='Y' 作为逻辑启用过滤，避免返回已逻辑删除的记录；该口径被 getCompanyTypeByCompanyCode 直接使用。

## 版本演进

- v0（draft）：依据代码路径导出。

```ground:caliber
name: 有效客户角色
predicate: "cust_role_info.enable = 'Y'"
scope: 查询当前企业已存在的企业角色
evidence: "code_path:CustRoleApplication.java:getCompanyTypeByCompanyCode 使用 enable=Y"
```
---END FILE---

---FILE: calibers/effect_cust_role.md ---
---
type: caliber
title: 已激活客户角色
page_key: effect_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - EFFECT 客户角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:unFreeze
  - db_dist:cust_role_info.status
contract_version: "0.1"
---

口径「已激活客户角色」筛选状态为 EFFECT 的 [[cust_role_info]] 记录，代表当前生效的客户企业角色。

## 需求背景

解冻操作把角色状态恢复为 EFFECT，说明 EFFECT 即业务认可的“生效”态，状态机见 [[cust_role_status_machine]]。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 19791 条。

```ground:caliber
name: 已激活客户角色
predicate: "cust_role_info.status = 'EFFECT'"
scope: 客户角色状态为已激活
evidence: "code_path:CustRoleApplication.java:unFreeze；db_dist: EFFECT 19791"
```
---END FILE---

---FILE: calibers/freeze_cust_role.md ---
---
type: caliber
title: 已冻结客户角色
page_key: freeze_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - FREEZE 客户角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:freeze
  - db_dist:cust_role_info.status
contract_version: "0.1"
---

口径「已冻结客户角色」筛选状态为 FREEZE 的 [[cust_role_info]] 记录，表示因业务原因被暂停使用但仍保留的角色。

## 需求背景

冻结由 freeze 操作触发，可通过 [[cust_role_status_machine]] 中的 unFreeze 迁回 EFFECT。库内为极少数态（11 条）。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认。

```ground:caliber
name: 已冻结客户角色
predicate: "cust_role_info.status = 'FREEZE'"
scope: 客户角色状态为冻结
evidence: "code_path:CustRoleApplication.java:freeze；db_dist: FREEZE 11"
```
---END FILE---

---FILE: calibers/writeoff_cust_role.md ---
---
type: caliber
title: 已注销客户角色
page_key: writeoff_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - WRITEOFF 客户角色
  - 注销角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
  - db_dist:cust_role_info.status
contract_version: "0.1"
---

口径「已注销客户角色」筛选状态为 WRITEOFF 的 [[cust_role_info]] 记录。注销是不可逆的终态：批量更新状态时会显式跳过这些记录（见 [[role_status_freeze_logout]]）。

## 需求背景

logout 把角色置为 WRITEOFF；updateStatusByCustCompany 在批量更新时跳过已注销记录，因此本口径也用于识别“不应再被业务动作影响”的角色。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 44 条。

```ground:caliber
name: 已注销客户角色
predicate: "cust_role_info.status = 'WRITEOFF'"
scope: 客户角色状态为注销
evidence: "code_path:CustRoleApplication.java:logout；db_dist: WRITEOFF 44"
```
---END FILE---

---FILE: calibers/valid_product_cust_role.md ---
---
type: caliber
title: 平台产品有效端口
page_key: valid_product_cust_role
domain: 客户角色与端口
status: draft
aliases:
  - enable=Y 端口
  - 产品有效企业角色
oid: 1
scope:
  databases:
    - db
    - db_dist
sources:
  - code_path:LocalTypeMenuService.java:listTenantProductMenuConfig
  - db_dist:platform_product_cust_role
contract_version: "0.1"
---

口径「平台产品有效端口」筛选 [[platform_product_cust_role]] 中 enable='Y' 的记录，得到某产品下当前生效的企业角色（端口）列表。

## 需求背景

菜单配置服务先按产品 code 取出有效端口，再按租户与产品查询已配置菜单并标记选中状态，见 [[menu_port_filter]]。术语“端口”的释义见 [[port]]。

## 版本演进

- v0（draft）：代码与 db_dist 双源确认，当前库内 enable=Y 共 53 条。

```ground:caliber
name: 平台产品有效端口
predicate: "platform_product_cust_role.enable = 'Y'"
scope: 产品下支持的企业角色（端口）列表
evidence: "code_path:LocalTypeMenuService.java:listTenantProductMenuConfig；db_dist: enable Y 53"
```
---END FILE---

---FILE: concepts/company_role.md ---
---
type: concept
title: 企业角色
page_key: company_role
domain: 客户角色与端口
status: draft
aliases:
  - 客户角色
  - companyType
  - roleType
  - company_type_code
  - role_type
oid: 1
scope:
  databases:
    - db
sources:
  - db_dist:cust_role_info.role_type
  - db_dist:platform_product_cust_role.company_type_code
contract_version: "0.1"
maps_to:
  - cust_role_info.role_type
  - platform_product_cust_role.company_type_code
also_confused_with:
  - cust_company_info.cust_company_type
  - cust_person_info.company_type
adjudication: boundary
boundary: "cust_role_info.role_type 是客户与产品的角色关联，单个角色值；cust_company_info.cust_company_type 是企业主数据上的角色列表（JSON 数组）；cust_person_info.company_type 是联系人所属角色。"
---

“企业角色”是本主题的核心术语，在客户角色语境中对应 [[cust_role_info]].role_type，在产品端口配置语境中对应 [[platform_product_cust_role]].company_type_code，两者共用编码值域（CORE、SUPPLIER、FINANCE 等）。

## 需求背景

同义词链（客户角色 / companyType / roleType / company_type_code / role_type）在代码与库表中混用，需要通过边界判定区分三处易混字段。角色在全量覆盖写入时以 JSON 数组形式传入并按单个值落库，见 [[role_full_overwrite]]；下游同步时会从 roleClass 中解析出 companyType，见 [[role_downstream_sync]]。

## 版本演进

- v0（draft）：依据 term_bridges 与 relation_audit（platform_product_cust_role.company_type_code ↔ cust_role_info.role_type 为 derived 逻辑关联）首次成页。
---END FILE---

---FILE: concepts/port.md ---
---
type: concept
title: 端口
page_key: port
domain: 客户角色与端口
status: draft
aliases:
  - 产品端口
  - 企业角色端口
oid: 1
scope:
  databases:
    - db
sources:
  - db_dist:platform_product_cust_role
  - code_path:LocalTypeMenuService.java
contract_version: "0.1"
maps_to:
  - platform_product_cust_role.company_type_code
also_confused_with:
  - 菜单端口
  - 系统接入端口
adjudication: synonym
boundary: "在客户角色与菜单配置语境中，'端口'指 platform_product_cust_role 表中定义的产品下可支持的企业角色（company_type_code），每个端口对应一个企业角色。"
---

“端口”在客户角色与菜单配置语境下是“平台产品支持的企业角色”的口语表述，落点见 [[platform_product_cust_role]].company_type_code，与 [[company_role]] 属于同义表述的不同视角：企业角色强调客户侧身份，端口强调产品侧可选项。

## 需求背景

菜单配置以端口为最小勾选单位：先取产品下的有效端口（口径见 [[valid_product_cust_role]]），再匹配租户已配置菜单，形成 tenant_product_menu 记录，规则见 [[menu_port_filter]]。因此“端口”易与菜单端口、系统接入端口混淆，需按表定锚。

## 版本演进

- v0（draft）：依据 term_bridges 与菜单配置代码路径首次成页。
---END FILE---

---FILE: rules/role_full_overwrite.md ---
---
type: rule
title: 角色全量覆盖规则
page_key: role_full_overwrite
domain: 客户角色与端口
status: draft
aliases:
  - addRoleInfo 全量覆盖
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:addRoleInfo
contract_version: "0.1"
---

该规则约束 [[cust_role_info]] 的写入方式：不是增量合并，而是按企业维度先清后建。

## 需求背景

客户角色以“全量覆盖”方式维护，保证企业角色集合与上游传入的 roleType 数组完全一致；由于每条记录 code 重生成、状态回落 ADD，覆盖后需要重新激活。与项目关系的联动见 [[project_rel_role_sync]]。

## 版本演进

- v0（draft）：依据 addRoleInfo 代码路径成页。

```ground:rule
name: 角色全量覆盖规则
content: "客户角色通过 addRoleInfo 全量覆盖：先按企业 code 删除旧角色，再按 roleType JSON 数组逐个插入新角色，默认状态为 ADD；每个角色 code 重新生成，roleType 去除引号，dbTenantCode 取自关联企业。"
impact: 影响 cust_role_info 表记录增删和 role_type 值
field_targets:
  - cust_role_info.role_type
  - cust_role_info.status
  - cust_role_info.ref_cust_company_info
evidence: "code_path:CustRoleApplication.java:addRoleInfo"
```
---END FILE---

---FILE: rules/role_status_freeze_logout.md ---
---
type: rule
title: 角色状态冻结/解冻/注销规则
page_key: role_status_freeze_logout
domain: 客户角色与端口
status: draft
aliases:
  - 角色状态变更规则
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:freeze
  - code_path:CustRoleApplication.java:unFreeze
  - code_path:CustRoleApplication.java:logout
  - code_path:CustRoleApplication.java:updateStatusByCustCompany
contract_version: "0.1"
---

该规则约束 [[cust_role_info]].status 的变更取值与边界条件，状态机全貌见 [[cust_role_status_machine]]。

## 需求背景

冻结、解冻、注销分别把状态置为 FREEZE、EFFECT、WRITEOFF；批量按企业更新状态时跳过已 WRITEOFF 的记录，保证注销终态不被批量动作覆盖。按状态切分的口径见 [[freeze_cust_role]]、[[effect_cust_role]]、[[writeoff_cust_role]]。

## 版本演进

- v0（draft）：依据 4 个代码路径成页。

```ground:rule
name: 角色状态冻结/解冻/注销规则
content: "冻结置 status=FREEZE，解冻置 status=EFFECT，注销置 status=WRITEOFF；批量更新企业角色状态时跳过已注销（WRITEOFF）的记录。"
impact: 影响 cust_role_info.status
field_targets:
  - cust_role_info.status
evidence: "code_path:CustRoleApplication.java:freeze, unFreeze, logout, updateStatusByCustCompany"
```
---END FILE---

---FILE: rules/project_rel_role_sync.md ---
---
type: rule
title: 项目关联角色同步规则
page_key: project_rel_role_sync
domain: 客户角色与端口
status: draft
aliases:
  - 项目角色同步
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:CustRoleApplication.java:addRoleInfo
contract_version: "0.1"
---

该规则把 [[cust_role_info]] 的变更传导到 [[cust_project_rel]]，使项目维度也能识别客户身份。

## 需求背景

添加客户角色后，企业所有项目关系记录的 companyType 被统一更新为“第一个角色值”，即项目侧只保留单一角色快照，与客户角色侧的多值集合并不等价。该同步无外键约束，属业务派生关系（derived）。

## 版本演进

- v0（draft）：依据 addRoleInfo 代码路径成页。

```ground:rule
name: 项目关联角色同步规则
content: "添加客户角色后，将该企业所有 cust_project_rel 记录的 companyType 更新为第一个角色值。"
impact: 影响 cust_project_rel.company_type
field_targets:
  - cust_project_rel.company_type
evidence: "code_path:CustRoleApplication.java:addRoleInfo"
```
---END FILE---

---FILE: rules/role_downstream_sync.md ---
---
type: rule
title: 角色同步下游规则
page_key: role_downstream_sync
domain: 客户角色与端口
status: draft
aliases:
  - roleClass 解析规则
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:RoleFacade.java:generateRoleClass
  - code_path:ClientCustRoleSyncService.java:setInvokeArg
contract_version: "0.1"
---

该规则定义客户角色同步到下游时角色标识的编码/解析约定，涉及 [[company_role]] 术语在跨系统报文中的表达。

## 需求背景

SysRole 的 roleClass 按 "custType_custId" 格式生成，同步下游时再解析出 companyType 与 companyId，因此 roleClass 是客户角色信息在下游侧的复合键载体（影响角色事件同步 PlatClientRoleDto）。

## 版本演进

- v0（draft）：依据 RoleFacade 与 ClientCustRoleSyncService 代码路径成页；下游侧落库表未在证据范围内。

```ground:rule
name: 角色同步下游规则
content: "SysRole 的 roleClass 按 \"custType_custId\" 格式生成，同步下游时解析出 companyType 和 companyId。"
impact: 影响角色事件同步（PlatClientRoleDto）
field_targets:
  - SysRoleDO.roleClass
evidence: "code_path:RoleFacade.java:generateRoleClass, ClientCustRoleSyncService.java:setInvokeArg"
```
---END FILE---

---FILE: rules/menu_port_filter.md ---
---
type: rule
title: 菜单端口筛选规则
page_key: menu_port_filter
domain: 客户角色与端口
status: draft
aliases:
  - 端口菜单筛选
oid: 1
scope:
  databases:
    - db
sources:
  - code_path:LocalTypeMenuService.java:listTenantProductMenuConfig
  - code_path:LocalTypeMenuService.java:listProductCustMenu
contract_version: "0.1"
---

该规则描述菜单配置页上“端口（企业角色）× 菜单”的筛选与选中逻辑，连接 [[platform_product_cust_role]] 与 tenant_product_menu。

## 需求背景

根据产品 code 查询 platform_product_cust_role 获取所有端口（企业角色），再按租户和产品查询已配置菜单，标记选中状态。端口取值来源口径见 [[valid_product_cust_role]]，术语见 [[port]]。

## 版本演进

- v0（draft）：依据 LocalTypeMenuService 两个方法成页；tenant_product_menu 表结构未在证据范围内。

```ground:rule
name: 菜单端口筛选规则
content: "根据产品 code 查询 platform_product_cust_role 获取所有端口（企业角色），再按租户和产品查询已配置菜单，标记选中状态。"
impact: 影响 tenant_product_menu 配置
field_targets:
  - platform_product_cust_role.company_type_code
  - tenant_product_menu.company_type
evidence: "code_path:LocalTypeMenuService.java:listTenantProductMenuConfig, listProductCustMenu"
```
---END FILE---