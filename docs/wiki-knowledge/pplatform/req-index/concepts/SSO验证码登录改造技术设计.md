---
title: SSO验证码登录改造技术设计.docx
source: desktop-reqdoc
---

# SSO验证码登录改造技术设计.docx

SSO验证码登录改造技术设计

1引言

1.1 文档目的

本文档旨在详细描述中燃系统的软件设计实现方案，为开发人员、测试人员和运维人员提供详细的技术实现指导。

1.2 项目背景

项目目标：

为规范登录操作，完善验证逻辑，防止恶意攻击，本期对登录交互进行调整。

核心功能：

登录注册等发送验证码场景 发送之前添加行为验证码校验

关联文档：

《产融需求规格说明书》

1.3 术语与定义

1.4 参考资料

【腾讯文档】【需求说明书】产融平台V1.24版本需求文档（1218）

产融平台V1.24版本需求文档（1218）

2. 总体设计概述

2.1 系统架构回顾

整体架构：采用分层架构设计，包含以下层次：

表现层（Presentation Layer）：负责用户交互和请求响应

业务逻辑层（Business Logic Layer）：实现核心业务逻辑

数据访问层（Data Access Layer）：负责数据持久化操作

基础设施层（Infrastructure Layer）：提供通用技术服务

功能模块划分：

2.2 设计范围与边界

本文档覆盖范围：

不包含内容：

第三方系统的内部实现

基础设施的部署配置

具体的测试用例设计

2.3 设计约束与原则

技术选型约束：

开发语言：Java 8+

框架：Spring Boot 2.x

数据库：MySQL 5.7+

缓存：Redis 6+

消息队列：RabbitMQ/

构建工具：Maven 3.6+

设计原则：

单一职责原则：每个类只负责一个功能领域

开闭原则：对扩展开放，对修改关闭

依赖倒置原则：依赖于抽象而不是具体实现

接口隔离原则：使用多个专门的接口

DRY原则：避免重复代码

安全性要求：

所有接口需要进行身份认证

敏感数据需要加密存储

操作日志需要完整记录

3. 模块详细设计

3.1. 需求说明

3.1.1. 功能需求

在SSO系统中新增行为验证码校验接口，支持以下功能：

1.行为验证码校验：提供独立的接口用于校验行为验证码（极验验证码）

2.缓存机制：校验成功后可将验证结果缓存到Redis，用于在登录时跳过重复校验

3.参数一致性校验：缓存中存储验证码参数，登录时校验参数是否一致

3.1.2. 业务场景

•场景1：前端先调用校验接口验证行为验证码，校验成功后缓存结果

•场景2：前端调用登录接口时，如果行为验证码校验失败，检查缓存中是否有之前校验通过的记录

•场景3：如果缓存中的参数与当前传入的参数一致，可以使用缓存跳过校验

3.2. 接口设计

3.2.1. 接口定义

接口路径：SsoCodeProvider.validateCaptcha

接口方法：

boolean validateCaptcha(String loginName, int second, String sysChannel,

String challenge, String validate, String seccode, boolean loginCaptcha，String imageSerialNo，String imgCode);

参数说明：

•loginName：登录名，必填

•second：缓存有效期（秒），必填

•sysChannel：系统渠道，必填

•challenge：行为验证码challenge参数，当行为验证码必填

•validate：行为验证码validate参数，当行为验证码必填

•seccode：行为验证码seccode参数，当行为验证码必填

•imageSerialNo 图片验证码参数

•imgCode 图片验证码参数

•loginCaptcha：是否缓存验证结果，true表示缓存，false表示不缓存

返回值：

•true：校验成功

•false：校验失败

3.3. 实现流程

3.3.1. 行为验证码校验流程

用户调用 validateBehaviorCaptcha 接口

↓

参数校验

├── loginName 为空 → 抛出异常

├── sysChannel 为空 → 抛出异常

└── challenge/validate/seccode 为空

├── 系统配置 captcha=0（不需要验证码）→ 直接返回 true

└── 系统配置 captcha=1（需要验证码）→ 抛出异常

↓

调用 ssoLoginProvider.secondValidate 校验行为验证码

↓

