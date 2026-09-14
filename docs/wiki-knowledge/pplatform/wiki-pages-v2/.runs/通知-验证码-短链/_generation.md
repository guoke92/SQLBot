---FILE: tables/short_link.md ---
---
type: table
title: 短链表 short_link
page_key: short_link
domain: notification
status: draft
aliases: [短链, 短链表, ShortLinkDO]
oid: 1
scope:
  databases: []
sources:
  - db:short_link
  - ShortLinkController.java:44-95
  - ShortLinkDO.java:@TableName
contract_version: "0.1"
---

short_link 是平台短链服务的核心存储表，承载短链码（number）、短链类型（type）、跳转目标（source_url）与有效期策略（is_forever / expire_time），并带有数据租户与逻辑租户隔离字段。访问侧由 [[short_link_type_route]] 决定跳转方式，由 [[short_link_expire_check]] 决定是否拦截过期链接，由 [[short_link_id_verify_code]] 防止短链被枚举。

短链在语义上先按有效期分为 [[permanent_short_link]] 与 [[temporary_short_link]]（见 [[short_link_expire_state]]），再按类型分为 [[normal_short_link]] 与 [[file_short_link]]，两条切分维度互相独立。

## 需求背景
短链服务面向通知与客户触达场景提供可对外投放的短链接，因此需要区分「永久有效」与「限时有效」两种投放策略，并对文件类目标链接隐藏真实路径。需求侧要求短链不可被顺序枚举，故在短链码中内嵌校验位。

## 版本演进
- 当前 DB 中 is_forever 全部为 "Y"，未见 "N" 样本；限时分支的行为依据代码常量与 [[temporary_short_link_expire_check]]。
- 需求文档提出「需要短链时由 ShortLinkAppication 生成短链」，代码链路中仅见访问侧 ShortLinkController，生成侧未被证实，见 REVIEW。

```ground:table
table: short_link
fields:
  - name: id
    type: ""
    desc: 短链表主键
    dict: ""
  - name: code
    type: ""
    desc: 编码
    dict: ""
  - name: name
    type: ""
    desc: 名称
    dict: ""
  - name: source_url
    type: ""
    desc: 源链接，短链实际跳转目标
    dict: ""
  - name: expire_time
    type: ""
    desc: 到期时间，仅非永久短链访问时校验
    dict: ""
  - name: number
    type: ""
    desc: 短链编码/短链码，用于按 number 查询或生成校验码
    dict: ""
  - name: type
    type: ""
    desc: 短链类型，NORMAL=普通链接，FILE=文件链接
    dict: ""
  - name: is_forever
    type: ""
    desc: 到期类型，Y=永久有效，N=限时有效；DB 当前全为 Y
    dict: ""
  - name: enable
    type: ""
    desc: 启用标识
    dict: ""
  - name: db_tenant_code
    type: ""
    desc: 数据租户标识
    dict: ""
  - name: app_tenant_code
    type: ""
    desc: 逻辑租户标识
    dict: ""
```
---END FILE---

---FILE: tables/cust_setting_config.md ---
---
type: table
title: 企业配置表 cust_setting_config
page_key: cust_setting_config
domain: notification
status: draft
aliases: [企业配置, 客户配置, CustSettingConfig]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config
  - CustSettingConfigEnhanceService.java
contract_version: "0.1"
---

cust_setting_config 保存单企业维度的开关与模板配置：既包含关键/非关键信息字段清单，也包含认证审核开关、打款验证、人脸识别，以及合同与协议类模板编码，还包含邀请码的有效期与重复发送间隔。审核类开关的判定见 [[enterprise_auth_audit_caliber]] 与 [[non_key_info_audit_caliber]]，配置开关的取值集合见 [[cust_setting_config_switch]]。

## 需求背景
企业认证与信息变更是有风险的写操作，需求侧要求企业可自行决定「认证是否需要审核」「非关键信息变更是否需要审核」，并允许开启打款验证作为认证辅助手段；邀请码则需要控制有效期与重复发送频率，防止刷取。

## 版本演进
- 审核开关、人脸识别、打款验证当前以字符串字面量 "yes"/"no" 存储，未见枚举类，取值集合见 [[cust_setting_config_switch]]。
- 邀请码有效期与重复发送间隔为「数值 + 单位」双列结构，单位由 *_unit / *_unti 列决定（sending_interval_unti 为库中实际列名拼写）。相关文档主张见 [[invitation_code_period]]。

```ground:table
table: cust_setting_config
fields:
  - name: key_word
    type: ""
    desc: 企业关键信息字段 JSON 数组
    dict: ""
  - name: no_key_word
    type: ""
    desc: 企业非关键信息字段 JSON 数组
    dict: ""
  - name: need_auth_verify
    type: ""
    desc: 企业认证审核开关，yes=需要审核，no=不需要
    dict: ""
  - name: need_verify_no_key
    type: ""
    desc: 非关键信息变更审核开关，yes=需要审核，no=不需要
    dict: ""
  - name: face_recognition
    type: ""
    desc: 人脸识别开关，no=不启用
    dict: ""
  - name: payment_verification
    type: ""
    desc: 打款验证开关，yes=启用
    dict: ""
  - name: payment_maximum_number
    type: ""
    desc: 最多申请打款次数
    dict: ""
  - name: invitation_code_period
    type: ""
    desc: 邀请码有效期数值，单位由 invitation_code_period_unit 决定
    dict: ""
  - name: invitation_code_period_unit
    type: ""
    desc: 邀请码有效期单位
    dict: ""
  - name: sending_interval
    type: ""
    desc: 邀请码重复发送时间间隔数值
    dict: ""
  - name: sending_interval_unti
    type: ""
    desc: 邀请码重复发送时间间隔单位
    dict: ""
  - name: user_agreement
    type: ""
    desc: 用户协议模板编码
    dict: ""
  - name: privacy_policy_agreement
    type: ""
    desc: 隐私政策模板编码
    dict: ""
  - name: authorization_online
    type: ""
    desc: 授权确认书-线上签署模板编码
    dict: ""
  - name: authorization_offline
    type: ""
    desc: 授权确认书-线下签署模板编码
    dict: ""
  - name: cfca_agreement
    type: ""
    desc: 数字证书服务协议模板编码
    dict: ""
```
---END FILE---

