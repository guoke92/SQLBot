---
type: entity
title: tenant_project表
created: 2026-08-28
updated: 2026-08-28
tags: [数据库, 项目管理, 运营配置]
related: [cust_project_rel表]
sources: ["需求文档/SSO验证码登录改造技术设计.docx"]
---
# tenant_project表

`tenant_project` 是项目运营配置相关的数据表，用于存储项目的基本信息及运营对接人等配置。该表在SSO验证码登录改造技术设计文档的附录部分（第4节）被提及，与核心的验证码功能关联较弱。

## 主要字段

- `op_contact_a`：运营对接人A
- `op_contact_b`：运营对接人B
- `verification_contact`：查验对接人
- `risk_control_contact_a`：风控对接人A
- `risk_control_contact_b`：风控对接人B
- `solution_manager`：方案经理
- `business_group`：关联业务部门
- `custom_field_one/two/three`：自定义字段
- `project_tag`：项目标签
- `bussiness_project_relation`：运营项目归属

## 相关接口

文档中描述了基于此表的项目信息导出、导入和分页查询接口。