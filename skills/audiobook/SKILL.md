---
name: audiobook
tagline: "Convert text to professional audiobooks"
description: "Transform books and documents into professional audiobooks with natural voices. Multiple narrators and styles available. No API keys needed. $2 FREE credits to start. Pay-as-you-go via SkillBoss."
version: "1.0.1"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "audio"
tags:
  - audiobook
  - tts
  - narration
  - books
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/pricing?utm_source=clawhub&utm_medium=skill&utm_campaign=audiobook - $2 FREE credits included!"
---

# Audiobook Generator

**Convert text to professional audiobooks**

## Quick Start

```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{"model": "audiobook", "input": {"prompt": "your request here"}}'
```

## Why SkillBoss?

- **One API key** for 100+ AI services
- **No vendor accounts** - Start in seconds
- **$2 FREE credits** to start
- **Pay-as-you-go** - No subscriptions

## Get Started

1. Get API key: [skillboss.co/pricing](https://skillboss.co/pricing?utm_source=clawhub&utm_medium=skill&utm_campaign=audiobook)
2. Set `SKILLBOSS_API_KEY`
3. Start building!

---

*Powered by [SkillBoss](https://skillboss.co) - One API for 100+ AI services*
