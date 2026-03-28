# ✍️ AI LinkedIn Ghostwriter & 30-Day Content Engine

**Slug:** `ai-linkedin-ghostwriter`  
**Category:** Content Marketing / Personal Branding  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + Claude AI

> Scrape the **top viral LinkedIn posts** in your niche, reverse-engineer what makes them explode, and generate a **full 30-day content calendar** written in YOUR voice — ready to post. Zero blank page. Zero writer's block. Ever again.

---

## 💥 Why This Skill Will Dominate ClawHub

LinkedIn has 1 billion users. 97% never post. The 3% who do get **all the leads, speaking gigs, clients, and opportunities**.

Every founder, agency owner, freelancer, consultant, and solopreneur NEEDS this. That's your entire audience — all at once.

**What this skill does:**
- 🔍 Scrapes the **top 50 viral posts** in any niche (last 30 days)
- 🧠 Analyzes **hooks, formats, structures & emotional triggers** that drove engagement
- 🎯 Identifies the **5 content formats** that work best in your specific niche
- ✍️ Generates **30 full LinkedIn posts** written in your personal tone & voice
- 📅 Organizes everything into a **ready-to-use content calendar**
- 🔁 Includes post variations for **A/B testing hooks**

---

## 🛠️ Apify Actors Used

| Actor | ID | Purpose |
|---|---|---|
| LinkedIn Post Scraper | `curious_coder/linkedin-post-scraper` | Scrape viral posts by keyword/hashtag |
| LinkedIn Profile Scraper | `dev_fusion/linkedin-profile-scraper` | Analyze top creators in niche |
| Google Search Scraper | `apify/google-search-scraper` | Find trending topics & news in niche |
| Reddit Scraper | `apify/reddit-scraper` | Discover raw pain points & questions from your audience |

---

## ⚙️ Full Workflow

```
INPUT: Your niche + target audience + tone + 3 content goals
        ↓
STEP 1 — Scrape Top 50 Viral Posts in Your Niche (last 30 days)
  └─ Filter by: likes, comments, shares, reposts
        ↓
STEP 2 — Analyze What Made Them Go Viral
  └─ Hook patterns, post length, format type, emotional triggers,
     CTA style, use of line breaks, storytelling structure
        ↓
STEP 3 — Identify Top 5 Winning Formats for Your Niche
  └─ e.g. Contrarian take / Personal story / How-to list /
     Unpopular opinion / Before & after transformation
        ↓
STEP 4 — Scrape Reddit & Google Trends
  └─ Find the raw questions, frustrations & desires of YOUR audience
        ↓
STEP 5 — Build Your Content Pillars (5 topics that own your niche)
  └─ Based on viral data + audience pain points + your expertise
        ↓
STEP 6 — Claude AI Writes 30 Full Posts in Your Voice
  └─ Week 1: Authority & expertise posts
  └─ Week 2: Personal story & vulnerability posts
  └─ Week 3: Contrarian & opinion posts
  └─ Week 4: Value, tips & actionable how-to posts
        ↓
OUTPUT: 30 posts + calendar + hook variations + posting schedule (JSON / Markdown)
```

---

## 📥 Inputs

