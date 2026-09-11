---
type: rule
title: 存量打包查询规则
page_key: rule/legacy_package_query
domain: CA证书认证
status: draft
aliases: [queryEligibleCompanies 规则]
oid: 1
scope:
  databases: [unknown]
sources: ["code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"]
contract_version: "0.1"
---

规则要求：查询 enable='Y'、ca_register_status='Y'、update_time>=since、identify_style!=SIMPLE 的企业，可选租户过滤。影响是确定存量 CA 数据打包的企业范围。

四个条件中，ca_register_status='Y' 表示只打包企业侧自认为已开通的证书，而 update_time 窗口使任务可以增量重跑。可选租户过滤意味着同一套查询可在多租户部署下复用。该查询对应的正式口径描述见 [[calibers/legacy_package_company_scope]]，打包内容对应一证四步（[[concepts/one_cert_four_steps]]）。

## 需求背景

语义分析中 reqdoc_claims 为空，暂无可引用的需求文档主张。四个筛选条件与可选租户过滤来自代码路径证据。

## 版本演进

暂无文档化的版本演进证据。由于 ca_register_status 会被失效回写置 N（[[rules/ca_invalidate_writeback]]），打包范围会随证书状态变化而收缩。

```ground:rule
name: 存量打包查询规则
content: 查询enable=Y、ca_register_status=Y、update_time>=since、identify_style!=SIMPLE的企业，可选租户过滤。
impact: 确定存量CA数据打包的企业范围
field_targets:
  - cust_company_info.enable
  - cust_company_info.ca_register_status
  - cust_company_info.update_time
  - cust_company_info.identify_style
evidence: "code_path:CfcaOneCertFourStepPackageApplication.java:queryEligibleCompanies"
```

相关页面：[[calibers/legacy_package_company_scope]]、[[rules/ca_invalidate_writeback]]、[[rules/simple_auth_force_no_ca]]。