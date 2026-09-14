---FILE: tables/platform_product.md ---
---
type: table
title: 平台产品定义表
page_key: platform_product
domain: 平台产品配置
status: draft
aliases: [平台产品表, PlatformProductDO, platform_product]
oid: 1
scope:
  databases: [platform]
sources:
  - db:platform_product
  - code:PlatformProductApplication.java
  - code:PlatformProductDomainService.java
  - code:PlatformProductTypeEnum.java
  - code:ProductStatusEnum.java
contract_version: "0.1"
---

平台产品定义表 `platform_product` 是平台侧产品目录的主数据表，承载产品编码、分类、生效状态、增信类型、端口与角色组合等多类配置项，被租户产品（[[tenant_product]]）、客户产品（[[cust_auth_application]]）与配置映射（[[cust_config_mapping]]）分别以 `platform_product_code` / `product_code` / `outer_channel` 间接引用。跨表引用、事件路由与列表白名单过滤统一以 [[platform_product_code]] 为键。

## 需求背景

需求文档 BR-001 要求保存或更新 PlatformProductDO 前调用 `checkBeforeSave` 校验产品基本信息、code 唯一性与产品类型枚举，失败抛 BaseException；实现侧由 Controller / Application / DomainService 三层同名方法承接，落库前拦截，见 [[product_code_name_unique]]。产品类型同时决定 [[general_product]] 与 [[interworking_product]] 两条口径的扩展点走向。

## 版本演进

- 代码枚举 `PlatformProductTypeEnum` 中另有 `ALL='2'`，仅作查询聚合哨兵值参与比较，DB 无该落库值，不作为存储值（enum_audit verdict=reject）。
- `product_status='0'`（待生效）在 DB 分布中未出现，但为 `effective()` 之前的初始态，保留在 [[platform_product_status]] 状态机内。
- 产品扩展配置自 Nacos 读取（[[product_ext_config_from_nacos]]），与 `cust_config_mapping` 的落库配置分属两套来源。

```ground:table
table: platform_product
fields:
  - name: product_code
    type: unknown
    desc: "平台产品编码（业务唯一键，用于跨表引用、事件路由、列表白名单过滤）"
    dict: ""
  - name: product_type
    type: unknown
    desc: "产品分类：GENERAL=通用产品，INTERWORKING=互通产品"
    dict: "GENERAL=通用产品;INTERWORKING=互通产品"
  - name: product_status
    type: unknown
    desc: "产品生效状态：'1'=已生效，'0'=待生效"
    dict: "1=已生效;0=待生效"
  - name: cust_role_combine
    type: unknown
    desc: "平台产品允许的企业角色组合（文本解析为 Set<Set<String>>，反欺诈校验用）"
    dict: ""
  - name: multiple_cust_role_flag
    type: unknown
    desc: "是否支持多企业角色(Y/N)，为 Y 时进入产品需校验企业角色"
    dict: "Y=支持;N=不支持"
  - name: multiple_project_flag
    type: unknown
    desc: "是否有多项目配置(Y/N)，为 Y 时进入产品需校验关联项目生效状态"
    dict: "Y=是;N=否"
  - name: platform_flag
    type: unknown
    desc: "是否平台标识(Y/N)"
    dict: "Y=是;N=否"
  - name: platform_code
    type: unknown
    desc: "平台编码，用于 listPlatformByProductCode 按平台聚合产品"
    dict: ""
  - name: product_cate
    type: unknown
    desc: "产品增信类型：STRONG/CREDIT/WEAKLY"
    dict: "STRONG=强增信;CREDIT=信用;WEAKLY=弱增信"
  - name: multiple_client_type
    type: unknown
    desc: "多端口过滤类型：default=按产品(BY_PRODUCT)，CompanyType=按企业角色(BY_COMPANY_TYPE)"
    dict: "default=按产品(BY_PRODUCT);CompanyType=按企业角色(BY_COMPANY_TYPE)"
  - name: wkfl_flag
    type: unknown
    desc: "产品是否启用工作流，映射 PlatformProductDTO.platformProductWfklConfigFlag"
    dict: ""
  - name: product_construction_status
    type: unknown
    desc: "产品建设情况，N=未建成时直接返回 GOTO_DETAIL 步骤"
    dict: "N=未建成"
  - name: basic_product
    type: unknown
    desc: "是否是产融底座"
    dict: ""
  - name: enable
    type: unknown
    desc: "逻辑启用标记 Y/N"
    dict: "Y=启用;N=停用"
  - name: logo_icon_url
    type: unknown
    desc: "产品 logo（附件 JSON，经 FileUtils 转真实 url）"
    dict: ""
```

关联：[[tenant_product]]、[[cust_auth_application]]、[[cust_config_mapping]]、[[platform_product_effective]]、[[platform_product_enabled]]、[[list_whitelist_filter]]、[[product_code_name_unique]]

---REVIEW: table | 平台产品定义表---
- 各字段物理类型与物理库名未在语义分析证据中出现，`type` 暂填 `unknown`，`scope.databases` 暂填 `platform`（待确认物理库名）。
- `platform_product_client.status` 在 DB 实测有值（Y:26），但代码枚举基线未声明且语义分析证据在此截断，取值域与含义未定。
---END REVIEW---

---END FILE---

---FILE: tables/cust_auth_application.md ---
---
type: table
title: 客户产品开通申请表
page_key: cust_auth_application
domain: 平台产品配置
status: draft
aliases: [客户产品表, 客户授权申请表, cust_auth_application]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductActiveConstant.java
  - code:CustProductDomainService.java
  - code:PlatFormProductProvierImpl.java
contract_version: "0.1"
---

