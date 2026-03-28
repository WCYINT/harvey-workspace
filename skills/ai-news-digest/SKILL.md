# AI News Digest — HTML Email

**slug:** ai-news-digest
**version:** 1.0.0
**description:** Curated AI industry news digest delivered as beautiful HTML email. Searches trusted sources, deduplicates stories, generates color-coded HTML with clickable links. Built-in dedup tracker prevents repeated stories.

**read_when:**
- User asks for AI news or tech news digest
- User wants a news summary or newsletter
- Cron job triggers scheduled news digest
- User mentions news deduplication

## What This Skill Does

1. **Searches** trusted AI/tech news sources via web search
2. **Deduplicates** against previously sent stories (tracked in `data/news-sent.txt`)
3. **Curates** the top 10-15 most important stories
4. **Generates** a beautiful HTML email with:
   - Color-coded categories (🔴 Breaking, 🟢 Product Launch, 🔵 Research, 🟡 Business, ⚪ Other)
   - Clickable headline links
   - 2-3 sentence summaries per story
   - Professional styling with responsive design
5. **Sends** via email (using Google Workspace / Gmail skill)
6. **Updates** dedup tracker to avoid repeats

## How to Use

### Manual Digest
```
Search for the latest AI industry news from the past 12 hours. Check these sources:
- TechCrunch AI, The Verge AI, Ars Technica
- VentureBeat AI, MIT Tech Review
- Twitter/X AI accounts

Read data/news-sent.txt for previously sent stories. Skip any duplicates.

Curate the top 10-15 stories. For each:
- Headline with source link
- 2-3 sentence summary
- Category tag: Breaking / Product / Research / Business / Other

Generate a beautiful HTML email with:
- Header: "🤖 AI News Digest — [Date]"
- Color-coded category badges
- Clickable headlines
- Clean, modern styling
- Dark mode compatible

Send to YOUR_EMAIL via Gmail.
Then append all sent headlines to data/news-sent.txt with today's date.
```

### Dedup Management
```bash
# View recent sent stories
bash skills/ai-news-digest/dedup.sh show

# Clear old entries (older than 7 days)
bash skills/ai-news-digest/dedup.sh clean 7

# Reset tracker
bash skills/ai-news-digest/dedup.sh reset
```

## Dedup Format

`data/news-sent.txt` stores one story per line:
```
YYYY-MM-DD|Story headline or key phrase
```

The agent checks this before including stories. Fuzzy matching recommended — don't require exact match, just similar topics.

## HTML Email Template

The agent should generate HTML like:
```html
<div style="max-width:600px;margin:0 auto;font-family:Arial,sans-serif;">
  <h1 style="color:#1a1a2e;">🤖 AI News Digest</h1>
  <p style="color:#666;">February 10, 2026 • 12 stories</p>
  
  <div style="border-left:4px solid #e74c3c;padding:12px;margin:16px 0;">
    <span style="background:#e74c3c;color:white;padding:2px 8px;border-radius:4px;font-size:12px;">BREAKING</span>
    <h3><a href="https://..." style="color:#1a1a2e;">Headline Here</a></h3>
    <p style="color:#555;">Summary text here...</p>
  </div>
</div>
```

## Files
- `dedup.sh` — Manage deduplication tracker
- `cron-setup.md` — Cron job configuration

## Dependencies
- Web search capability (built into OpenClaw)
- Email sending capability (Google Workspace skill or similar)
- No external packages needed