┌──────────────┬──────────────┐

│  校验成功     │  校验失败     │

│  返回 true    │  返回 false   │

└──────────────┴──────────────┘

↓ (校验成功)

loginCaptcha == true?

├── 是 → 缓存验证结果和参数到Redis

└── 否 → 不缓存

↓

返回 true

3.3.2. 缓存存储格式

缓存Key格式：

sso:behavior_captcha:{loginName}#{sysChannel}

缓存Value格式：

{challenge}|{validate}|{seccode}

示例：

•Key: sso:behavior_captcha:13800138000#sysChannel1

•Value: abc123|def456|ghi789

缓存有效期：由 second 参数指定（秒），转换为毫秒后存储

3.3.3. 登录时验证码校验流程

用户调用 doLogin 接口

↓

LoginCaptchaCk.checkCaptcha 方法

↓

检查是否传入了验证码参数

├── 图形验证码 → 校验图形验证码

└── 行为验证码参数

↓

先正常校验行为验证码

↓

┌──────────────┬──────────────┐

│  校验成功     │  校验失败     │

│  直接返回     │  检查缓存     │

│              │  ┌──────────┐

│              │  │ 用传入参数│

│              │  │ 拼接字符串│

│              │  │ 与缓存比较│

│              │  └──────────┘

│              │  ┌──────────┐

│              │  │ 一致     │

│              │  │ 删除缓存 │

│              │  │ 返回true │

│              │  └──────────┘

│              │  ┌──────────┐

│              │  │ 不一致   │

│              │  │ 抛出异常 │

│              │  └──────────┘

3.4. 核心代码实现

3.4.1. 接口实现（SsoCodeProviderImpl）

3.4.2. 缓存检查实现（SsoCacheUtil）

public boolean checkBehaviorCaptchaCache(String loginName, String sysChannel,

String challenge, String validate, String seccode) {

String redisKey = this.getBehaviorCaptchaCacheKey(loginName, sysChannel);

String cacheValue = (String) redisClient.get(redisKey);

if (StringUtils.isBlank(cacheValue)) {

return false;

}

// 如果传入了行为验证码参数，用传递的参数拼接后与Redis中的值比较

boolean hasParams = StringUtils.isNotBlank(challenge)

&& StringUtils.isNotBlank(validate)

&& StringUtils.isNotBlank(seccode);

if (hasParams) {

// 用传递的参数拼接，格式：challenge|validate|seccode

String paramValue = challenge + "|" + validate + "|" + seccode;

// 直接与Redis中的值进行字符串比较

if (paramValue.equals(cacheValue)) {

// 参数一致，验证通过后删除缓存，确保只能使用一次

redisClient.delete(redisKey);

return true;

} else {

// 参数不一致，返回false

return false;

}

}

return false;

}

3.4.3. 登录时验证码检查实现（LoginCaptchaCk）

public void checkCaptcha(SsoSystemDO ssoSystemDO, LoginForm loginForm, HttpServletRequest request) {

boolean hasImgCode = StringUtils.isNotBlank(loginForm.getImgCode());

boolean hasBehaviorCaptcha = StringUtils.isNotBlank(loginForm.getChallenge())

&& StringUtils.isNotBlank(loginForm.getValidate())

&& StringUtils.isNotBlank(loginForm.getSeccode());

// 校验图形验证码

if (hasImgCode) {

// 图形验证码校验逻辑

} else if (hasBehaviorCaptcha) {

// 先正常校验行为验证码

SecondValidateRequest secondValidate = new SecondValidateRequest();

secondValidate.setAppId(loginForm.getSysChannel());

secondValidate.setChallenge(loginForm.getChallenge());

secondValidate.setValidate(loginForm.getValidate());

secondValidate.setSeccode(loginForm.getSeccode());

SecondValidateResult validateResult = ssoLoginProvider.secondValidate(secondValidate);

// 如果校验不通过，再检查缓存

if (validateResult.getSuccess() != 1) {

String loginNameForCache = loginForm.getLoginName();

if (StringUtils.isNotBlank(loginNameForCache) && StringUtils.isNotBlank(loginForm.getSysChannel())) {

// 检查缓存中的参数是否一致

if (ssoCacheUtil.checkBehaviorCaptchaCache(loginNameForCache, loginForm.getSysChannel(),

loginForm.getChallenge(), loginForm.getValidate(), loginForm.getSeccode())) {

// 缓存中存在验证通过记录，且参数一致，使用缓存跳过校验

return;

}

}

// 缓存中没有或参数不一致，校验失败

throw new BaseException(SSOResultCodeEnum.ERROR_CODE_10929.getCode(),

SSOResultCodeEnum.ERROR_CODE_10929.getMessage());

}

// 校验通过，直接返回

} else if (ssoSystemDO.getCaptcha() == 1) {

throw new BaseException(SSOResultCodeEnum.ERROR_CODE_10930.getCode(),

SSOResultCodeEnum.ERROR_CODE_10930.getMessage());

}

}