客户产品开通申请表 `cust_auth_application` 记录「企业 × 产品」粒度的开通授权状态，是客户端展示与进入产品校验的事实表。它不直接存平台产品编码，而是通过 `ref_cust_auth_application_tenant_product` 关联租户产品（[[tenant_product]]），再由租户产品上溯到 [[platform_product]]。开通状态取值来自常量类 `CustProductActiveConstant`，写值点为 `setOpenStatus(...)`，而非枚举类。

## 需求背景

「我的产品 / 已开通产品列表 / 进入产品校验」三类场景全部以本表 `open_status` 为判活依据，对应三条口径 [[cust_product_opened]]、[[cust_product_opening]]、[[cust_product_not_opened]]，状态流转见 [[cust_product_open_status]]。需求文档把该状态写作 PENDING/ACTIVE/CANCEL 与实现不符，实现为 OPENED/OPENING/NOT_OPENED。

## 版本演进

- 常量类 `CustProductActiveConstant` 承载三个字面量，与 DB 落库值同域（enum_audit verdict=confirm ×3）。
- `NOT_OPENED` 同时是「查无授权记录」时的默认回退值，见 [[cust_product_not_opened]]。

```ground:table
table: cust_auth_application
fields:
  - name: open_status
    type: unknown
    desc: "客户产品开通状态：OPENED/OPENING/NOT_OPENED"
    dict: "OPENED=已开通;OPENING=开通中;NOT_OPENED=未开通"
  - name: ref_cust_auth_application_tenant_product
    type: unknown
    desc: "关联 tenant_product.code，客户产品与租户产品的关联键"
    dict: ""
```

关联：[[tenant_product]]、[[platform_product]]、[[cust_product_open_status]]、[[product_open_status]]

---END FILE---

---FILE: tables/tenant_product.md ---
---
type: table
title: 租户产品表
page_key: tenant_product
domain: 平台产品配置
status: draft
aliases: [租户产品, 上架产品, tenant_product]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java
  - code:ProductOpenStatusEnum.java
contract_version: "0.1"
---

(document_claim，未证实)

租户产品表 `tenant_product` 描述「租户 × 平台产品」的上架/开通关系，向上引用 [[platform_product]] 的 `product_code`，向下被 [[cust_auth_application]] 以 `ref_cust_auth_application_tenant_product` 引用。它是客户端可见产品集合的前置校验层：租户产品未上架时，客户产品无法开通。

## 需求背景

租户产品上架状态是「开通客户产品」的前置校验条件，口径为 [[tenant_product_on_shelf]]；开通动作与多级回调的分流规则见 [[multi_level_callback_pending]]，状态流转见 [[tenant_product_open_status]]。需求文档未展开 `TenantProductController.create` 落库状态与 `checkOnTheWay` 在途校验的具体实现，该段主张（2.1 前半段）为文档声明、尚未证实。

## 版本演进

- 需求文档主张 `tenant_product.open_status` 取 PENDING / ACTIVE / CANCEL（ProductOpenStatusEnum）；代码证据表明实现使用 `ProductOpenStatusEnum.Y` 与 `.P`，并与 `BooleanEnum.Y` 的 `'Y'` 同域比较，文档叙述被证伪，本页以代码为准。
- 需求文档 2.1 的「create → 落 PENDING → checkOnTheWay → 置 ACTIVE」链路在证据中未展开，仅作未证实主张记录。

```ground:table
table: tenant_product
fields:
  - name: platform_product_code
    type: unknown
    desc: "租户产品对应的平台产品编码，引用 platform_product.product_code"
    dict: ""
  - name: open_status
    type: unknown
    desc: "租户产品开通/上架状态：Y=已开通，P=处理中(多级回调)"
    dict: "Y=已开通/P=处理中(等待多级回调)"
```

关联：[[platform_product]]、[[cust_auth_application]]、[[tenant_product_open_status]]、[[tenant_product_on_shelf]]、[[multi_level_callback_pending]]

---REVIEW: table | 租户产品表---
`tenant_product.open_status` 的 `P` 值：`ProductOpenStatusEnum` 文件未展开，label「处理中(多级回调)」据注释与上下文推定，需核对 `getDictKey()` 实际返回值与 DB 取值分布后再固化。
---END REVIEW---

---END FILE---

---FILE: tables/cust_config_mapping.md ---
---
type: table
title: 客户配置映射表
page_key: cust_config_mapping
domain: 平台产品配置
status: draft
aliases: [配置映射, cust_config_mapping]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java
  - code:CustProductDomainService.java
contract_version: "0.1"
---

客户配置映射表 `cust_config_mapping` 承载「类型 + 内码 + 外码」形式的外部配置映射。在平台产品域中被复用的场景是把企业角色映射为平台产品编码：`getProductCompanyTypeConfig` 实际传参为 `(type='COMPANY_TYPE_MAPPING', innerCode=companyType, outerChannel=platformProductCode)`，即 `outer_channel` 存的是平台产品编码而非渠道。查询口径见 [[config_mapping_enabled]]，键名歧义见 [[config_mapping_filter_key]]。

## 需求背景

需求文档 BR-003 主张「平台产品扩展配置按 productCode+key+expectedValue 三元组查询 cust_config_mapping」。代码证据表明 `getProductExtConfig` / `getProductConfig` 实际读取 Nacos `app-list.yml` 的 extConfig / clientConfig（`nacosFacade.listProductApp()`），`cust_config_mapping` 仅服务于 `getConfig` / `listConfig` 的 `type+innerCode+outerChannel` 查询。该主张被证伪，本页以代码为准，扩展配置的真源见 [[product_ext_config_from_nacos]]。

## 版本演进

- 首次契约化即按「代码为准」记录 BR-003 的证伪结论；若后续需求文档修订，需同步本页与 [[product_ext_config_from_nacos]]。

