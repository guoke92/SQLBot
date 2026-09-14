---
type: process
title: 企业 CA 注册状态（cust_company_info.ca_register_status）
page_key: ca_register_status
domain: CA证书认证
status: draft
aliases: [ca_register_status, CA注册状态, 证书注册状态]
oid: 1
scope:
  databases: [unknown]
sources:
  - code:CaActivationApplication.java
  - code:CaCertificationConfirmApplication.java
  - code:CaCertificationPreCheckApplication.java
  - code:CaOpenCaApplication.java
  - db:cust_company_info
contract_version: "0.1"
belong: processes
---

企业侧的 CA 注册生命周期位：Y=已注册、N=未注册、P=处理中。它与上送状态 [[ca_submit_status]] 是两件事：本状态描述企业在签章中台的登记/证书有效性，上送状态只描述一条 ca_certification_info 行是否已成功推送给中台。中台证书态到本状态的归一由 [[sign_center_cert_status]] 负责。

## 需求背景

注册成功（custDocFacade.openCa / cbsCompanyRegister）后回写 Y；预检发现证书 CANCELLED/EXPIRED/FAIL 或中台登记企业名与库中不一致时，resetCaRegisterStatusToN 把 Y 回写为 N，从而让企业在下一轮 [[need_register_ca_judgement|需开通 CFCA 判定口径]] 中被重新判定为需开通。需要注意 CaOpenCaApplication.isOpenCa 中还有一条"仅内存视为未开通"的路径（caEval.isInvalid()），不落库，因此库里仍是 Y。

## 版本演进

- v0：首次固化三态与回写规则。存量企业打包口径 [[legacy_package_companies]] 以 ca_register_status='Y' 为筛选起点。

```ground:process
name: 企业 CA 注册状态
field: cust_company_info.ca_register_status
states:
  - value: Y
    label: 已注册
    source: code_enum
  - value: N
    label: 未注册
    source: code_enum
  - value: P
    label: 处理中
    source: code_enum
transitions:
  - from: N
    event: "custDocFacade.openCa / cbsCompanyRegister 注册成功"
    to: Y
    evidence: "code_path:CaActivationApplication.java#activateByOpCompanyId（第 5 步注释）；CaCertificationConfirmApplication.java#confirm"
  - from: P
    event: "注册成功回写"
    to: Y
    evidence: "code_path:CaCertificationConfirmApplication.java#confirm（读取 caRegisterStatus）"
  - from: Y
    event: "pre4Step 预检发现证书 CANCELLED/EXPIRED/FAIL 或中台登记企业名与库中不一致"
    to: N
    evidence: "code_path:CaCertificationPreCheckApplication.java#resetCaRegisterStatusToN"
  - from: Y
    event: "caEval.isInvalid() 时局部视为未开通（仅内存，不落库）"
    to: N
    evidence: "code_path:CaOpenCaApplication.java#isOpenCa"
```

关联页面：[[cust_company_info]]、[[ca_submit_status]]、[[sign_center_cert_status]]、[[cert_status]]、[[ca_certificate]]、[[need_register_ca_judgement]]。