```json
{
  "your_profile": {
    "niche": "Digital Marketing for SaaS",
    "target_audience": "SaaS founders and CMOs",
    "tone": "direct, no-fluff, slightly contrarian",
    "expertise": "Paid ads, LinkedIn growth, demand generation",
    "personal_story": "Went from agency employee to $30K/month freelancer in 18 months",
    "content_goals": ["generate inbound leads", "build authority", "grow to 10K followers"]
  },
  "scraping": {
    "hashtags": ["saasmarketing", "b2bmarketing", "linkedingrowth"],
    "top_creators_to_analyze": ["competitor1_linkedin_url", "competitor2_linkedin_url"],
    "lookback_days": 30,
    "min_likes": 200
  },
  "output": {
    "posts_count": 30,
    "include_hook_variations": true,
    "include_posting_schedule": true,
    "format": "markdown"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "niche_analysis": {
    "top_formats": [
      { "format": "Contrarian take", "avg_likes": 847, "share": "34% of viral posts" },
      { "format": "Personal transformation story", "avg_likes": 612, "share": "28% of viral posts" },
      { "format": "Numbered how-to list", "avg_likes": 430, "share": "19% of viral posts" }
    ],
    "best_posting_times": "Tuesday & Thursday 8-9am",
    "optimal_post_length": "900-1,200 characters",
    "top_performing_hooks": [
      "I made $X doing Y. Here's exactly how:",
      "Unpopular opinion: [contrarian statement]",
      "Nobody talks about this but [insight]"
    ]
  },
  "content_pillars": [
    "Paid Ads that actually convert (tactical)",
    "The reality of freelancing no one shows (personal)",
    "Why most SaaS marketing is broken (contrarian)",
    "Behind-the-scenes of scaling to $30K/month (story)",
    "Frameworks & templates you can steal (value)"
  ],
  "posts": [
    {
      "day": 1,
      "pillar": "Contrarian",
      "format": "Unpopular opinion",
      "hook": "Unpopular opinion: Your LinkedIn content isn't failing because of the algorithm.",
      "body": "It's failing because you're writing for your peers.\nNot your buyers.\n\nEvery post is full of industry jargon.\nEvery insight assumes too much context.\nEvery CTA is vague.\n\nYour ideal client — the SaaS founder drowning in churn —\ndoesn't care about 'omnichannel synergy'.\n\nThey care about:\n→ Getting more trials\n→ Converting free users to paid\n→ Not bleeding budget on ads that don't work\n\nWrite for them.\nUse their words.\nSolve their specific problem in every post.\n\nThe algorithm rewards relevance.\nRelevance comes from specificity.\nSpecificity comes from knowing your buyer cold.\n\nStop writing for likes.\nStart writing for leads.",
      "cta": "What's the #1 mistake you see in B2B content? Drop it below 👇",
      "hook_variation_a": "Unpopular opinion: Your LinkedIn content isn't failing because of the algorithm.",
      "hook_variation_b": "I reviewed 200 SaaS LinkedIn profiles last month. 94% made the same mistake."
    },
    {
      "day": 3,
      "pillar": "Personal story",
      "format": "Transformation story",
      "hook": "18 months ago I was billing $4,500/month as a freelancer and thinking about quitting.",
      "body": "Today I cleared $30K last month.\n\nHere's the exact shift that changed everything:\n\nI stopped selling 'Facebook Ads services'.\nI started selling 'predictable SaaS trial growth'.\n\nSame skill set.\nCompletely different positioning.\n\nThe old me: 'I run ads for businesses'\nThe new me: 'I help SaaS founders get their first 1,000 trials without burning cash'\n\nResults:\n→ Average client value went from $1,500 to $6,000/month\n→ Sales calls dropped from 15/month to 4/month\n→ Close rate went from 20% to 75%\n\nPositioning isn't about lying.\nIt's about being the most relevant option\nfor one specific person with one specific problem.\n\nNiche down until it feels uncomfortable.\nThen go one level deeper.",
      "cta": "What's your current positioning? I'll give you honest feedback 👇",
      "hook_variation_a": "18 months ago I was billing $4,500/month as a freelancer and thinking about quitting.",
      "hook_variation_b": "The day I raised my prices by 4x and started getting MORE clients, not fewer."
    }
  ],
  "calendar": [
    { "day": "Monday", "week": 1, "post_id": 1, "pillar": "Contrarian", "status": "ready" },
    { "day": "Wednesday", "week": 1, "post_id": 2, "pillar": "Value/How-to", "status": "ready" },
    { "day": "Friday", "week": 1, "post_id": 3, "pillar": "Personal Story", "status": "ready" }
  ],
  "posting_schedule": {
    "frequency": "3x per week",
    "best_days": ["Tuesday", "Thursday", "Saturday"],
    "best_time": "8:00 AM - 9:00 AM (audience local time)",
    "monthly_reach_estimate": "15,000 - 45,000 impressions (based on niche benchmarks)"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class LinkedIn ghostwriter and content strategist.

VIRAL POST ANALYSIS FROM SCRAPING:
{{viral_posts_data}}

AUDIENCE PAIN POINTS FROM REDDIT:
{{reddit_pain_points}}

TRENDING TOPICS THIS MONTH:
{{trending_topics}}

MY PROFILE:
- Niche: {{niche}}
- Target audience: {{target_audience}}
- Tone: {{tone}}
- Expertise: {{expertise}}
- Personal story: {{personal_story}}
- Goals: {{content_goals}}

TASK:
1. Identify the top 5 content formats that dominate this niche
2. Define 5 content pillars based on viral patterns + audience pain points
3. Write 30 full LinkedIn posts (10 per format type) in the user's exact tone
4. For each post include: hook, full body, CTA, 2 hook variations for A/B test
5. Build a 30-day posting calendar (3x/week: Mon/Wed/Fri or Tue/Thu/Sat)
6. Add estimated reach based on niche engagement benchmarks

RULES FOR EVERY POST:
- Hook = first line must stop the scroll. Make a bold claim or ask a sharp question.
- Use white space aggressively — short punchy lines, never walls of text
- No corporate jargon. Write like a human talking to a human.
- End with a CTA that invites conversation, not just likes
- Optimal length: 900-1,200 characters

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Output | Apify CU | Cost | Posts Generated |
|---|---|---|---|
| 1 niche analysis + 30 posts | ~35 CU | ~$0.35 | 30 full posts |
| 3 clients (90 posts) | ~105 CU | ~$1.05 | 90 full posts |
| 10 clients (300 posts) | ~340 CU | ~$3.40 | 300 full posts |
| Agency package (50 clients) | ~1,700 CU | ~$17 | 1,500 full posts |

> 💡 **$5 free Apify credits on signup** = your first 14 clients' content completely free.  
> 👉 [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)

---

## 🔗 Use Cases That Print Money

| Use Case | Revenue Opportunity |
|---|---|
| **LinkedIn Ghostwriting Agency** | Charge $1,500-$5,000/month per client for 12 posts |
| **30-Day Content Sprint Service** | Sell a $500 one-time package — costs you $0.35 in Apify |
| **Founder Personal Brand Package** | Bundle with audit + strategy call for $2,000+ |
| **SaaS Content Marketing Retainer** | Ongoing monthly content for $3,000/month |
| **Your own LinkedIn growth** | Build to 10K+ followers → inbound leads on autopilot |

---

## 📊 Why This Skill Beats Everything in Your Catalog

| Feature | Content Generator (existing) | **AI LinkedIn Ghostwriter** |
|---|---|---|
| Scrapes viral content for inspiration | ✅ | ✅ |
| Analyzes WHY posts went viral | ❌ | ✅ |
| Writes in YOUR personal voice | ❌ | ✅ |
| Full 30-day calendar included | ❌ | ✅ |
| A/B hook variations | ❌ | ✅ |
| Audience pain point research | ❌ | ✅ |
| Sellable as a $1,500+/month service | ❌ | ✅ |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your Apify API Token**  
Sign up free → [https://www.apify.com?fpr=dx06p](https://www.apify.com?fpr=dx06p)  
Go to: **Settings → Integrations → API Token**

**Step 2 — Fill in your profile details**  
Niche, audience, tone, your story, your goals. The more specific, the better the output.

**Step 3 — Add your target hashtags & run**  
30 posts + full calendar ready in under 5 minutes.

---

## ⚡ Pro Tips to Get Maximum Engagement

- **Post consistency beats post perfection** — 3x/week for 90 days beats 1 viral post
- **Your best hook is always your first line** — rewrite it 5 times before posting
- **Reply to every comment in the first 60 minutes** — LinkedIn rewards fast engagement
- **Pin your best performing post** — new visitors see your best content first
- **Use the A/B hook variations** — test the same post with 2 different openers 2 weeks apart

---

## 🏷️ Tags

`linkedin` `content-marketing` `ghostwriting` `personal-branding` `agencies` `freelancers` `content-calendar` `apify` `ai-copywriting` `social-media` `thought-leadership` `lead-generation`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + Claude AI*