```ground:table
table: cust_config_mapping
fields:
  - name: outer_channel
    type: unknown
    desc: "配置映射外部渠道，实现中被用作 platformProductCode 过滤键"
    dict: ""
```

关联：[[platform_product]]、[[config_mapping_enabled]]、[[config_mapping_filter_key]]、[[product_ext_config_from_nacos]]

---END FILE---

---FILE: processes/platform_product_status.md ---
---
type: process
title: 平台产品生效状态流转
page_key: platform_product_status
domain: 平台产品配置
status: draft
aliases: [平台产品生效状态, product_status 状态机]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#effective
  - code:PlatformProductDomainService.java#effective
  - code:PlatformProduct.java:100
  - code:ProductStatusEnum.java
contract_version: "0.1"
---

平台产品生效状态描述产品定义自身从「待生效」进入「已生效」的单向跃迁，落库字段为 [[platform_product]] 的 `product_status`。它与租户侧、客户侧的「开通状态」是三套不同语义，辨析见 [[product_open_status]]。

## 需求背景

产品只有生效后才进入客户端可选集合，判活口径为 [[platform_product_effective]]；上架到租户是另一道闸口，见 [[tenant_product_open_status]]。保存前的类型与唯一性校验见 [[product_code_name_unique]]。

## 版本演进

- `ProductStatusEnum` 提供 `TO_BE_EFFECTIVE='0'` 与 `EFFECTIVE='1'` 两个 dictKey；DB 分布仅见 `'1'`（20 行），`'0'` 为生效前初始态，未在样本数据中出现。

```ground:process
name: 平台产品生效状态
field: platform_product.product_status
states:
  - value: "0"
    label: 待生效
    source: code_enum
  - value: "1"
    label: 已生效
    source: db_dist
transitions:
  - from: "0"
    event: 人工提交生效 effective()
    to: "1"
    evidence: "code_path:PlatformProductApplication.java#effective -> PlatformProductDomainService.java#effective -> PlatformProduct.java:100"
```

关联：[[platform_product]]、[[platform_product_effective]]、[[product_open_status]]、[[product_code_name_unique]]

---END FILE---

---FILE: processes/cust_product_open_status.md ---
---
type: process
title: 客户产品开通状态流转
page_key: cust_product_open_status
domain: 平台产品配置
status: draft
aliases: [客户产品开通状态, open_status 状态机]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java#initProduct
  - code:CustProductDomainService.java#doActiveProduct
  - code:CustProductDomainService.java#listTenantProductWithOpenedCustProduct
  - code:PlatFormProductProvierImpl.java#queryProductStatus
contract_version: "0.1"
---

客户产品开通状态刻画「企业 × 产品」的开通生命周期，落库于 [[cust_auth_application]] 的 `open_status`，取值为字面量常量类 `CustProductActiveConstant` 定义的 NOT_OPENED / OPENING / OPENED。该状态是客户端「我的产品 / 已开通产品」列表与进入产品校验的判活依据。

## 需求背景

三条口径 [[cust_product_not_opened]]、[[cust_product_opening]]、[[cust_product_opened]] 分别服务初始化开通、列表展示与判活/回退三类场景。需求文档对状态字面量的叙述（PENDING/ACTIVE/CANCEL）与实现不符，见 [[product_open_status]] 的边界裁定。

## 版本演进

- 常量类（非 Enum）承载写值点：`setOpenStatus(CustProductActiveConstant.OPENED/OPENING/NOT_OPENED)`，enum_audit 三项均 verdict=confirm。
- 「查无授权记录」会从 OPENED 语义回退为 NOT_OPENED，属展示层补位而非失败态。

```ground:process
name: 客户产品开通状态
field: cust_auth_application.open_status
states:
  - value: NOT_OPENED
    label: 未开通
    source: code_const
  - value: OPENING
    label: 开通中
    source: code_const
  - value: OPENED
    label: 已开通
    source: code_const
transitions:
  - from: NOT_OPENED
    event: initProduct 初始化客户产品
    to: OPENING
    evidence: "code_path:CustProductDomainService.java#initProduct"
  - from: OPENING
    event: doActiveProduct 开通完成
    to: OPENED
    evidence: "code_path:CustProductDomainService.java#doActiveProduct"
  - from: OPENED
    event: 查无授权记录回退
    to: NOT_OPENED
    evidence: "code_path:CustProductDomainService.java#listTenantProductWithOpenedCustProduct;PlatFormProductProvierImpl.java#queryProductStatus"
```

关联：[[cust_auth_application]]、[[tenant_product]]、[[cust_product_opened]]、[[cust_product_opening]]、[[cust_product_not_opened]]、[[product_open_status]]

---END FILE---

---FILE: processes/tenant_product_open_status.md ---
---
type: process
title: 租户产品开通状态流转
page_key: tenant_product_open_status
domain: 平台产品配置
status: draft
aliases: [租户产品开通状态, 租户产品上架状态]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java#activeAndNotify
  - code:ProductOpenStatusEnum.java
  - reqdoc:2.1
contract_version: "0.1"
---

租户产品开通状态描述「租户 × 平台产品」的上架生命周期，落库于 [[tenant_product]] 的 `open_status`，实现取值为 Y（已开通/已上架）与 P（处理中，等待多级回调）。它是客户产品开通的前置闸口。

## 需求背景

只有租户产品已上架（[[tenant_product_on_shelf]]）才允许开通客户产品（[[cust_product_open_status]]）。多级产品（ACFLOW / ORDER）开通时置 P 等待回调，其余产品即时生效并推送同步事件，规则见 [[multi_level_callback_pending]]。需求文档 2.1「激活后发布 PlatProductEventType 事件并同步下游 client」在代码中获得确认（`migratoryPointService.push(RpcPoint.PRODUCT_SYNC, PlatProductEventType.EFFECTED, ...)`）。

