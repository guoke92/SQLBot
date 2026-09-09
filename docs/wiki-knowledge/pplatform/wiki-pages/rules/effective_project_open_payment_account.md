---
type: rule
title: "生效后开通交e保账户"
page_key: effective_project_open_payment_account
belong: rules
domain: "tenant-project"
status: published
aliases: ["交e保开户"]
oid: 1
sources:
  - "semantic_analysis"
contract_version: "0.1"
field_targets: [tenant_project.platform_product_code]
scope:
  databases: [lowcode_pplatform]
---

项目生效后，ACFLOW/RVSFACTOR 产品会触发 bocomFactory.openPaymentBocomAccount(projectId) 开户。

## 需求背景
规则来源于 TenantProjectApplication.effective 方法，定义特定平台产品的开户触发逻辑。

## 版本演进
v0.1 版本基于代码路径证据建立，后续需补充需求文档表述。

```ground:rule
name: "生效后开通交e保账户"
content: "项目生效后，ACFLOW/RVSFACTOR 产品会触发 bocomFactory.openPaymentBocomAccount(projectId) 开户"
impact: "产生交e保开户异步/同步操作"
field_targets:
  - "tenant_project.platform_product_code"
evidence: "code_path:TenantProjectApplication.java:effective"
```

相关：[[tenant_project]] [[tenant_project_lifecycle]]