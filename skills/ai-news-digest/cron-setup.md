# Cron Job Setup — AI News Digest

## OpenClaw Cron Job

```bash
openclaw cron create news-digest \
  --schedule "30 2,6,10,14,18,22 * * *" \
  --model anthropic/claude-sonnet-4-20250514 \
  --channel YOUR_CHANNEL_ID \
  --prompt "Generate an AI news digest:

1. Search for AI industry news from the past 6-8 hours using web search. Check:
   - TechCrunch AI, The Verge, Ars Technica AI
   - VentureBeat, MIT Technology Review
   - Major AI company blogs (OpenAI, Anthropic, Google DeepMind, Meta AI)

2. Read data/news-sent.txt for previously sent stories. Skip duplicates (fuzzy match — same topic counts as duplicate).

3. If fewer than 3 new stories found, reply 'No significant new AI stories' and stop.

4. Curate the top stories. For each provide:
   - Headline with source URL
   - 2-3 sentence summary
   - Category: Breaking / Product / Research / Business / Other

5. Generate a beautiful HTML email:
   - Header: '🤖 AI News Digest — [Date, Time]'
   - Color-coded category badges (red=breaking, green=product, blue=research, yellow=business)
   - Clickable headlines
   - Responsive design, dark-mode compatible
   - Footer with unsubscribe note

6. Send the HTML email to YOUR_EMAIL using Gmail.

7. Append all sent headlines to data/news-sent.txt:
   Format: YYYY-MM-DD|Headline text

8. Post a brief summary to this channel:
   📰 **AI News Digest Sent** — X stories
   Top story: [headline]"
```

### Schedule Examples

| Frequency | Cron Expression |
|-----------|----------------|
| 6x daily (every 4h) | `30 2,6,10,14,18,22 * * *` |
| 3x daily | `0 4,12,20 * * *` |
| 2x daily (morning + evening) | `0 6,18 * * *` |
| Daily morning digest | `0 6 * * *` |

### Timezone

```bash
--schedule "30 8,20 * * * @ America/New_York"
```