## 版本演进

- 需求文档所称 PENDING/ACTIVE/CANCEL 在实现中不存在，实际为 `ProductOpenStatusEnum.P` / `.Y`，且与 `BooleanEnum.Y` 的 `'Y'` 同域比较（见 [[product_open_status]]）。
- 需求文档 2.1 前半段（`create` 落库状态、`checkOnTheWay` 在途校验）未被证据覆盖，属未证实主张，见 [[tenant_product]]。

```ground:process
name: 租户产品开通状态
field: tenant_product.open_status
states:
  - value: "Y"
    label: 已开通/已上架
    source: code_const
  - value: "P"
    label: 处理中(等待多级回调)
    source: code_const
transitions:
  - from: "P"
    event: "activeAndNotify：ACFLOW/ORDER 产品置 P 等待多级回调"
    to: "P"
    evidence: "code_path:TenantProductApplication.java#activeAndNotify"
  - from: "P"
    event: "activeAndNotify：其他产品 domainService.active 生效"
    to: "Y"
    evidence: "code_path:TenantProductApplication.java#activeAndNotify + reqdoc:2.1"
```

关联：[[tenant_product]]、[[cust_auth_application]]、[[tenant_product_on_shelf]]、[[multi_level_callback_pending]]、[[product_open_status]]

---END FILE---

---FILE: calibers/cust_product_opened.md ---
---
type: caliber
title: 客户产品已开通
page_key: cust_product_opened
domain: 平台产品配置
status: draft
aliases: [已开通产品, OPENED]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「客户产品已开通」是客户端已开通产品列表、进入产品校验与 `queryProductStatus` 默认判活的统一判据，等价于 [[cust_auth_application]] 中该「企业 × 产品」记录的 `open_status` 为 OPENED。

## 需求背景

进入产品、展示「我的产品」、判断产品可用性均以该口径为准；未命中时按 [[cust_product_not_opened]] 回退展示。状态写入路径见 [[cust_product_open_status]]。

## 版本演进

- 初版口径，与常量类写值点一致，无历史变更。

```ground:caliber
name: 客户产品已开通
predicate: "cust_auth_application.open_status = 'OPENED'"
scope: 客户端已开通产品列表/进入产品校验/queryProductStatus 默认判活
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[product_open_status]]

---END FILE---

---FILE: calibers/cust_product_opening.md ---
---
type: caliber
title: 客户产品开通中
page_key: cust_product_opening
domain: 平台产品配置
status: draft
aliases: [开通中产品, OPENING]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「客户产品开通中」用于「我的产品」列表与初始化开通场景，标识记录已建立但尚未完成开通，等价于 [[cust_auth_application]] 的 `open_status = 'OPENING'`。

## 需求背景

开通中产品展示在列表中但不视为可用，待 [[cust_product_open_status]] 流转到 OPENED 后由 [[cust_product_opened]] 口径接管。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 客户产品开通中
predicate: "cust_auth_application.open_status = 'OPENING'"
scope: 我的产品列表/初始化开通
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[cust_product_opened]]

---END FILE---

---FILE: calibers/cust_product_not_opened.md ---
---
type: caliber
title: 客户产品未开通
page_key: cust_product_not_opened
domain: 平台产品配置
status: draft
aliases: [未开通产品, NOT_OPENED]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「客户产品未开通」既表达记录初始态，也承担「查无授权记录」时的回退语义，等价于 [[cust_auth_application]] 的 `open_status = 'NOT_OPENED'`。

## 需求背景

租户产品未开通回退与展示均使用该口径；在 `listTenantProductWithOpenedCustProduct` 与 `queryProductStatus` 中作为默认值出现，见 [[cust_product_open_status]]。

## 版本演进

- 初版口径，同时作为默认回退值，无历史变更。

```ground:caliber
name: 客户产品未开通
predicate: "cust_auth_application.open_status = 'NOT_OPENED'"
scope: 租户产品未开通回退与展示
evidence: code
```

关联：[[cust_auth_application]]、[[cust_product_open_status]]、[[tenant_product_open_status]]

---END FILE---

---FILE: calibers/platform_product_effective.md ---
---
type: caliber
title: 平台产品已生效
page_key: platform_product_effective
domain: 平台产品配置
status: draft
aliases: [已生效产品, product_status=1]
oid: 1
scope:
  databases: [platform]
sources:
  - db
contract_version: "0.1"
---

「平台产品已生效」是平台产品列表与生效动作后的判活口径，等价于 [[platform_product]] 的 `product_status = '1'`。它与租户上架、客户开通分属三层语义，见 [[product_open_status]]。

## 需求背景

产品列表只展示已生效产品；生效动作的跃迁路径见 [[platform_product_status]]。启用标记是另一维度，见 [[platform_product_enabled]]。

## 版本演进

- DB 分布中 `'1'` 已出现（20 行），`'0'` 为生效前初始态未落样本。

```ground:caliber
name: 平台产品已生效
predicate: "platform_product.product_status = '1'"
scope: 平台产品列表/生效
evidence: db
```

关联：[[platform_product]]、[[platform_product_status]]、[[product_open_status]]

---END FILE---

---FILE: calibers/general_product.md ---
---
type: caliber
title: 通用产品
page_key: general_product
domain: 平台产品配置
status: draft
aliases: [GENERAL, 通用类产品]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「通用产品」是 [[platform_product]] 的 `product_type = 'GENERAL'` 口径，用于 `listPlatformProduct` 与客户产品扩展点的 GENERAL 分支，并参与「进入产品项目生效校验」的类型前置判断（[[project_effective_check]]）。

## 需求背景

通用产品在 `multiple_project_flag='Y'` 时需校验企业关联项目生效状态，未命中返回「暂无操作权限」。

## 版本演进

- 代码枚举 `PlatformProductTypeEnum.GENERAL` 与 DB 落库值同值（DB 计数 9，verdict=confirm）。

```ground:caliber
name: 通用产品
predicate: "platform_product.product_type = 'GENERAL'"
scope: listPlatformProduct/客户产品扩展点 GENERAL
evidence: code
```

关联：[[platform_product]]、[[interworking_product]]、[[project_effective_check]]

---END FILE---

---FILE: calibers/interworking_product.md ---
---
type: caliber
title: 互通产品
page_key: interworking_product
domain: 平台产品配置
status: draft
aliases: [INTERWORKING, 互通类产品]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「互通产品」是 [[platform_product]] 的 `product_type = 'INTERWORKING'` 口径，落到互通产品扩展点分支。

## 需求背景

与 [[general_product]] 并列构成产品分类全集；分类值在保存前由 `checkBeforeSave` 校验（[[product_code_name_unique]]）。

## 版本演进

- 代码枚举 `PlatformProductTypeEnum.INTERWORKING` 与 DB 落库值同值（DB 计数 11，verdict=confirm）。

```ground:caliber
name: 互通产品
predicate: "platform_product.product_type = 'INTERWORKING'"
scope: 互通产品扩展点
evidence: code
```

关联：[[platform_product]]、[[general_product]]、[[product_code_name_unique]]

---END FILE---

---FILE: calibers/platform_product_enabled.md ---
---
type: caliber
title: 平台产品启用
page_key: platform_product_enabled
domain: 平台产品配置
status: draft
aliases: [产品启用, enable=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - db
contract_version: "0.1"
---

「平台产品启用」是 [[platform_product]] 的逻辑启用口径，`enable = 'Y'`，作用于产品列表可见性与唯一性检查，与生效状态 `product_status` 相互独立。

## 需求背景

保存与唯一性检查（[[product_code_name_unique]]）只考虑启用中的记录；列表白名单过滤见 [[list_whitelist_filter]]。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 平台产品启用
predicate: "platform_product.enable = 'Y'"
scope: 产品列表/唯一性检查
evidence: db
```