---FILE: tables/cust_message_send_policy.md ---
---
type: table
title: 消息发送策略表 cust_message_send_policy
page_key: cust_message_send_policy
domain: notification
status: draft
aliases: [消息发送策略, 消息配置, CustMessageSendPolicy]
oid: 1
scope:
  databases: []
sources:
  - db:cust_message_send_policy
contract_version: "0.1"
---

cust_message_send_policy 以「消息类型 + 场景码」为粒度控制企业侧消息是否发送，是通知组件在客户域的开关表。发送开关默认 Y，并另有启用标识 enable 控制记录本身是否生效。

## 需求背景
通知触达需要按企业的业务场景做精细化开关（例如某企业不希望收到某类短信），因此需要按 msg_kind 与 scenes_type 组合配置发送策略，避免在代码中硬编码场景。

## 版本演进
- 当前该表只有配置语义，未见与验证码/短链链路的直接关联证据，相关通知发送规则见 [[verify_code_scenes_whitelist]] 与 [[notice_local_downstream_route]]。

```ground:table
table: cust_message_send_policy
fields:
  - name: msg_kind
    type: ""
    desc: 消息类型
    dict: ""
  - name: scenes_type
    type: ""
    desc: 场景码
    dict: ""
  - name: send_enable
    type: ""
    desc: 发送标识，默认 Y
    dict: ""
  - name: name
    type: ""
    desc: 名称
    dict: ""
  - name: enable
    type: ""
    desc: 启用标识
    dict: ""
```
---END FILE---

---FILE: enums/short_link_type.md ---
---
type: enum
title: 短链类型 short_link.type
page_key: short_link_type
domain: notification
status: draft
aliases: [ShortLinkType, 短链类型枚举, NORMAL, FILE]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52-55
  - db:short_link.type
contract_version: "0.1"
---

short_link.type 区分短链的跳转处理方式，取值由 [[normal_short_link]] 与 [[file_short_link]] 两个术语桥分别承接，路由行为见 [[short_link_type_route]]。

## 需求背景
文件类目标链接不能直接把存储路径暴露给外部，因此需要与普通链接区分，前者在跳转前必须经过文件服务加密。

## 版本演进
- 取值写点为 ShortLinkController.java:52 的 NORMAL 分支与 55 的 else 分支（FILE），与 extract-enums 基线一致。

```ground:enum
field: short_link.type
values:
  - value: NORMAL
    java_name: ShortLinkType.NORMAL
    stored_as: getDictKey
    label: 普通短链
    note: DB 值分布 NORMAL 4750；ShortLinkController.java:52 判断后直接跳转
  - value: FILE
    java_name: ShortLinkType.FILE
    stored_as: getDictKey
    label: 文件短链
    note: DB 值分布 FILE 605；ShortLinkController.java:55 else 分支调用 filePathEncrypt
```
---END FILE---

---FILE: enums/short_link_is_forever.md ---
---
type: enum
title: 到期类型 short_link.is_forever
page_key: short_link_is_forever
domain: notification
status: draft
aliases: [isForever, BooleanEnum.Y, BooleanEnum.N, 永久标识]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - db:short_link.is_forever
contract_version: "0.1"
---

short_link.is_forever 是短链有效期策略开关，也是 [[short_link_expire_state]] 状态机的状态字段。Y 对应 [[permanent_short_link]]，N 对应 [[temporary_short_link]]。

## 需求背景
短链既可能长期投放（永久有效），也可能作为限时活动的临时入口，需要以单一字段表达两种策略，避免用 expire_time 是否为空来隐式推断。

## 版本演进
- DB 当前全部为 "Y"，"N" 仅有代码常量证据（ShortLinkController.java:48 的等于 N 判断），属于代码已实现但数据未覆盖的取值。

```ground:enum
field: short_link.is_forever
values:
  - value: Y
    java_name: BooleanEnum.Y
    stored_as: getDictKey
    label: 永久有效
    note: DB 全部为 Y；代码只在等于 N 时校验过期
  - value: N
    java_name: BooleanEnum.N
    stored_as: getDictKey
    label: 限时有效
    note: DB 当前无 N 样本，仅代码常量证据
```
---END FILE---

---FILE: enums/cust_setting_config_switch.md ---
---
type: enum
title: 企业配置开关取值 cust_setting_config.*
page_key: cust_setting_config_switch
domain: notification
status: draft
aliases: [审核开关, needAuthVerify, needVerifyNoKey, faceRecognition, paymentVerification]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config
  - CustSettingConfigEnhanceService.java
contract_version: "0.1"
---

cust_setting_config 中的审核与认证类开关统一采用字符串 "yes"/"no" 表达，代码中未见对应枚举类，判断时使用字符串字面量比较。业务术语承接见 [[enterprise_auth_audit]]、[[non_key_info_audit]]、[[face_recognition_off]]、[[payment_verification_on]]。

## 需求背景
企业侧开关需要被运营与前端直接读写，字符串 yes/no 便于配置页面展示；但这也意味着取值没有类型约束，需要文档固定口径。

## 版本演进
- 当前 yes/no 均为单行或多行 DB 样本 + 代码字面量证据，尚未抽取为枚举；若后续新增枚举类，本页需同步。

