---
name: healthcare-video-maker
version: 1.0.5
displayName: "Healthcare Video Maker — Create Medical Marketing and Health Promotion Videos"
description: >
  Create healthcare marketing videos, patient acquisition content, and health-promotion campaigns for hospitals, clinics, and telehealth platforms. NemoVideo produces provider profiles, service-line showcases, facility tours, patient testimonials (with HIPAA-compliant consent workflows), and public health education — all calibrated to build trust in an industry where trust determines whether a patient books or bounces.
metadata: {"openclaw": {"emoji": "🏥", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Healthcare Video Maker — Medical Marketing and Health Promotion Videos

Healthcare marketing operates under constraints that no other industry faces: you cannot make claims without clinical evidence, you cannot show patient outcomes without HIPAA-compliant consent, you cannot use fear as a motivator without ethical review, and your target audience — the person deciding which doctor to trust with their body — is making a decision driven more by emotional confidence than by any rational comparison of board certifications and complication rates. The patient searching "best cardiologist near me" at 11 PM is scared. They want to see a face, hear a voice, and feel that this person understands their fear and has the competence to address it. A photo and a bio don't accomplish this. A 60-second video of the cardiologist explaining what a first visit looks like — calmly, in simple language, looking directly at the camera — accomplishes it in the first 15 seconds. NemoVideo produces these videos at scale for healthcare organizations that understand video is their highest-converting marketing asset but lack the internal production capacity to serve every provider, every service line, and every campaign with polished content.

## Use Cases

1. **Provider Profile Video (60-90 sec)** — Dr. James Park, interventional cardiologist. Filmed in his office, natural light, diplomas visible but not featured. Structure: name and specialty title card (5 sec), why he chose cardiology (15 sec — personal story, not resume), his approach to patients (20 sec — "I explain everything in plain language because you shouldn't need a medical degree to understand your own heart"), what a first visit looks like (20 sec — demystifying the process), and CTA: "Schedule a consultation" with phone and online booking link (10 sec). Warm, professional, zero medical jargon. Hosted on the provider's profile page and Google Business listing.
2. **Service Line Showcase (2 min)** — The hospital's new orthopedic surgery center. NemoVideo produces: facility exterior and lobby (10 sec), state-of-the-art OR walk-through (20 sec), surgeon explaining the robotic-assisted knee replacement process with animation overlay (30 sec), recovery-room and PT facility (15 sec), patient testimonial — "I was walking without a cane in 6 weeks" with consent disclosure (20 sec), outcomes data overlay (98% satisfaction, 2.1 day average stay, 15,000 procedures — 15 sec), and CTA with appointment scheduling link (10 sec).
3. **Telehealth Service Explainer (60 sec)** — "See your doctor from home." NemoVideo creates an animated explainer: download the app (screen recording), schedule an appointment (calendar interface), join the video visit (split screen — patient at home, doctor in office), prescriptions sent to your pharmacy (pharmacy icon animation), follow-up scheduled automatically. Each step: 10 seconds with step number and action text. CTA: download link and QR code.
4. **Health Awareness Campaign (30-60 sec)** — September is National Cholesterol Awareness Month. NemoVideo produces a social-media campaign video: the statistic hook ("1 in 3 Americans has high cholesterol — most don't know it"), animated visualization of cholesterol in arteries (10 sec), risk factors checklist (diet, family history, inactivity — animated checkmarks), the simple action ("A blood test takes 5 minutes. Schedule yours today."), and hospital branding with booking link. Exported 9:16 for Reels/TikTok, 1:1 for Facebook.
5. **Facility Virtual Tour (2-3 min)** — A new patient wants to see the clinic before visiting. NemoVideo processes gimbal walk-through footage: parking and entrance (10 sec), reception and waiting area (15 sec), exam rooms (15 sec), imaging center (15 sec), lab (10 sec), and specialty areas with department labels. Ambient background music. Text overlays: department names, floor numbers, and "Free parking" callout. Designed to reduce first-visit anxiety.

## How It Works

### Step 1 — Film Providers and Facilities
Record provider interviews in their office (smartphone + lavalier mic minimum). Film facility walk-throughs with a gimbal for smooth motion. Capture patient testimonials with signed HIPAA-compliant video consent forms.

### Step 2 — Provide Clinical and Marketing Data
Enter provider bios, service-line outcomes data, patient satisfaction scores, and any health-awareness campaign materials. NemoVideo auto-generates text overlays and data visualizations.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "healthcare-video-maker",
    "prompt": "Create a 75-second provider profile video. Dr. James Park, Interventional Cardiologist, Valley Heart Center. Filmed in his office, bookshelf background. Structure: (1) Title card: Dr. James Park, MD, FACC, Interventional Cardiology, 5 sec. (2) Personal story: chose cardiology after his father survived a heart attack when James was 12 — the cardiologist who treated his father became his role model, 15 sec. (3) Patient approach: explains everything in plain language, draws diagrams on a whiteboard during appointments, his phone number is on his business card for urgent questions, 20 sec. (4) First visit walkthrough: a conversation about your history, an EKG that takes 5 minutes, a plan you understand before you leave, 20 sec. (5) CTA: Schedule a consultation, phone 555-0199, or book online at valleyheart.com/dr-park, 10 sec. Tone: warm, calm, confident. No medical jargon. Music: gentle piano, very low volume. Lower-third with name and credentials for first 5 sec only.",
    "duration": "75 sec",
    "style": "provider-profile",
    "lower_third": true,
    "cta_overlay": true,
    "compliance": "hipaa",
    "music": "gentle-piano",
    "format": "16:9"
  }'
```

### Step 4 — Compliance Review and Publish
Route through the hospital's marketing compliance review. Verify no protected health information is disclosed, patient testimonials have signed consent, and all claims are evidence-based. Publish to provider profile pages, Google Business, YouTube, and social media.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the provider, service, facility, or campaign |
| `duration` | string | | Target length: "30 sec", "60 sec", "90 sec", "2 min", "3 min" |
| `style` | string | | "provider-profile", "service-line", "telehealth-explainer", "health-awareness", "facility-tour" |
| `lower_third` | boolean | | Show provider name, title, and credentials (default: true) |
| `cta_overlay` | boolean | | Render phone number, booking URL, or QR code (default: true) |
| `compliance` | string | | "hipaa", "general-healthcare", "pharmaceutical-dtp" |
| `music` | string | | "gentle-piano", "warm-ambient", "professional-subtle", "none" |
| `format` | string | | "16:9", "9:16", "1:1" |

## Output Example

```json
{
  "job_id": "hvm-20260328-001",
  "status": "completed",
  "title": "Meet Dr. James Park — Interventional Cardiologist",
  "duration_seconds": 74,
  "format": "mp4",
  "resolution": "1920x1080",
  "file_size_mb": 22.1,
  "output_url": "https://mega-api-prod.nemovideo.ai/output/hvm-20260328-001.mp4",
  "sections": [
    {"label": "Title Card + Credentials", "start": 0, "end": 5},
    {"label": "Personal Story — Father's Heart Attack", "start": 5, "end": 20},
    {"label": "Patient Approach — Plain Language", "start": 20, "end": 40},
    {"label": "First Visit — What to Expect", "start": 40, "end": 60},
    {"label": "CTA — Schedule Consultation", "start": 60, "end": 74}
  ],
  "compliance_check": {
    "hipaa": "passed — no PHI disclosed",
    "claims_verified": "all statements are provider-opinion or process-description",
    "patient_testimonials": "none included"
  }
}
```

## Tips

1. **The personal story is the trust-builder** — "My father had a heart attack when I was 12" connects more than "I graduated from Johns Hopkins." Patients choose doctors they trust, and trust starts with vulnerability.
2. **Demystify the first visit** — Patient anxiety about the unknown is the #1 barrier to booking. "Here's exactly what happens when you walk in" reduces that anxiety in 20 seconds.
3. **No jargon, ever** — "Interventional cardiology" means nothing to the patient. "I fix blocked arteries" does. Every medical term needs a plain-language translation.
4. **HIPAA compliance is non-negotiable** — Any patient appearing on camera requires a signed video-consent form separate from the general treatment consent. NemoVideo flags videos containing potential PHI.
5. **Google Business Profile is the highest-ROI placement** — The provider profile video on Google gets seen by every patient who searches the doctor's name. It's the first impression before the website.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | Website / Google Business / YouTube |
| MP4 9:16 | 1080p | Instagram Reels / TikTok / Stories |
| MP4 1:1 | 1080p | Facebook / LinkedIn / Twitter |
| GIF | 720p | CTA animation / provider intro loop |

## Related Skills

- [yoga-video-creator](/skills/yoga-video-creator) — Yoga and wellness video production
- [mental-health-video](/skills/mental-health-video) — Mental health content creation
- [nutrition-video-maker](/skills/nutrition-video-maker) — Nutrition and diet content
