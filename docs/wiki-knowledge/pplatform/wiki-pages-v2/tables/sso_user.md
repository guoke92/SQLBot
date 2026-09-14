---
type: table
title: sso_user 单点登录用户表
page_key: sso_user
domain: 平台内部服务对接
status: draft
aliases:
  - SSO用户表
  - 单点登录用户映射
oid: 1
scope:
  databases:
    - lowcode_pplatform
sources:
  - code
contract_version: "0.1"
belong: tables
---

sso_user 保存单点登录侧的账号映射：`sso_id` 为 SSO 用户标识，`login_name`、`user_name` 为登录名与用户名，`sys_channel` 记录系统渠道。内部服务在接入 SSO 时需要把平台账号与外部登录身份对应起来，本表是这一映射的落点；租户侧的 SSO 渠道配置见 [[tenant_setting_config]] 的 `sso_tenant_chanel`。

## 需求背景
平台按租户提供不同渠道的登录入口，登录侧服务需要按渠道解析 SSO 身份并映射为平台用户，因此渠道（`sys_channel`）与租户渠道配置需要保持一致。

## 版本演进
- v0.1（本页）：字段清单来自代码语义分析，字段物理类型与字典绑定尚未在证据中出现，暂留空。