```ground:enum
field: cust_setting_config.need_auth_verify, cust_setting_config.need_verify_no_key, cust_setting_config.face_recognition, cust_setting_config.payment_verification
values:
  - value: "yes"
    java_name: 无枚举
    stored_as: 字符串字面量
    label: need_auth_verify 需要企业认证审核
    note: 代码判断 "no" 时不需审核
  - value: "yes"
    java_name: 无枚举
    stored_as: 字符串字面量
    label: need_verify_no_key 需要非关键信息变更审核
    note: 代码判断 "no" 时不需审核
  - value: "no"
    java_name: 无枚举
    stored_as: 字符串字面量
    label: face_recognition 不启用人脸识别
    note: DB 单行样本
  - value: "yes"
    java_name: 无枚举
    stored_as: 字符串字面量
    label: payment_verification 启用打款验证
    note: DB 单行样本
```
---END FILE---

---FILE: processes/short_link_expire_state.md ---
---
type: process
title: 短链有效期状态
page_key: short_link_expire_state
domain: notification
status: draft
aliases: [短链有效期状态机, is_forever 状态]
oid: 1
scope:
  databases: []
sources:
  - db:short_link.is_forever
  - ShortLinkController.java:48
contract_version: "0.1"
---

该状态机描述短链按 is_forever 的两态划分：永久有效与限时有效。两个状态对应 [[permanent_short_link]] 与 [[temporary_short_link]]，判定发生在访问跳转链路上，具体口径见 [[permanent_short_link_skip_expire]] 与 [[temporary_short_link_expire_check]]。

## 需求背景
短链的过期语义不应由 expire_time 是否为空隐式表达，需求侧要求显式的到期类型字段，使访问端可以明确区分「永不校验过期」与「必须校验过期」。

## 版本演进
- Y 态有 DB 全量数据支撑；N 态仅有代码常量证据，DB 无样本，转换条件（谁会写入 N、何时写入）在本次分析中无证据。

```ground:process
name: 短链有效期状态
field: short_link.is_forever
states:
  - value: "Y"
    label: 永久有效
    source: db_dist
  - value: "N"
    label: 限时有效
    source: code_const
transitions: []
```
---END FILE---

---FILE: calibers/permanent_short_link_skip_expire.md ---
---
type: caliber
title: 永久短链不校验到期时间
page_key: permanent_short_link_skip_expire
domain: notification
status: draft
aliases: [永久有效短链口径, is_forever=Y 不校验]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - db:short_link.is_forever
contract_version: "0.1"
---

凡是 is_forever='Y' 的短链，在访问跳转时完全不校验 expire_time，即使该列有值也不影响跳转。该口径与 [[temporary_short_link_expire_check]] 构成互斥边界，术语定义见 [[permanent_short_link]]。

## 需求背景
永久短链用于长期投放（例如印刷物、长期协议链接），需求侧要求其不受投放期限影响，避免误过期导致业务中断。

## 版本演进
- DB 中所有样本均为 Y，即当前线上全量短链都命中该口径。

```ground:caliber
name: 永久短链不校验到期时间
predicate: short_link.is_forever = 'Y'
scope: 短链访问跳转
evidence: ShortLinkController.java:48 + db
```
---END FILE---

---FILE: calibers/temporary_short_link_expire_check.md ---
---
type: caliber
title: 限时短链到期校验
page_key: temporary_short_link_expire_check
domain: notification
status: draft
aliases: [限时有效短链口径, is_forever=N 校验]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
contract_version: "0.1"
---

is_forever='N' 的短链在访问时必须校验 expire_time，过期即拦截。该口径的拦截动作与异常语义见 [[short_link_expire_check]]，术语定义见 [[temporary_short_link]]。

## 需求背景
限时短链承载活动、临时入口等场景，需求侧要求到期自动失效，不能依赖人工下架。

## 版本演进
- 该分支当前无 DB 数据样本，仅由代码常量分支支撑；上线后一旦出现 N 态数据即会生效。

```ground:caliber
name: 限时短链到期校验
predicate: short_link.is_forever = 'N'
scope: 短链访问跳转
evidence: ShortLinkController.java:48
```
---END FILE---

---FILE: calibers/normal_short_link_redirect.md ---
---
type: caliber
title: 普通短链直接跳转
page_key: normal_short_link_redirect
domain: notification
status: draft
aliases: [NORMAL 跳转口径]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52
contract_version: "0.1"
---

type='NORMAL' 的短链直接使用 source_url 重定向，不经过文件服务。该口径与 [[file_short_link_encrypt_redirect]] 互斥，术语定义见 [[normal_short_link]]。

## 需求背景
普通短链指向的是页面或外部系统地址，本就可公开，直接重定向可减少一次文件服务调用。

## 版本演进
- DB 中 NORMAL 值分布为 4750，是当前短链的主流形态。

```ground:caliber
name: 普通短链直接跳转
predicate: short_link.type = 'NORMAL'
scope: 短链访问跳转
evidence: ShortLinkController.java:52
```
---END FILE---

---FILE: calibers/file_short_link_encrypt_redirect.md ---
---
type: caliber
title: 文件短链加密后跳转
page_key: file_short_link_encrypt_redirect
domain: notification
status: draft
aliases: [FILE 跳转口径, 文件短链加密]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:55
  - db:short_link.type
contract_version: "0.1"
---

type='FILE' 的短链在跳转前必须先用 filePathEncrypt(source_url,false) 处理 source_url，再重定向，避免真实文件路径暴露。术语定义见 [[file_short_link]]，对应规则见 [[short_link_type_route]]。

## 需求背景
文件类链接的存储路径属于敏感信息，需求侧要求短链对外只暴露短链码，真实路径需加密后跳转。

## 版本演进
- DB 中 FILE 值分布为 605，为短链的次要形态。

```ground:caliber
name: 文件短链加密后跳转
predicate: short_link.type = 'FILE'
scope: 短链访问跳转
evidence: ShortLinkController.java:55 + db
```
---END FILE---

---FILE: calibers/enterprise_auth_audit_caliber.md ---
---
type: caliber
title: 企业认证需要审核
page_key: enterprise_auth_audit_caliber
domain: notification
status: draft
aliases: [needAuthVerify 口径]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_auth_verify
contract_version: "0.1"
---

