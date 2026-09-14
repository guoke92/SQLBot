---
type: caliber
title: SFTP 渠道启用
page_key: sftp_channel_enable
domain: 外部渠道与银行对接
status: draft
aliases:
  - 影像通道启用口径
  - cust_sftp.enable = 'Y'
oid: 1
scope:
  databases:
    - cust
sources:
  - code:CustAccessApplication.initSftp
contract_version: "0.1"
belong: calibers
---

影像 SFTP 通道按 channel + enable 联查初始化，匹配不到即抛 SERVER_BUSY，建档流程不得降级继续。

## 需求背景
非自主建档必须提交营业执照、法人正反面、经办人正反面与授权书影像（[[independent_archive_validation]]），影像缺失会导致后续运营审核无法进行，因此通道不可用时快速失败。配置见 [[cust_sftp]]。

## 版本演进
暂无版本演进记录。

```ground:caliber
name: SFTP 渠道启用
predicate: "cust_sftp.enable = 'Y'"
scope: 影像 SFTP 通道初始化，匹配不到直接抛 SERVER_BUSY
evidence: "code:CustAccessApplication.initSftp"
```