关联：[[platform_product]]、[[platform_product_effective]]、[[product_code_name_unique]]

---END FILE---

---FILE: calibers/tenant_product_on_shelf.md ---
---
type: caliber
title: 租户产品已上架
page_key: tenant_product_on_shelf
domain: 平台产品配置
status: draft
aliases: [租户产品已开通, open_status=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「租户产品已上架」是开通客户产品的前置校验口径，也是租户产品列表的可见条件，等价于 [[tenant_product]] 的 `open_status = 'Y'`。

## 需求背景

客户产品开通（[[cust_product_opening]]）前必须命中该口径；处理中的 P 值需等待多级回调（[[multi_level_callback_pending]]），流转见 [[tenant_product_open_status]]。

## 版本演进

- 初版口径；需求文档所述 ACTIVE 字面量与实现不符，实际为 `'Y'`。

```ground:caliber
name: 租户产品已上架
predicate: "tenant_product.open_status = 'Y'"
scope: 开通客户产品前置校验/租户产品列表
evidence: code
```

关联：[[tenant_product]]、[[tenant_product_open_status]]、[[multi_level_callback_pending]]

---END FILE---

---FILE: calibers/config_mapping_enabled.md ---
---
type: caliber
title: 配置映射启用
page_key: config_mapping_enabled
domain: 平台产品配置
status: draft
aliases: [cust_config_mapping.enable=Y]
oid: 1
scope:
  databases: [platform]
sources:
  - code
contract_version: "0.1"
---

「配置映射启用」是 `getConfig` / `listConfig` 查询 [[cust_config_mapping]] 时的启用过滤口径，`enable = 'Y'`。

## 需求背景

企业角色到平台产品编码的映射查询依赖该过滤（[[company_type]]、[[config_mapping_filter_key]]）；产品扩展配置不落本表，见 [[product_ext_config_from_nacos]]。

## 版本演进

- 初版口径，无历史变更。

```ground:caliber
name: 配置映射启用
predicate: "cust_config_mapping.enable = 'Y'"
scope: getConfig/listConfig 查询
evidence: code
```

关联：[[cust_config_mapping]]、[[config_mapping_filter_key]]、[[product_ext_config_from_nacos]]

---END FILE---

---FILE: rules/product_code_name_unique.md ---
---
type: rule
title: 平台产品编码与名称唯一
page_key: product_code_name_unique
domain: 平台产品配置
status: draft
aliases: [BR-001, checkBeforeSave]
oid: 1
scope:
  databases: [platform]
sources:
  - db:platform_product.product_code(UNI)/uq_name
  - code:PlatformProductController.java#checkBeforeSave
  - code:PlatformProductApplication.java#checkBeforeSave
  - code:PlatformProductDomainService.java#checkBeforeSave
  - reqdoc:BR-001
contract_version: "0.1"
---

保存或更新 PlatformProductDO 之前必须通过 `checkBeforeSave`：校验产品基本信息、`product_code` 唯一性与产品类型枚举（[[general_product]] / [[interworking_product]]），任一失败抛 BaseException，落库被阻断。DB 侧 `product_code` 唯一索引与名称唯一索引构成第二道防线。

## 需求背景

需求文档 BR-001 与实现一致：Controller → Application → DomainService 三层同名 `checkBeforeSave` 承接校验。类型枚举只接受 GENERAL / INTERWORKING，查询哨兵值 ALL='2' 不可作为存储值提交。

## 版本演进

- BR-001 首次契约化即标记为已确认（confirmed），锚点证据为代码与需求文档双源。

```ground:rule
name: 平台产品编码/名称唯一
content: "platform_product.product_code 与 name 建唯一索引，保存前 checkBeforeSave 校验产品基本信息、code 唯一与类型枚举"
impact: 重复编码/名称阻断保存
field_targets:
  - platform_product.product_code
  - platform_product.name
evidence: "code_path:PlatformProductController.java#checkBeforeSave;PlatformProductApplication.java#checkBeforeSave;PlatformProductDomainService.java#checkBeforeSave + reqdoc:BR-001"
```

关联：[[platform_product]]、[[general_product]]、[[interworking_product]]、[[platform_product_enabled]]

---END FILE---

---FILE: rules/cust_role_combine_antifraud.md ---
---
type: rule
title: 企业角色组合反欺诈
page_key: cust_role_combine_antifraud
domain: 平台产品配置
status: draft
aliases: [checkCustRoleCombine, 2.3 角色组合校验]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java#checkCustRoleCombine
  - code:TenantProductApplication.java#checkProjectProductByCustType
  - reqdoc:2.3
contract_version: "0.1"
---

同一企业在同一产品下聚合其 `companyType` 集合，仅当角色数 ≥ 2 且该集合不在 [[platform_product]] 的 `cust_role_combine` 允许集合内时抛 `BaseException(系统暂不支持该角色组合)`。该规则阻断「一企业一产品扮演多角色」的欺诈路径，作用于企业加入项目与开通产品两个入口。

## 需求背景

需求文档 2.3「客户加入项目-角色组合校验」与实现一致（confirmed）：`checkCustRoleCombine` 聚合角色集合后读取 `cust_role_combine` 判定，`checkProjectProductByCustType` 做产品维度收敛。角色取值域见 [[company_type]]。

## 版本演进

- `cust_role_combine` 为文本字段，需解析为 `Set<Set<String>>` 后比较，属实现侧约定。

```ground:rule
name: 企业角色组合反欺诈
content: "聚合同一企业在同一产品下的 companyType 集合，仅当角色数>=2 且集合不在 platform_product.cust_role_combine 允许集合内时抛 BaseException(系统暂不支持该角色组合)"
impact: 阻断企业加入项目/开通产品，防止一企业一产品扮演多角色
field_targets:
  - platform_product.cust_role_combine
  - cust_project_rel.company_type
evidence: "code_path:TenantProductApplication.java#checkCustRoleCombine;TenantProductApplication.java#checkProjectProductByCustType + reqdoc:2.3"
```

关联：[[platform_product]]、[[company_type]]、[[platform_operator_exemption]]

---END FILE---

---FILE: rules/project_effective_check.md ---
---
type: rule
title: 进入产品项目生效校验
page_key: project_effective_check
domain: 平台产品配置
status: draft
aliases: [multiple_project_flag, 关联项目校验]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#gotoProductSupplierFirstRelatedProject
  - code:projectRelProductRangeAdapter.listProject
contract_version: "0.1"
---

(document_claim，未证实)

当 [[platform_product]] 的 `multiple_project_flag='Y'` 且产品为 [[general_product]] 时，进入产品前必须校验企业关联项目生效（`projectRelProductRangeAdapter.listProject`），否则返回「暂无操作权限」。

## 需求背景

该规则与多企业角色校验（[[cust_role_combine_antifraud]]）共同构成进入产品的前置闸口；平台运营方被豁免，见 [[platform_operator_exemption]]。

## 版本演进

- 需求文档 2.2「租户项目生命周期 effective/invalid/change/delete 与 SyncTenantProjectJobHandle 下游同步」在证据中未展开，`TenantProjectApplication` 仅被 codemap 提及，属未证实主张，暂记于本页。

```ground:rule
name: 进入产品项目生效校验
content: "platform_product.multiple_project_flag=Y 且产品为通用类型时，需企业关联项目生效(projectRelProductRangeAdapter.listProject)，否则返回 暂无操作权限"
impact: 未关联生效项目禁止进入产品
field_targets:
  - platform_product.multiple_project_flag
  - tenant_project.project_status
evidence: "code_path:PlatformProductApplication.java#gotoProductSupplierFirstRelatedProject"
```

关联：[[platform_product]]、[[general_product]]、[[platform_operator_exemption]]

---END FILE---

---FILE: rules/platform_operator_exemption.md ---
---
type: rule
title: 平台运营方豁免
page_key: platform_operator_exemption
domain: 平台产品配置
status: draft
aliases: [运营方豁免, custProductInclusion]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#gotoProductSupplierByCompanyType
  - code:CustProductDomainService.java#custProductInclusion
contract_version: "0.1"
---

平台运营方不参与项目状态检查，且在 `custProductInclusion` 中直接返回 true，因此可进入并开通全部产品。判定依据是企业的角色类型（[[company_type]]）。

## 需求背景

该豁免是 [[project_effective_check]] 与 [[cust_role_combine_antifraud]] 的例外分支，保障运营侧不受业务闸口限制。

## 版本演进

- 初版规则，无历史变更。

```ground:rule
name: 平台运营方豁免
content: "平台运营方不检查项目状态，且在 custProductInclusion 中直接返回 true"
impact: 运营方可进入/开通全部产品
field_targets:
  - cust_company_info.cust_company_type
evidence: "code_path:PlatformProductApplication.java#gotoProductSupplierByCompanyType;CustProductDomainService.java#custProductInclusion"
```

关联：[[project_effective_check]]、[[cust_role_combine_antifraud]]、[[company_type]]

---END FILE---

---FILE: rules/list_whitelist_filter.md ---
---
type: rule
title: 产品列表白名单过滤
page_key: list_whitelist_filter
domain: 平台产品配置
status: draft
aliases: [BR-002, filterLimitProduct, platform.limit.product.support]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductController.java#listTenantProduct
  - code:PlatformProductController.java#filterLimitProduct
  - code:PlatformProductProviderImpl.java#listOpenProductByCompanyId
  - reqdoc:BR-002
contract_version: "0.1"
---

Nacos 配置 `platform.limit.product.support` 非空时，仅返回 `productCode` 命中白名单的产品，用于收敛客户端可见的平台产品集合。列表取数链路为：AGW 请求直接返回；非 AGW 取当前 `dbTenantCode`，按 [[tenant_product]] 已开通列表过滤，再经白名单过滤。

## 需求背景

需求文档 BR-002 与实现一致（confirmed）：`listTenantProduct` 完成租户维度过滤后调用 `filterLimitProduct` 做白名单裁剪。白名单以 [[platform_product_code]] 为匹配键。

## 版本演进

- 初版规则，配置项取值由 Nacos 管理，运行期可变。

```ground:rule
name: 列表白名单过滤
content: "Nacos 配置 platform.limit.product.support 非空时，仅返回包含 productCode 的产品"
impact: 控制客户端可见平台产品集合
field_targets:
  - platform_product.product_code
evidence: "code_path:PlatformProductController.java#listTenantProduct;PlatformProductController.java#filterLimitProduct;PlatformProductProviderImpl.java#listOpenProductByCompanyId + reqdoc:BR-002"
```

关联：[[platform_product]]、[[tenant_product]]、[[platform_product_code]]、[[tenant_product_on_shelf]]

---END FILE---

---FILE: rules/multi_level_callback_pending.md ---
---
type: rule
title: 多级产品回调置中
page_key: multi_level_callback_pending
domain: 平台产品配置
status: draft
aliases: [activeAndNotify, ACFLOW/ORDER 置 P]
oid: 1
scope:
  databases: [platform]
sources:
  - code:TenantProductApplication.java#activeAndNotify
  - code:ProductOpenStatusEnum.java
contract_version: "0.1"
---

租户产品开通时按产品分流：ACFLOW / ORDER 产品把 [[tenant_product]] 的 `open_status` 置为 P，等待多级回调；其他产品直接由 `domainService.active` 生效置 Y，并推送 EFFECTED 事件。

## 需求背景

该规则决定 [[tenant_product_open_status]] 的流转分支，并直接决定 [[tenant_product_on_shelf]] 口径何时成立。P 状态的产品不满足客户产品开通前置条件。

## 版本演进

- 需求文档所述 PENDING/ACTIVE/CANCEL 与实现的 P/Y 不符，本规则以代码为准（见 [[product_open_status]]）。

```ground:rule
name: 多级产品回调置中
content: "ACFLOW/ORDER 产品开通时把 tenant_product.open_status 置 P 等待多级回调，其他产品直接生效并推送 EFFECTED 事件"
impact: 租户产品开通状态流转
field_targets:
  - tenant_product.open_status
evidence: "code_path:TenantProductApplication.java#activeAndNotify"
```

关联：[[tenant_product]]、[[tenant_product_open_status]]、[[tenant_product_on_shelf]]、[[product_open_status]]

---END FILE---

---FILE: rules/product_ext_config_from_nacos.md ---
---
type: rule
title: 产品扩展配置来源 Nacos
page_key: product_ext_config_from_nacos
domain: 平台产品配置
status: draft
aliases: [getProductExtConfig, app-list.yml, clientConfig]
oid: 1
scope:
  databases: [platform]
sources:
  - code:PlatformProductApplication.java#getProductExtConfig
  - code:NacosFacade.java#listProductApp
contract_version: "0.1"
---

`getProductExtConfig` / `getProductConfig` 读取 Nacos `app-list.yml` 中的 `extConfig` / `clientConfig`（经 `nacosFacade.listProductApp()`），产品扩展与页面配置查询不落库。[[cust_config_mapping]] 只服务 `getConfig` / `listConfig` 的 `type+innerCode+outerChannel` 查询，两者来源不同，不可混用。

## 需求背景

需求文档 BR-003 主张扩展配置按 productCode+key+expectedValue 三元组查询 `cust_config_mapping`，代码证据证伪该主张，详见 [[cust_config_mapping]]。

## 版本演进

- BR-003 首次契约化即标记为 refuted，本规则固化「Nacos 为准」的实现事实。

```ground:rule
name: 产品扩展配置来源 Nacos
content: "getProductExtConfig/getProductConfig 读取 app-list.yml 的 extConfig/clientConfig，而非 cust_config_mapping 表"
impact: 产品扩展/页面配置查询不落库
field_targets:
  - platform_product.product_code
evidence: "code_path:PlatformProductApplication.java#getProductExtConfig;NacosFacade.java#listProductApp"
```

关联：[[cust_config_mapping]]、[[platform_product]]、[[config_mapping_filter_key]]

---END FILE---

---FILE: concepts/product_open_status.md ---
---
type: concept
title: 产品开通状态
page_key: product_open_status
domain: 平台产品配置
status: draft
aliases: [openStatus, open_status, product_status, 开通状态]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java
  - code:TenantProductApplication.java
  - code:ProductStatusEnum.java
contract_version: "0.1"
maps_to: cust_auth_application.open_status
also_confused_with:
  - tenant_product.open_status
  - platform_product.product_status
adjudication: boundary
boundary: "三张表语义不同：platform_product.product_status 为产品定义层生效状态('0'/'1')；tenant_product.open_status 为租户上架状态(Y/P)；cust_auth_application.open_status 为企业级开通状态(OPENED/OPENING/NOT_OPENED)。需求文档称 PENDING/ACTIVE/CANCEL 与实现不符。"
---

「产品开通状态」是需求文档与接口层最易混淆的术语：同一句「产品是否开通」在三张表上对应三套取值域与三种业务含义。本概念页用于固定辨析边界，默认指企业级的 [[cust_auth_application]] `open_status`。

## 需求背景

- 定义层：[[platform_product]] 的 `product_status`（'0' 待生效 / '1' 已生效），见 [[platform_product_status]]。
- 上架层：[[tenant_product]] 的 `open_status`（Y 已上架 / P 处理中），见 [[tenant_product_open_status]]。
- 开通层：[[cust_auth_application]] 的 `open_status`（OPENED / OPENING / NOT_OPENED），见 [[cust_product_open_status]]。

需求文档把租户上架状态写作 PENDING / ACTIVE / CANCEL，实现为 P / Y，属文档与实现的命名漂移。

## 版本演进

- 三套语义在实现中长期并存，未做字段改名，仅通过本概念页的边界裁定区分。

关联：[[cust_auth_application]]、[[tenant_product]]、[[platform_product]]、[[cust_product_open_status]]、[[tenant_product_open_status]]、[[platform_product_status]]

---END FILE---

---FILE: concepts/platform_product_code.md ---
---
type: concept
title: 平台产品编码
page_key: platform_product_code
domain: 平台产品配置
status: draft
aliases: [productCode, platformProductCode, product_code, platform_product_code]
oid: 1
scope:
  databases: [platform]
sources:
  - db:platform_product.product_code
  - code:PlatformProductApplication.java
contract_version: "0.1"
maps_to: platform_product.product_code
also_confused_with:
  - platform_product.platform_code
adjudication: boundary
boundary: "product_code 为产品级编码(ACFLOW/AMS/DRAFT/ORDER/RVSFACTOR_PC/STORAGE/VOUCHER)；platform_code 为平台级编码(AMS/DRAFT/HTCP*/PPLATFORM/XYC)，两者不可互换。"
---

「平台产品编码」指产品级唯一键 `platform_product.product_code`，是跨表引用、事件路由与列表白名单过滤的统一键值。与「平台编码」`platform_code` 形近义异，不可互换。

## 需求背景

向下游传递时以 `platformProductCode` 出现，例如 [[tenant_product]] 的 `platform_product_code` 与 [[cust_config_mapping]] 的 `outer_channel`；白名单过滤见 [[list_whitelist_filter]]。

## 版本演进

- 产品级编码与平台级编码自始分列，未发生合并或改名。

关联：[[platform_product]]、[[tenant_product]]、[[cust_config_mapping]]、[[list_whitelist_filter]]、[[config_mapping_filter_key]]

---END FILE---

---FILE: concepts/config_mapping_filter_key.md ---
---
type: concept
title: 配置映射过滤键
page_key: config_mapping_filter_key
domain: 平台产品配置
status: draft
aliases: [outerChannel, productCode, platformProductCode]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustProductDomainService.java#getProductCompanyTypeConfig
contract_version: "0.1"
maps_to: cust_config_mapping.outer_channel
also_confused_with:
  - cust_config_mapping.inner_code
adjudication: boundary
boundary: "getProductCompanyTypeConfig 实际传参为 (type='COMPANY_TYPE_MAPPING', innerCode=companyType, outerChannel=platformProductCode)，outer_channel 存的是平台产品编码而非渠道。"
---

「配置映射过滤键」澄清 [[cust_config_mapping]] 三个键位的实际语义：`outer_channel` 在平台产品域被当作平台产品编码使用，`inner_code` 存企业角色码，`type` 为映射类型（如 COMPANY_TYPE_MAPPING）。字段名与内容不一致，阅读需求文档时须按内容而非名称理解。

## 需求背景

企业角色到平台产品编码的映射查询依赖该三元组，配合 [[config_mapping_enabled]] 过滤；角色语义见 [[company_type]]，产品编码语义见 [[platform_product_code]]。

## 版本演进

- 字段名沿用渠道语义，实现在产品域复用后语义漂移，暂不改名，仅以本页裁定。

关联：[[cust_config_mapping]]、[[platform_product_code]]、[[company_type]]、[[config_mapping_enabled]]

---END FILE---

---FILE: concepts/company_type.md ---
---
type: concept
title: 企业角色
page_key: company_type
domain: 平台产品配置
status: draft
aliases: [companyType, custCompanyType, company_type_code, roleType]
oid: 1
scope:
  databases: [platform]
sources:
  - code:CustCompanyTypeEnum.java
  - code:TenantProductApplication.java#checkCustRoleCombine
contract_version: "0.1"
maps_to: cust_company_info.cust_company_type
also_confused_with:
  - cust_project_rel.company_type
  - platform_product_cust_role.company_type_code
adjudication: synonym
boundary: "均为同一 CustCompanyTypeEnum 取值域(CORE/SUPPLIER/DEALER/FINANCE/PLATFORM_OPERATOR_COMPANY 等)，在多表以不同列名出现。"
---

「企业角色」在平台产品域对应同一取值域 `CustCompanyTypeEnum`，但在不同表以 `cust_company_type` / `company_type` / `company_type_code` 等列名出现，属同义异名，不构成边界冲突。

## 需求背景

角色信息参与三处判断：产品角色组合反欺诈（[[cust_role_combine_antifraud]]，读取 [[platform_product]] 的 `cust_role_combine`）、进入产品项目校验（[[project_effective_check]]）、平台运营方豁免（[[platform_operator_exemption]]）。角色到平台产品编码的映射键位辨析见 [[config_mapping_filter_key]]。

## 版本演进

- 多表列名不统一，取值域统一，未做字段归并。

关联：[[cust_role_combine_antifraud]]、[[platform_operator_exemption]]、[[config_mapping_filter_key]]、[[platform_product]]

---END FILE---