3.5. 安全机制

3.5.1. 参数一致性校验

•缓存存储：校验成功时，将 challenge|validate|seccode 拼接后存储到Redis

•参数比对：登录时，用传入的参数拼接后与缓存中的值进行字符串比较

•安全保证：只有使用相同的验证码参数才能使用缓存，防止参数替换攻击

3.5.2. 一次性使用

•缓存删除：验证通过后立即删除缓存，确保只能使用一次

•防止重复使用：即使参数一致，缓存使用后也会被删除，不能重复使用

3.5.3. 系统配置检查

•灵活配置：根据系统配置的 captcha 字段判断是否需要验证码

•兼容处理：如果系统配置为不需要验证码（captcha=0），参数为空时直接返回true

3.6. 使用示例

3.6.1. 后端调用流程

1. 前端调用 validateBehaviorCaptcha 接口

├── 校验行为验证码

├── 校验成功且 loginCaptcha=true

└── 缓存验证结果：sso:behavior_captcha:13800138000#sysChannel1 = "abc123|def456|ghi789"

2. 前端调用 doLogin 接口

├── 先正常校验行为验证码

├── 如果校验失败

│   ├── 检查缓存：sso:behavior_captcha:13800138000#sysChannel1

│   ├── 用传入参数拼接："abc123|def456|ghi789"

│   ├── 与缓存值比较：一致

│   └── 删除缓存，使用缓存跳过校验

└── 如果校验成功，直接返回

3.6.2 产融改造

产融需要在调用sendPhoneCode之前调用行为验证码的接口去校验和加缓存

3.7. 配置说明

3.7.1. 常量配置

在 SSOConstants 中定义了缓存key前缀：

/**

* 行为验证码缓存key前缀

*/

String BEHAVIOR_CAPTCHA_CACHE_KEY_PREFIX = "sso:behavior_captcha:";

3.7.2. 系统配置

系统配置表 sso_system 中的 captcha 字段：

•0：可以不加验证码

•1：需要图片验证码或行为验证码

3.8. 注意事项

3.8.1. 缓存有效期

•缓存有效期由 second 参数指定（秒）

•建议设置为5-10分钟，避免缓存时间过长带来的安全风险

3.8.2. 参数一致性

•登录时必须使用与校验时相同的验证码参数

•参数不一致时，即使缓存存在也不能使用

3.8.3. 一次性使用

•缓存使用后立即删除，确保只能使用一次

•不能重复使用同一个缓存进行多次登录

3.8.4. 系统配置

•如果系统配置为不需要验证码（captcha=0），参数为空时直接返回true

•如果系统要求验证码（captcha=1），参数为空时抛出异常

9. 错误码说明

•ERROR_CODE_10929：行为验证码校验失败

•ERROR_CODE_10930：系统要求验证码但未传入

3.10. 测试建议

3.10.1. 功能测试

1.正常流程测试：

–调用校验接口，校验成功并缓存

–调用登录接口，使用缓存跳过校验

2.参数一致性测试：

–使用不同的验证码参数，验证不能使用缓存

3.一次性使用测试：

–使用缓存登录后，再次登录时缓存已删除

3.10.2. 安全测试

1.参数替换攻击：尝试使用不同的参数绕过校验

2.缓存重放攻击：尝试重复使用同一个缓存

系统配置测试：验证不同系统配置下的行为