当 need_auth_verify='yes' 时，企业认证进入审核流程；代码中 'no' 直接返回不需要审批。术语定义见 [[enterprise_auth_audit]]，与其相邻的开关口径见 [[non_key_info_audit_caliber]]。

## 需求背景
认证涉企业主体资质，需求侧允许企业按自身风控要求决定是否引入人工审核环节。

## 版本演进
- 当前为字符串字面量判断，无枚举约束，取值见 [[cust_setting_config_switch]]。

```ground:caliber
name: 企业认证需要审核
predicate: cust_setting_config.need_auth_verify = 'yes'
scope: 企业变更/认证审核
evidence: CustSettingConfigEnhanceService.java + db
```
---END FILE---

---FILE: calibers/non_key_info_audit_caliber.md ---
---
type: caliber
title: 非关键信息变更需要审核
page_key: non_key_info_audit_caliber
domain: notification
status: draft
aliases: [needVerifyNoKey 口径]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_verify_no_key
contract_version: "0.1"
---

当 need_verify_no_key='yes' 时，非关键信息变更进入审核；关键信息有变更时优先返回需要审核，非关键信息再按此开关判断。术语定义见 [[non_key_info_audit_caliber]] 对应术语页 [[non_key_info_audit]]。

## 需求背景
企业信息中的关键信息与非关键信息风险等级不同，需求侧要求分别配置审核策略，避免为低风险变更引入高成本审核。

## 版本演进
- 当前为字符串字面量判断，无枚举约束，取值见 [[cust_setting_config_switch]]。

```ground:caliber
name: 非关键信息变更需要审核
predicate: cust_setting_config.need_verify_no_key = 'yes'
scope: 企业变更审核
evidence: CustSettingConfigEnhanceService.java + db
```
---END FILE---

---FILE: calibers/face_recognition_off.md ---
---
type: caliber
title: 人脸识别关闭
page_key: face_recognition_off
domain: notification
status: draft
aliases: [faceRecognition=no 口径]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.face_recognition
contract_version: "0.1"
---

face_recognition='no' 表示该企业不启用人脸识别作为认证手段。本口径仅有 DB 单行样本证据，代码侧未在本次分析中取得判断位置。

## 需求背景
人脸识别属于可选认证强度配置，需求侧允许企业关闭以适配不同地区的合规要求。

## 版本演进
- 仅 DB 样本支撑；若后续取到代码判断位置，应补充到本页证据。

```ground:caliber
name: 人脸识别关闭
predicate: cust_setting_config.face_recognition = 'no'
scope: 企业认证配置
evidence: db
```
---END FILE---

---FILE: calibers/payment_verification_on.md ---
---
type: caliber
title: 打款验证开启
page_key: payment_verification_on
domain: notification
status: draft
aliases: [paymentVerification=yes 口径]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.payment_verification
contract_version: "0.1"
---

payment_verification='yes' 表示该企业启用打款验证，认证时可通过向企业对公账户打款并回填金额完成验证。最多申请次数由 payment_maximum_number 控制。

## 需求背景
打款验证用于在无人值守场景下替代人工审核，需求侧要求企业可自行开启。

## 版本演进
- 仅 DB 样本支撑；打款次数上限字段当前无代码消费证据。

```ground:caliber
name: 打款验证开启
predicate: cust_setting_config.payment_verification = 'yes'
scope: 企业认证配置
evidence: db
```
---END FILE---

---FILE: rules/notification_channel_abstraction.md ---
---
type: rule
title: 通知通道三类抽象
page_key: notification_channel_abstraction
domain: notification
status: draft
aliases: [通知组件通道抽象, 邮件短信微信]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:MessageTypeEnum
  - WechatNotificationService.java:1
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
---

通知组件以邮件、短信、微信三类通道抽象承载各类触达场景，业务侧按场景选择通道，通道实现各自封装发送细节。验证码场景的选择见 [[verify_code_scenes_whitelist]]，站内信与下游路由见 [[notice_local_downstream_route]]。

## 需求背景
需求文档（平台基础组件业务规则文档 2.2）要求通知能力以通道抽象方式提供，避免业务方直接依赖具体供应商接口；代码侧 MessageTypeEnum 与 WechatNotificationService 与该叙述一致。

## 版本演进
- 当前抽象为三类通道；后续若新增通道类型，本页与通道相关规则需同步。

```ground:rule
name: 通知通道三类抽象
content: 通知组件以邮件/短信/微信三类抽象承载触达场景
impact: 决定业务侧按场景选择通道的调用方式
field_targets: []
evidence: MessageFacade.java:MessageTypeEnum + WechatNotificationService.java:1 + reqdoc:平台基础组件业务规则文档#2.2
```
---END FILE---

---FILE: rules/sms_send_fail_silent.md ---
---
type: rule
title: 短信发送失败不抛异常
page_key: sms_send_fail_silent
domain: notification
status: draft
aliases: [短信失败静默, sendSmsMessage 不抛异常]
oid: 1
scope:
  databases: []
sources:
  - PlatMessageApplication.java:34-45
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
---

PlatMessageApplication.sendSmsMessage 捕获发送异常并返回 fail，不向调用方抛出。与之同构的微信侧行为见 [[wechat_notify_fail_silent]]。

## 需求背景
需求文档（平台基础组件业务规则文档 2.2）明确发送失败记录日志、不抛异常给业务；代码实现与该叙述一致。

## 版本演进
- 需求文档另提出「短信需要幂等时使用 RedisSmsLock 检查/加锁」，链路上未出现 RedisSmsLock 调用，未证实，见 REVIEW。

```ground:rule
name: 短信发送失败不抛异常
content: PlatMessageApplication.sendSmsMessage 捕获异常并返回 fail，不向调用方抛出
impact: 短信发送失败不影响主流程
field_targets: []
evidence: PlatMessageApplication.java:34-45 + reqdoc:平台基础组件业务规则文档#2.2
```
---END FILE---

