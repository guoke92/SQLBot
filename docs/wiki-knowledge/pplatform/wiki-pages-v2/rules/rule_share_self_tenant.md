---
type: rule
title: 自营假租户共享落表
page_key: rule_share_self_tenant
domain: 租户配置/灰度/运营邮件
status: draft
aliases: [existEarlyLLsTenant, doSaveTenantShare, 自营假租户, 共享租户]
oid: 1
scope:
  databases: [unknown]
sources:
  - "code_path:TenantDomainService.java:existEarlyLLsTenant / doSaveTenantShare"
contract_version: "0.1"
belong: rules
---

当同一 dbTenantCode 已存在主记录、但本次落库的 tenant_flg_en 与之不同、且既有记录 share_flag='Y' 时，判定为「自营假租户」：不新增 [[tenant_setting_config]] 主表记录，而是把 name / bandName / tenantFlgEn 写入 tenant_setting_config_share，并只在 share 表内做唯一校验，最后返回既有租户 id。

这条规则解释了为什么同一 db_tenant_code 下可以有多个 tenant_flg_en（见 [[tenant_flg_en]]），也决定了 share_flag 的语义：它是「允许挂多个项目标识」的开关。

## 需求背景
XYC 自营租户需要在一个数据租户下挂多个项目标识，但又不允许污染租户主配置（生效状态、灰度、运营邮件等应以主记录为准），因此把额外的项目标识下沉到共享表。

## 版本演进
v0.1（本页）：首版契约，锚点证据来自语义分析；共享表 tenant_setting_config_share 的字段清单未采集（见 REVIEW）。

```ground:rule
name: 自营假租户共享落表
content: "同 dbTenantCode 已存在主记录、且 tenant_flg_en 不同、且既有记录 share_flag='Y' 时判定为自营假租户：不新增主表，改写入 tenant_setting_config_share（仅对 name/bandName/tenantFlgEn 做 share 表内唯一校验），返回既有租户 id"
impact: "XYC 自营租户下可挂多个项目标识"
field_targets:
  - tenant_setting_config.db_tenant_code
  - tenant_setting_config.share_flag
  - tenant_setting_config_share.tenant_flg_en
evidence: "code_path:TenantDomainService.java:existEarlyLLsTenant / doSaveTenantShare"
```