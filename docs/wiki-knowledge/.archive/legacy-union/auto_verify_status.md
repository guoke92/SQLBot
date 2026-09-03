---
oid: 1
scope:
  datasources:
  - 15
sources:
- knowledge-extraction:ca-certification@r1
status: published
contract_version: '0.1'
created: '2026-08-31'
updated: '2026-08-31'
type: enum
title: 自动核验状态
page_key: auto_verify_status
domain: CA认证与服务费
aliases:
- 人脸核验结果
- 认证通过
- 认证不通过
- 人工认证
anchors:
- auto_verify_status
---
# 自动核验状态

cust_certification_info.auto_verify_status 六值：TO_BE_VERIFIED 待核查 / AUTOMATIC_AUTHENTICATION_PASSED 自动通过 / AUTOMATIC_AUTHENTICATION_FAILED 自动不通过 / MANUAL_AUTHENTICATION_PASSED 人工通过 / MANUAL_AUTHENTICATION__FAILED 人工不通过（双下划线）/ NO_RECORD 库无记录。auto_verify_count 递减剩余核验次数。

```ground:enum
enum: auto_verify_status
fields:
- cust_certification_info.auto_verify_status
values:
  TO_BE_VERIFIED:
    label: 待核查
  AUTOMATIC_AUTHENTICATION_PASSED:
    label: 自动认证通过
  AUTOMATIC_AUTHENTICATION_FAILED:
    label: 自动认证不通过
  MANUAL_AUTHENTICATION_PASSED:
    label: 人工认证通过
  MANUAL_AUTHENTICATION__FAILED:
    label: 人工认证不通过
  NO_RECORD:
    label: 库无记录
```

## 关联
- [[cust_certification_info|cust_certification_info]]
