---
type: process
title: 企业经办人状态
page_key: cust_person_info_status_state
domain: DBAss/SSO登录与通道
status: draft
aliases:
  - cust_person_info.status 状态机
oid: 1
scope:
  databases: [unknown]
sources:
  - code:SaaSAuthController.java:makePersonEffect
contract_version: "0.1"
belong: processes
---

企业经办人状态机，作用于 [[cust_person_info.status]]：字面量 ADD（新增待生效）→ EFFECT（生效），
由 SSO 登录初始化 / 切换企业触发。启用态联系人过滤见 [[enabled_person_contact]]。

## 需求背景

经办人新增后需在用户真实登录并确认企业上下文时才转为生效，避免未验证的经办人参与用户列表补全。

文档中“切换公司 = SaaSAuthController.changeCompany → SaaSAuthService.change(ChangeCompanyDTO) → SsoFacade 切换租户上下文并刷新缓存”
的链路与代码不符（refuted）：实际 changeCompany 调用 `saaSAuthService.getCompanyByUserAndCode(userId, companyId, companyType)`，
再改写 Cookie、`roleFacade.getAuthUrls` 并 `setReisUserInfo`，未见 change(ChangeCompanyDTO)/SsoFacade 切换。
该主张仅作业务叙述保留，不作为契约。

## 版本演进

- v0（草稿）：状态值来自代码字面量写值点；切换企业链路以代码为准。

```ground:process
name: 企业经办人状态
field: cust_person_info.status
states:
  - value: ADD
    label: 新增待生效
    source: code_const
  - value: EFFECT
    label: 生效
    source: code_const
transitions:
  - from: ADD
    event: SSO 登录初始化/切换企业（init / changeCompany）
    to: EFFECT
    evidence: "code_path:SaaSAuthController.java:makePersonEffect"
```

相关：[[cust_person_info]]、[[enabled_person_contact]]、[[login_init_cookie]]。