---FILE: tables/short_link.md ---
---
type: table
title: short_link 短链表
page_key: table/short_link
domain: 通知/验证码/短链
status: draft
aliases: [短链, 短链表, shortLink, short_link]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:short_link
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
contract_version: "0.1"
---

short_link 是短链跳转链路的唯一数据源：一行代表一条可访问短链，业务访问键是 `number`，跳转目标是 `source_url`。`type` 决定跳转前是否需要用 `fileService.filePathEncrypt` 换链，`is_forever` / `expire_time` 决定是否放行，`enable` 与 `db_tenant_code` 提供逻辑有效性与租户维度的过滤面。表内 `code` 属框架级通用编码字段，与业务访问口径不是同一件事，勿与 `number` 混用。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定，业务定位完全来自代码与 DB 实测。

## 版本演进

v0 首版。DB 实测存量（type：FILE=605 / NORMAL=4750；is_forever 全为 Y 共 5355 条；db_tenant_code 仅 base 一个租户）是当前数据现状快照，不是版本变更记录。

```ground:table
table: short_link
scope.database: unknown
fields:
  - field: id
    meaning: 短链主键；/sl/{number} 映射式短链中，number 去掉末位校验字符后经 LongBase64Utils.decode 还原为该 id 用于查询
    evidence: code
  - field: number
    meaning: 短链编码，是 /cust-web/sl/{number} 的唯一查询键；在 /sl/{number} 中 number 末位字符为校验位（LongBase64Utils.generateVerifyCode(link.getNumber())）
    evidence: code
  - field: code
    meaning: 通用编码字段（框架级），与业务访问用的 number 不是同一口径，勿混用
    evidence: db
  - field: source_url
    meaning: 短链跳转的源链接；type=FILE 时该值需经 fileService.filePathEncrypt 换取可访问地址后再 redirect
    evidence: db
  - field: type
    meaning: "短链类型：NORMAL=普通链接直接跳转；FILE=文件类链接需加密换链后跳转（DB 实测分布 FILE=605 / NORMAL=4750）"
    evidence: db
  - field: is_forever
    meaning: 是否永久有效；=Y 时跳过 expire_time 过期校验，=N 时按到期时间判过期（DB 实测当前存量全为 Y，5355 条）
    evidence: db
  - field: expire_time
    meaning: 短链到期时间，仅在 is_forever=N 时参与校验
    evidence: db
  - field: enable
    meaning: 逻辑有效标识（DB 实测全为 Y）
    evidence: db
  - field: db_tenant_code
    meaning: 数据租户标识（DB 实测当前存量仅 base 一个租户）
    evidence: db
```

## 关联

[[concepts/短链]] · [[processes/短链类型路由]] · [[processes/短链有效期标志]] · [[calibers/短链已过期]] · [[calibers/永久短链]] · [[calibers/普通短链]] · [[calibers/文件短链]]

---END FILE---

---FILE: tables/cust_message_send_policy.md ---
---
type: table
title: cust_message_send_policy 消息发送策略表
page_key: table/cust_message_send_policy
domain: 通知/验证码/短链
status: draft
aliases: [消息发送策略, 消息策略表, custMessageSendPolicy]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_message_send_policy
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

cust_message_send_policy 是通知链路的场景开关表：一行代表「某场景 × 某渠道」是否实际发送。`scenes_type` 是定位消息模板与场景实现类的主键式入口，与代码中的 SmsTemplateConstant / NoticeTemplateConstant / EmailTemplateConstansts 常量值对齐；`msg_kind` 区分短信/邮件/站内信等渠道维度；`send_enable` 是最终是否发出的闸门。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版，无历史版本记录。`send_enable` 默认 Y。

```ground:table
table: cust_message_send_policy
scope.database: unknown
fields:
  - field: scenes_type
    meaning: 消息场景码，对应代码中的 SmsTemplateConstant / NoticeTemplateConstant / EmailTemplateConstansts 常量值，用于定位消息模板与场景实现类
    evidence: db
  - field: msg_kind
    meaning: 消息类型（短信/邮件/站内信等渠道维度的策略分类）
    evidence: db
  - field: send_enable
    meaning: 发送标识（默认 Y），控制该场景消息是否实际发送
    evidence: db
  - field: name
    meaning: 策略名称
    evidence: db
```

## 关联

[[concepts/场景码]] · [[concepts/站内信]] · [[processes/消息渠道]] · [[calibers/短信发送默认参数]] · [[calibers/消息模板缺失]] · [[rules/通知发送失败不阻断主流程]] · [[rules/前置校验异常不受静默策略保护]]

---END FILE---

---FILE: tables/cust_setting_config.md ---
---
type: table
title: cust_setting_config 企业配置表
page_key: table/cust_setting_config
domain: 通知/验证码/短链
status: draft
aliases: [企业配置, 租户配置表, custSettingConfig]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_setting_config
contract_version: "0.1"
---

