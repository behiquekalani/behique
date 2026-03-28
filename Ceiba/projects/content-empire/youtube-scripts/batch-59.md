# YouTube Script Batch 59 — Music: FL Studio, Production, and Building a Producer Brand

---

**Video 1: FL Studio Mixing Chain Basics — The Setup Every Beginner Needs**
**Channel:** Music
**Hook (0-30s):** If your mixes sound muddy, too loud in some areas and thin in others, or just not professional, the problem is almost never the sounds you are using. It is the order of your processing chain and how you are applying it. This video fixes that.
**Intro (30s-2min):** Mixing is the process of taking raw recorded or programmed tracks and making them work together as one coherent piece. It is not about making things louder. It is about making things clearer. In FL Studio, your mixing chain lives in the Mixer. Today I am walking you through a foundational mixing chain that applies to almost every genre, from trap to house to lo-fi. Once you internalize this structure, your mixes will never sound the same way again.
**Main Content:**

**The Signal Flow Concept**
Audio moves through a chain. Each plugin you insert processes what comes before it. Order matters. An EQ before a compressor does a different job than a compressor before an EQ. The general rule: use EQ to remove problem frequencies before compression, use compression to control dynamics, then use EQ again to shape the final tone. This is called the pre-EQ / compression / post-EQ chain.

**Insert Channel Setup in the FL Mixer**
Every track in your pattern should be routed to its own Mixer insert. This is the most important habit in FL Studio. Do not leave everything on Master. When tracks share a channel, you lose individual control. Route each instrument: kick to Insert 1, snare to Insert 2, bass to Insert 3, and so on. This takes five extra minutes and changes everything about how you mix.

**The Core Plugin Stack**
For each insert channel, the baseline chain is: Parametric EQ 2 (high-pass at 20-30Hz to remove sub rumble), Fruity Peak Controller or your compressor of choice, and a limiter on the master. That is the skeleton. Everything else, reverb, saturation, stereo imaging, is added intentionally for specific tracks, not by default.

**Gain Staging**
Mix levels before you reach for a single plugin. If your tracks are peaking at -3dB or lower on each insert, your master bus will have headroom to work with. Most beginner mixes sound bad because everything is running at 0dB before plugins are even applied. Fix the gain first, then process.

**The Master Bus Chain**
Your master bus should have one job: gentle glue and limiting, not heavy processing. Use a compressor set to a slow attack (50ms or higher), a 4-6dB limiter ceiling, and a reference track plugged into a comparison tool. Compare your master to a professional track at the same loudness every ten minutes. Train your ears by comparison, not by assumption.

**CTA:** Subscribe for the next video where I cover sidechain compression, which is probably the single most important technique in modern music production. Drop a comment telling me what genre you produce and I will tailor specific tips to your setup.
**Thumbnail concept:** FL Studio Mixer screenshot with color-coded inserts, a visible EQ plugin open, clean labels. Text overlay: "THE MIXING CHAIN. Build it right."
**Tags:** FL Studio mixing tutorial, FL Studio mixer setup, mixing chain FL Studio, how to mix in FL Studio, FL Studio beginner mixing, gain staging FL Studio, parametric EQ FL Studio, music production tutorial, FL Studio 21 mixing, mixing basics music production

---

**Video 2: Sidechain Compression in FL Studio — The Right Way**
**Channel:** Music
**Hook (0-30s):** That pumping, breathing sound in almost every modern dance track is not an accident and it is not just one plugin. Sidechain compression is a technique that makes your bass and kick work together instead of fighting each other, and it takes about ten minutes to set up correctly in FL Studio.
**Intro (30s-2min):** Sidechain compression is one of those techniques that separates beginner mixes from professional ones. When your kick drum hits, it tells other instruments to briefly reduce in volume. This creates space in the low frequencies, keeps the kick punchy and audible, and gives the entire track an energy that static mixing cannot replicate. There are multiple ways to do this in FL Studio. I am going to show you two: the proper routing method and the Fruity Peak Controller method.
**Main Content:**