---FILE: rules/wechat_notify_fail_silent.md ---
---
type: rule
title: 微信验证码通知失败不抛异常
page_key: wechat_notify_fail_silent
domain: notification
status: draft
aliases: [微信通知失败静默, sendVerificationCodeNotification 返回 true]
oid: 1
scope:
  databases: []
sources:
  - WechatNotificationService.java:70-80
  - reqdoc:平台基础组件业务规则文档#2.2
contract_version: "0.1"
---

WechatNotificationService.sendVerificationCodeNotification 捕获异常、记录日志并返回 true，调用方不会因微信通知失败而中断。与短信侧对称的规则见 [[sms_send_fail_silent]]。

## 需求背景
需求文档要求发送失败记录日志、不抛异常给业务；微信服务号通知依赖第三方接口，更需容错。

## 版本演进
- 当前返回值为 true 的语义是「已尽力发送」，不表示对方已收到，这一点在统计口径上需注意。

```ground:rule
name: 微信验证码通知失败不抛异常
content: WechatNotificationService.sendVerificationCodeNotification 捕获异常记录日志并返回 true
impact: 微信通知失败不影响主流程
field_targets: []
evidence: WechatNotificationService.java:70-80 + reqdoc:平台基础组件业务规则文档#2.2
```
---END FILE---

---FILE: rules/verify_code_scenes_whitelist.md ---
---
type: rule
title: 验证码场景白名单
page_key: verify_code_scenes_whitelist
domain: notification
status: draft
aliases: [VERIFY_CODE_SCENES, 验证码场景]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:VERIFY_CODE_SCENES
contract_version: "0.1"
---

MessageFacade.VERIFY_CODE_SCENES 指定需要走 sendVerifyCode 的场景：批量签署、落地手机、重置密码、注册手机、法人授权、客户建档认证、CA 意向确认。其余场景不生成验证码。相关的有效期依赖见 [[verify_code_period_config_require]]，落库回填见 [[verify_code_phone_writeback]]。

## 需求背景
验证码有短信成本与骚扰风险，需求侧要求按场景白名单开放，避免任意业务调用验证码能力。

## 版本演进
- 白名单当前为代码常量，新增场景需要改代码并发布；表 cust_message_send_policy 的场景开关与白名单的关系在本分析中无证据。

```ground:rule
name: 验证码场景白名单
content: MessageFacade.VERIFY_CODE_SCENES 指定需要走 sendVerifyCode 的场景：批量签署、落地手机、重置密码、注册手机、法人授权、客户建档认证、CA意向确认
impact: 决定是否生成并注入验证码
field_targets: []
evidence: MessageFacade.java:VERIFY_CODE_SCENES
```
---END FILE---

---FILE: rules/verify_code_period_config_require.md ---
---
type: rule
title: 验证码有效期配置缺失抛异常
page_key: verify_code_period_config_require
domain: notification
status: draft
aliases: [缺少验证码有效期配置, getIndentifyConfigDTO 为空]
oid: 1
scope:
  databases: []
sources:
  - MessageFacade.java:sendVerifyCode
contract_version: "0.1"
---

sendVerifyCode 中若 indentifycodeFacade.getIndentifyConfigDTO 返回空，抛 CommonException「缺少验证码有效期配置」。即验证码发送强依赖有效期配置。

## 需求背景
验证码若无有效期则无法判断是否可复用，需求侧要求把有效期配置作为发送前置条件，配置缺失时快速失败而非静默发送。

## 版本演进
- 当前为抛异常失败策略；是否应降级为默认有效期，本次分析无证据。

```ground:rule
name: 验证码有效期配置缺失抛异常
content: sendVerifyCode 中若 indentifycodeFacade.getIndentifyConfigDTO 返回空，抛 CommonException 缺少验证码有效期配置
impact: 验证码发送依赖有效期配置
field_targets: []
evidence: MessageFacade.java:sendVerifyCode
```
---END FILE---

---FILE: rules/contract_sign_verify_code_multi_limit.md ---
---
type: rule
title: 合同签署验证码多笔限制
page_key: contract_sign_verify_code_multi_limit
domain: notification
status: draft
aliases: [多笔限制, sendVerifyCode 入参限制]
oid: 1
scope:
  databases: []
sources:
  - CustVerifyCodeController.java:sendVerifyCode
contract_version: "0.1"
---

CustVerifyCodeController.sendVerifyCode 中 serviceKey 与 businessId 不能同时为多笔，否则抛异常，用于限制批量签署验证码的入参组合。

## 需求背景
批量签署与单笔签署的验证码归属不同，需求侧要求禁止两种多笔标识同时传入，避免验证码无法定位到唯一业务对象。

## 版本演进
- 当前为入参校验；批量签署场景的具体处理见 [[verify_code_scenes_whitelist]]。

```ground:rule
name: 合同签署验证码多笔限制
content: CustVerifyCodeController.sendVerifyCode 中 serviceKey 与 businessId 不能同时为多笔，否则抛异常
impact: 限制批量签署验证码入参组合
field_targets: []
evidence: CustVerifyCodeController.java:sendVerifyCode
```
---END FILE---

---FILE: rules/verify_code_phone_writeback.md ---
---
type: rule
title: 短信验证码手机号回填合同签署表
page_key: verify_code_phone_writeback
domain: notification
status: draft
aliases: [setVerifyContractPhone, 验证码接收人落库]
oid: 1
scope:
  databases: []
sources:
  - CustVerifyCodeApplication.java:sendVerifyCode
contract_version: "0.1"
---

当消息类型为 PHONE 时，CustVerifyCodeApplication 将接收手机号通过 contractSignInfoProvider.setVerifyContractPhone 写入合同签署信息，使验证码接收人可追溯。该调用为 RPC 提供方关系，目标表名未在代码中直接出现（推测为合同签署表），关系判定为 derived。