cust_setting_config 按企业（`cust_id`）保存认证与邀请类业务的可配置项：哪些字段算关键信息、变更是否需要审核、认证是否走人脸或打款验证、以及一组协议模板编号。它以配置驱动代替硬编码，本主题相关的主要是邀请码有效期与发送间隔这两个窗口参数。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版，无历史版本记录。

```ground:table
table: cust_setting_config
scope.database: unknown
fields:
  - field: invitation_code_period
    meaning: 邀请码有效期数值（DB 实测=1），需与 invitation_code_period_unit 组合使用
    evidence: db
  - field: invitation_code_period_unit
    meaning: 邀请码有效期单位
    evidence: db
  - field: sending_interval
    meaning: 邀请码重复发送时间间隔数值（DB 实测=1）
    evidence: db
  - field: sending_interval_unti
    meaning: 邀请码重复发送时间间隔单位（列名 unti 为库表既有拼写，非笔误）
    evidence: db
  - field: key_word
    meaning: 企业关键信息字段清单（JSON 数组字符串），变更审核判定用；DB 实测值含 name/custCompanyType/legalName/legalPhone/legalCertificationNo/legalCertificationType/legalEmail/registProvinceCity/timePermanent/phone/certificationNo/certificationType
    evidence: db
  - field: no_key_word
    meaning: 企业非关键信息字段清单（JSON 数组字符串）；DB 实测 contactTel/custEmail/paidInCapital
    evidence: db
  - field: need_auth_verify
    meaning: 企业认证是否需审核：no=直接免审（custChangeInfoNeedApply 首判），否则进入关键信息比对
    evidence: db
  - field: need_verify_no_key
    meaning: 非关键信息变更是否需审核：no=非关键信息变更不触发审核
    evidence: db
  - field: face_recognition
    meaning: 人脸识别开关（DB 实测 no）
    evidence: db
  - field: payment_verification
    meaning: 打款验证开关（DB 实测 yes）
    evidence: db
  - field: payment_maximum_number
    meaning: 最多申请打款次数（DB 实测 3）
    evidence: db
  - field: user_agreement
    meaning: 用户协议模板编号（DB 实测 CT-202404031806394575219）
    evidence: db
  - field: privacy_policy_agreement
    meaning: 隐私政策协议模板编号（DB 实测 CT-202404031807156758507）
    evidence: db
  - field: authorization_offline
    meaning: 授权确认书-线下签署模板编号（DB 实测 CT-202404081721209495040）
    evidence: db
  - field: cust_id
    meaning: 配置所属企业 id
    evidence: db
```

## 关联

[[calibers/邀请码有效期]] · [[concepts/验证码]]

---END FILE---

---FILE: processes/短链类型路由.md ---
---
type: process
title: 短链类型路由
page_key: process/短链类型路由
domain: 通知/验证码/短链
status: draft
aliases: [短链跳转分支, NORMAL/FILE 路由]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
  - db:short_link.type
contract_version: "0.1"
---

短链跳转在拿到 `source_url` 后并不是无条件 redirect，而是按 `short_link.type` 分流：普通链接直接下发目标地址，文件类链接必须先换取可访问地址。这一分支是短链链路里唯一影响「跳到哪里」的判定点，也是文件短链权限控制的实际落点。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。DB 存量分布 FILE=605 / NORMAL=4750。

```ground:process
name: 短链类型路由
field: short_link.type
states:
  - value: NORMAL
    label: "普通短链：直接 302 到 source_url"
    source: code_enum
  - value: FILE
    label: "文件短链：source_url 需 filePathEncrypt 换链后 302"
    source: db_dist
transitions:
  - from: NORMAL
    event: GET /cust-web/sl/{number} 命中且未过期
    to: NORMAL
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java#orderCategory
  - from: FILE
    event: type != NORMAL 时走 else 分支执行 filePathEncrypt(sourceUrl,false)
    to: FILE
    evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java#orderCategory
```

## 关联

[[tables/short_link]] · [[concepts/短链]] · [[calibers/普通短链]] · [[calibers/文件短链]] · [[processes/短链有效期标志]]

---END FILE---

---FILE: processes/短链有效期标志.md ---
---
type: process
title: 短链有效期标志
page_key: process/短链有效期标志
domain: 通知/验证码/短链
status: draft
aliases: [短链是否永久, isForever]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
  - db:short_link.is_forever
contract_version: "0.1"
---

`is_forever` 是一个开关式取值而非流程推进字段：为 Y 时整条过期判定被短路，为 N 时才把 `expire_time` 拉进比较。当前存量全部为 Y，意味着现网短链实际处于「永不判过期」的状态。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。DB 实测存量 is_forever 全为 Y（5355 条），N 分支目前无存量样本。