**Why Sidechain Exists**
The kick and bass occupy the same frequency range, 60 to 200Hz roughly. When both are loud at the same time, they clash and your mix gets muddy. Sidechain compression ducks the bass every time the kick hits, creating a rhythmic pumping effect. In genre-specific music like house, techno, and trap, this is not just a technical tool. It is a stylistic choice.

**Method 1: Proper Sidechain Routing**
Route your kick drum to a separate Mixer insert that you will use as a sidechain trigger. In the channel you want to duck (your bassline insert), load Fruity Peak Controller or a sidechain-capable compressor like Maximus. Set the sidechain source to the kick insert channel. Adjust attack (how fast the ducking starts) and release (how fast the volume returns). Short attack, medium release for tight pumping. Long attack, long release for subtle glue.

**Method 2: Fruity Peak Controller**
This is FL Studio's native approach. On your bass insert, add Fruity Peak Controller as an effect. Right-click the Volume knob on that same insert and select "Link to controller." Choose the Peak Controller. Now the bass volume responds to the peak of whatever signal the Peak Controller is reading. Route it to read the kick channel. Adjust the base and volume knobs to dial in the depth and recovery of the effect.

**Genre-Specific Sidechain Settings**
House music: heavy pumping, 1:1 ratio with the kick, very audible effect. Lo-fi hip hop: subtle, nearly invisible, just keeping the low end clean. Trap: tight and fast, synced to the hi-hat pattern as much as the kick. Cinematic: extremely slow release, barely perceptible, used for space management rather than rhythmic effect. Know which one you need before you start dialing.

**Common Mistakes**
Sidechaining the entire mix to the kick is a beginner mistake. Only sidechain elements that compete in the same frequency space. Mid-range and high elements usually do not need it. Also avoid over-sidechaining to the point where the bass disappears on the kick hit. You want a dip, not silence. Aim for 3 to 6dB of gain reduction on the sidechain.

**CTA:** Subscribe for the next video on vocal production with AI. Comment below with your favorite genre and I will walk through a sidechain example for it in a future video.
**Thumbnail concept:** FL Studio Mixer with a waveform showing the classic sidechain pumping shape, arrows pointing to the duck and recovery. Text: "WHY YOUR BASS SOUNDS MUDDY. Fix this."
**Tags:** sidechain compression FL Studio, FL Studio sidechain tutorial, how to sidechain in FL Studio, Fruity Peak Controller sidechain, bass and kick FL Studio, FL Studio mixing techniques, pumping effect FL Studio, music production sidechain, FL Studio 21 tutorial, sidechain bass tutorial

---

**Video 3: Vocal Production with AI — From Raw Recording to Polished Track**
**Channel:** Music
**Hook (0-30s):** Raw vocal recordings always sound worse than the final track. Every professional vocal you have heard has been processed, cleaned, tuned, and layered. I am going to show you how to go from a rough vocal take to a finished, radio-quality vocal chain, and where AI fits into that process in 2025.
**Intro (30s-2min):** Vocal production is a multi-step process. Capture, clean, tune, compress, add texture, and place in the mix. Most beginner producers skip steps or do them in the wrong order. AI tools have added a new layer to this workflow that can save hours on tedious tasks like pitch correction, noise removal, and even generating vocal harmonies. This video covers the full chain.
**Main Content:**

**Step 1: Capture and Room Treatment**
The best processing in the world cannot fix a recording made in a bad acoustic environment. Before anything else, address your recording space. A closet full of clothes is better than an empty room with parallel walls. Get the microphone six to eight inches from the source, off-axis slightly to reduce plosives. Record at 24-bit, 44.1kHz minimum. Capture three takes of every phrase.

