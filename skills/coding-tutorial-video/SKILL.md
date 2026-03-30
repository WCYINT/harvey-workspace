---
name: coding-tutorial-video
version: 1.0.5
displayName: "Coding Tutorial Video Maker — Create Programming Walkthroughs and Dev Tutorials"
description: >
    Coding Tutorial Video Maker — Create Programming Walkthroughs and Dev Tutorials. Works by connecting to the NemoVideo AI backend. Supports MP4, MOV, AVI, WebM, and MKV output formats. Automatic credential setup on first use — no manual configuration needed.
metadata: {"openclaw": {"emoji": "👨‍💻", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
apiDomain: https://mega-api-prod.nemovideo.ai
repository: https://github.com/nemovideo/nemovideo_skills
---

# Coding Tutorial Video Maker — Programming Walkthroughs and Dev Tutorials

The tutorial starts with "Hello and welcome to my channel," shows a VS Code window with a font size that requires a magnifying glass, types code so fast the viewer pauses every three seconds to catch up, and at the thirteen-minute mark says "Now this next part is really simple" before writing forty lines of regex that looks like a cat walked across the keyboard. Coding tutorials are the backbone of self-taught developer education — 70% of professional developers learned at least one language from YouTube — but the format fails in predictable ways: code too small to read on a phone, explanations that assume the viewer already knows the thing being taught, terminal output scrolling past before anyone can read it, and the classic "just pause the video" as a substitute for pacing. This tool transforms screen recordings, code snippets, and technical walkthroughs into polished coding tutorials — syntax-highlighted code appearing line by line at readable speed, zoomed-in focus regions that track the cursor through complex files, terminal output with freeze-frame annotations on the important lines, error-and-fix sequences that show the mistake before the solution, architecture diagrams that build themselves as the concept unfolds, and chapter markers that let viewers jump to exactly the function they're stuck on. Built for developer educators building course content, open-source maintainers creating contributor onboarding videos, bootcamp instructors recording supplementary material, conference speakers turning talks into tutorial series, tech leads documenting internal tooling for their teams, and any developer who's ever thought "I should make a video about this" and then spent six hours figuring out OBS settings instead of teaching.

## Example Prompts

### 1. Full-Stack Project Build — React + API from Scratch
"Create a 15-minute tutorial building a task-management app with React and a Node.js API. Structure as a real build, not a lecture. Start in the terminal — 'We're building this from an empty directory to a deployed app. No boilerplate, no starter template, just npm init and determination.' Project setup (0-90 sec): terminal commands appearing line by line — npm init, install dependencies (list them on screen as they install: express, cors, dotenv, pg). Show the package.json briefly, highlight the scripts section. API first (90-300 sec): create server.js — code appearing line by line with syntax highlighting (One Dark theme). Explain as we type: 'This middleware order matters. CORS before routes, error handler after. Swap them and you'll spend two hours debugging a problem that doesn't exist.' First route: GET /tasks — write it, test with curl in a split terminal (left: code, right: terminal), show the JSON response. POST /tasks — write the handler, show the validation: 'If someone sends an empty title, we reject it here. Not in the frontend, not in the database, here. Validate early.' Database (300-420 sec): PostgreSQL setup — show the connection config, explain connection pooling with a visual diagram: 'One connection per request means 1,000 users opens 1,000 connections. Your database will file a restraining order.' Create the tasks table — SQL on screen with each column explained. React frontend (420-700 sec): create-react-app (or Vite — 'Vite, because life is short and Create React App is no longer recommended by the React team'). Component structure diagram appearing: App → TaskList → TaskItem, and AddTaskForm. Build each component with code on screen — useFetch hook first, then the list, then the form with optimistic updates. 'When you add a task, it appears instantly in the UI before the API confirms. If the API fails, we roll it back. Users shouldn't wait for your server to feel productive.' Deployment (700-840 sec): Docker setup — Dockerfile with each line annotated, docker-compose.yml with the service diagram, deploy to Railway or Fly.io — terminal showing the deploy log. Final: open the deployed URL, add a task, refresh to prove persistence. Closing: full architecture diagram — 'React ↔ Express API ↔ PostgreSQL, containerized, deployed, and handling tasks better than you handle yours.' Chapter markers for every section. Dark theme throughout — One Dark Pro, 16pt font minimum, terminal in Dracula theme."

### 2. Algorithm Explanation — Visual Step-by-Step
"Build a 7-minute tutorial explaining merge sort with visual animation. No 'Today we're going to learn about...' — start with the problem: 'You have a million user records to sort by signup date. Bubble sort would take roughly until the heat death of the universe. Let's do better.' Visual array on screen: [38, 27, 43, 3, 9, 82, 10] as colored blocks. Step-by-step split: the array divides into halves, each half divides again — animate each split with blocks sliding apart. Label: 'We keep splitting until each piece has one element. One element is always sorted. That's not lazy — that's the insight.' Merge phase: two single-element arrays merge with a comparison animation — highlight the comparison, show which element goes first, build the sorted subarray. Speed up as the concept becomes clear — first merge at 0.5x, second at 1x, final merge at 1.5x. Show the full merge tree completing with all elements flowing into the sorted result. Code implementation: Python on screen — def merge_sort(arr), the recursive split, the merge function. Walk through the code with the array example: 'When we hit this line, arr is [38, 27]. Left becomes [38], right becomes [27]. We merge them: 27 < 38, so 27 goes first. [27, 38]. That's it.' Complexity analysis: Big-O notation appearing on screen — O(n log n) with a visual showing why: n elements at each level, log n levels. Comparison chart: merge sort vs bubble sort vs quick sort — animated race on a 10,000-element array. Closing: 'Merge sort is stable, predictable, and O(n log n) in every case. Quick sort is usually faster in practice but panics on sorted input. Choose your fighter.' Chapter markers: concept, visual walkthrough, code, complexity."

### 3. DevOps — CI/CD Pipeline Setup
"Produce a 10-minute tutorial setting up a GitHub Actions CI/CD pipeline from scratch. Start with the motivation: 'You push to main and pray. Your deployment process is you SSHing into a server at midnight and typing commands from memory. Let's replace prayer with automation.' Repository setup (0-60 sec): show the project structure — a Node.js app with tests. 'We have a working app and passing tests. Now we need a robot to verify that for every push, because humans forget to run tests and robots don't.' Workflow file (60-240 sec): create .github/workflows/ci.yml — build it line by line. Start with the trigger: 'on: push to main and pull requests. Every PR gets tested before it can merge. No exceptions, not even for you.' Jobs section: name it, choose the runner (ubuntu-latest — 'Microsoft is paying for this compute, thank them later'). Steps: checkout, setup Node, install dependencies, run tests. Show each step with the YAML on the left and a plain-English explanation on the right: 'actions/checkout@v4 clones your repo into the runner. Without this, the runner is staring at an empty directory wondering why you called.' Test the pipeline (240-360 sec): push the workflow, switch to the GitHub Actions tab — show the job running in real time, green checkmarks appearing. Then break a test intentionally — push, show the red X, show the PR blocked from merging. 'This is the point. It's cheaper to catch a bug here than in production at 3 AM.' Add deployment (360-540 sec): add a deploy job that runs only on main push — Docker build, push to registry, deploy to staging. Show the environment secrets setup in GitHub Settings. Conditional deployment: 'needs: [test]' — 'The deploy job waits for tests to pass. It will wait forever if it has to. It's more patient than you are.' Advanced (540-600 sec): add a matrix strategy for Node 18/20/22, caching node_modules (show the time difference: 45 sec vs 12 sec), Slack notification on failure. Closing: push a real change, watch CI pass, watch deploy trigger, check the staging URL. 'From push to deployed in 90 seconds. You can finally close that SSH terminal.'"

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Describe the topic, project structure, code walkthrough flow, and target audience level |
| `duration` | string | | Target video length (e.g. "7 min", "10 min", "15 min") |
| `style` | string | | Tutorial style: "project-build", "concept-visual", "devops-walkthrough", "debugging", "live-coding" |
| `music` | string | | Background audio: "lofi-coding", "ambient-minimal", "none" |
| `format` | string | | Output ratio: "16:9", "9:16", "1:1" |
| `theme` | string | | Editor theme: "one-dark", "dracula", "github-light", "monokai" |
| `font_size` | string | | Code font size: "readable" (16pt+), "compact" (14pt), "mobile-friendly" (18pt+) |

## Workflow

1. **Describe** — Outline the project, concepts, code walkthrough order, and target skill level
2. **Upload** — Add screen recordings, code files, terminal sessions, or diagram sketches
3. **Generate** — AI produces the tutorial with syntax highlighting, zoom tracking, and annotations
4. **Review** — Preview the video, verify code accuracy, adjust the explanation pacing
5. **Export** — Download in your chosen format and resolution

## API Example

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "coding-tutorial-video",
    "prompt": "Create a 15-minute React + Node.js task app tutorial: empty directory to deployed app, Express API with validation, PostgreSQL with connection pooling diagram, React frontend with optimistic updates, Docker deployment, architecture diagram closing. One Dark theme, 16pt font, chapter markers per section",
    "duration": "15 min",
    "style": "project-build",
    "theme": "one-dark",
    "font_size": "readable",
    "music": "lofi-coding",
    "format": "16:9"
  }'
```

## Tips for Best Results

1. **Start in the terminal, not with a slide** — "npm init in an empty directory" is a better hook than "Today we'll learn about..." because developers want to see the starting point. The AI opens on a terminal frame with your first command when you describe a project-build flow.
2. **Specify font size as "readable" or 18pt+** — Half of tutorial viewers watch on phones. Code at 12pt is invisible on a 6-inch screen. The AI enforces minimum 16pt for all code frames and zooms into active regions in large files so every character is legible.
3. **Show the error before the solution** — "Break the test, show the red X, then fix it" teaches debugging instincts that correct-only tutorials never build. The AI sequences error-then-fix when you describe intentional mistakes in your prompt.
4. **Add architecture diagrams at transitions** — "Component tree: App → TaskList → TaskItem" between code sections gives viewers a mental map. The AI generates animated diagrams that build themselves piece by piece at the section breaks you specify.
5. **Use split-screen for input/output** — "Left: code editor, right: terminal showing the curl response" lets viewers see cause and effect simultaneously. The AI generates side-by-side layouts when you describe terminal testing alongside code changes.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube tutorial / course platform content |
| MP4 9:16 | 1080p | TikTok / YouTube Shorts code tip |
| MP4 1:1 | 1080p | LinkedIn dev post / Twitter/X code walkthrough |
| GIF | 720p | Code snippet animation / README demo |

## Related Skills

- [software-demo-video](/skills/software-demo-video) — Software demo and app walkthrough videos
- [tech-review-video](/skills/tech-review-video) — Tech review and comparison videos
- [gaming-video-maker](/skills/gaming-video-maker) — Gaming montages, highlights and let's play videos