## 需求背景
签署类验证码需要留痕，需求侧要求记录验证码接收手机号，便于后续争议处理与合规审计。

## 版本演进
- 目标表为推断，未在代码中直接出现表名，见 REVIEW。

```ground:rule
name: 短信验证码手机号回填合同签署表
content: 当消息类型为 PHONE 时，CustVerifyCodeApplication 将接收手机号通过 contractSignInfoProvider.setVerifyContractPhone 写入合同签署信息
impact: 验证码接收人落库到合同签署侧
field_targets: []
evidence: CustVerifyCodeApplication.java:sendVerifyCode
```
---END FILE---

---FILE: rules/wechat_verify_code_template_fixed.md ---
---
type: rule
title: 微信验证码通知模板固定
page_key: wechat_verify_code_template_fixed
domain: notification
status: draft
aliases: [templateNo 1000001, sysCode beehive]
oid: 1
scope:
  databases: []
sources:
  - WechatNotificationService.java:TemplateNo
  - WechatNotificationService.java:SysCode
contract_version: "0.1"
---

微信验证码通知固定使用 sysCode=beehive、templateNo=1000001，dataMap 含 phone_number、code、system_name 三个变量。

## 需求背景
微信服务号模板消息需预先报备，需求侧要求验证码类通知统一使用同一模板，便于模板审核与运维。

## 版本演进
- 模板号当前硬编码；若更换模板需同步发布，且涉及已报备模板的替换。

```ground:rule
name: 微信验证码通知模板固定
content: 微信验证码通知使用 sysCode=beehive，templateNo=1000001，dataMap 含 phone_number/code/system_name
impact: 固定短信/企微验证码模板
field_targets: []
evidence: WechatNotificationService.java:TemplateNo/SysCode
```
---END FILE---

---FILE: rules/notice_local_downstream_route.md ---
---
type: rule
title: 站内信本地与下游路由
page_key: notice_local_downstream_route
domain: notification
status: draft
aliases: [resolveLocalNoticeSystem, 待办路由]
oid: 1
scope:
  databases: []
sources:
  - CustNoticeService.java:resolveLocalNoticeSystem
contract_version: "0.1"
---

CustNoticeService.pageTodo 对 ACCOUNT_PRODUCT 映射本地 system=pplatform，BEECREDIT 映射本地 system=BEECREDIT，其余产品走 Dubbo 下游产品查询待办。

## 需求背景
站内信与待办分属不同产品线，部分产品数据在本库、部分在下游，需求侧要求查询时按产品自动路由，避免全量聚合。被否证的需求主张：「所有通知同步发送站内信」——代码中 sendAllMessageForSubmit 是分别发送站内信、待办、短信，并未统一强制站内信，故该主张不成立。

## 版本演进
- 本地映射当前为硬编码产品码集合，新增本地产品需改代码；下游路由依赖 Dubbo 可用性。

```ground:rule
name: 站内信本地与下游路由
content: CustNoticeService.pageTodo 对 ACCOUNT_PRODUCT 映射本地 system=pplatform，BEECREDIT 映射本地 system=BEECREDIT，其余走 Dubbo 下游产品
impact: 决定待办查询走本库还是下游
field_targets: []
evidence: CustNoticeService.java:resolveLocalNoticeSystem
```
---END FILE---

---FILE: rules/todo_unread_status.md ---
---
type: rule
title: 待办未读口径
page_key: todo_unread_status
domain: notification
status: draft
aliases: [noticeStatus=0, 未读条件]
oid: 1
scope:
  databases: []
sources:
  - CustNoticeService.java:pageTodo
  - NoticeFacade.java:pageTodoCount
contract_version: "0.1"
---

待办查询与统计统一使用 noticeStatus='0' 作为未完成/未读条件，列表与计数共用同一口径。

## 需求背景
需求侧要求角标数量与列表内容一致，因此统计与分页必须共用同一状态条件。

## 版本演进
- 当前口径集中在两处调用点，未抽为常量，修改时需同时改分页与计数。

```ground:rule
name: 待办未读口径
content: 待办查询与统计使用 noticeStatus='0' 作为未完成/未读条件
impact: 待办数量统计口径
field_targets: []
evidence: CustNoticeService.java:pageTodo + NoticeFacade.java:pageTodoCount
```
---END FILE---

---FILE: rules/short_link_expire_check.md ---
---
type: rule
title: 短链过期校验
page_key: short_link_expire_check
domain: notification
status: draft
aliases: [链接已过期, 短链拦截]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - ShortLinkController.java:83
contract_version: "0.1"
---

is_forever='N' 且 expire_time <= now 时抛出链接已过期，短链访问被拦截。对应的口径页为 [[temporary_short_link_expire_check]]，永久短链不受此校验见 [[permanent_short_link_skip_expire]]。

## 需求背景
限时短链到期必须自动失效，需求侧要求访问端直接拦截而不是返回目标地址。

## 版本演进
- 该分支当前无 DB 数据，属于已实现未使用的能力。

```ground:rule
name: 短链过期校验
content: is_forever='N' 且 expire_time <= now 时抛出链接已过期
impact: 短链访问拦截
field_targets:
  - short_link.is_forever
  - short_link.expire_time
evidence: ShortLinkController.java:48,83
```
---END FILE---

---FILE: rules/short_link_type_route.md ---
---
type: rule
title: 短链类型路由
page_key: short_link_type_route
domain: notification
status: draft
aliases: [NORMAL 直接跳转, FILE 加密跳转]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52-55
  - ShortLinkController.java:92-95
contract_version: "0.1"
---

type='NORMAL' 时直接跳转 source_url；type='FILE' 时先 filePathEncrypt(source_url,false) 再跳转。对应口径页 [[normal_short_link_redirect]] 与 [[file_short_link_encrypt_redirect]]。

