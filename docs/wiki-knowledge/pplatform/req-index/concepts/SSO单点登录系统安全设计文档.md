---
title: SSO单点登录系统安全设计文档.docx
source: desktop-reqdoc
---

# SSO单点登录系统安全设计文档.docx

SSO单点登录系统安全设计文档

文档说明

本文档详细说明SSO单点登录系统在身份鉴别信息强度和安全要求、异常登录行为处理及超时机制等方面的设计实现，确保系统满足相关安全标准和合规要求，为安全审计和系统评审提供依据。

一、身份鉴别信息强度和安全要求

1.1. 密码长度不小于八位且必须包含大小写字母、符号和数字中两种以上

1.1.2. 系统实现方案

1. 密码强度验证机制

系统通过 PasswordUtils 类实现密码强度验证，支持多级密码强度策略配置。密码强度验证在用户注册、密码修改等关键操作时强制执行。

2. 密码强度等级定义

系统支持4个密码强度等级，其中等级2、等级3和等级4均满足要求：

•强度等级2（满足要求）：

–密码长度：8-15位

–必须包含：大写字母、小写字母、数字

–正则表达式：(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[_a-zA-Z0-9\\W]{8,15}

–字符类型：包含大小写字母和数字，共2种以上字符类型

•强度等级3（满足要求）：

–密码长度：8-15位

–必须包含：大写字母、小写字母、数字、特殊字符

–正则表达式：(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*(_|\\W))[_a-zA-Z0-9\\W]{8,15}

–字符类型：包含大小写字母、数字和特殊字符，共3种以上字符类型

•强度等级4（超标准要求）：

–密码长度：8-32位

–必须包含：大写字母、小写字母、数字、特殊字符

–正则表达式：(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*(_|\\W))[_a-zA-Z0-9\\W]{8,32}

–字符类型：包含大小写字母、数字和特殊字符，共3种以上字符类型

3. 验证流程

1.用户在注册或修改密码时，前端提交新密码

2.后端调用 PasswordUtils.matchesPassword(pwdStrong, password) 方法进行验证

3.根据系统配置的密码强度等级（pwdStrong字段）进行相应验证

4.验证失败时返回对应的错误码：

–ERROR_CODE_10918：密码强度不符合要求（等级2）

–ERROR_CODE_10919：密码强度不符合要求（等级3）

–ERROR_CODE_10927：密码强度不符合要求（等级4）

5.验证通过后方可保存密码

4. 关键代码实现

// 密码强度验证核心代码

public static SSOResultDTO<String> matchesPassword(Integer pwdStrong, String password) {

if(pwdStrong == 2) {

if(!matchesFor2(password)) {

return new SSOResultDTO<String>(SSOResultCodeEnum.ERROR_CODE_10918);

}

}else if(pwdStrong == 3) {

if(!matchesFor3(password)) {

return new SSOResultDTO<String>(SSOResultCodeEnum.ERROR_CODE_10919);

}

}else if(pwdStrong == 4) {

if(!matchesFor4(password)) {

return new SSOResultDTO<String>(SSOResultCodeEnum.ERROR_CODE_10927);

}

}

return null;

}

// 强度等级2验证：必须包含大小写字母和数字

public static boolean matchesFor2(String password) {

if (StringUtils.isEmpty(password)) {

return false;

}

String regex = "(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])[_a-zA-Z0-9\\W]{8,15}";

return password.matches(regex);

}

// 强度等级3验证：必须包含大小写字母、数字和特殊字符

public static boolean matchesFor3(String password) {

if (StringUtils.isEmpty(password)) {

return false;

}

String regex = "(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*(_|\\W))[_a-zA-Z0-9\\W]{8,15}";

return password.matches(regex);

}

5. 配置说明

•系统支持按业务系统（sysChannel）配置不同的密码强度要求

6. 验证场景

•用户注册：新用户注册时强制验证密码强度

•密码修改：用户修改密码时强制验证新密码强度

•管理员重置密码：管理员重置用户密码时强制验证密码强度

1.2. 对用户密码进行混淆后进行加密存储，RSA密钥长度不小于2048位或采用国密算法

1.2.2. 系统实现方案

1. 密码传输加密（RSA/国密算法）

RSA加密传输：

•前端使用RSA公钥对密码进行加密传输

•系统支持RSA-2048及以上密钥长度

•密钥对系统实时生成，每次请求更新

•后端使用对应私钥进行解密

2. 密码存储加密（BCrypt算法）

系统采用 BCrypt 算法对密码进行加密存储，BCrypt是一种基于Blowfish密码算法的自适应哈希函数，具有以下特性：

•随机盐值：每次加密都会生成随机盐值（Salt），确保相同密码加密后结果不同

•抗彩虹表攻击：BCrypt算法具有抗彩虹表攻击能力

•可配置强度：支持可配置的加密强度（log rounds，默认10轮）

•不可逆加密：密码以哈希值形式存储，无法逆向还原

3. 加密实现流程

传输加密流程：

到达登录页面，后端生成的秘钥对，公钥给前端

↓

用户输入密码

↓

前端使用RSA公钥加密

↓

传输加密后的密码到后端

↓

后端使用RSA私钥解密

↓

获得明文密码用于验证

存储加密流程：

明文密码

↓

BCryptPasswordEncoder.encode()

↓

生成随机盐值（Salt）

↓

使用BCrypt算法加密

↓

存储BCrypt哈希值到数据库

4. RSA密钥配置

•密钥长度：系统支持RSA-2048及以上密钥长度

•密钥管理：公钥和私钥实时生成，后端保存

•密钥轮换：支持密钥定期轮换和版本管理

5. 密码混淆机制

系统在密码存储前进行以下处理，实现密码混淆：

•BCrypt哈希：使用BCrypt算法对密码进行哈希，每次加密使用不同的随机盐值

•不可逆存储：密码以哈希值形式存储，无法通过哈希值还原原始密码

•盐值随机化：每次加密生成不同的盐值，相同密码加密后结果不同

6. 截图

RSA密钥长度：系统支持RSA-2048及以上密钥长度，满足合规要求

传输加密：前端使用RSA公钥或国密算法对密码进行加密传输，后端使用对应私钥解密

1.3. 用户信息及用户身份鉴别信息分离存储

1.3.2. 系统实现方案

1. 数据表分离设计

系统目前用户信息和历史密码做分离管理：

（1）用户基本信息表（sso_user）

•存储用户基本信息：sso_id、login_name、user_name、phone、email等

•存储加密后的密码：password字段（BCrypt哈希值）

•存储密码相关元数据：pwd_update_time、pwd_is_locked、pwd_locked_time、login_fail_count等

（2）密码历史表（sso_user_pwd_history）

•独立存储用户密码历史记录

•字段包括：id、sso_id、password（历史密码哈希值）、sys_channel、create_time等

•用于防止用户重复使用近期密码

•与用户基本信息表通过sso_id关联

（3）用户系统关联表（sso_user_system）

•存储用户与业务系统的关联关系

•独立存储各系统的原密码（如需要）：password字段

•字段包括：id、sso_id、user_sys_channel、password、user_status等

•与用户基本信息表通过sso_id关联

2. 物理分离策略

•独立数据表：用户基本信息、密码历史、系统关联信息分别存储在不同的数据表中

•独立存储空间：不同表的数据存储在独立的存储空间中，降低数据泄露风险

•访问权限分离：不同表可以配置不同的访问权限，密码相关表访问权限更严格

3. 逻辑分离策略

•密码字段隔离：密码字段仅在必要时进行查询和更新，不暴露在通用查询接口中

•密码验证独立：密码验证通过专门的Service层方法处理，不与其他业务逻辑混合

•密码历史独立管理：密码历史记录通过独立的Service进行管理，与用户基本信息管理分离

4. 访问控制策略

•接口分离：密码相关操作通过专门的Provider接口进行，不与其他用户信息操作混合

•字段隐藏：密码字段不直接暴露在通用查询接口中，仅在密码验证和修改时使用

•操作审计：密码更新操作记录操作历史，与用户基本信息更新操作分离记录

5. 数据关联关系

sso_user (用户基本信息表)

├── sso_id (主键)

├── login_name

├── user_name

├── phone

├── email

└── password (加密后的密码)

sso_user_pwd_history (密码历史表)

├── id (主键)

├── sso_id (外键 -> sso_user.sso_id)

├── password (历史密码哈希值)

└── sys_channel

sso_user_system (用户系统关联表)

├── id (主键)

├── sso_id (外键 -> sso_user.sso_id)

├── user_sys_channel

└── password (系统原密码，如需要)

6. 安全优势

•降低泄露风险：即使用户信息表被访问，密码历史信息仍独立保护

•便于审计：密码历史独立存储，便于追溯和审计

•灵活扩展：可根据需要扩展密码相关字段，不影响用户基本信息表结构

•权限控制：可以对密码相关表设置更严格的访问权限

7. 截图

1.4. 要求用户定期修改身份鉴别信息

1.4.2. 系统实现方案

1. 密码过期策略配置

系统支持按业务系统配置密码有效期和提醒机制：

•pwdUpdateDays：密码有效期（天数），系统级配置，0表示不强制

•pwdUpdateRemind：密码过期提醒天数，提前提醒用户更换密码

•pwdUpdateTime：用户密码最后更新时间，存储在用户表中

2. 密码过期检查机制

系统在用户登录时自动检查密码是否过期：

检查逻辑：

•密码已过期：pwdUpdateTime + pwdUpdateDays <= 当前日期 时，密码已过期

•密码即将过期：pwdUpdateTime + pwdUpdateDays - pwdUpdateRemind <= 当前日期 时，密码即将过期

•密码正常：pwdUpdateTime + pwdUpdateDays > 当前日期 时，密码正常

3. 密码过期处理流程

用户登录

↓

验证密码正确性

↓

检查密码是否过期

↓

┌─────────────────┬─────────────────┬──────────┐

│  密码已过期      │  密码即将过期    │  密码正常 │

│  强制修改密码    │  提示用户修改    │  允许登录 │

│  返回30903      │  返回20904       │          │

│  不允许登录     │  允许登录但提醒  │          │

└─────────────────┴─────────────────┴──────────┘

4. 密码过期强制修改

当密码已过期时：

•系统返回错误码30903："密码已过期，请修改密码"

•不允许用户登录，强制用户修改密码

•记录密码过期日志

5. 密码过期提醒

当密码即将过期时：

•系统返回错误码20904："密码即将过期，提醒用户修改"

•允许用户登录，但提示用户密码即将过期

•提醒信息包含密码过期日期

6. 密码更新记录

用户修改密码时：

•系统记录pwdUpdateTime为当前时间

•同时将旧密码保存到密码历史表（sso_user_pwd_history）

•更新用户表的密码字段和更新时间

•重置密码过期状态

7. 关键代码实现

// 密码过期检查

Integer pwdUpdateDays = ssoSystemDO.getPwdUpdateDays();

if (pwdUpdateDays > 0 && null != ssoUserDO.getPwdUpdateTime()) {

LocalDate plusDays = ssoUserDO.getPwdUpdateTime().plusDays(pwdUpdateDays).toLocalDate();

long days = ChronoUnit.DAYS.between(LocalDate.now(), plusDays);

if (days <= 0) {

// 密码已过期，强制修改

history.setOperatorResult(0);

history.setRemark(history.getRemark() + "-" + SSOResultCodeEnum.SWITCH_CODE_30903.getMessage());

ssoUserLoginHistoryService.saveOrUpdate(history);

return new SSOResultDTO<>(SSOResultCodeEnum.SWITCH_CODE_30903);

} else if (days <= ssoSystemDO.getPwdUpdateRemind()) {

// 密码即将过期，提醒用户

SSOResultDTO<String> result = new SSOResultDTO<>(SSOResultCodeEnum.CORRECT_CODE_20904);

result.setMessage(String.format(result.getMessage(), plusDays));

return result;

}

}

8. 配置示例

二、异常登录行为处理及超时机制

2.1. 系统可对异常登录进行日志记录

2.1.2. 系统实现方案

1. 登录日志表设计

系统设计了专门的登录历史表（sso_user_login_history）用于记录所有登录操作：

主要字段：

•id：主键

•sso_id：用户ID，关联用户表

•login_name：登录名

•sys_channel：业务系统编号

•login_ip：登录IP地址

•login_type：登录类型（登录/登出）

•operator_result：操作结果（0-失败，1-成功）

•remark：备注信息（详细描述登录结果）

•create_time：操作时间

2. 日志记录场景

系统对以下场景进行完整的日志记录：

（1）登录成功

•记录用户ID、登录名、系统编号、登录IP、登录时间

•operator_result = 1

•remark = "SSO密码 登陆成功" 或相应成功描述

（2）登录失败

•记录登录名、系统编号、登录IP、失败时间

•operator_result = 0

•remark = "SSO密码 登陆失败" 或具体失败原因：

–"登陆用户不存在"

–"用户未开通此系统"

–"密码错误"

–"账户已被锁定"

–"密码已过期，需要修改密码"

（3）账户锁定

•记录锁定原因、锁定时间

•operator_result = 0

•remark = "账户已被锁定，剩余锁定时间X分钟"

（4）密码过期

•记录密码过期信息

•operator_result = 0

•remark = "密码已过期，需要修改密码"

（5）登出操作

•login_type = "登出"

•operator_result = 1

•remark = "登出成功"

3. 日志记录实现

// 创建登录历史记录

SsoUserLoginHistoryDO history = SsoUserLoginHistoryDO.builder()

.loginType("登录")

.loginName(loginName)

.sysChannel(sysChannel)

.loginIp(NetworkUtil.getIp(request))

.ssoId(ssoUserDO.getSsoId())

.operatorResult(1) // 0-失败，1-成功

.remark("SSO密码 登陆成功")

.build();

// 保存日志

ssoUserLoginHistoryService.saveOrUpdate(history);

4. 异常登录识别

系统通过以下方式识别异常登录行为：

•登录失败记录：记录所有登录失败的尝试，包括失败原因

•IP地址记录：记录每次登录的IP地址，用于识别异常IP访问

•时间记录：记录登录时间，用于识别异常时段登录

•设备信息记录：记录用户代理（UA）信息，用于识别异常设备访问

5. 日志查询与分析

•日志查询接口：系统提供日志查询接口，支持按用户、时间、IP、操作结果等条件查询

•异常行为分析：支持异常登录行为分析和统计

•审计功能：所有关键操作均记录审计日志，支持回溯与审计

6. 截图

2.2. 系统有登录超时自动退出机制且超时时间不大于30分钟

2.2.2. 系统实现方案

1. 会话管理机制

系统使用Redis存储用户会话信息，实现分布式会话管理：

•会话存储：使用Redis存储用户会话信息

•会话Key格式：sso:session:{sessionId}

•会话信息：包括用户ID、登录名、系统编号、登录时间、过期时间等

•会话过期：支持可配置的会话过期时间，默认30分钟

2. 超时配置

系统支持灵活的超时时间配置：

•系统级配置：按业务系统（sysChannel）配置不同的超时时间

•用户级配置：支持按用户（loginName）配置个性化超时时间

•默认超时时间：30分钟（可配置）

•配置优先级：用户级配置 > 系统级配置 > 默认配置

3. 超时检查机制

用户每次访问系统时，系统自动检查会话是否过期：

检查流程：

用户访问系统

↓

检查Cookie中的sessionId

↓

从Redis获取会话信息

↓

┌──────────────────┬──────────────────┐

│  会话不存在      │  会话存在        │

│  返回未登录      │  检查是否超时    │

│  错误码10900     │                  │

└──────────────────┴──────────────────┘

↓

┌───────────┴───────────┐

│  已超时               │  未超时

│  清除会话             │  检查是否需要续期

│  返回未登录           │  ┌──────────────┐

│                       │  │ 需要续期     │

│                       │  │ 更新过期时间 │

│                       │  └──────────────┘

│                       │  允许访问

4. 自动续期机制

当用户操作时间超过登录有效时间的一半时，自动续期：

•续期条件：当前时间 - 最后刷新时间 > 超时时间/2 时，更新会话过期时间

•续期操作：续期后重新设置Redis过期时间和Cookie过期时间

•用户体验：自动续期机制提升用户体验，同时保证安全性

5. 会话失效处理

会话失效后：

•清除Redis中的会话信息

•返回未登录错误码10900

•要求用户重新登录

6. Cookie设置

•系统通过Cookie存储sessionId

•Cookie过期时间与Redis会话过期时间保持一致

•支持"记住我"功能，可设置更长的过期时间（但不超过系统配置的最大值）

7. 关键代码实现

// 会话超时检查

SsoUser ssoUser = ssoCacheUtil.getCacheSsoUser(cookieName, ssoIdKey);

if (ssoUser != null && version.equals(ssoUser.getVersion())) {

// 检查是否需要续期

if (System.currentTimeMillis() - ssoUser.getExpireFreshTime() > ssoUser.getExpireMinite() * 10000) {

// 更新缓存，续期

ssoUser.setExpireFreshTime(System.currentTimeMillis());

loginUtils.putLoginStore(ssoIdKey, ssoUser,

loginUtils.getRedisExpireMinute(ssoUser.getSysChannel(), ssoUser.getLoginName()));

}

// 允许访问

} else {

// 会话不存在或已过期，返回未登录

return new SSOResultDTO<>(SSOResultCodeEnum.ERROR_CODE_10900);

}

8. 配置示例

# Nacos配置

sso.cookie.expire.minute.sysChannel1 = 30  # 系统1超时30分钟

sso.cookie.expire.minute.sysChannel2 = 20  # 系统2超时20分钟

sso.cookie.expire.minute.user001 = 15       # 用户user001超时15分钟

2.3. 系统可限制非法登录次数

2.3.2. 系统实现方案

1. 登录失败计数机制

系统设计了完整的登录失败计数和账户锁定机制：

失败计数字段：

•loginFailCount：用户登录失败次数（存储在sso_user表）

•loginFailLockedCount：系统配置的最大失败次数（存储在sso_system表）

•pwdLockedMinute：账户锁定时长（分钟，存储在sso_system表）

2. 失败计数流程

用户登录

↓

验证密码

↓

┌──────────────┬──────────────┐

│  密码正确     │  密码错误     │

│  重置失败计数 │  失败计数+1   │

│  允许登录     │  检查是否达到锁定阈值

│               │  ┌──────────────┐

│               │  │ 达到阈值     │

│               │  │ 锁定账户     │

│               │  │ 设置锁定时间 │

│               │  └──────────────┘

│               │  返回登录失败

3. 账户锁定机制

当用户登录失败次数达到系统配置的最大失败次数（loginFailLockedCount）时：

•锁定账户：设置账户锁定标志 pwdIsLocked = true

•设置锁定时间：pwdLockedTime = 当前时间 + pwdLockedMinute

•记录锁定日志：记录账户锁定操作日志

4. 锁定检查机制

用户再次登录时，系统首先检查账户是否被锁定：

•检查逻辑：当前时间 <= pwdLockedTime 时，账户处于锁定状态

•锁定期间：即使用户密码正确，也不允许登录

•返回信息：返回锁定错误信息，提示剩余锁定时间

5. 自动解锁机制

锁定时间到期后，账户自动解锁：

•解锁逻辑：当前时间 > pwdLockedTime 时，清除锁定状态

•解锁操作：解锁时重置失败计数 loginFailCount = 0

•解锁时间：锁定时间到期后自动解锁，无需人工干预

6. 关键代码实现

// 登录失败处理

if (!matches) {

// 失败计数+1

ssoUserDO.setLoginFailCount(ssoUserDO.getLoginFailCount() + 1);

// 检查是否达到锁定阈值

if (ssoUserDO.getLoginFailCount() >= ssoSystemDO.getLoginFailLockedCount()) {

// 锁定账户

ssoUserDO.setPwdLockedTime(

LocalDateTime.now().plusMinutes(ssoSystemDO.getPwdLockedMinute())

);

ssoUserDO.setPwdIsLocked(true);

}

// 记录失败日志

history.setOperatorResult(0);

history.setRemark("SSO密码 登陆失败");

ssoUserLoginHistoryService.saveOrUpdate(history);

}

// 账户锁定检查

LocalDateTime pwdLockedTime = ssoUserDO.getPwdLockedTime();

if (null != pwdLockedTime) {

if (LocalDateTime.now().compareTo(pwdLockedTime) <= 0) {

// 账户仍被锁定

SSOResultDTO<String> result = new SSOResultDTO<>(SSOResultCodeEnum.CORRECT_CODE_20903);

result.setMessage(String.format(result.getMessage(),

ssoUserDO.getLoginFailCount(), ssoSystemDO.getPwdLockedMinute()));

return result;

} else if (ssoUserDO.getPwdIsLocked() && LocalDateTime.now().compareTo(pwdLockedTime) > 0) {

// 锁定时间已过，自动解锁

ssoUserDO.setLoginFailCount(0);

ssoUserDO.setPwdLockedTime(LocalDateTime.now());

ssoUserDO.setPwdIsLocked(false);

}

}

7. 配置示例

# 系统配置（SsoSystemDO）

loginFailLockedCount = 5      # 连续失败5次锁定

pwdLockedMinute = 30          # 锁定30分钟

8. 安全特性

•防止暴力破解：限制登录尝试次数，增加攻击成本

•自动解锁：锁定时间到期后自动解锁，减少管理员干预

•失败计数持久化：失败次数存储在数据库，防止重启后计数丢失

•可配置策略：不同业务系统可配置不同的锁定策略

9. 截图
