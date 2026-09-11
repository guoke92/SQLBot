---
type: entity
title: cust_project_rel表
created: 2026-08-28
updated: 2026-08-28
tags: [数据库, 项目管理, 企业关联]
related: [tenant_project表]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# cust_project_rel表

`cust_project_rel` 是项目企业关联表，用于存储项目与企业之间的关联关系及对应的运营对接人信息。该表在SSO验证码登录改造技术设计文档的附录部分（第4节）被提及，与核心的验证码功能关联较弱。

## 主要字段

- `op_contact_a`：运营对接人A
- `op_contact_b`：运营对接人B
- `op_contact_a_group`：运营组别
- `verification_contact`：查验对接人
- `risk_control_contact_a`：风控对接人A
- `risk_control_contact_b`：风控对接人B

## 相关接口

文档中描述了基于此表的项目关联企业分页查询接口，以及项目信息导入时对此表的更新逻辑。