# AI News Digest — HTML Email

> Curated AI industry news digest with beautiful HTML emails and smart deduplication.

**Version:** 1.0.0
**Tags:** ai-news, newsletter, email, digest, html-email, deduplication, curation, tech-news

## Features

- 🔍 **Smart Search** — Scans trusted AI/tech news sources
- 🚫 **Deduplication** — Tracks sent stories to avoid repeats
- 🎨 **Beautiful HTML** — Color-coded categories, clickable links, responsive design
- 📧 **Email Delivery** — Sends via Gmail/Google Workspace
- ⏰ **Cron Ready** — Schedule 2-6x daily digests
- 🏷️ **Categorized** — Breaking, Product, Research, Business, Other

## How It Works

1. Agent searches web for latest AI news
2. Checks `data/news-sent.txt` to skip previously sent stories
3. Curates top stories with summaries and category tags
4. Generates styled HTML email
5. Sends via email and updates dedup tracker

## Setup

1. Copy this skill to your OpenClaw skills directory
2. Ensure you have email sending capability (e.g., Google Workspace skill with Gmail)
3. Set up a cron job (see [cron-setup.md](cron-setup.md))

## Dedup Management

```bash
# View recently sent stories
bash dedup.sh show

# Clean entries older than 7 days
bash dedup.sh clean 7

# Reset tracker
bash dedup.sh reset
```

## Output Example

The digest email includes color-coded stories:

- 🔴 **BREAKING** — Major announcements, funding rounds
- 🟢 **PRODUCT** — New launches, updates, features
- 🔵 **RESEARCH** — Papers, benchmarks, breakthroughs
- 🟡 **BUSINESS** — Deals, partnerships, market moves
- ⚪ **OTHER** — Opinion, policy, regulation

## Requirements

- OpenClaw agent with web search capability
- Email sending skill (Gmail recommended)
- No additional packages needed

## License

MIT — see [LICENSE](LICENSE)