## 需求背景
文件类短链需要隐藏真实存储路径，需求侧要求文件短链必须走文件服务加密后再重定向。

## 版本演进
- 两个分支当前均有 DB 数据（NORMAL 4750 / FILE 605）。

```ground:rule
name: 短链类型路由
content: type='NORMAL' 直接跳转 source_url；type='FILE' 先 filePathEncrypt(source_url,false) 再跳转
impact: 文件短链需走文件服务加密
field_targets:
  - short_link.type
  - short_link.source_url
evidence: ShortLinkController.java:52-55,92-95
```
---END FILE---

---FILE: rules/short_link_id_verify_code.md ---
---
type: rule
title: 短链 ID 映射校验
page_key: short_link_id_verify_code
domain: notification
status: draft
aliases: [generateVerifyCode, LongBase64Utils.decode]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:71-90
contract_version: "0.1"
---

shortLink 接口取 number 最后一位为校验码，用 LongBase64Utils.decode 解出 id，并用 generateVerifyCode(link.number) 校验，防止短链被顺序枚举。字段含义见 [[short_link]] 的 number 与 id。

## 需求背景
短链对外可被穷举访问，需求侧要求短链码内嵌校验位，使猜测的 id 无法直接映射为可访问链接。

## 版本演进
- 当前校验在访问侧完成；生成侧如何写入校验位未在本次分析取得证据，见 REVIEW。

```ground:rule
name: 短链 ID 映射校验
content: shortLink 接口取 number 最后一位为校验码，LongBase64Utils.decode 得到 id，并用 generateVerifyCode(link.number) 校验
impact: 防止短链被枚举
field_targets:
  - short_link.number
  - short_link.id
evidence: ShortLinkController.java:71-90
```
---END FILE---

---FILE: concepts/permanent_short_link.md ---
---
type: concept
title: 永久短链
page_key: permanent_short_link
domain: notification
status: draft
aliases: [永久有效短链, isForever=Y]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
  - db:short_link.is_forever
maps_to: short_link.is_forever = 'Y'
field_targets:
  - short_link.is_forever
  - short_link.expire_time
adjudication: boundary
also_confused_with:
  - temporary_short_link
contract_version: "0.1"
---

永久短链指 is_forever='Y' 的短链，业务上不设投放截止时间。判定边界：is_forever='Y' 时完全不校验 expire_time；'N' 时校验。与 [[temporary_short_link]] 互为边界，两者与类型维度（[[normal_short_link]] / [[file_short_link]]）正交。

## 需求背景
长期投放的短链（印刷物料、长期协议入口）不能因时间流逝而失效，需求侧要求显式的永久语义。

## 版本演进
- DB 中全部短链当前均为该状态，实际等价于「当前线上默认形态」。
- 状态机见 [[short_link_expire_state]]，口径页见 [[permanent_short_link_skip_expire]]。
---END FILE---

---FILE: concepts/temporary_short_link.md ---
---
type: concept
title: 限时短链
page_key: temporary_short_link
domain: notification
status: draft
aliases: [非永久短链, isForever=N]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:48
maps_to: short_link.is_forever = 'N'
field_targets:
  - short_link.is_forever
  - short_link.expire_time
adjudication: boundary
also_confused_with:
  - permanent_short_link
contract_version: "0.1"
---

限时短链指 is_forever='N' 的短链，业务上有明确投放截止时间。判定边界：需 expire_time > now，否则视为过期并拦截。与 [[permanent_short_link]] 互为边界。

## 需求背景
活动、临时入口类链接需要到期自动失效，需求侧要求以字段而非人工下架控制。

## 版本演进
- 该状态当前在 DB 中无数据样本，属于代码已实现、数据未启用。
- 口径页见 [[temporary_short_link_expire_check]]，拦截规则见 [[short_link_expire_check]]。
---END FILE---

---FILE: concepts/normal_short_link.md ---
---
type: concept
title: 普通短链
page_key: normal_short_link
domain: notification
status: draft
aliases: [NORMAL 短链]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:52
maps_to: short_link.type = 'NORMAL'
field_targets:
  - short_link.type
  - short_link.source_url
adjudication: boundary
also_confused_with:
  - file_short_link
contract_version: "0.1"
---

普通短链指 type='NORMAL' 的短链。判定边界：直接使用 source_url 重定向，不做加密处理。与 [[file_short_link]] 互为边界；类型维度与有效期维度（[[permanent_short_link]] / [[temporary_short_link]]）正交。

## 需求背景
指向页面与外部系统的短链本就可公开，需求侧不要求额外隐藏处理。

## 版本演进
- DB 值分布 NORMAL 4750，是短链主要形态。
- 口径页见 [[normal_short_link_redirect]]，路由规则见 [[short_link_type_route]]。
---END FILE---

---FILE: concepts/file_short_link.md ---
---
type: concept
title: 文件短链
page_key: file_short_link
domain: notification
status: draft
aliases: [FILE 短链]
oid: 1
scope:
  databases: []
sources:
  - ShortLinkController.java:55
maps_to: short_link.type = 'FILE'
field_targets:
  - short_link.type
  - short_link.source_url
adjudication: boundary
also_confused_with:
  - normal_short_link
contract_version: "0.1"
---

文件短链指 type='FILE' 的短链。判定边界：source_url 需经 filePathEncrypt 加密后再重定向，避免暴露真实文件路径。与 [[normal_short_link]] 互为边界。

## 需求背景
文件存储路径属于敏感信息，需求侧要求对外只暴露短链码。

## 版本演进
- DB 值分布 FILE 605。
- 口径页见 [[file_short_link_encrypt_redirect]]，路由规则见 [[short_link_type_route]]。
---END FILE---

---FILE: concepts/enterprise_auth_audit.md ---
---
type: concept
title: 企业认证审核
page_key: enterprise_auth_audit
domain: notification
status: draft
aliases: [needAuthVerify]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_auth_verify
maps_to: cust_setting_config.need_auth_verify = 'yes'
field_targets:
  - cust_setting_config.need_auth_verify
