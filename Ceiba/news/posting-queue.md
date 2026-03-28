# AI News Posting Queue
# Generated 2026-03-20. Screenshot carousels + pair with captions.

## Ready to Post (13 carousels)

### Week 1: Launch Week (post 2/day to build momentum)

**Day 1 (Launch)**
- AM: NVIDIA GTC 2026 (bolt/ink) - Jensen Huang keynote, biggest story
- PM: Anthropic Cowork Launch (diamond/ink) - Claude Desktop agent

**Day 2**
- AM: OpenAI Misalignment Monitoring (shield/bone) - safety angle
- PM: Nemotron 3 Super (bolt/bone) - 5x throughput, open source

**Day 3**
- AM: Mistral EU AI Levy (brain/slate) - regulation debate
- PM: NVIDIA + Thinking Machines (bolt/slate) - gigawatt partnership

**Day 4**
- AM: OpenAI Agent Runtime (diamond/ink) - Responses API
- PM: Roche + NVIDIA (circle/warm) - pharma AI

**Day 5**
- AM: NousCoder-14B (slate) - open source coding
- PM: OpenAI DevDay (brain/ink) - AgentKit recap

**Day 6-7: Weekend**
- Trump AI Regulation Blueprint (shield) - policy content
- NemoClaw (special) - if relevant
- OpenAI Monitors (duplicate angle) - skip or save

## Posting Format Per Post
1. Screenshot 4-6 slides from carousel HTML (1080x1080 each)
2. Copy caption from Ceiba/news/posts/ JSON file
3. Post as carousel on Instagram
4. Cross-post hook slide to Stories with "New post" sticker

## Screenshot Instructions
1. Open HTML file in Safari/Chrome
2. Set browser zoom so one slide fills screen at 1080x1080
3. Screenshot each slide (Cmd+Shift+4, drag to exact bounds)
4. Or run: `python3 tools/carousel_to_images.py --all` (needs Playwright browsers)

## Files
- Carousels: `Ceiba/news/carousels/*.html`
- Captions: `Ceiba/news/posts/*.json`
- Images (when generated): `Ceiba/news/carousel-images/`