**Step 2: Cleaning with AI Tools**
RX by iZotope has an AI-powered noise removal tool that isolates vocals from room noise, breath, and handling sounds. Adobe Podcast's Enhance Speech tool is free and processes recordings online using AI. Either tool can turn a mediocre home recording into something workable in under two minutes. Run your raw vocal through one of these before any other processing.

**Step 3: Pitch Correction**
Melodyne is the industry standard for transparent pitch correction. It lets you see the melody visually and adjust individual notes. For a natural sound, use subtle correction. Do not pull every note to dead center. Human imperfection is what makes vocals sound alive. Auto-Tune (or FL Studio's built-in pitch correction) is better for intentional vocal effects where the robotic quality is part of the aesthetic.

**Step 4: The Vocal Chain in the Mixer**
Recommended chain: high-pass EQ (cut everything below 80-100Hz), de-esser (tame harsh sibilance), compression (LA-2A style for natural vocals, heavy limiting for rap), presence boost EQ (3-6kHz range adds clarity), saturation (subtle harmonic content), reverb and delay (send effects, not insert, so you can control blend).

**Step 5: AI-Generated Harmonies**
Tools like Kits.ai and iZotope's Nectar can generate harmony voices from a single vocal recording. Feed it your lead vocal, choose intervals (third below, fifth above), and the AI creates additional vocal layers that sit under the lead. Layer two or three harmony tracks at low volume beneath your lead for a fuller sound without recording additional takes.

**CTA:** Subscribe for the next video on creating sample packs for income. Drop your biggest vocal production struggle in the comments and I will address it directly in a future video.
**Thumbnail concept:** Waveform before and after treatment, side by side. Left: rough, noisy, jagged. Right: clean, processed, polished. Text: "VOCAL PRODUCTION. Raw to ready."
**Tags:** vocal production tutorial FL Studio, how to produce vocals, AI vocal tools music, iZotope RX vocals, Melodyne pitch correction, vocal chain tutorial, home studio vocals, FL Studio vocal mixing, music production vocals 2025, AI music tools 2025

---

**Video 4: How to Create a Sample Pack and Sell It for Passive Income**
**Channel:** Music
**Hook (0-30s):** Sample packs are one of the most underrated income streams for music producers. You make them once. They sell forever. I am going to show you how to put one together, what to include, how to package it, and where to sell it.
**Intro (30s-2min):** If you produce music consistently, you already have the raw material for multiple sample packs. Every loop you made that did not fit a track, every drum hit you designed, every melody you sketched and abandoned, those are sample pack assets. The question is whether you organize them and sell them or leave them sitting in a folder forever. This video makes the case for selling them and walks you through the process.
**Main Content:**

**What Goes Into a Sample Pack**
A useful sample pack contains one or more of the following: drum hits (kick, snare, clap, hi-hat, percussion), drum loops (full bar patterns at multiple BPMs), melody loops (one-bar and two-bar musical phrases), bass loops, one-shots (single playable notes for multiple instruments), FX (risers, impacts, transitions). You do not need all of these. A focused pack with 50 high-quality drum hits outperforms a bloated pack with 300 mediocre sounds.

**Quality Over Quantity**
Every sound in the pack needs to be properly gain staged (peaks around -6 to -3dB), named clearly (Kick_Punchy_120BPM.wav), organized into labeled folders, and free of any copyrighted material. If you sampled anything from a commercial record and used it in a loop, you cannot sell that loop. Original sounds only.

**Packaging and Presentation**
The cover art matters. A professional-looking thumbnail with a clear genre label and BPM range will outsell identical content in a poorly designed wrapper. Use Canva or Figma for the cover. Name the pack clearly: "Dark Trap Drums Vol.1 — 50 Hits, 90-140BPM." Write a short description of the vibe and which DAWs the sounds were tested in.

**Where to Sell**
Splice is the biggest platform but difficult to get on as a new creator. Looperman is free and has an existing user base. Gumroad works for selling directly with no platform cut beyond payment processing fees. Your own website via Shopify or a simple landing page with a payment link is the highest-margin option. Start with Gumroad or Looperman to get initial reviews and traction, then build toward direct sales.

**Marketing the Pack**
Post short videos showing the sounds in action. Use the drum hits in a quick beat, record a screen-capture, post it to Instagram Reels or TikTok with the caption "pack linked in bio." Show people how the sounds work inside a real track. That ten-second video will drive more sales than any product description.

**CTA:** Subscribe for the next video on building a producer brand. Drop a comment telling me what genre you produce and I will give you three sample pack ideas you could build this week.
**Thumbnail concept:** A Gumroad product page mockup showing a sample pack with a revenue number visible. Behind it, a folder structure on a dark desktop. Text: "SELL YOUR SOUNDS. Passive income for producers."
**Tags:** how to sell sample packs, sample pack creation tutorial, make money as a music producer, sell samples online, Gumroad for producers, FL Studio sample pack, passive income music producer, Looperman tips, how to make a drum kit, music producer income

---

**Video 5: How to Build a Producer Brand That Gets You Noticed**
**Channel:** Music
**Hook (0-30s):** Most producers focus ninety percent of their energy on music and ten percent on being known. But there are producers with average skills who are doing four to five figures a month because they understand personal branding. This video is about closing that gap.
**Intro (30s-2min):** Producer branding is not about being fake or performative. It is about being intentional about how you show up, what you consistently communicate, and how easy it is for the right people to find and trust you. In 2025, a producer with a clear brand, consistent online presence, and a few smart content pieces will get more placement opportunities, more sample pack sales, and more custom beat requests than a technically superior producer who is invisible online. Here is how to build it.
**Main Content:**

**Define Your Sound Before Your Visual Identity**
Your brand starts with your music, not your logo. What genre do you make? What is the emotional territory you work in? Dark and cinematic? Energetic and club-ready? Melancholic and lo-fi? Write one sentence that describes your sound as if you were telling a new listener who has never heard you. Every other branding decision should flow from this sentence.

**Your Producer Name and Online Handle**
Pick a name that is easy to say, easy to spell, and available across platforms. Check Instagram, Twitter/X, YouTube, and SoundCloud before you commit. Your handle should be the same everywhere. This is not just convenience, it is discoverability. When someone discovers your music, they should be able to find your full catalog with one search.

**Content Strategy for Producers**
The content that works for producers: process videos (how did you build this beat), reaction videos (what I think about current trends), technique breakdowns (here is how I got that sound), sample pack showcases (hear these sounds in a real beat), and beat breakdowns (stem by stem, explaining every choice). All of these serve the audience of other producers and aspiring producers, which is the right audience to build if you want to sell sample packs, get placements, and grow a music education income stream.

**Consistency Over Volume**
You do not need to post every day. You need to post consistently enough that people who find you once can come back and find new content. One video per week, every week, builds trust faster than five videos in one week followed by a month of silence. Use a simple content calendar. Monday: idea. Wednesday: recording. Friday: posted. That is a sustainable system.

**The Collaboration Network**
Every major producer you admire has a network of other producers, engineers, vocalists, and artists they work with regularly. Start building that network intentionally. Feature other producers in your videos. Comment meaningfully on their work. Reach out with collaboration proposals that benefit both parties. The music industry runs on relationships, not just talent.

**CTA:** Subscribe and hit the bell. My next video covers making money as a producer beyond beat sales, which most producers never even consider as an option. What part of your producer brand do you feel least confident about? Drop it in the comments.
**Thumbnail concept:** Side-by-side split. Left: generic unlabeled beat on SoundCloud, zero plays. Right: branded producer page with consistent visual identity, large play count. Text: "WHY NOBODY KNOWS YOUR NAME."
**Tags:** music producer branding, how to build a producer brand, music producer marketing, producer content strategy, how to grow as a music producer, FL Studio producer brand, music industry for beginners, producer YouTube strategy, make money as producer 2025, producer social media tips