adjudication: boundary
also_confused_with:
  - non_key_info_audit
contract_version: "0.1"
---

企业认证审核指企业在认证环节需要人工审核。判定边界：代码中 'no' 直接返回不需要审批；'yes' 继续判断。与 [[non_key_info_audit]] 互为边界，二者属于不同触发路径。

## 需求背景
认证涉主体资质，需求侧允许企业按风控要求决定是否引入人工审核。

## 版本演进
- 取值以字符串字面量存储，见 [[cust_setting_config_switch]]；口径页见 [[enterprise_auth_audit_caliber]]。
---END FILE---

---FILE: concepts/non_key_info_audit.md ---
---
type: concept
title: 非关键信息变更审核
page_key: non_key_info_audit
domain: notification
status: draft
aliases: [needVerifyNoKey]
oid: 1
scope:
  databases: []
sources:
  - CustSettingConfigEnhanceService.java
  - db:cust_setting_config.need_verify_no_key
maps_to: cust_setting_config.need_verify_no_key = 'yes'
field_targets:
  - cust_setting_config.need_verify_no_key
  - cust_setting_config.key_word
  - cust_setting_config.no_key_word
adjudication: boundary
also_confused_with:
  - enterprise_auth_audit
contract_version: "0.1"
---

非关键信息变更审核指企业对非关键信息字段的修改需要审核。判定边界：关键信息有变更时先返回需要审核，非关键信息再按此开关判断；关键与非关键字段清单分别存于 key_word / no_key_word。与 [[enterprise_auth_audit]] 互为边界。

## 需求背景
关键与非关键信息风险等级不同，需求侧要求分别配置审核策略。

## 版本演进
- 口径页见 [[non_key_info_audit_caliber]]，取值见 [[cust_setting_config_switch]]。
---END FILE---

---FILE: concepts/invitation_code_period.md ---
---
type: concept
title: 邀请码有效期
page_key: invitation_code_period
domain: notification
status: draft
aliases: [invitationCodePeriod]
oid: 1
scope:
  databases: []
sources:
  - db:cust_setting_config.invitation_code_period
  - db:cust_setting_config.invitation_code_period_unit
maps_to: cust_setting_config.invitation_code_period
field_targets:
  - cust_setting_config.invitation_code_period
  - cust_setting_config.invitation_code_period_unit
adjudication: boundary
also_confused_with:
  - invitation_code_sending_interval
contract_version: "0.1"
---

邀请码有效期指邀请码自发出起可用的时长。判定边界：invitation_code_period 是数值列，单位由 invitation_code_period_unit 决定，二者必须成对解读；与「邀请码重复发送时间间隔」（sending_interval / sending_interval_unti）是不同语义，不可混用。

## 需求背景
邀请码需要控制有效窗口并在重复发送上做限流，防止刷取与长期滞留可用码。

## 版本演进
- 需求文档提出「邀请码随机生成8位、30天有效」，代码中未见邀请码生成逻辑，DB 中 invitation_code_period=1，文档与实现一致性未证实，见 REVIEW。
---END FILE---

---TODO: concepts/invitation_code_sending_interval.md ---
注：本页为 [[invitation_code_period]] 的对照术语，字段为 cust_setting_config.sending_interval / sending_interval_unti，语义为「邀请码重复发送时间间隔」。因本次语义分析的 term_bridges 未单列该术语桥（仅在 boundary 中被提及），按规则 1「禁止发明」不单独建页，仅在本注释中登记待补。
---END TODO---

---REVIEW: process | 短链生成流程---
类型：process | 标题：短链生成流程
问题：需求文档主张「需要短链时由 ShortLinkAppication 生成短链」，代码链路仅见访问侧 ShortLinkController，ShortLinkAppication 的生成逻辑全文未取得，生成时的字段写入（number、type、is_forever、expire_time）与校验位计算方式均无法锚定。
证据：ShortLinkController.java:1（仅见访问）+ reqdoc:平台基础组件业务规则文档#2.2
处理建议：补齐 ShortLinkAppication 源码后，补建 process 页并在 [[short_link]] 页补充生成侧关系。
---END REVIEW---

---REVIEW: rule | 短信幂等 RedisSmsLock---
类型：rule | 标题：短信发送幂等
问题：需求文档主张「短信需要幂等时使用 RedisSmsLock 检查/加锁」，本次链路分析中未出现 RedisSmsLock 调用点。
证据：链路上未出现 RedisSmsLock 调用 + reqdoc:平台基础组件业务规则文档#2.2
处理建议：确认幂等是否由其他组件（如分布式锁封装类）承担，或确认该主张已废弃。
---END REVIEW---

---REVIEW: concept | 邀请码生成与有效期---
类型：concept | 标题：邀请码生成与有效期
问题：需求文档主张「邀请码随机生成8位、30天有效」，与 DB cust_setting_config.invitation_code_period=1 存在数量级差异（单位未定），且未找到邀请码生成代码。
证据：未在代码中见邀请码生成逻辑；DB cust_setting_config.invitation_code_period=1 + reqdoc:客户管理平台业务规则文档#3.2.2
处理建议：确认 invitation_code_period_unit 的实际取值后再判定「30 天有效」是否成立，必要时在 [[invitation_code_period]] 页更新口径。
---END REVIEW---

---REVIEW: table | 短链生成侧与短信验证码落库目标表---
类型：table | 标题：关系推断待确认
问题：1）CustVerifyCodeApplication 通过 IContractSignInfoProvider.setVerifyContractPhone 写手机号，目标表名未在代码中直接出现，relation_audit 判定为 derived（推测为合同签署表）；2）short_link 所属物理库名未在本次分析中给出，frontmatter scope.databases 暂为空。
处理建议：补充接口实现类与数据源配置后回填。
---END REVIEW---