```ground:process
name: 短链有效期标志
field: short_link.is_forever
states:
  - value: Y
    label: 永久有效，跳过 expire_time 校验
    source: db_dist
  - value: N
    label: 非永久，访问时比对 expire_time
    source: code_enum
transitions: []
```

## 关联

[[tables/short_link]] · [[calibers/短链已过期]] · [[calibers/永久短链]] · [[processes/短链类型路由]]

---END FILE---

---FILE: processes/消息渠道.md ---
---
type: process
title: 消息渠道（MessageTypeEnum）
page_key: process/消息渠道
domain: 通知/验证码/短链
status: draft
aliases: [MessageTypeEnum, 消息类型路由, PHONE/EMAIL/NOTICE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

消息下发前先由场景实现类的 `messageType()` 决定渠道，再据此构造不同的 MessageContext：邮件走 EmailMessageContext，站内信走 NoticeMessageContext 并额外回填模板编号、system、systemName，其余（含短信）落到基础 MessageContext 并回填短信模板编号。渠道同时决定验证码是否生成——只有验证码场景才会写入 `params.smsCode` / `timeLimit`。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:process
name: 消息渠道（MessageTypeEnum）
field: messageContext.messageType
states:
  - value: PHONE
    label: 短信渠道
    source: code_enum
  - value: EMAIL
    label: 邮件渠道
    source: code_enum
  - value: NOTICE
    label: 站内信渠道
    source: code_enum
transitions:
  - from: EMAIL
    event: getMessageService(scenesType).messageType()=EMAIL → new EmailMessageContext()
    to: EMAIL
    evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#getMessageContext
  - from: NOTICE
    event: messageType()=NOTICE → new NoticeMessageContext() 并回填 noticeTemplate 的 templateNo/system/systemName
    to: NOTICE
    evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#getDefaultTemplateNo
  - from: PHONE
    event: messageType() 非 EMAIL/NOTICE → 构造基础 MessageContext，按 messageSmsTemplate 回填 templateNo
    to: PHONE
    evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#getMessageContext
  - from: PHONE
    event: 验证码场景（@MessageSpi.sendVerifyCode()=true）生成验证码并写入 params.smsCode/timeLimit
    to: PHONE
    evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#sendVerifyCode
```

## 关联

[[tables/cust_message_send_policy]] · [[concepts/站内信]] · [[concepts/场景码]] · [[concepts/验证码]] · [[calibers/短信发送默认参数]] · [[calibers/消息模板缺失]]

---END FILE---

---FILE: calibers/短链已过期.md ---
---
type: caliber
title: 短链已过期
page_key: caliber/短链已过期
domain: 通知/验证码/短链
status: draft
aliases: [文件链接已过期, 短链过期判定]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
  - db:short_link.is_forever
  - db:short_link.expire_time
contract_version: "0.1"
---

过期判定只在 `is_forever=N` 时才真正成立：先由永久标志短路，再用当前时间与 `expire_time` 比较。命中即抛出统一文案异常，跳转链路整体中断。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 短链已过期
predicate: short_link.is_forever = 'N' AND short_link.expire_time <= NOW()
scope: ShortLinkController#orderCategory / #shortLink 跳转前置校验，命中即抛 CommonException("不好意思，您访问的文件链接已过期！")
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java#orderCategory + db:short_link.is_forever/expire_time
```

## 关联

[[tables/short_link]] · [[processes/短链有效期标志]] · [[calibers/永久短链]]

---END FILE---

---FILE: calibers/永久短链.md ---
---
type: caliber
title: 永久短链
page_key: caliber/永久短链
domain: 通知/验证码/短链
status: draft
aliases: [is_forever=Y, 不过期短链]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:short_link
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
contract_version: "0.1"
---

永久短链是过期校验的短路条件：只要标志为 Y，`expire_time` 无论取什么值都不参与判定，直接进入解析跳转。当前存量全部命中该口径。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。DB 值分布 is_forever(Y:5355)，暂无 N 样本。

```ground:caliber
name: 永久短链
predicate: short_link.is_forever = 'Y'
scope: 跳过 expire_time 校验，直接解析跳转
evidence: db:short_link 值分布 is_forever(Y:5355) + code_path:ShortLinkController.java#shortLink
```

## 关联

[[tables/short_link]] · [[processes/短链有效期标志]] · [[calibers/短链已过期]]

---END FILE---

---FILE: calibers/普通短链.md ---
---
type: caliber
title: 普通短链
page_key: caliber/普通短链
domain: 通知/验证码/短链
status: draft
aliases: [NORMAL 短链, 直接跳转短链]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
contract_version: "0.1"
---

type 为 NORMAL 时，`source_url` 被视作外部可直达地址，直接 sendRedirect，不做任何换链与鉴权加工。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 普通短链
predicate: short_link.type = 'NORMAL'
scope: sourceUrl 直接 resp.sendRedirect
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java#orderCategory
```

## 关联

[[tables/short_link]] · [[processes/短链类型路由]] · [[calibers/文件短链]]

---END FILE---

---FILE: calibers/文件短链.md ---
---
type: caliber
title: 文件短链
page_key: caliber/文件短链
domain: 通知/验证码/短链
status: draft
aliases: [FILE 短链, 换链短链, filePathEncrypt]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
  - db:short_link.type
contract_version: "0.1"
---

文件短链口径以「非 NORMAL」定义：只要不是普通类型，`source_url` 就必须先经 filePathEncrypt 换成可访问地址再 redirect，避免把内部文件路径直接暴露给浏览器。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。DB 存量 FILE=605。

```ground:caliber
name: 文件短链
predicate: short_link.type = 'FILE'（即非 NORMAL）
scope: sourceUrl 经 fileService.getDefaultFileService().filePathEncrypt(sourceUrl,false) 后再 redirect
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java#shortLink + db:short_link.type(FILE:605)
```

## 关联

[[tables/short_link]] · [[processes/短链类型路由]] · [[calibers/普通短链]]

---END FILE---

---FILE: calibers/未完成待办.md ---
---
type: caliber
title: 未完成待办
page_key: caliber/未完成待办
domain: 通知/验证码/短链
status: draft
aliases: [noticeStatus=0, 待办数量口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/facade/NoticeFacade.java
contract_version: "0.1"
---

待办数以状态字面量 `'0'` 为唯一过滤条件，列表页与角标计数两条链路共用同一口径，因此两处数字天然一致。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 未完成待办
predicate: notice.notice_status = '0'
scope: NoticeFacade#pageTodoCount 与 CustNoticeService#pageTodo 均以 noticeStatus='0' 统计个人待办数
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/facade/NoticeFacade.java#pageTodoCount
```

## 关联

[[concepts/站内信]] · [[calibers/产融本库待办]] · [[calibers/AMS待办按联系人id查询]]

---END FILE---

---FILE: calibers/产融本库待办.md ---
---
type: caliber
title: 产融本库待办
page_key: caliber/产融本库待办
domain: 通知/验证码/短链
status: draft
aliases: [ACCOUNT_PRODUCT, BEECREDIT, resolveLocalNoticeSystem]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java
contract_version: "0.1"
---

productAppId 决定待办数据落在本库还是下游系统：ACCOUNT_PRODUCT 与 BEECREDIT 映射到本地 system 值后走 NoticeProvider 直接查本库，不再发起 Dubbo 调用。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 产融本库待办
predicate: productAppId = 'ACCOUNT_PRODUCT' → system='pplatform'；productAppId = 'BEECREDIT' → system='BEECREDIT'
scope: CustNoticeService#resolveLocalNoticeSystem，命中则走 NoticeProvider 本库查询，不调下游 Dubbo
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java#resolveLocalNoticeSystem
```

## 关联

[[calibers/未完成待办]] · [[calibers/AMS待办按联系人id查询]] · [[concepts/站内信]]

---END FILE---

---FILE: calibers/AMS待办按联系人id查询.md ---
---
type: caliber
title: AMS 待办按联系人 id 查询
page_key: caliber/AMS待办按联系人id查询
domain: 通知/验证码/短链
status: draft
aliases: [productAppId=AMS, getPersonId, 待办 userId 口径]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java
contract_version: "0.1"
---

AMS 场景下待办查询的主键不是登录用户 id，而是联系人（cust_person_info）的 id，由 getPersonId 取得。这个口径差异是跨系统待办对账时最容易出错的地方。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: AMS 待办按联系人 id 查询
predicate: productAppId = 'AMS' → userId = cust_person_info.id（getPersonId）
scope: CustNoticeService#pageTodo / CustNoticeController#getProductNoticeCount
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustNoticeService.java#pageTodo
```

## 关联

[[calibers/未完成待办]] · [[calibers/产融本库待办]]

---END FILE---

---FILE: calibers/短信发送默认参数.md ---
---
type: caliber
title: 短信发送默认参数
page_key: caliber/短信发送默认参数
domain: 通知/验证码/短链
status: draft
aliases: [sendSmsMessage 兜底, SMS_CUST_LIMIT_REMINDER]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-notice-component/src/main/java/com/lls/lowcode/pplatform/notices/application/PlatMessageApplication.java
contract_version: "0.1"
---

短信发送入口对三个可空入参各有一套兜底：场景码、业务类型、系统标识。空值不会导致失败，而是被静默替换为默认值，因此调用方漏传时会发出一条「默认场景」短信而非报错。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 短信发送默认参数
predicate: scenesType 为空 → SMS_CUST_LIMIT_REMINDER；businessType 为空 → 'cust_company_info'；system 为空 → pplatform
scope: PlatMessageApplication#sendSmsMessage
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-notice-component/src/main/java/com/lls/lowcode/pplatform/notices/application/PlatMessageApplication.java#sendSmsMessage
```

## 关联

[[tables/cust_message_send_policy]] · [[concepts/场景码]] · [[processes/消息渠道]]

---END FILE---

---FILE: calibers/签约验证码固定场景.md ---
---
type: caliber
title: 签约验证码固定场景
page_key: caliber/签约验证码固定场景
domain: 通知/验证码/短链
status: draft
aliases: [SMS_BATCH_SIGN_CONTRACT, 签约验证码场景覆盖]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

签约验证码重载方法不接收场景码参数，而是强制覆盖为批量签约常量。调用方传入的任何场景值在此链路上都无效。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 签约验证码固定场景
predicate: scenesType = SmsTemplateConstant.SMS_BATCH_SIGN_CONTRACT
scope: MessageFacade#sendVerifyCode(serviceKey,businessId,businessType,system,signatoryId) 强制覆盖场景码
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#sendVerifyCode
```

## 关联

[[concepts/验证码]] · [[concepts/场景码]] · [[calibers/验证码场景白名单]] · [[rules/签约验证码接收人手机号回写合同签署表]]

---END FILE---

---FILE: calibers/验证码校验口径.md ---
---
type: caliber
title: 验证码校验口径
page_key: caliber/验证码校验口径
domain: 通知/验证码/短链
status: draft
aliases: [checkIndentifyCode, indentifyWay/indentifyChannel]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/message/NoticeIndentifyProviderImpl.java
contract_version: "0.1"
---

校验入口以「识别方式 + 识别渠道」两个维度定位待校验凭证，实现本身只做透传，真正的比对逻辑在下游 IndentifycodeInfoProvider。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 验证码校验口径
predicate: indentifyWay = PHONE 或 EMAIL AND indentifyChannel = 手机号或邮箱
scope: NoticeIndentifyProvider#checkIndentifyCode 透传 IndentifycodeInfoProvider
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/message/NoticeIndentifyProviderImpl.java#checkIndentifyCode
```

## 关联

[[concepts/验证码]] · [[calibers/验证码有效期参数]] · [[calibers/验证码场景白名单]]

---END FILE---

---FILE: calibers/验证码场景白名单.md ---
---
type: caliber
title: 验证码场景白名单
page_key: caliber/验证码场景白名单
domain: 通知/验证码/短链
status: draft
aliases: [VERIFY_CODE_SCENES, 验证码场景集合]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

白名单是「允许直接调用 sendVerifyCode」的场景集合常量。不在此集合中的场景只能走普通发消息链路，不会生成验证码。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。集合成员以 MessageFacade.VERIFY_CODE_SCENES 常量为准。

```ground:caliber
name: 验证码场景白名单
predicate: scenesType ∈ {SMS_BATCH_SIGN_CONTRACT, LANDED_PHONE, RESET_PASSWORD, REGISTER_PHONE, SMS_LEDGAL_AUTHORIZE, SMS_CUST_BUILD_AUTH, SMS_CA_INTENT_CONFIRM}
scope: MessageFacade.VERIFY_CODE_SCENES 常量集合（直接调用 sendVerifyCode 的场景）
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#VERIFY_CODE_SCENES
```

## 关联

[[concepts/验证码]] · [[concepts/场景码]] · [[calibers/签约验证码固定场景]] · [[processes/消息渠道]]

---END FILE---

---FILE: calibers/验证码有效期参数.md ---
---
type: caliber
title: 验证码有效期参数
page_key: caliber/验证码有效期参数
domain: 通知/验证码/短链
status: draft
aliases: [timeLimit, codeDuration, 验证码有效期配置]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

有效期不是硬编码常数，而是「数值 + 单位显示名」拼接后写入模板参数 `timeLimit`。配置缺失时直接抛异常，属于前置校验而非静默降级。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 验证码有效期参数
predicate: params.timeLimit = indentifycodeCofig.codeDuration + codeDurationUnit.getDisplayName()
scope: MessageFacade#sendVerifyCode，配置缺失抛 CommonException("缺少验证码有效期配置！")
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#sendVerifyCode
```

## 关联

[[concepts/验证码]] · [[rules/前置校验异常不受静默策略保护]] · [[calibers/验证码校验口径]]

---END FILE---

---FILE: calibers/邀请码有效期.md ---
---
type: caliber
title: 邀请码有效期
page_key: caliber/邀请码有效期
domain: 通知/验证码/短链
status: draft
aliases: [invitationCodePeriod, 邀请码过期窗口]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_setting_config.invitation_code_period
  - db:cust_setting_config.invitation_code_period_unit
contract_version: "0.1"
---

邀请码有效期由配置项驱动，必须数值与单位成对读取，单看数值无法确定实际窗口。DB 实测 invitation_code_period=1。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 邀请码有效期
predicate: cust_setting_config.invitation_code_period + invitation_code_period_unit
scope: 邀请码有效期由配置驱动（DB 实测 invitation_code_period=1），非固定常数
evidence: db:cust_setting_config.invitation_code_period/invitation_code_period_unit
```

## 关联

[[tables/cust_setting_config]] · [[concepts/验证码]]

---END FILE---

---FILE: calibers/消息模板缺失.md ---
---
type: caliber
title: 消息模板缺失
page_key: caliber/消息模板缺失
domain: 通知/验证码/短链
status: draft
aliases: [消息模板查找失败, getDefaultTemplateNo 异常]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

模板查找按「租户 + 场景」两个维度定位，任两者组合查不到即判定缺失并抛出带租户与场景的异常文案，便于运维直接定位配置缺口。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:caliber
name: 消息模板缺失
predicate: 站内信/短信/邮件模板按 dbTenantCode + scenesType 均查不到
scope: MessageFacade#getDefaultTemplateNo 抛 CommonException("消息模板查找失败！租户【x】场景【y】")
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#getDefaultTemplateNo
```

## 关联

[[processes/消息渠道]] · [[concepts/场景码]] · [[rules/前置校验异常不受静默策略保护]]

---END FILE---

---FILE: concepts/短链.md ---
---
type: concept
title: 短链
page_key: concept/短链
domain: 通知/验证码/短链
status: draft
aliases: [短链接, shortLink, short_link]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:short_link
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/controller/shortlink/ShortLinkController.java
maps_to: short_link 表（number 为访问键，source_url 为目标链接，type 决定是否需要换链）
also_confused_with: ["/sl/{number} 的 id 映射方式", "short_link.code 通用编码字段"]
adjudication: boundary
boundary: /cust-web/sl/{number} 按 short_link.number 查询；/sl/{number} 则把 number 去掉末位校验字符后 Base64 解码为 short_link.id 查询，并校验末位字符 = LongBase64Utils.generateVerifyCode(link.number)；两者均可能因链接不存在/过期/校验失败抛同一文案异常
contract_version: "0.1"
---

短链是「一条 number 换取一次跳转」的映射凭证。系统内存在两条访问链路，取键方式完全不同：一条按业务编码 number 直查，另一条把 number 当作含校验位的 Base64 串解出主键。讨论短链时必须先说明走的是哪条链路，否则「用 number 还是 id 查」会直接对不上。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

## 关联

[[tables/short_link]] · [[processes/短链类型路由]] · [[processes/短链有效期标志]] · [[calibers/普通短链]] · [[calibers/文件短链]] · [[calibers/短链已过期]] · [[calibers/永久短链]]

---END FILE---

---FILE: concepts/验证码.md ---
---
type: concept
title: 验证码
page_key: concept/验证码
domain: 通知/验证码/短链
status: draft
aliases: [verifyCode, indentifyCode, smsCode]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/message/NoticeIndentifyProviderImpl.java
maps_to: 验证码生成与校验：IndentifycodeFacade#getIndentifyCode / IndentifycodeInfoProvider#checkIndentifyCode，回填 MessageContext.verifyCode 与模板参数 smsCode
also_confused_with: [邀请码 invitationCode, 签约签约码 serviceKey]
adjudication: boundary
boundary: 验证码为短时校验凭证（有效期取 indentifycodeCofig.codeDuration+单位），随消息下发；邀请码是邀请认证场景的长期凭证，有效期由 cust_setting_config.invitation_code_period/unit 控制，两者存储与校验链路不同
contract_version: "0.1"
---

验证码是一次性的短时校验凭证，生命周期压在「生成 → 随消息下发 → 用户回填 → 校验」这条链上，有效期来自 indentifycodeCofig 配置并以 timeLimit 参数渲染进模板。它与邀请码在形态上都是「一串码」，但存储与过期控制完全不在同一套机制里。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

## 关联

[[calibers/验证码有效期参数]] · [[calibers/验证码校验口径]] · [[calibers/验证码场景白名单]] · [[calibers/签约验证码固定场景]] · [[rules/验证码接收渠道取值]] · [[processes/消息渠道]]

---END FILE---

---FILE: concepts/站内信.md ---
---
type: concept
title: 站内信
page_key: concept/站内信
domain: 通知/验证码/短链
status: draft
aliases: [消息盒子, notice, NOTICE]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/facade/NoticeFacade.java
maps_to: MessageTypeEnum.NOTICE 渠道 + noticeFacade.getNoticeTemplate(dbTenantCode, sceneType) 模板 + NoticeProvider
also_confused_with: ["待办（noticeStatus=0）", "待办任务 notice_task_* 场景"]
adjudication: boundary
boundary: 站内信按 NOTICE 模板渲染消息内容；待办是站内信中 noticeStatus='0' 未完成态的子集，通过 completeBySceneType(sceneType) 关闭待办，二者共用表但统计口径不同
contract_version: "0.1"
---

站内信是 NOTICE 渠道下的消息载体，按模板渲染内容后落库并可在消息盒子中查看。待办复用同一张表，但只取未完成态子集，并通过场景关闭动作而非阅读动作来消解——这是「站内信」与「待办」最常被混为一谈的边界。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

## 关联

[[processes/消息渠道]] · [[calibers/未完成待办]] · [[calibers/产融本库待办]] · [[calibers/AMS待办按联系人id查询]]

---END FILE---

---FILE: concepts/场景码.md ---
---
type: concept
title: 场景码
page_key: concept/场景码
domain: 通知/验证码/短链
status: draft
aliases: [scenesType, sceneType, 场景类型]
oid: 1
scope:
  databases: [unknown]
sources:
  - db:cust_message_send_policy.scenes_type
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
maps_to: cust_message_send_policy.scenes_type 及 SmsTemplateConstant/NoticeTemplateConstant/EmailTemplateConstansts 常量
also_confused_with: [businessType, msg_kind]
adjudication: boundary
boundary: scenesType 决定消息模板与场景实现类（@MessageSpi.scenesType）；businessType 决定业务数据来源表（如 cust_company_info / cust_person_info），二者在 SendMessageReq 中同级且都必传
contract_version: "0.1"
---

场景码回答的是「这条消息属于哪类业务事件」，是模板选择与场景实现类路由的键；businessType 回答的是「去取哪张业务表的数据」。两者在请求对象里并排出现且都必传，很容易被当作同义参数，实际上一个决定怎么发、一个决定发什么。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

## 关联

[[tables/cust_message_send_policy]] · [[calibers/短信发送默认参数]] · [[calibers/验证码场景白名单]] · [[calibers/消息模板缺失]] · [[processes/消息渠道]]

---END FILE---

---FILE: concepts/通知失败不阻断业务.md ---
---
type: concept
title: 通知失败不阻断业务
page_key: concept/通知失败不阻断业务
domain: 通知/验证码/短链
status: draft
aliases: [发送失败仅记录日志, 静默失败策略]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-notice-component/src/main/java/com/lls/lowcode/pplatform/notices/application/PlatMessageApplication.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMessageSendService.java
maps_to: PlatMessageApplication#sendSmsMessage / CustMessageSendService#sendSms / WechatNotificationService#sendVerificationCodeNotification 的 catch 分支
also_confused_with: ["MessageFacade#getDefaultTemplateNo 抛出的模板缺失异常（该场景会抛出）"]
adjudication: boundary
boundary: 发送动作本身失败被吞掉并返回 fail/false；但模板查找失败、验证码有效期配置缺失等前置校验异常会向上抛出，不属"静默失败"范围
contract_version: "0.1"
---

「通知失败不阻断业务」指的只覆盖发送动作本身：渠道不可用时吞掉异常、返回失败结果或记日志，让建档、变更、签约等主流程继续推进。它不覆盖前置校验——模板缺失、验证码配置缺失这类问题仍会向上抛，因为这属于配置错误而非渠道抖动。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

## 关联

[[rules/通知发送失败不阻断主流程]] · [[rules/前置校验异常不受静默策略保护]] · [[calibers/消息模板缺失]]

---END FILE---

---FILE: rules/通知发送失败不阻断主流程.md ---
---
type: rule
title: 通知发送失败不阻断主流程
page_key: rule/通知发送失败不阻断主流程
domain: 通知/验证码/短链
status: draft
aliases: [静默降级, 通知失败仅记日志]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-notice-component/src/main/java/com/lls/lowcode/pplatform/notices/application/PlatMessageApplication.java
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMessageSendService.java
contract_version: "0.1"
---

通知是主流程的旁路：短信、邮件、站内信、微信通知在各自入口都对发送动作做了异常收敛，失败结果以返回值或日志体现，不向上传播。这条规则是「渠道抖动不影响业务办理」的落地方式。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:rule
name: 通知发送失败不阻断主流程
content: 短信发送在 PlatMessageApplication#sendSmsMessage 中 try/catch，异常时返回 PlatMessageRespDto.fail(e.getMessage())；CustMessageSendService 各 sendSms/sendEmail/sendMessage 方法 catch 后仅记录日志；微信通知在 WechatNotificationService 中 catch 后返回 true。
impact: 建档、变更、签约等主流程不因通知渠道不可用而回滚或失败
field_targets: [cust_message_send_policy.send_enable]
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-notice-component/src/main/java/com/lls/lowcode/pplatform/notices/application/PlatMessageApplication.java#sendSmsMessage + code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplatform/cust/service/CustMessageSendService.java#sendSms
```

## 关联

[[concepts/通知失败不阻断业务]] · [[rules/前置校验异常不受静默策略保护]] · [[tables/cust_message_send_policy]]

---END FILE---

---FILE: rules/前置校验异常不受静默策略保护.md ---
---
type: rule
title: 前置校验异常不受静默策略保护
page_key: rule/前置校验异常不受静默策略保护
domain: 通知/验证码/短链
status: draft
aliases: [模板缺失异常, 验证码配置缺失异常]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

静默降级只保护「发送」这一步。参数缺失、模板查不到、验证码有效期配置不存在这些属于配置或调用契约问题，全部以异常形式抛给调用方，让问题在接入阶段就暴露。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:rule
name: 前置校验异常不受静默策略保护
content: receiver/dbTenantCode/paramMap 为空分别抛 BaseException；模板查找失败抛 CommonException("消息模板查找失败！...")；验证码有效期配置缺失抛 CommonException("缺少验证码有效期配置！")。
impact: 配置缺失会直接暴露给调用方，需在接入场景前确保模板与验证码配置就绪
field_targets: [cust_message_send_policy.scenes_type]
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#sendVerifyCode
```

## 关联

[[concepts/通知失败不阻断业务]] · [[rules/通知发送失败不阻断主流程]] · [[calibers/消息模板缺失]] · [[calibers/验证码有效期参数]]

---END FILE---

---FILE: rules/验证码接收渠道取值.md ---
---
type: rule
title: 验证码接收渠道取值
page_key: rule/验证码接收渠道取值
domain: 通知/验证码/短链
status: draft
aliases: [receiver 取第一个, 邮箱默认第一个]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java
contract_version: "0.1"
---

receiver 的类型决定取哪个渠道值：字符串直接使用，集合只取第 0 个，其他类型直接拒绝。这意味着多接收人场景下只有第一个人真正收到验证码并参与校验。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:rule
name: 验证码接收渠道取值
content: receiver 为 String 时直接作为 indentifyChannel；为 List 时取第 0 个（注释明确"邮箱默认第一个"）；其他类型落 error 日志并抛 BaseException("系统消息通知暂不支持验证码!")。
impact: 多接收人场景只有第一个接收人参与验证码生成与校验
field_targets: []
evidence: code_path:lowcode-pplatform-components/lowcode-pplatform-sso-component/src/main/java/com/lls/lowcode/pplatform/facade/MessageFacade.java#sendVerifyCode
```

## 关联

[[concepts/验证码]] · [[calibers/验证码校验口径]] · [[processes/消息渠道]]

---END FILE---

---FILE: rules/签约验证码接收人手机号回写合同签署表.md ---
---
type: rule
title: 签约验证码接收人手机号回写合同签署表
page_key: rule/签约验证码接收人手机号回写合同签署表
domain: 通知/验证码/短链
status: draft
aliases: [setVerifyContractPhone, 签署手机号回写]
oid: 1
scope:
  databases: [unknown]
sources:
  - code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplat
contract_version: "0.1"
---

签约场景下发送验证码不是纯通知动作，它同时把接收手机号写回合同签署记录（短信渠道时），供后续签署校验比对。这条规则把「发验证码」与「合同签署状态」耦合在一起。

## 需求背景

v0 语义分析未提供 reqdoc_claims，本节暂无需求文档主张可锚定。

## 版本演进

v0 首版。

```ground:rule
name: 签约验证码接收人手机号回写合同签署表
content: CustVerifyCodeApplication#sendVerifyCode 中，当 messageType=PHONE 时，按 serviceKey 与 businessId 的笛卡尔积调用 contractSignInfoProvider.setVerifyContractPhone(id, businessType, key, phone, companyId)。
impact: 合同签署记录保存验证码接收手机号，供后续签署校验
field_targets: []
evidence: code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplat
```

## 关联

[[concepts/验证码]] · [[calibers/签约验证码固定场景]] · [[rules/验证码接收渠道取值]]

---END FILE---

---REVIEW: rule | 签约验证码接收人手机号回写合同签署表---
语义分析给出的 evidence 字符串在中途被截断（"code_path:lowcode-pplatform-customer-management/src/main/java/com/lls/lowcode/pplat"），无法还原完整类路径与行号锚点。本页按"字段值逐字来源"的约束保留了截断原文，未自行补全。待语义分析重新给出完整 code_path 后需回填 evidence。
---END REVIEW---

---REVIEW: table | short_link / cust_message_send_policy / cust_setting_config---
三张表的物理库名在本次语义分析中未被证据覆盖：所有 DB 证据仅以 `db:<表名>` 形式给出，未出现库/实例名。frontmatter 的 scope.databases 因此暂记为 [unknown]，属占位而非推断。待补充分库信息（或确认这些表是否同库）后统一回填。
---END REVIEW---

---REVIEW: process | 短链类型路由---
状态机 transitions 中 NORMAL 与 FILE 两条迁移的 evidence 均指向 ShortLinkController.java#orderCategory，但 FILE 分支的实际执行点在语义分析的另一处证据中被描述为 #shortLink。两处方法锚点是否指同一段分支逻辑尚未确认，本页按原文保留 orderCategory，未做合并。
---END REVIEW---