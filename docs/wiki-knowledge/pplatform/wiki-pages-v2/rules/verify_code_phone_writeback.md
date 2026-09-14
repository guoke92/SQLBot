---
type: rule
title: 短信验证码手机号回填合同签署表
page_key: verify_code_phone_writeback
domain: notification
status: draft
aliases: [setVerifyContractPhone, 验证码接收人落库]
oid: 1
scope:
  databases: []
sources:
  - CustVerifyCodeApplication.java:sendVerifyCode
contract_version: "0.1"
belong: rules
---

当消息类型为 PHONE 时，CustVerifyCodeApplication 将接收手机号通过 contractSignInfoProvider.setVerifyContractPhone 写入合同签署信息，使验证码接收人可追溯。该调用为 RPC 提供方关系，目标表名未在代码中直接出现（推测为合同签署表），关系判定为 derived。

## 需求背景
签署类验证码需要留痕，需求侧要求记录验证码接收手机号，便于后续争议处理与合规审计。

## 版本演进
- 目标表为推断，未在代码中直接出现表名，见 REVIEW。

```ground:rule
name: 短信验证码手机号回填合同签署表
content: 当消息类型为 PHONE 时，CustVerifyCodeApplication 将接收手机号通过 contractSignInfoProvider.setVerifyContractPhone 写入合同签署信息
impact: 验证码接收人落库到合同签署侧
field_targets: []
evidence: CustVerifyCodeApplication.java:sendVerifyCode
```