项目运营配置

4.1 主要数据表

4.1.1 tenant_project (项目表)

•字段:

–op_contact_a - 运营对接人A

–op_contact_b - 运营对接人B

–verification_contact - 查验对接人

–risk_control_contact_a - 风控对接人A

–risk_control_contact_b - 风控对接人B

–solution_manager - 方案经理

–business_group - 关联业务部门

–custom_field_one - 自定义字段一

–custom_field_two - 自定义字段二

–custom_field_three - 自定义字段三

–project_tag - 项目标签

–bussiness_project_relation - 运营项目归属

3.1.2 cust_project_rel (项目企业关联表)

•字段:

–op_contact_a - 运营对接人A

–op_contact_b - 运营对接人B

–op_contact_a_group - 运营组别

–verification_contact - 查验对接人

–risk_control_contact_a - 风控对接人A

–risk_control_contact_b - 风控对接人B

4.2. 接口设计

4.1 项目信息导出接口

接口路径: POST /cust-web/project/export

请求参数:

{

"name": "项目名称（可选）",

"projectStatus": "项目状态（可选）",

"isPrd": "是否生产数据（可选）",

"channelCode": "项目专属服务码（可选）",

...

}

响应:

•成功: 返回Excel文件下载流

•失败: 返回错误信息

功能说明:

•导出两个Sheet：

–Sheet1: 项目运营配置 - 包含项目基本信息及可编辑字段

–Sheet2: 关联企业 - 包含项目关联的企业信息及可编辑字段

•支持按条件筛选项目

•自动关联查询企业信息

4.2 项目信息导入接口

接口路径: POST /cust-web/project/import

请求参数:

{

"files": [

{

"filePath": "文件路径"

}

]

}

响应:

{

"success": true/false,

"message": "导入成功" / "导入失败，请下载错误文件查看详情",

"data": "错误文件下载URL（如果有错误）"

}

功能说明:

•读取Excel文件的两个Sheet

•执行数据校验（项目存在性、企业存在性、唯一性、对接人存在性）

•所有校验通过后才执行更新操作

•如有错误，生成错误文件供下载

校验规则:

1.项目存在性校验: 项目ID不能为空，项目必须存在

2.企业存在性校验: 企业ID不能为空，企业必须存在

3.唯一性校验: 项目+企业组合必须唯一

4.对接人存在性校验: 对接人姓名必须在系统中存在（仅校验值不为空的字段）

更新逻辑:

•只更新值不为空且与数据库值不同的字段

•Sheet1更新项目表的指定字段

•Sheet2更新关联关系表（cust_project_rel）的指定字段

4.3 根据项目ID查询关联企业分页数据接口

接口路径: POST /cust-web/project/company/page

请求参数:

{

"current": 1,

"size": 10,

"queryCondition": {

"projectId": "项目ID"

}

}

响应:

{

"success": true,

"data": {

"current": 1,

"size": 10,

"total": 100,

"records": [

{

"companyId": 123,

"companyType": "核心企业",

"custBuildStatus": "已认证",

"opContactA": "张三",

"opContactB": "李四",

"opContactAGroup": "运营一组",

"verificationContact": "王五",

"verificationContactGroup": "查验一组",

"riskControlContactA": "赵六",

"riskControlContactB": "钱七",

"riskControlContactAGroup": "风控一组",

"createTime": "2024-01-01 10:00:00",

"updateUser": "管理员",

"updateTime": "2024-01-02 15:30:00"

}

]

}

}

功能说明:

•根据项目ID（流程申请编号）查询关联企业

•支持分页查询

•返回字段从 cust_project_rel 表获取（对接人、组别等）

4.3 外部接口对接

4.3.1 运营中台接口

4.4 测试建议

项目关联关系关联上就需要绑定默认的关联关系？

术语/缩写 | 定义 | 说明

API | Application Programming Interface | 应用程序编程接口

DTO | Data Transfer Object | 数据传输对象

VO | Value Object | 值对象

DAO | Data Access Object | 数据访问对象

AOP | Aspect Oriented Programming | 面向切面编程

IOC | Inversion of Control | 控制反转

MQ | Message Queue | 消息队列
