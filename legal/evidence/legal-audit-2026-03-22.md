# PRE-LAUNCH LEGAL AUDIT
# Date: 2026-03-22
# Scope: All products, content, and marketing in /behique/ prior to Gumroad + Instagram launch
# NOT LEGAL ADVICE. This is a risk assessment. Consult an attorney before launch.

---

## TABLE OF CONTENTS

1. [Product-by-Product Audit](#1-product-by-product-audit)
2. [Copyright Infringement Findings](#2-copyright-infringement-findings)
3. [Trademark Issues](#3-trademark-issues)
4. [Plagiarism Concerns](#4-plagiarism-concerns)
5. [Required Disclosures (Missing)](#5-required-disclosures-missing)
6. [Fair Use Assessment](#6-fair-use-assessment)
7. [Student/Third-Party Content](#7-studentthird-party-content)
8. [Font and Asset Licensing](#8-font-and-asset-licensing)
9. [Risk Matrix](#9-risk-matrix)
10. [Remediation Checklist](#10-remediation-checklist)

---

## 1. PRODUCT-BY-PRODUCT AUDIT

### Product 1: Budget Calculator Excel ($9.99)
- **Copyright risk:** LOW. Original spreadsheet. No third-party content detected.
- **Trademark risk:** NONE. Generic product name.
- **AI disclosure:** Not present. Needs adding if AI was used in creation.
- **Copyright notice:** Not present in product listing.
- **License terms:** Not present.
- **Status:** MOSTLY CLEAN. Needs copyright notice and license terms added.

### Product 2: The Ecommerce Playbook ($14.99)
- **COPYRIGHT RISK: CRITICAL/RED.**
- The product listing explicitly states: "I transcribed 242 video lessons, organized them into 20 modules, and turned the whole thing into one structured book."
- The FAQ states: "Every module is based on transcriptions from real, paid ecommerce courses."
- The Social Proof section says: "I transcribed and restructured real course material."
- The ebook_builder.py tool confirms this pipeline: it scans "Gym KB" directories for transcript files and assembles them into an ebook.
- The tool's footer text reads: "This book was compiled from [X] video course transcripts... The content represents real course material that was transcribed using AI (OpenAI Whisper) and formatted for easy reading."
- Content-Empire.md lists this as: "Building from Gym transcripts"
- **This is textbook copyright infringement.** Transcribing someone else's paid course and reselling the transcriptions as a book is creating an unauthorized derivative work. It does not matter that AI did the transcription or that the content was reorganized. The original course creators own the copyright to their instructional content.
- **This product will get DMCA'd.** Gumroad will take it down. The course creators can sue for statutory damages ($150,000 per work infringed if willful). The marketing copy is a written confession of infringement.

### Product 3: AI Meditation Experience (FREE / $4.99)
- **Copyright risk:** LOW. Appears to be original code and design.
- **Trademark risk:** LOW. Generic product name.
- **Medical claims risk:** MEDIUM. Copy says breathing patterns "actually calm your nervous system" and are "based on research on nervous system regulation." These are health claims. While box breathing and 4-7-8 are well-documented techniques, making specific health outcome claims in marketing without citing studies could trigger FTC scrutiny or platform policy violations.
- **Status:** Mostly clean. Add disclaimer about not being medical advice.

### Product 4: "How I Built an AI Employee" Guide ($19.99)
- **Copyright risk:** LOW. This appears to be genuinely original content documenting Kalani's own system. The guide at `products/ai-employee-guide.md` describes his specific hardware setup, architecture, and configuration in his own words.
- **Trademark risk:** LOW. Generic product name.
- **AI disclosure:** Not present. If AI assisted in writing the guide, this needs disclosure.
- **Copyright notice:** NOT present in the product file.
- **License terms:** NOT present.
- **Third-party IP:** The guide references specific tools (Ollama, Claude, n8n, Syncthing, Whisper) by name. This is nominative fair use for describing tools you actually use. No issue.
- **Status:** CLEAN content. Needs copyright notice, license, and AI disclosure.

### Product 5: Shopify Theme Bundle ($69.99) / Individual Themes ($14.99-$49.99)
- **Copyright risk:** LOW if themes are original code.
- **Trademark risk:** MEDIUM. "Shopify" is a registered trademark. Using "Shopify Theme" in a product name is acceptable nominative fair use (describing what the product works with), but the theme cannot imply endorsement by or affiliation with Shopify.
- **Status:** Needs review of actual theme files for any copied code from other Shopify themes.

---

## 2. COPYRIGHT INFRINGEMENT FINDINGS

### FINDING 1: THE ECOMMERCE PLAYBOOK IS UNAUTHORIZED DERIVATIVE WORK [RED]

**Evidence locations:**
- `Ceiba/projects/content-empire/product-listings.md` lines 60-112
- `Ceiba/projects/Content-Empire.md` lines 21, 88, 123
- `tools/ebook_builder.py` lines 237-241

**The smoking gun (from product-listings.md):**
> "I bought and studied real ecommerce courses. Not YouTube videos. Not free PDFs. Actual paid programs from people running real stores. Then I transcribed 242 video lessons, organized them into 20 modules, and turned the whole thing into one structured book."

**Why this is infringement:**
1. The original course videos are copyrighted works
2. Transcribing them creates a reproduction (the transcript)
3. Reorganizing them into a book creates a derivative work
4. Selling the derivative work is commercial distribution of copyrighted material
5. The ebook_builder.py tool automates this pipeline, proving systematic reproduction
6. The product listing FAQ explicitly admits the content is "100% sourced from real course material"

**Legal exposure:**
- DMCA takedown from any course creator who discovers this
- Gumroad will remove the product immediately upon DMCA claim
- Statutory damages: up to $150,000 per work infringed (willful infringement)
- The marketing copy itself is evidence of willfulness. It's not even plausibly deniable.

**What makes this worse:**
- The marketing copy brags about this as a feature. "The source courses cost thousands combined. At $14.99, the value gap is massive."
- This framing positions the product as a cheaper replacement for the courses. This fails the fourth fair use factor (market substitution) completely.

### FINDING 2: INSTAGRAM CONTENT REFERENCES TRANSCRIBED COURSE CONTENT [YELLOW]

**Evidence locations:**
- `instagram-content-batch-1.md` lines 38, 198, 240-280, 330-337

Multiple Instagram posts reference transcribing courses:
- Post 1, Slide 5: "I transcribed 368 course videos with Whisper and built searchable knowledge bases from them."
- Post 6 (full reel script): Entire reel is about turning "242 ecommerce course videos" into a searchable knowledge base.
- Post 8: "I distilled 242 ecommerce courses into one resource."

**Risk:** Even if the ebook product is pulled, these posts create public evidence of mass transcription of copyrighted course content. Course creators who see these posts could issue DMCA claims or pursue legal action. Additionally, publicly stating you transcribed someone's paid courses could trigger their legal team even if you never sell the ebook.

### FINDING 3: EBOOK BUILDER TOOL AUTOMATES INFRINGEMENT PIPELINE [YELLOW]

**Evidence location:** `tools/ebook_builder.py`

The tool's sole purpose is converting "Gym KB" transcript directories into formatted ebooks for sale. The footer it generates explicitly states the content was "transcribed using AI (OpenAI Whisper)." While a tool is not itself infringement, it exists only to facilitate producing derivative works from copyrighted course transcripts.

---

## 3. TRADEMARK ISSUES

### ISSUE 1: "BEHIKE" AND THE COHIBA BEHIKE CONFLICT [YELLOW]

**Background:**
- "Cohiba Behike" is a premium Cuban cigar brand. "Cohiba" is a registered trademark of Empresa Cubana del Tabaco (internationally) and General Cigar Co. (in the US due to embargo-related claims).
- "Behike" refers to a line within the Cohiba brand.
- The ip-protection-reference.md file already identifies this conflict (line 180).

**Analysis:**
- Cohiba Behike operates in Class 34 (tobacco products).
- Kalani's "Behike" would operate in Class 9 (digital products) and Class 41 (education).
- Different classes significantly reduce likelihood of confusion.
- However, "Cohiba Behike" is a well-known mark. Well-known marks receive broader protection under dilution doctrine (even across classes).
- The Taino cultural origin of the word "behike/behique" (meaning spiritual healer) provides a legitimate independent derivation argument.

**Recommendation:** Proceed with "Behike" but:
1. Do a full USPTO TESS search before filing
2. Consider "BehikeAI" as the primary mark to further differentiate
3. Consult a trademark attorney before filing application
4. Document the Taino cultural derivation as evidence of independent origin

### ISSUE 2: USE OF OTHER BRAND NAMES IN MARKETING [GREEN/YELLOW]

**Evidence locations:**
- `service-offering.md`: "Hormozi $100M Offers framework" in section headers
- `Content-Empire.md`: "DotCom Secrets (Russell Brunson)" and "$100M Offers (Alex Hormozi)" as strategy headers
- `product-listings.md`: "The Hormozi value equation"
- `instagram-content-batch-1.md`: "Hormozi value equation applied to conversion posts"

**Analysis:**
- Mentioning other creators' names and book titles for reference/attribution is nominative fair use. You are allowed to say "I applied concepts from Alex Hormozi's book."
- However, the service-offering.md labels entire sections with framework names: "The Offer (Hormozi $100M Offers framework)." If this is internal documentation, no issue. If this appears in customer-facing material, it implies endorsement or licensing.
- Book titles are not trademarkable (they are copyrightable as creative works). Referencing "$100M Offers" by name is fine.

**Recommendation:** Keep brand name references in internal strategy docs. Remove explicit framework labels from any customer-facing marketing. Never imply endorsement or partnership.

### ISSUE 3: INSTAGRAM HANDLE CONFLICTS [GREEN]

- @behikeai: No conflict found with existing major brands. The handle exists and is controlled by Kalani.
- @kalaniandrez: Personal handle. No conflict.

---

## 4. PLAGIARISM CONCERNS

### CONCERN 1: OPB FRAMEWORK PROXIMITY TO DAN KOE [YELLOW]

**Evidence locations:**
- `Ceiba/05-Knowledge/ip-protection-reference.md` lines 147-163, 348-391
- `Ceiba/IDEAS_BACKLOG.md` line 137
- CLAUDE.md project memory references "OPB Framework as Business Foundation"

**Analysis:**
- "OPB" stands for "One Person Business," which is a concept Dan Koe has built content around.
- The concept of a one-person business is not copyrightable or trademarkable. Thousands of creators discuss this topic.
- However, if Kalani's framework replicates Dan Koe's specific structure, step names, or proprietary terminology, it becomes a derivative work.
- The ip-protection-reference.md already contains correct legal analysis of this issue (Section 9).

**Risk level:** Depends on execution. If the OPB content uses Kalani's own structure, examples, and terminology: GREEN. If it mirrors Dan Koe's specific framework steps: RED.

**Recommendation:** Review any OPB product content side-by-side with Dan Koe's published framework. Ensure original structure, original examples, original terminology. Reference Dan Koe by name with attribution if citing concepts, but build an independent expression.

### CONCERN 2: VIRAL VAULT 15-POINT SCORING [YELLOW]

**Evidence locations:**
- `Ceiba/IDEAS_BACKLOG.md` line 128: "15-point scoring checklist from Viral Vault adapted for our product scoring engine."
- Multiple dashboard HTML files reference "Integrate Viral Vault 15-point scoring."

**Analysis:**
- "Viral Vault" appears to be a specific product/course.
- Directly adapting their proprietary scoring checklist and embedding it in a product is potentially infringing.
- A scoring methodology itself (as a "system" or "method") cannot be copyrighted per 17 U.S.C. 102(b).
- However, the specific expression (exact criteria, exact wording, exact weighting) can be.

**Recommendation:** If using Viral Vault concepts, create an original scoring system inspired by the general approach but with your own criteria, weights, and terminology. Do not copy their specific checklist.

### CONCERN 3: STRATEGY FRAMEWORKS THAT ARE TOO PRECISELY ATTRIBUTED [YELLOW]

**Evidence:**
- `service-offering.md`: Every section header is labeled with the source framework: "Hormozi $100M Offers framework," "Dream Outcome," "Value Equation," "Price Anchoring."
- `Content-Empire.md`: Sections literally titled "DotCom Secrets (Russell Brunson)" and "$100M Offers (Alex Hormozi)."
- `product-listings.md`: "Funnel logic (DotCom Secrets)" and "Value equation (Hormozi)"

**Analysis:**
- This is not itself infringement. Teaching and applying business concepts from published books is legal.
- The issue is that labeling your own strategy documents with someone else's framework names makes your work look like a derivative presentation of their material.
- If any customer-facing content literally says "We use the Hormozi $100M Offers framework," it implies you are either licensed by Hormozi or are reselling his methodology.

**Recommendation:** Internalize the concepts. Remove framework attribution from customer-facing materials. Use your own terminology for the same concepts. Internal docs can reference sources for your own learning purposes.

---

## 5. REQUIRED DISCLOSURES (MISSING)

### MISSING 1: AI INVOLVEMENT DISCLOSURE [RED for copyright registration, YELLOW for Gumroad]

**Finding:** No product in the repository contains an AI involvement disclosure.

**Products that used AI in creation:**
- AI Employee Guide: Likely AI-assisted in drafting (needs disclosure if registering copyright)
- Budget Calculator: Unknown
- Meditation App: Code likely AI-assisted
- Ecommerce Playbook: Explicitly AI-transcribed source material + AI formatting

**Legal requirement:** Since February 2023, the US Copyright Office requires disclosure of AI-generated content when registering. Failure to disclose can invalidate the registration. This is not optional.

**Gumroad policy:** Gumroad does not currently require AI disclosure but may update policies. Proactive disclosure builds trust and protects against future policy changes.

**Recommendation:** Add an "About This Product" section to every product that honestly states: "This [product type] was created by [Your Name] with the assistance of AI tools for [specific uses: drafting, formatting, grammar checking, etc.]. All content was reviewed, edited, and approved by the author."

### MISSING 2: COPYRIGHT NOTICES [RED]

**Finding:** No product file contains a copyright notice.

**Files audited that lack copyright notices:**
- `products/ai-employee-guide.md`: No copyright notice anywhere in the file
- `product-listings.md`: No copyright notice in any listing
- `themes/behike-store/landing-pages/index.html`: Footer has "(c) 2026 Behike. All rights reserved." -- this is the ONLY copyright notice found in any product or marketing file.

**The ip-protection-reference.md provides exact templates** for copyright notices (lines 280-336) but none have been implemented in any actual product.

**Recommendation:** Add the full copyright page template from the IP reference to every product before listing.

### MISSING 3: ANTI-AI-TRAINING META TAGS [YELLOW]

**Finding:** Only 2 files have the `noai, noimageai` meta tag:
- `Ceiba/faces/behike-os.html` (internal dashboard, not a product)
- `Ceiba/faces/particle-face.html` (internal dashboard, not a product)

**The landing page (`themes/behike-store/landing-pages/index.html`) does NOT have this tag.** None of the product files have anti-AI-training notices.

**Recommendation:** Add `<meta name="robots" content="noai, noimageai">` to all public-facing HTML. Add the anti-AI-training paragraph from the IP reference template to all PDF/ebook products.

### MISSING 4: LICENSE TERMS [RED]

**Finding:** No product listing includes license terms or terms of use. The ip-protection-reference.md recommends license terms for every product (line 399-403) but none have been created.

**Recommendation:** Create a standard license document and include it with every digital product. At minimum, state: personal use only, no redistribution, no resale, no AI training use.

### MISSING 5: PRIVACY POLICY AND TERMS OF SERVICE [YELLOW]

**Finding:** The landing page footer links to "Privacy" and "Terms" but both point to `#` (non-functional placeholder links, line 571-572 of index.html).

**Risk:** If you collect email addresses via the newsletter form, you need a functioning privacy policy. Without one, you may violate CAN-SPAM, GDPR (if EU visitors), and Puerto Rico's data protection regulations. Gumroad also requires sellers to have accessible terms.

---

## 6. FAIR USE ASSESSMENT

### Using "Dan Koe style" in marketing: RISKY (YELLOW)
- Saying "inspired by Dan Koe" as attribution: acceptable
- Saying "Dan Koe style" as a product description or selling point: trademark dilution risk. It uses his name to sell your product.
- **Recommendation:** Do not use other creators' names as selling points. Build your own brand identity.

### Referencing "Hormozi framework" in marketing: ACCEPTABLE if internal (GREEN)
- In internal strategy docs: fine
- In customer-facing copy: avoid. Say "value-based pricing" instead of "Hormozi value equation."

### Teaching concepts from business books: SAFE (GREEN)
- Ideas, concepts, and methods cannot be copyrighted
- You can teach about value ladders, sales funnels, and pricing psychology
- You cannot reproduce the specific text, examples, or structure of the books
- Your current approach of learning from books and applying concepts is legally sound

### Transcribing and reselling course content: NOT FAIR USE (RED)
- Commercial use (against)
- Nature: creative instructional content (against)
- Amount: entire courses transcribed (against)
- Market effect: directly replaces the original product (against)
- This fails all four fair use factors. It is not fair use under any analysis.

---

## 7. STUDENT/THIRD-PARTY CONTENT

### FINDING 1: STUDENT ESSAYS CONTAIN FULL NAMES [RED]

**Evidence locations:**
- `student-essays-pet-peeves.md`: Contains 14 students' full names
  - Lucas Colon Pastoriza, Carlos Aguila Gonzalez, Karliany Rodriguez Almodovar, Dwight Frias Martinez, Luidariel Vega Garcia, Carlos Martis Velez, Onix Gonzalez Gonzalez, Edgardo Hernandez Medero, Perla Maldonado Rivera, Angelica Mendez Velez, Alanis Nazario Rivera, Yahir Rivera Adorno, Yamilet Diaz Diaz, Joel Sosa Rivera, Josue Aguayo Ortiz
- `student-essays-souvenirs.md`: Contains NO student names (essays labeled as "Essay 1", "Essay 2", etc.)

**The reel briefs note that "All student names removed per production rules" (pet-peeves-batch-1.md line 5).** This is good for the reel briefs but the source file still has all names.

**Issues:**
1. **FERPA concerns:** If Kalani collected these as a teaching assistant or in an academic role, student educational records are protected under FERPA. Using them commercially without explicit written consent from each student is a FERPA violation.
2. **Privacy/consent:** Even outside FERPA, using someone's personal essay commercially requires their consent, especially when their full name is attached.
3. **Copyright ownership:** Students own the copyright to their own essays. Using them in a content pipeline (including as training data for AI content generation) requires permission.

**The ai-content-agent-design.md makes this worse:** It explicitly describes using these student essays as "training data" for AI content generation (line 10: "Train an AI agent on the content library (real student essays, personal stories)"). This is:
- Using copyrighted student work without permission
- Using personal content as commercial training data without consent
- Potentially a FERPA violation if collected in an academic context

### FINDING 2: STUDENT ESSAYS BEING USED IN COMMERCIAL CONTENT PIPELINE [RED]

**Evidence:**
- `ai-content-agent-design.md`: "Input: Content Library (training data) - 19 souvenir essays, 16 pet peeve essays"
- `reel-briefs/souvenirs-batch-1.md` and `reel-briefs/pet-peeves-batch-1.md`: Reel scripts directly derived from student essays
- The reel briefs closely paraphrase student essays. For example, Reel 01 ("The Empty Palette") is a direct adaptation of Essay 1 (Makeup Palette) from souvenirs.

**Even with names removed, the content is still their copyrighted work.** Using it to create commercial Instagram reels without permission is infringement.

### FINDING 3: CHATGPT CONVERSATION DATA [GREEN]

**Evidence checked:** `Ceiba/projects/ai-marketplace/ORIGINAL_IDEAS_CHATGPT.md`
- This appears to contain Kalani's own ideas from ChatGPT conversations
- ChatGPT output is not copyrightable (per OpenAI's terms, users own their outputs for commercial use)
- No evidence of other users' data in these files

---

## 8. FONT AND ASSET LICENSING

### FINDING 1: SF PRO FONT REFERENCES [YELLOW]

**Evidence locations:**
- `themes/behike-store/landing-pages/index.html` line 28: `font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text'`
- `themes/behike-store/landing-pages/chat-widget.js` lines 101, 146, 211: Same SF Pro references

**Analysis:**
- The CSS `font-family` stack lists SF Pro Display and SF Pro Text as preferred fonts, with system fallbacks.
- SF Pro is Apple's proprietary font. It is free to download from Apple's developer site but its license restricts use to Apple platforms only.
- Using `-apple-system` and `BlinkMacSystemFont` as the primary declarations means the browser uses the system font, which is fine. The explicit `'SF Pro Display'` references are technically requesting Apple's proprietary font by name.
- In practice, if the font files are not bundled/served (they are not in this repo), and the CSS falls back to system fonts, this is a very low risk. Browsers on Apple devices will use the system font; browsers on other devices will fall to Helvetica/Arial.

**Recommendation:** For maximum safety, remove the explicit 'SF Pro Display' and 'SF Pro Text' references and rely on `-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif`. This achieves the same visual result without referencing a licensed font.

### FINDING 2: INSTAGRAM SVG ICON [GREEN]

- `index.html` line 460: Contains an inline SVG of the Instagram logo
- Meta's brand guidelines allow use of the Instagram glyph icon for linking to your own profile
- Current usage (linking to @behikeai) is compliant

---

## 9. RISK MATRIX

### RED: MUST FIX BEFORE LAUNCH

| # | Issue | Location | Risk | Action Required |
|---|-------|----------|------|----------------|
| R1 | **Ecommerce Playbook is unauthorized derivative work** | product-listings.md (Product 2), ebook_builder.py, Content-Empire.md | DMCA takedown, lawsuit, up to $150K statutory damages per work | DO NOT LIST THIS PRODUCT. Rebuild from scratch with original content or remove entirely. |
| R2 | **Student essays used commercially without consent** | student-essays-pet-peeves.md, student-essays-souvenirs.md, reel-briefs/, ai-content-agent-design.md | FERPA violation, copyright infringement, privacy lawsuit | Get written consent from every student OR remove all student content from the repo and reel pipeline. |
| R3 | **Student full names in source files** | student-essays-pet-peeves.md | Privacy violation, potential FERPA liability | Remove all student names immediately, even from source files. |
| R4 | **No copyright notices on any product** | All product files | Weakened legal position, no basis for enforcement | Add copyright notices to every product before listing. |
| R5 | **No license terms on any product** | All product listings | No legal framework for buyer usage, no recourse against redistribution | Create and attach license terms to every product. |
| R6 | **Marketing copy confesses to infringement** | product-listings.md lines 70-74, 100, 105; instagram-content-batch-1.md multiple posts | Written evidence of willful infringement | Rewrite ALL marketing copy. Remove all references to "transcribed course content," "242 lessons," "real course material." |

### YELLOW: SHOULD FIX (legal gray area, could cause problems)

| # | Issue | Location | Risk | Action Required |
|---|-------|----------|------|----------------|
| Y1 | Behike/Cohiba Behike trademark proximity | Brand name across all files | Dilution claim from tobacco company | Do USPTO search, consult trademark attorney before filing |
| Y2 | Instagram posts reference transcribed courses | instagram-content-batch-1.md Posts 1, 5, 6, 8 | Course creators find posts, trigger legal action | Rewrite posts to reference "knowledge systems" without mentioning transcribed courses |
| Y3 | OPB framework proximity to Dan Koe | Memory files, strategy docs | Derivative work claim if too similar | Review side-by-side, ensure original expression |
| Y4 | Viral Vault 15-point scoring adaptation | IDEAS_BACKLOG.md, dashboard files | IP claim from Viral Vault | Create original scoring criteria, do not copy their checklist |
| Y5 | No AI involvement disclosure | All products | Invalid copyright registration if filed without disclosure | Add AI disclosure to every product |
| Y6 | Strategy docs labeled with others' framework names | service-offering.md, Content-Empire.md | Implied endorsement, confusing attribution | Remove framework labels from customer-facing docs |
| Y7 | No privacy policy or terms of service | Landing page index.html | CAN-SPAM, GDPR, PR data protection violations | Create and publish privacy policy + ToS before collecting emails |
| Y8 | Landing page missing noai meta tag | index.html | Content scraped for AI training | Add meta tag |
| Y9 | Health claims in meditation product | product-listings.md | FTC scrutiny, platform policy violations | Add "not medical advice" disclaimer |
| Y10 | SF Pro font references | index.html, chat-widget.js | Apple font license violation (technical, low enforcement risk) | Remove explicit SF Pro references from font stack |
| Y11 | ebook_builder.py facilitates infringement pipeline | tools/ebook_builder.py | Tool exists to produce derivative works | Repurpose for original content only, or remove |

### GREEN: CLEAN (no issues found)

| # | Item | Status |
|---|------|--------|
| G1 | AI Employee Guide content | Original work, documents own system |
| G2 | Budget Calculator product concept | Original, no third-party content |
| G3 | Meditation app code | Original implementation |
| G4 | Landing page design | Original HTML/CSS, no copied templates detected |
| G5 | Chat widget code | Original implementation |
| G6 | Instagram handle @behikeai | No conflicts found |
| G7 | Service offering concept | Original business model |
| G8 | Instagram icon usage | Compliant with Meta brand guidelines |
| G9 | Referencing business book concepts (not specific text) | Fair use / ideas not copyrightable |
| G10 | ChatGPT conversation data | Kalani's own outputs, compliant with OpenAI terms |

---

## 10. REMEDIATION CHECKLIST

### Before listing ANYTHING on Gumroad:

- [ ] **KILL the Ecommerce Playbook product.** Do not list it. Do not reference it. Do not sell it.
- [ ] **Remove all student names** from student-essays-pet-peeves.md (replace with anonymized labels like in souvenirs file)
- [ ] **Get written consent from students** before using their essays in any commercial content, OR remove all student essay content from the reel pipeline
- [ ] **Add copyright notice** to every product (use template from ip-protection-reference.md Section 8)
- [ ] **Add license terms** to every product and Gumroad listing
- [ ] **Add AI disclosure** to every product ("Created by [author] with assistance from AI tools for [specific uses]")
- [ ] **Rewrite product-listings.md** to remove ALL references to transcribed courses
- [ ] **Rewrite instagram-content-batch-1.md** Posts 1, 5, 6, and 8 to remove references to transcribed courses
- [ ] **Create a privacy policy** and link it from the landing page
- [ ] **Create terms of service** and link it from the landing page
- [ ] **Add `noai, noimageai` meta tag** to landing page and all public HTML
- [ ] **Add anti-AI-training clause** to all ebook/PDF products
- [ ] **Add health disclaimer** to meditation product listing
- [ ] **Remove explicit SF Pro font references** from CSS (keep system font fallbacks)
- [ ] **Remove framework attribution labels** from any customer-facing marketing copy
- [ ] **Do USPTO trademark search** for "Behike" before filing

### Before posting on Instagram:

- [ ] **Rewrite Post 1 Slide 5** (remove "transcribed 368 course videos" reference)
- [ ] **Rewrite Post 6 entirely** (the whole reel is about transcribing courses)
- [ ] **Rewrite Post 8** (remove "distilled 242 ecommerce courses" framing)
- [ ] **Verify all reel briefs based on student essays** have explicit consent or are removed
- [ ] **Remove all student names** from any file that could be accessed or referenced during content production

---

## SUMMARY

The biggest risk in this repo is the Ecommerce Playbook product. It is straightforward copyright infringement with written evidence. If it gets listed and a course creator finds it, Kalani faces a DMCA takedown at minimum and a lawsuit at worst. The marketing copy is literally a confession.

The second biggest risk is the student essay pipeline. Using other people's creative work commercially without consent is both a copyright and privacy issue. If any of these students were in Kalani's class, FERPA adds another layer of liability.

Everything else is fixable with standard legal housekeeping: copyright notices, license terms, AI disclosures, privacy policy, and cleaning up marketing language.

The AI Employee Guide and Budget Calculator are clean products with original content. Those can ship after adding the required legal notices. The meditation app is clean after adding a health disclaimer. The Shopify themes need a review of their actual code files but the concept is clean.

**Bottom line: Two products need major intervention. Everything else needs standard legal packaging. Do not launch until R1-R6 are resolved.**
