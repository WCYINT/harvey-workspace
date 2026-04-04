# ERRORS.md - Harvey 问题追踪

> 记录 Harvey 遇到的重要问题、解决方案和经验教训
> 重要：仅记录需要 James 手动处理的问题，或已解决的重要Bug
> 常规问题请直接处理，不要堆在这里

---

## 已关闭问题

_(暂无)_

---

## 学习总结

### 2026-04-01 自我修复记录
- **误报教训**: 检查了 HARVEY_EMAIL_AUTH 历史值，MEMORY.md 记录为 DSswQ3xnSWXgbkyK（2026-03-27更新），但实际工作值为 SEMefmThGnEKJiTz
- **教训**: 验证后再相信 memory 中的 auth code，下一次以实际测试结果为准
- **教训**: 看到 535 错误不一定是 auth code 过期，可能是值本身就不对

## ERR-20260402-SMTP-AUTH (发现时间: 2026-04-02 06:00) ✅ 已解决

**描述**: SMTP 535 authentication failed，163邮箱发送失败
**症状**: daily_skills_summary.py 06:00 AM run失败
**分析**:
- 05:03 AM run成功，06:00 AM run失败 (同一auth code `SEMefmThGnEKJiTz`)
- 09:00 AM run成功 → 确认是163.com临时锁定，已自动解除
- Auth code `SEMefmThGnEKJiTz` 仍然有效
- 原因: 163.com对短时间内的多次SMTP尝试触发了临时安全锁定
**状态**: ✅ 已自动恢复 (2026-04-02 09:00)
**启示**: 163.com的SMTP锁定是临时性的，等待几分钟即可自动解除
**预防**: 下次遇到535错误时，先等待几分钟再重试，而非立即判定auth code失效

## ERR-20260402-EMAIL-LOCKOUT (发现时间: 2026-04-02 09:08)

**描述**: 163邮箱账号被安全锁定，SMTP + IMAP 双挂
**症状**: 
- SMTP: (535, b'Error: authentication failed')
- IMAP: [b'SELECT Unsafe Login. Please contact kefu@188.com for help']
**分析**: Auth code `SEMefmThGnEKJiTz` 在 06:00 AM SMTP失败后，触发账号安全锁定，导致 IMAP 也失效
**状态**: ✅ 已解决 (2026-04-03) — James 已重新生成授权码，SMTP auth_test 验证通过
**预防**: 后续如遇 163.com 锁定，需 James 登录 webmail.163.com 解除并重新生成 auth code
