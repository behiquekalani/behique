# Claude Code for Everyone: Automate Your Life Without Writing Code

Copyright 2026 Behike. All rights reserved.

AI Disclosure: This course was created with the assistance of AI tools. All content has been reviewed, tested, and validated by a human author. Commands and workflows were tested on real systems.

By Behike | $19.99 (Video Course) | $9.99 (Companion PDF Only)

---

## COURSE OVERVIEW

**10 lessons. 12,000+ words of real teaching. Zero fluff.**

This course takes you from "I've never opened a terminal" to "I just automated my entire weekly workflow." Every lesson has real terminal examples with expected output. Every lesson has a common mistakes section. The complexity builds. Lesson 1 is dead simple. Lesson 10 is advanced.

**Target audience:** Non-technical professionals, small business owners, freelancers, content creators, and anyone who uses a computer daily but has never touched the terminal.

**What you will build by the end:** A custom automation system that organizes your files, processes your data, connects to your tools, and runs repeatable workflows with one command.

---

## FULL SCRIPT: LESSON 1

### What Is Claude Code and Why Should You Care
**Runtime: 6 minutes | ~1,000 words**

---

[SCREEN: Black screen with white text: "LESSON 1" then fade to "What Is Claude Code and Why Should You Care"]

[VOICE: Have you ever watched someone use the terminal on their computer and thought, that looks like magic? They type a few words, hit enter, and suddenly files are organized, reports are generated, websites appear out of nowhere. And you think, I would need a computer science degree to do that.]

[SCREEN: Quick montage of terminal commands running, files moving, websites appearing]

[VOICE: You don't. And that's what this course is about. There is a tool called Claude Code. It was built by Anthropic, the AI company. And what it does is simple. It lets you control your computer using plain English. No programming language. No memorizing commands. You just tell it what you want done, and it does it.]

[SCREEN: Claude Code website, anthropic.com/claude-code, scrolling through the main page]

[VOICE: Now, technically, Claude Code was made for software developers. But here's what nobody is talking about. It is the single most powerful tool for people who don't code. Because it removes the entire barrier. You don't need to know Python. You don't need to know what a terminal command is. You just need to know what you want.]

[SCREEN: Split screen. Left side shows a complex Python script. Right side shows someone typing "organize my downloads folder by file type" in Claude Code]

[VOICE: In this course, we're going to go from zero to automating real tasks on your computer. Organizing files. Analyzing data. Building web pages. Connecting to tools like Notion and Google Calendar. Processing invoices. Building your own custom commands. All of it. Using nothing but plain English sentences.]

[SCREEN: Quick preview montage of what's coming in later lessons]

[VOICE: But first, we need to install it. Let's do that right now.]

[SCREEN: Browser open to the Claude Code installation page]

[VOICE: Step one. You need a terminal. The terminal is just an app on your computer where you type text instead of clicking buttons. On Mac, you already have one built in. It's called Terminal, and you can find it in your Applications folder under Utilities. On Windows, you can use PowerShell, which is also built in.]

[SCREEN: Show opening Terminal on Mac from Applications > Utilities. Brief flash of PowerShell on Windows]

[VOICE: But I recommend downloading a terminal called Warp. It's free, it works on both Mac and Windows, and it's designed to be friendly for people who are new to this. I'll leave the link in the course materials. For this course, I'm using Warp.]

[SCREEN: Show warp.dev website, download button, quick install]

[VOICE: Step two. Install Claude Code. Open your terminal. You're going to see a blinking cursor. Don't panic. Just paste this one command.]

[SCREEN: Terminal open, cursor blinking. Show the command being pasted:]

```
npm install -g @anthropic-ai/claude-code
```

[VOICE: If you see an error about npm not being found, you need to install Node.js first. Go to nodejs.org, download the installer, run it, and then try the command again. Node.js is just a piece of software that Claude Code needs to run. Think of it like needing a battery before you can use a remote control.]

[SCREEN: Show nodejs.org download page briefly, then back to terminal]

[VOICE: Hit enter. Let it run. You'll see some text scroll by. That's normal. When it's done, you'll see a success message with a version number.]

[SCREEN: Terminal showing the install process completing]

```
added 1 package in 4s
```

[VOICE: That's it. Claude Code is installed. Now let's start it.]

[SCREEN: Terminal with cursor blinking]

[VOICE: Type the word "claude" in your terminal. Lowercase. Hit enter.]

[SCREEN: Terminal showing:]

```
claude
```

[VOICE: The first time you run it, it will ask you to sign in. You need an Anthropic account with a subscription. For casual use, a few automations per day, the $25 startup plan works fine. If you're going to use it heavily, the $100 max plan is what I use. I'll walk you through the options in the course materials.]

[SCREEN: Show the Claude Code startup screen, the authentication prompt, and a brief view of the Anthropic pricing page]

[VOICE: Once you're signed in, you'll see the Claude Code interface. It looks like a chat window inside your terminal. There's a cursor waiting for you to type something. And here's the beautiful part. You just type what you want in English.]

[SCREEN: Claude Code running, showing the prompt area with the > cursor]

[VOICE: Let's try our first command. I'm going to ask Claude a simple question about my computer.]

[SCREEN: Type into Claude Code:]

```
What files are on my Desktop?
```

[VOICE: I typed "What files are on my Desktop?" in plain English. Watch what happens.]

[SCREEN: Claude Code processes the request. It runs an ls command internally, then displays a formatted list of files on the Desktop]

```
I found the following files on your Desktop:

  Documents/
  project-notes.txt
  invoice-march.pdf
  vacation-photo.jpg
  budget-2026.xlsx
  readme.md

6 items total: 1 folder, 5 files.
```

[VOICE: It listed every file on my Desktop. I didn't type any command. I didn't need to know that the actual terminal command for this is "ls ~/Desktop". Claude figured that out for me. It translated my English into the right command, ran it, and gave me a clean answer.]

[SCREEN: Highlight the natural language input vs. the clean output]

[VOICE: Let's try one more. I want to know how much storage space is left on my computer.]

[SCREEN: Type into Claude Code:]

```
How much free disk space do I have?
```

[SCREEN: Claude Code runs the appropriate system command and returns:]

```
Your disk usage:
  Total: 494 GB
  Used: 287 GB (58%)
  Free: 207 GB (42%)

You have plenty of space available.
```

[VOICE: Done. Two questions. Two answers. No technical knowledge required. That is Claude Code.]

[SCREEN: Clean summary slide]

[VOICE: Let's recap what we just did. We installed a terminal. We installed Claude Code with one command. We launched it by typing "claude". And we asked it two questions in plain English and got useful answers. That's the foundation. Every single lesson from here builds on this exact pattern. You tell Claude what you want. It does it.]

**Common Mistakes in Lesson 1:**

1. **"npm not found" error.** You skipped installing Node.js. Go to nodejs.org, download the LTS version, install it, restart your terminal, then try again.
2. **Using the wrong terminal.** On Windows, use PowerShell or Warp, not the old Command Prompt (cmd). Command Prompt doesn't handle modern tools well.
3. **Typing "Claude" with a capital C.** The command is lowercase: `claude`. Case matters in the terminal.
4. **Forgetting to restart the terminal after installing Node.js.** Close your terminal app completely, reopen it, then run the install command.

[SCREEN: Text on screen: "Next: Lesson 2 - Talking to Your Computer"]

[VOICE: In the next lesson, we're going to go deeper. I'll show you how to give Claude instructions that actually get things done. Renaming files, creating folders, moving things around. All by describing what you want. No commands. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 2

### Talking to Your Computer
**Runtime: 7 minutes | ~1,100 words**

---

[SCREEN: Black screen with white text: "LESSON 2" then fade to "Talking to Your Computer"]

[VOICE: In lesson one, we installed Claude Code and asked it a couple of questions. But asking questions is just the beginning. The real power is giving it instructions. Telling it to do things. And the way you tell it matters.]

[SCREEN: Claude Code open in terminal, cursor blinking]

[VOICE: Think of Claude Code like a very smart assistant who just started today. If you tell them "do the thing with the files," they'll stare at you. But if you tell them "take every PDF in the Downloads folder and move it to a new folder called Invoices," they'll nail it. Same thing here. The more specific you are, the better the result.]

[SCREEN: Split screen comparison. Left side: vague prompt. Right side: specific prompt]

[VOICE: Let me show you the difference. I have a file on my Desktop called "notes.txt". I want to rename it. Here's the vague way.]

[SCREEN: Type into Claude Code:]

```
rename my notes file
```

[SCREEN: Claude Code responds:]

```
I found a file called notes.txt on your Desktop. What would you
like to rename it to?
```

[VOICE: See? It found the file, but it's asking me a follow-up question because I wasn't specific enough. That works, but it's slow. Now watch the specific way.]

[SCREEN: Type into Claude Code:]

```
Rename the file notes.txt on my Desktop to meeting-notes-march-2026.txt
```

[SCREEN: Claude Code responds:]

```
Done. Renamed:
  ~/Desktop/notes.txt → ~/Desktop/meeting-notes-march-2026.txt
```

[VOICE: One sentence. Done. No follow-up needed. This is the core skill of this entire course. Learning to describe what you want clearly. Not perfectly. Not technically. Just clearly.]

[SCREEN: Text overlay: "Clear > Perfect"]

[VOICE: Let me give you a framework. When you're telling Claude to do something, try to answer three questions in your sentence. What do you want done? Where should it happen? What should the result look like? You don't need to hit all three every time, but the more of them you include, the faster Claude works.]

[SCREEN: Three-question framework displayed as clean text:
1. WHAT do you want done?
2. WHERE should it happen?
3. What should the RESULT look like?]

[VOICE: Let's practice. I want to create a new folder structure for a project I'm working on.]

[SCREEN: Type into Claude Code:]

```
Create a folder on my Desktop called "Client Project" with three
subfolders inside it: Assets, Documents, and Deliverables
```

[SCREEN: Claude Code runs mkdir commands and responds:]

```
Created the following structure:

  ~/Desktop/Client Project/
    Assets/
    Documents/
    Deliverables/

3 folders created inside "Client Project".
```

[VOICE: Three folders, nested correctly, created in about two seconds. Now let me show you something even more useful. Follow-up messages.]

[SCREEN: Same Claude Code session continues]

[VOICE: Claude Code remembers the conversation. So I don't need to repeat myself. I can just keep building on what I said before.]

[SCREEN: Type into Claude Code:]

```
Now move all the PDFs from my Downloads folder into the Documents
subfolder
```

[SCREEN: Claude Code scans Downloads, finds PDFs, moves them:]

```
Found 4 PDF files in Downloads. Moved them to
~/Desktop/Client Project/Documents/:

  contract-v2.pdf
  invoice-0042.pdf
  project-brief.pdf
  requirements.pdf
```

[VOICE: Four PDFs moved. I didn't tell it where the Documents folder was. It remembered from our previous message. This is what makes Claude Code feel like a conversation instead of a command line. You're building context as you go.]

[SCREEN: Highlight that the session has memory within the conversation]

[VOICE: Let me show you one more pattern that will save you hours. Multi-step instructions. You can give Claude Code a series of steps in one message.]

[SCREEN: Type into Claude Code:]

```
Do these three things:
1. Find all image files (jpg, png) in my Downloads folder
2. Create a folder called "Photos" on my Desktop if it doesn't exist
3. Move all those images into the Photos folder and rename them
   using the format photo-001.jpg, photo-002.jpg, and so on
```

[SCREEN: Claude Code processes all three steps:]

```
Step 1: Found 8 image files in Downloads (5 .jpg, 3 .png)
Step 2: Created ~/Desktop/Photos/
Step 3: Moved and renamed all 8 files:

  photo-001.jpg (was: IMG_4521.jpg)
  photo-002.jpg (was: screenshot-2026.png)
  photo-003.jpg (was: DSC_0087.jpg)
  photo-004.png (was: diagram.png)
  photo-005.jpg (was: headshot.jpg)
  photo-006.png (was: logo-v3.png)
  photo-007.jpg (was: product-photo.jpg)
  photo-008.jpg (was: banner-draft.jpg)

All images organized and renamed.
```

[VOICE: Eight files. Found, moved, and renamed. In one message. No manual clicking and dragging. No renaming one by one. Just describe the process and let it work.]

[SCREEN: Before/after comparison. Messy Downloads folder vs. clean Photos folder]

[VOICE: Now, let me talk about something important. Permissions. When Claude Code is about to do something that changes your files, like moving, renaming, or deleting, it will ask for your permission first. You'll see a prompt that says something like "Allow this action?" and you can say yes or no.]

[SCREEN: Show a Claude Code permission prompt:]

```
Claude wants to run: mv ~/Downloads/*.pdf ~/Desktop/Client\ Project/Documents/

Allow? [y/n]
```

[VOICE: This is a safety net. Nothing happens without your approval. If you're comfortable and you want Claude to stop asking for every single action, you can press Shift+Tab to turn on "accept edits" mode. This lets Claude run multiple steps without pausing each time. I use this when I know exactly what I've asked for and I trust the operation.]

[SCREEN: Show pressing Shift+Tab and the mode indicator appearing]

[VOICE: One last thing before we move on. If Claude does something you didn't want, you can always undo it. Just tell it.]

[SCREEN: Type into Claude Code:]

```
Undo that last action. Move the files back to Downloads with their
original names.
```

[SCREEN: Claude Code reverses the operation]

[VOICE: It remembers what it did and can reverse it. You're never locked in.]

**Common Mistakes in Lesson 2:**

1. **Being too vague.** "Fix my files" tells Claude nothing. "Move all .pdf files from Downloads to Desktop/Invoices" tells it everything.
2. **Forgetting context resets between sessions.** Claude remembers within a conversation, but if you close the terminal and reopen it, the context is gone. Start fresh.
3. **Saying yes to something you don't understand.** Read the permission prompt. It shows you the exact command Claude wants to run. If it looks wrong, say no and clarify your request.
4. **Trying to undo after closing the session.** Claude can only undo within the same conversation. If you closed the terminal, you'll need to manually fix things or give Claude explicit instructions about what to reverse.

[SCREEN: Text on screen: "Next: Lesson 3 - File Organization on Autopilot"]

[VOICE: In the next lesson, we're putting this to real use. We're going to take a messy folder and let Claude organize the entire thing automatically. Not just by file type, but by actually reading what's inside the files. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 3

### File Organization on Autopilot
**Runtime: 7 minutes | ~1,100 words**

---

[SCREEN: Black screen with white text: "LESSON 3" then fade to "File Organization on Autopilot"]

[VOICE: Your Downloads folder is a disaster. Don't feel bad about it. Everyone's is. Random PDFs mixed with screenshots mixed with spreadsheets mixed with files named "final-final-v3-REAL.docx". In this lesson, we're going to fix that in about 60 seconds.]

[SCREEN: Show a cluttered folder with 25+ files of various types, messy filenames]

[VOICE: First, make sure your terminal is pointed at the right folder. When Claude Code starts, it operates from whatever folder your terminal is in. So if you want it to work on your Downloads folder, you need to navigate there first.]

[SCREEN: Terminal showing:]

```
cd ~/Downloads
claude
```

[VOICE: That "cd" command means "change directory." It moves your terminal into the Downloads folder. Now when Claude starts, it can see everything in there. Let's verify.]

[SCREEN: Type into Claude Code:]

```
List all the files in this folder and tell me how many of each
type there are
```

[SCREEN: Claude Code responds:]

```
Found 27 files in this folder:

  PDF files:     8
  Images:        6 (4 .jpg, 2 .png)
  Spreadsheets:  4 (3 .xlsx, 1 .csv)
  Documents:     3 (.docx)
  Archives:      2 (.zip)
  Other:         4 (2 .json, 1 .txt, 1 .md)
```

[VOICE: 27 files. Eight different types. Normally, you would spend 10 minutes dragging these into folders one by one. Let's do it in one sentence.]

[SCREEN: Type into Claude Code:]

```
Organize all files into subfolders by type: PDFs, Images,
Spreadsheets, Documents, Archives, and Other. Keep the original
filenames.
```

[SCREEN: Claude Code creates folders and moves files:]

```
Created 6 folders and organized 27 files:

  PDFs/          (8 files)
  Images/        (6 files)
  Spreadsheets/  (4 files)
  Documents/     (3 files)
  Archives/      (2 files)
  Other/         (4 files)

All files moved. Original filenames preserved.
```

[VOICE: Done. 27 files sorted into 6 folders. But this is the basic version. Claude can do something way more interesting. It can read what's inside the files and organize them by content, not just file extension.]

[SCREEN: Type into Claude Code:]

```
Look inside all the PDFs and organize them into subfolders based
on what they are: invoices in one folder, contracts in another,
and reports in a third. If you can't tell what a PDF is, put it
in a "Review" folder.
```

[SCREEN: Claude Code reads each PDF and reorganizes:]

```
Analyzed 8 PDFs by content:

  PDFs/Invoices/    (3 files)
    invoice-march-2026.pdf
    invoice-0042.pdf
    vendor-payment.pdf

  PDFs/Contracts/   (2 files)
    service-agreement.pdf
    nda-signed.pdf

  PDFs/Reports/     (2 files)
    q1-sales-report.pdf
    marketing-analysis.pdf

  PDFs/Review/      (1 file)
    scan-003.pdf  (couldn't determine type)
```

[VOICE: It opened each PDF, read the content, figured out whether it was an invoice, a contract, or a report, and sorted them accordingly. The one it couldn't figure out went into a Review folder so you can check it manually. This is not just file sorting. This is intelligent document processing.]

[SCREEN: Side by side of the before and after folder structure]

[VOICE: Now let me show you something practical that I use every single week. A cleanup command you can run anytime.]

[SCREEN: Type into Claude Code:]

```
Do a full cleanup of this folder:
1. Organize files by type into subfolders
2. Find and flag any duplicate files (same content, different names)
3. Rename files that have messy names (like IMG_4521 or
   Screenshot 2026-03-15) to something descriptive based on
   their content
4. Give me a summary of what you did when you're done
```

[SCREEN: Claude Code runs through all four steps and returns:]

```
Cleanup complete. Here's what happened:

ORGANIZED: 27 files into 6 type-based folders
DUPLICATES FOUND: 2 pairs
  - budget-2026.xlsx and budget-2026 (1).xlsx (identical)
  - report-draft.pdf and report-draft-copy.pdf (identical)
  Kept the originals, moved duplicates to Duplicates/ folder

RENAMED: 4 files
  - IMG_4521.jpg → product-photo-white-tshirt.jpg
  - Screenshot 2026-03-15.png → slack-conversation-march.png
  - DSC_0087.jpg → outdoor-team-photo.jpg
  - download.pdf → bank-statement-february-2026.pdf

Your Downloads folder is now organized with 0 loose files.
```

[VOICE: It organized, found duplicates, renamed files based on what's actually in them, and gave a clean summary. All from one message. This is the kind of thing that would take you 30 minutes to do manually. Claude did it in under a minute.]

[SCREEN: Clean summary slide]

[VOICE: One thing I want you to notice. Claude didn't delete the duplicates. It moved them to a separate folder. This is the safe approach. You review them, and you decide what to delete. Always tell Claude what to do with duplicates rather than assuming it should delete them.]

**Common Mistakes in Lesson 3:**

1. **Not starting Claude from the right folder.** If Claude is running from your home directory, it can still access Downloads, but it's slower and the paths get confusing. Navigate to the folder first with `cd`, then start Claude.
2. **Telling Claude to "delete duplicates" without reviewing them first.** Sometimes two files have the same content but you need both in different locations. Always move duplicates to a review folder first.
3. **Running organization on a folder with thousands of files.** Start with a test folder of 20-30 files. Once you see how Claude organizes, then point it at the big folder. This way you can correct its approach before it moves 500 files.
4. **Forgetting that Claude renames files permanently.** If you ask Claude to rename files, write down or screenshot the original names first. Or tell Claude to create a log file with the old and new names.

[SCREEN: Text on screen: "Next: Lesson 4 - Working with Data"]

[VOICE: In the next lesson, we're going to work with real data. CSV files, Excel sheets, the kind of stuff you normally open in a spreadsheet and spend an hour crunching numbers in. Claude is going to do that analysis in seconds and turn it into a presentation. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 4

### Working with Data
**Runtime: 8 minutes | ~1,200 words**

---

[SCREEN: Black screen with white text: "LESSON 4" then fade to "Working with Data"]

[VOICE: If you've ever opened a massive spreadsheet and thought "I have no idea where to start," this lesson is for you. Claude Code can read CSV files, Excel spreadsheets, JSON data, and more. It can analyze them, find patterns, calculate totals, and generate reports. All without you opening a single spreadsheet app.]

[SCREEN: Show a folder with several data files: sales-data.csv, expenses-q1.xlsx, customer-list.json]

[VOICE: Here's the key thing that makes Claude different from tools like ChatGPT or the Claude web app for data work. Those tools have upload limits. You paste a CSV and it can handle maybe a few hundred rows before it starts hallucinating or losing track. Claude Code operates directly on your file system. It can read a 50,000-row spreadsheet because it writes actual Python code to process it. It doesn't try to hold the whole thing in memory the way a chatbot does.]

[SCREEN: Navigate to the data folder and start Claude:]

```
cd ~/Documents/financial-data
claude
```

[VOICE: I have a folder with financial data for a small business. Multiple Excel files, a couple of CSVs. Let's start simple.]

[SCREEN: Type into Claude Code:]

```
Read the file sales-data.csv and give me a summary. How many
rows? What columns does it have? What's the total revenue?
```

[SCREEN: Claude Code reads the file, writes a quick Python script, runs it:]

```
Sales Data Summary:
  Rows: 1,847
  Columns: 8 (Date, Product, Category, Quantity, Unit Price,
           Revenue, Region, Sales Rep)

  Total Revenue: $284,392.50
  Date Range: January 1 to March 31, 2026
  Unique Products: 42
  Regions: 4 (North, South, East, West)
```

[VOICE: In five seconds, Claude read almost 2,000 rows, identified the structure, calculated the total revenue, and gave us the range and breakdown. Now let's ask something more useful.]

[SCREEN: Type into Claude Code:]

```
What are the top 5 products by revenue? And which region is
performing worst?
```

[SCREEN: Claude Code processes and responds:]

```
Top 5 Products by Revenue:

  1. Premium Widget      $38,420   (13.5% of total)
  2. Standard Kit        $31,890   (11.2%)
  3. Pro Bundle          $28,750   (10.1%)
  4. Enterprise License  $24,100   (8.5%)
  5. Starter Pack        $19,340   (6.8%)

Worst Performing Region:
  South - $48,220 (17% of total revenue)
  vs. best region East at $92,150 (32.4%)

  South has 40% fewer transactions than the average region.
```

[VOICE: Now I know which products make the most money and which region needs attention. This kind of analysis would take you 20 minutes in Excel. Let's take it further.]

[SCREEN: Type into Claude Code:]

```
Now do this across all the Excel files in this folder. Read every
file, consolidate the data, and give me:
1. Total spend by category
2. Month-over-month revenue trend
3. The single biggest expense
Then create a PowerPoint presentation with these findings.
```

[SCREEN: Claude Code processes multiple files, creates analysis:]

```
Processed 4 files: sales-data.csv, expenses-q1.xlsx,
marketing-spend.xlsx, payroll-summary.xlsx

TOTAL SPEND BY CATEGORY:
  Payroll:     $142,000  (49.8%)
  Marketing:    $68,500  (24.0%)
  Operations:   $45,200  (15.9%)
  Software:     $18,900   (6.6%)
  Travel:       $10,400   (3.7%)

MONTH-OVER-MONTH REVENUE:
  January:   $82,100
  February:  $94,350  (+14.9%)
  March:     $107,940 (+14.4%)

BIGGEST SINGLE EXPENSE:
  Q1 Social Media Campaign - $28,500 (Marketing)

Presentation created: financial-summary-q1.pptx
  Slide 1: Executive Summary
  Slide 2: Revenue Trends (bar chart)
  Slide 3: Spending Breakdown (pie chart)
  Slide 4: Top Growth Areas
  Slide 5: Recommendations
```

[VOICE: Claude read four different files, combined the data, calculated everything, and built a five-slide PowerPoint with charts. This is the kind of task that would normally take an analyst half a day. And we did it with one message.]

[SCREEN: Open the PowerPoint briefly to show the charts and layout]

[VOICE: Let me show you one more trick that's incredibly useful for anyone who works with data regularly. You can ask Claude to watch for patterns you wouldn't notice manually.]

[SCREEN: Type into Claude Code:]

```
Look at the sales data and find anything unusual or surprising.
Outliers, sudden spikes, patterns I should know about.
```

[SCREEN: Claude Code analyzes and responds:]

```
Interesting findings:

1. SPIKE: March 14 had 3x normal daily revenue ($12,400 vs
   $3,600 average). 80% came from Enterprise License sales
   in the East region. Possible bulk order or promotion.

2. PATTERN: Tuesday and Wednesday consistently have 30% higher
   sales than Monday. Weekend sales are near zero.

3. OUTLIER: Sales rep "Jordan K." has the highest average deal
   size ($890) but the lowest volume (47 deals). Opposite of
   "Morgan T." who has the highest volume (198 deals) but
   lowest average ($210).

4. TREND: The "Starter Pack" is declining month over month
   (-8% per month) while "Pro Bundle" is growing (+22%).
   Consider promotional shift.
```

[VOICE: This is the kind of insight that lives inside your data but nobody finds because nobody has time to dig that deep. Claude does. And it takes seconds, not hours.]

**Common Mistakes in Lesson 4:**

1. **Giving Claude a corrupted file.** If your Excel file is open in another app, Claude might not be able to read it. Close the file in Excel or Numbers first.
2. **Not specifying what you mean by "analyze."** "Analyze this data" is too vague. Say what you want: totals, trends, outliers, comparisons. The more specific your question, the more useful the answer.
3. **Expecting perfect charts in PowerPoint.** Claude generates functional presentations, but they won't look like a designer made them. Use them as a starting point and polish the formatting in PowerPoint or Google Slides.
4. **Forgetting to verify the numbers.** Spot-check a few totals manually, especially the first time you use Claude on important financial data. Trust but verify.

[SCREEN: Text on screen: "Next: Lesson 5 - Automating Repetitive Tasks"]

[VOICE: Next lesson, we're going to take the boring stuff you do every week and turn it into one-click automations. Batch renaming, file conversion, multi-step workflows. The stuff you keep saying you'll get around to automating. We're doing it now.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 5

### Automating Repetitive Tasks
**Runtime: 7 minutes | ~1,000 words**

---

[SCREEN: Black screen with white text: "LESSON 5" then fade to "Automating Repetitive Tasks"]

[VOICE: Here's the thing about repetitive tasks. You know you should automate them. But learning a scripting language just to rename 50 files feels like overkill. So you keep doing it by hand. This lesson fixes that. You're going to describe the process in English, and Claude builds the automation for you.]

[SCREEN: Show a folder full of files with ugly names: IMG_4521.jpg, DSC_0012.jpg, photo(1).jpg, etc.]

[VOICE: Let's start with the most common request. Batch renaming. I have 20 photos from a product shoot. The camera named them IMG_4521, IMG_4522, and so on. I need them named product-001, product-002, sequential, clean.]

[SCREEN: Type into Claude Code:]

```
Rename all .jpg files in this folder using the pattern
product-001.jpg, product-002.jpg, and so on. Keep them in order
by the original filename.
```

[SCREEN: Claude Code processes:]

```
Renamed 20 files:

  IMG_4521.jpg → product-001.jpg
  IMG_4522.jpg → product-002.jpg
  IMG_4523.jpg → product-003.jpg
  ...
  IMG_4540.jpg → product-020.jpg

20 files renamed successfully.
```

[VOICE: Twenty files. Done. Now let's add a step. I want to resize these for my website. They're all 4000 pixels wide, and I need them at 1080 pixels.]

[SCREEN: Type into Claude Code:]

```
Resize all the product photos to 1080px wide. Keep the aspect
ratio. Save them in a new folder called "web-ready".
```

[SCREEN: Claude Code writes and runs a Python script:]

```
Created folder: web-ready/
Resized 20 images to 1080px wide (aspect ratio preserved):

  web-ready/product-001.jpg  (4000x3000 → 1080x810)
  web-ready/product-002.jpg  (4000x3000 → 1080x810)
  ...

Original files untouched. Web-ready versions saved separately.
Average file size reduction: 4.2MB → 380KB (91% smaller)
```

[VOICE: Notice something important. Claude kept the originals untouched and created a separate folder for the resized versions. That's the safe default. You still have your high-resolution originals. And the web versions are 91% smaller, which means your website loads faster.]

[SCREEN: Compare file sizes visually]

[VOICE: Now let me show you file format conversion. You don't need to install any extra software for this. Claude writes the code to handle it.]

[SCREEN: Type into Claude Code:]

```
Convert all PNG screenshots in my Desktop/Screenshots folder to
JPG format. Reduce quality to 80% to save space. Put them in a
new folder called Compressed.
```

[SCREEN: Claude Code processes:]

```
Converted 12 PNG files to JPG (80% quality):

  Screenshots/Compressed/
    screenshot-01.jpg  (2.4MB → 340KB)
    screenshot-02.jpg  (1.8MB → 280KB)
    ...

Total space saved: 22.6MB → 3.8MB (83% reduction)
Original PNG files preserved in Screenshots/
```

[VOICE: 83% space saved. No app installed. No subscription to a conversion tool. Claude wrote a Python script, ran it, and cleaned up after itself.]

[SCREEN: Type into Claude Code:]

```
Now take everything we just did and write me a script I can
run anytime. It should:
1. Look in ~/Desktop/New-Products/ for any new photos
2. Rename them sequentially
3. Resize to 1080px
4. Save web-ready versions in ~/Desktop/Web-Ready/
Call it process-photos.sh
```

[SCREEN: Claude Code creates the script:]

```
Created: process-photos.sh

To run it anytime, just open your terminal and type:
  bash ~/process-photos.sh

It will automatically process any new photos in New-Products/
and output web-ready versions.
```

[VOICE: Now you have a reusable script. Every time you get new product photos, you drop them in the New-Products folder, run one command, and they come out renamed, resized, and ready for your website. That is automation. You described the process once. Now it runs forever.]

**Common Mistakes in Lesson 5:**

1. **Running batch operations on the wrong folder.** Always double check which folder you're in with `pwd` before running any bulk rename or conversion. There's no "undo all" for 200 renamed files.
2. **Not keeping originals.** Always tell Claude to preserve the originals when doing conversions or resizes. Use phrases like "save to a new folder" or "keep the originals untouched."
3. **Assuming Claude has image editing software installed.** Claude writes Python code to handle images using libraries like Pillow. If it hits an error about a missing library, just say "install whatever you need" and it will handle it.
4. **Forgetting about file permissions.** On Mac, some folders like Documents or Desktop might have privacy restrictions. If Claude says "permission denied," go to System Settings > Privacy & Security > Files and Folders and grant your terminal access.

[SCREEN: Text on screen: "Next: Lesson 6 - Building Simple Web Pages"]

[VOICE: Next lesson, we're building a website. You describe what you want, Claude builds it, and you preview it in your browser. No HTML knowledge needed. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 6

### Building Simple Web Pages
**Runtime: 7 minutes | ~1,100 words**

---

[SCREEN: Black screen with white text: "LESSON 6" then fade to "Building Simple Web Pages"]

[VOICE: You don't need to know HTML. You don't need to know CSS. You don't need Squarespace or Wix or a $30/month subscription. You can describe a website in English, and Claude will build it for you. Then you preview it in your browser. Let me show you how.]

[SCREEN: Empty terminal, ready to start]

[VOICE: Let's create a project folder and start Claude from there.]

[SCREEN: Terminal showing:]

```
mkdir ~/Desktop/my-website
cd ~/Desktop/my-website
claude
```

[VOICE: Now, I'm going to describe the website I want. Watch how specific I get. Remember the framework from Lesson 2. What, where, and what should the result look like.]

[SCREEN: Type into Claude Code:]

```
Build me a personal portfolio website with these sections:
- A hero section with my name "Alex Rivera" and tagline
  "Freelance Designer & Photographer"
- An About section with placeholder text
- A portfolio grid showing 6 project thumbnails
  (use placeholder images)
- A contact section with a simple form
  (name, email, message)
- Dark theme, modern, clean typography
- Make it responsive so it looks good on phones
```

[SCREEN: Claude Code builds the site, showing files being created:]

```
Created your portfolio website:

  index.html    - Main page structure
  style.css     - Dark theme styling
  script.js     - Form handling and smooth scrolling

To preview it, open index.html in your browser:
  open index.html

Or I can start a local server:
  python3 -m http.server 8000
  Then visit http://localhost:8000
```

[VOICE: Claude created three files. The HTML structure, the CSS styling, and a small JavaScript file for the contact form. Let's see what it looks like.]

[SCREEN: Browser opens showing the website. Dark theme, clean layout, all sections visible]

[VOICE: That's a full portfolio website. Dark theme, responsive, working contact form. Built in about 30 seconds. Now here's where it gets fun. I don't like the color scheme. I want to change it.]

[SCREEN: Type into Claude Code:]

```
Change the accent color from blue to a warm orange. Make the
fonts bigger. Add a subtle gradient to the hero section.
```

[SCREEN: Claude updates the CSS, browser refreshes:]

```
Updated style.css:
  - Accent color: #2196F3 → #FF6B35
  - Base font size: 16px → 18px
  - Hero gradient: dark charcoal to warm black

Refresh your browser to see changes.
```

[VOICE: I described the changes in English. Claude updated the CSS. I refresh my browser and it's exactly what I asked for. No need to learn what "hex codes" or "font-size" mean. Just describe what you see and what you want different.]

[SCREEN: Show the updated website with orange accents and bigger fonts]

[VOICE: Let me show you another common use case. Landing pages. If you run a small business or you're launching a product, you need a landing page. Normally you'd pay someone $500 to make one, or spend a weekend fighting with a template.]

[SCREEN: Type into Claude Code:]

```
Build a product landing page for a digital course called
"Photography Basics". Include:
- A hero with the course title and a "Buy Now" button
- 3 feature cards: "30+ Video Lessons", "Lifetime Access",
  "Certificate Included"
- A pricing section showing $49.99
- Student testimonials section (use 3 fake testimonials)
- A FAQ section with 5 questions and answers about the course
- Light theme, Apple-style minimalism
```

[SCREEN: Claude Code builds it, preview shows a clean landing page]

[VOICE: A complete landing page. Hero, features, pricing, testimonials, FAQ. All built in under a minute. And if you want to ship this for real, you can host it for free on Netlify or GitHub Pages. Claude can even help you deploy it.]

[SCREEN: Type into Claude Code:]

```
Add a mobile menu that collapses on small screens. And make the
Buy Now button link to https://gumroad.com/my-product
```

[SCREEN: Claude Code updates the files]

[VOICE: Every change is a conversation. You see something you want different, you say it. Claude updates it. You refresh. This loop, describe, update, refresh, is how professional developers work with AI right now. You're doing the same thing. The only difference is you're describing in English instead of writing code.]

**Common Mistakes in Lesson 6:**

1. **Expecting a production-ready website.** What Claude builds is a great starting point. For a real business website, you'll want a designer to review the layout and a developer to add proper hosting. But for portfolios, side projects, and prototypes, it works as-is.
2. **Forgetting to test on mobile.** Claude says "responsive" but always check. Open your browser's developer tools (right-click, Inspect, toggle device toolbar) to see how it looks on a phone.
3. **Making too many changes at once.** If you give Claude 15 changes in one message, it might miss some. Give 3-4 changes at a time, verify, then continue.
4. **Not saving your work.** The files are on your computer, but they're not backed up. Copy the folder somewhere safe, or let Claude set up a git repository for version control.

[SCREEN: Text on screen: "Next: Lesson 7 - Connecting to Notion, Calendar, and Email"]

[VOICE: Next lesson is where this course levels up. We're going to connect Claude Code to your actual tools, Notion, Google Calendar, Gmail, using something called MCP. This is the biggest unlock in the entire course. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 7

### Connecting to Notion, Calendar, and Email with MCP
**Runtime: 9 minutes | ~1,200 words**

---

[SCREEN: Black screen with white text: "LESSON 7" then fade to "Connecting to Notion, Calendar, and Email"]

[VOICE: Everything we've done so far has been local. Files on your computer. Folders on your Desktop. That's useful, but the real power comes when Claude can reach outside your machine. Talk to your Notion workspace. Read your Google Calendar. Draft emails in Gmail. That's what MCP does.]

[SCREEN: Diagram showing Claude Code in the center, with arrows connecting to Notion, Gmail, Google Calendar, Slack]

[VOICE: MCP stands for Model Context Protocol. Think of it like a USB port for AI. It's a standard way for Claude Code to plug into other tools and services. Without MCP, Claude is limited to your local files. With MCP, it can access almost any app that has an API.]

[SCREEN: Show mcp.zapier.com website]

[VOICE: The easiest way to set up MCP is through Zapier. They provide pre-built connections to thousands of apps. You don't need to write any code. You just pick which tools you want Claude to access, give it permission, and paste one command into your terminal. Let me walk you through it step by step.]

[SCREEN: Step-by-step walkthrough of Zapier MCP setup]

[VOICE: Step one. Go to mcp.zapier.com. Create an account if you don't have one. Step two. Click "New MCP Server." For the client, select Claude Code. Give it a name like "My Tools." Step three. Click "Add Tools." Search for Notion. Select the Notion tools you want, things like "read pages," "create pages," "update database." Click "Add Tools."]

[SCREEN: Show adding Notion tools in Zapier, the permission screen]

[VOICE: Notion will ask you to grant access. Pick which workspace and which pages Claude should be able to see. You control this. Claude only sees what you explicitly share.]

[SCREEN: Show the Notion permission dialog]

[VOICE: Step four. Once the tools are added, Zapier gives you a command to copy. It looks something like this.]

[SCREEN: Show the copy command:]

```
claude mcp add zapier -- npx -y @anthropic-ai/mcp-remote https://mcp.zapier.com/api/mcp/s/YOUR-KEY-HERE
```

[VOICE: Paste that into your terminal and hit enter. That's it. Claude Code now has access to Notion. To verify it worked, run this.]

[SCREEN: Terminal showing:]

```
claude mcp list
```

```
MCP Servers:
  zapier  (connected, 24 tools available)
```

[VOICE: 24 tools available. That means Claude can read, write, and search your Notion workspace. Now let's use it.]

[SCREEN: Start Claude Code and type:]

```
Fetch all pages from my Notion workspace that have the status
"Not Started" in my Content Pipeline database
```

[SCREEN: Claude Code queries Notion and responds:]

```
Found 5 pages with status "Not Started":

  1. "How to Use AI for Product Research"
  2. "Weekly Newsletter Issue #12"
  3. "Client Onboarding Checklist"
  4. "Social Media Calendar for April"
  5. "eBay Listing Template"

Database: Content Pipeline
Workspace: My Workspace
```

[VOICE: Claude just reached into your Notion, found your content pipeline, and pulled back every item that hasn't been started. Now watch what happens when I tell it to actually write the content.]

[SCREEN: Type into Claude Code:]

```
Take the first article, "How to Use AI for Product Research."
Research the topic, write a 1,000-word article, and save it
back to Notion. Update the status to "Done."
```

[SCREEN: Claude Code processes, writes, and updates Notion:]

```
Completed:
  - Researched topic via web search
  - Wrote 1,042-word article with 5 sections
  - Saved article body to Notion page
  - Updated status: "Not Started" → "Done"

Article is now live in your Content Pipeline.
```

[VOICE: It wrote the article and pushed it directly into Notion. No copy-pasting. No switching between apps. One command, done.]

[SCREEN: Show the updated Notion page with the article and "Done" status]

[VOICE: Now let me add Google Calendar and Gmail. Same process. Go back to Zapier, add Google Calendar tools and Gmail tools to your MCP server. Grant permissions. The command you already ran covers it because all tools go through the same server.]

[SCREEN: Show adding Gmail and Calendar tools in Zapier]

[VOICE: Once those are connected, you can do things like this.]

[SCREEN: Type into Claude Code:]

```
Check my Google Calendar for tomorrow. List all meetings with
their times and attendees.
```

[SCREEN: Claude Code responds:]

```
Tomorrow (March 23, 2026):

  9:00 AM - Team Standup (15 min)
    Attendees: You, Sarah M., David K.

  11:00 AM - Client Review (1 hour)
    Attendees: You, Lisa from Acme Corp

  2:30 PM - Design Feedback Session (30 min)
    Attendees: You, Jordan P.

3 meetings total. 1h 45m of meeting time.
```

[VOICE: Now combine them.]

[SCREEN: Type into Claude Code:]

```
Draft an email to Lisa from Acme Corp summarizing what we
discussed in last week's meeting. Check my Notion for the
meeting notes from that page, use those details. Don't send
it, just create a draft in Gmail.
```

[SCREEN: Claude Code pulls from Notion, drafts in Gmail:]

```
Done:
  - Found meeting notes in Notion: "Acme Corp - March 15 Notes"
  - Created Gmail draft to lisa@acmecorp.com
  - Subject: "Follow-up: March 15 Review"
  - Body includes: action items, next steps, timeline

Draft saved in Gmail. Review and send when ready.
```

[VOICE: Claude pulled data from Notion, used it to write a professional email, and saved it as a draft in Gmail. Three apps. One command. This is what MCP makes possible.]

**Common Mistakes in Lesson 7:**

1. **Granting too many permissions.** Only give Claude access to the specific Notion pages and databases it needs. Don't share your entire workspace if you only need it to access one database.
2. **Forgetting that MCP tools count against your context.** Claude Code has lazy loading that reduces context usage by 95%, but if you add 200 MCP tools, performance can still slow down. Keep it to the tools you actually use.
3. **Expecting MCP to work offline.** MCP requires an internet connection. If you're working offline, stick to local file operations.
4. **Not testing the connection.** After running `claude mcp add`, always verify with `claude mcp list`. If the server shows 0 tools, the connection failed and you need to re-authorize.

[SCREEN: Text on screen: "Next: Lesson 8 - Processing Documents and PDFs"]

[VOICE: Next lesson, we're going to process real business documents. Invoices, receipts, PDFs, scanned images. Claude reads them all and turns chaos into a clean spreadsheet. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 8

### Processing Documents and PDFs
**Runtime: 8 minutes | ~1,100 words**

---

[SCREEN: Black screen with white text: "LESSON 8" then fade to "Processing Documents and PDFs"]

[VOICE: If you handle invoices, receipts, contracts, or any kind of business documents, this lesson is going to save you hours every month. We're going to take a pile of documents in different formats, PDFs, images, Excel files, and turn them into one clean, organized spreadsheet. Then we're going to generate a report ready to send to your accountant.]

[SCREEN: Show a folder with mixed document types: invoice.pdf, receipt.jpg, expense-report.xlsx, scan-001.png]

[VOICE: Here's a real scenario. You're a freelancer or small business owner. Every month you get invoices from vendors, receipts from expenses, and you need to consolidate all of this for your bookkeeper. You currently spend two hours copying numbers from PDFs into a spreadsheet. Let's make that take two minutes.]

[SCREEN: Navigate to the folder and start Claude:]

```
cd ~/Documents/invoices-march
claude
```

[SCREEN: Type into Claude Code:]

```
Process all files in this folder. They're invoices and receipts
in different formats (PDF, images, Excel). For each one, extract:
- Invoice/receipt number
- Date
- Vendor name
- Total amount
- Tax amount (if available)

Put everything into one Excel file called consolidated-march.xlsx
```

[SCREEN: Claude Code processes each file:]

```
Processing 9 documents...

  invoice-acme.pdf        ✓ Invoice #4521, Acme Corp, $2,340.00
  receipt-office.jpg      ✓ Receipt #891, Office Depot, $127.43
  invoice-hosting.pdf     ✓ Invoice #H-2026-03, DigitalOcean, $48.00
  scan-001.png            ✓ Invoice #1089, FedEx, $89.50
  expense-report.xlsx     ✓ 4 line items extracted
  receipt-lunch.jpg       ✓ Receipt, Restaurant Miraflores, $45.20
  invoice-software.pdf    ✓ Invoice #SW-445, Adobe, $54.99
  scan-002.png            ✓ Receipt #2244, Uber, $23.80
  contractor-invoice.pdf  ✓ Invoice #F-103, J. Martinez, $1,500.00

Created: consolidated-march.xlsx
  9 documents processed
  13 line items total
  Grand total: $4,228.92
  Tax total: $312.40
```

[VOICE: Nine documents. Three different formats. Claude read each one, extracted the important data, and put it all in one spreadsheet. It even handled the scanned images by using optical character recognition. Let's look at what it created.]

[SCREEN: Open consolidated-march.xlsx showing clean columns]

[VOICE: Clean columns. Invoice number, date, vendor, amount, tax. All in one place. Now let's generate the report.]

[SCREEN: Type into Claude Code:]

```
Create a monthly expense report based on that spreadsheet.
Include:
- Summary of total expenses by category
- Top vendors by spend
- A comparison section (leave blank for last month data)
- Save it as a PDF called march-2026-report.pdf
```

[SCREEN: Claude Code generates the report:]

```
Created: march-2026-report.pdf

  Page 1: Executive Summary
    Total Expenses: $4,228.92
    Tax Deductible: $3,102.50
    Number of Transactions: 13

  Page 2: Breakdown by Category
    Services:   $1,500.00  (35.5%)
    Products:    $127.43   (3.0%)
    Software:    $102.99   (2.4%)
    Shipping:     $89.50   (2.1%)
    Other:     $2,409.00   (57.0%)

  Page 3: Vendor Analysis
    Top 3 by spend: J. Martinez, Acme Corp, Office Depot

  Page 4: Month-over-Month (blank template)
```

[VOICE: A four-page expense report, ready to email to your bookkeeper. From raw documents to finished report in about three minutes.]

[SCREEN: Show the PDF report briefly]

[VOICE: Now, here's a power move. Let's say you do this every month. Same process, same format, same output. Instead of typing all of that again next month, let's save it.]

[SCREEN: Type into Claude Code:]

```
Take the exact workflow we just did and save it as a reusable
script. It should:
1. Look in ~/Documents/invoices/ for new files
2. Process all documents and extract invoice data
3. Create a consolidated Excel file
4. Generate a PDF report
5. Move processed files to a "completed" subfolder

Call it process-invoices.sh
```

[SCREEN: Claude Code creates the script:]

```
Created: ~/process-invoices.sh

Run it anytime with:
  bash ~/process-invoices.sh

It will process any new files in ~/Documents/invoices/ and
output the report to ~/Documents/reports/
```

[VOICE: Next month, you drop your invoices into that folder and run one command. The entire process takes 30 seconds instead of two hours. That's the pattern of this course. Do it once with Claude, then save it as a reusable workflow.]

**Common Mistakes in Lesson 8:**

1. **Low-quality scans.** Claude can read scanned documents, but if the image is blurry or the text is too small, it will miss data. Scan at 300 DPI minimum and make sure the text is legible.
2. **Assuming 100% accuracy on financial data.** Always verify the extracted numbers against the original documents, especially for tax filings. Claude is very good but not perfect with handwritten numbers or unusual invoice formats.
3. **Mixing currencies.** If you have invoices in different currencies, tell Claude explicitly. Say "all amounts are in USD" or "convert EUR amounts to USD using today's rate."
4. **Processing sensitive documents without thinking about privacy.** Claude Code processes files locally on your machine, which is good. But if you're using MCP connections, data could travel through third-party servers. For sensitive financial documents, keep processing local.

[SCREEN: Text on screen: "Next: Lesson 9 - Custom Commands and Hooks"]

[VOICE: In the next lesson, we're going to build your own custom commands. Slash commands that let you run complex workflows with two words. And hooks that make Claude follow your rules automatically. This is where you start building a real system. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 9

### Custom Commands and Hooks
**Runtime: 9 minutes | ~1,200 words**

---

[SCREEN: Black screen with white text: "LESSON 9" then fade to "Custom Commands and Hooks"]

[VOICE: By now you've been typing full instructions every time you want Claude to do something. That works, but it's slow when you repeat the same workflow every day. This lesson changes that. We're going to build custom commands, so you can type /process-invoices and Claude runs your entire workflow automatically. And we're going to set up hooks, rules that Claude follows without you having to ask.]

[SCREEN: Terminal with Claude Code running]

[VOICE: Let's start with custom commands. A custom command is just a markdown file. You write your instructions in plain English, save the file in a special folder, and it becomes a slash command you can use anytime.]

[SCREEN: Show the folder structure:]

```
Your project folder/
  .claude/
    commands/
      your-command-name.md
```

[VOICE: Every command goes in the .claude/commands/ folder inside your project. The filename becomes the command name. If the file is called "weekly-report.md", the command is /weekly-report. Let me build one from scratch.]

[SCREEN: Open a text editor and create the file:]

```
File: .claude/commands/weekly-report.md
```

```
You are generating a weekly report. Follow these steps:

1. Read all files in the ~/Documents/work-logs/ folder that
   were modified in the last 7 days
2. Summarize the key accomplishments from each file
3. List any blockers or unfinished items
4. Format the output as a clean report with sections:
   - Accomplishments
   - In Progress
   - Blockers
   - Next Week Priorities
5. Save the report as weekly-report-YYYY-MM-DD.md in
   ~/Documents/reports/
```

[VOICE: That's it. Just a markdown file with plain English instructions. Save it, restart Claude Code, and now you have a new command. Let me show you.]

[SCREEN: Restart Claude Code, type /]

```
> /weekly-report
```

[SCREEN: Claude Code runs the entire workflow automatically:]

```
Processing weekly report...

Read 4 work log files from the last 7 days.

Weekly Report - March 22, 2026

ACCOMPLISHMENTS:
- Completed client onboarding for Acme Corp
- Published 3 blog posts to content pipeline
- Processed Q1 invoices and sent to accounting
- Updated product photos for eBay listings

IN PROGRESS:
- Shopify store homepage redesign (60% complete)
- Email automation sequence (draft stage)

BLOCKERS:
- Waiting on brand assets from designer

NEXT WEEK PRIORITIES:
- Finish Shopify redesign
- Launch email sequence
- Prepare Q1 revenue report

Saved to: ~/Documents/reports/weekly-report-2026-03-22.md
```

[VOICE: One command. The entire weekly report process. Every week you type /weekly-report and it's done. Let me show you how to make commands even more flexible using arguments.]

[SCREEN: Create another command file:]

```
File: .claude/commands/draft-email.md
```

```
Draft a professional email based on the following details:
$ARGUMENTS

Requirements:
- Professional but friendly tone
- Keep it under 200 words
- Include a clear call to action
- Save the draft to ~/Documents/email-drafts/
```

[VOICE: See that $ARGUMENTS placeholder? Whatever you type after the command becomes the argument. So you can do this.]

[SCREEN: Type into Claude Code:]

```
> /draft-email Follow up with Lisa at Acme Corp about the
  proposal we sent last week. Ask if she has questions and
  suggest a call next Tuesday.
```

[SCREEN: Claude Code generates the email:]

```
Draft saved to: ~/Documents/email-drafts/acme-followup.md

Subject: Following Up on Our Proposal

Hi Lisa,

I wanted to check in on the proposal we sent over last week
for the Q2 project. Have you had a chance to review it?

If you have any questions or want to discuss the details,
I'd love to set up a quick call. Would next Tuesday work
for you? I'm open anytime after 10 AM.

Looking forward to hearing from you.

Best,
Alex
```

[VOICE: Custom command with dynamic input. You can build commands for anything you repeat. Email drafts, meeting prep, content outlines, data pulls. If you do it more than twice, make it a command.]

[SCREEN: Text: "Now let's talk about Hooks"]

[VOICE: Hooks are different from commands. Commands are things you run on purpose. Hooks are things that run automatically when certain events happen. Think of them as rules that Claude follows without you asking.]

[VOICE: Hooks live in your settings file. There are several types, but the three most useful ones for non-technical users are PreToolUse, PostToolUse, and Stop. PreToolUse runs before Claude does something. PostToolUse runs after. Stop runs when Claude finishes a task.]

[SCREEN: Show the settings file location:]

```
~/.claude/settings.json
```

[VOICE: Let me show you a practical example. I want Claude to never modify any file in my "contracts" folder. A safety rule.]

[SCREEN: Show the settings.json configuration:]

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "if echo \"$TOOL_INPUT\" | grep -q 'contracts'; then echo '{\"decision\": \"block\", \"reason\": \"Cannot modify files in contracts folder\"}'; fi"
      }
    ]
  }
}
```

[VOICE: This hook watches every time Claude tries to edit or write a file. If the file path contains "contracts," it blocks the action. Claude will tell you it can't modify that file. Your contracts are safe no matter what you accidentally ask for.]

[VOICE: Here's another useful hook. After every edit Claude makes, automatically run a formatting tool.]

[SCREEN: Show another hook:]

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "command": "echo 'Edit completed at '$(date) >> ~/.claude/edit-log.txt"
      }
    ]
  }
}
```

[VOICE: This one logs every edit Claude makes with a timestamp. So you have an audit trail of everything that was changed and when. Simple but powerful.]

[SCREEN: Show a Stop hook:]

```json
{
  "hooks": {
    "Stop": [
      {
        "command": "say 'Task complete'"
      }
    ]
  }
}
```

[VOICE: This hook makes your Mac say "Task complete" out loud whenever Claude finishes a task. Small thing, but useful when you kick off a long process and walk away from your computer.]

**Common Mistakes in Lesson 9:**

1. **Putting commands in the wrong folder.** The .claude/commands/ folder must be inside your project directory for project commands, or in ~/.claude/commands/ for global commands that work everywhere.
2. **Forgetting to restart Claude Code after adding a command.** New commands only show up after you restart. Press Ctrl+C twice and run `claude` again.
3. **Writing hooks that break Claude.** If your hook script has an error, it can block Claude from working entirely. Test hooks on a test project first, not your main work folder.
4. **Making hooks too aggressive.** A PreToolUse hook that blocks all edits means Claude can't do anything. Be specific about what you're blocking.

[SCREEN: Text on screen: "Next: Lesson 10 - Building a Real Project from Scratch"]

[VOICE: Final lesson. We're going to take everything from this course and build a real, functional tool from scratch. A complete project. See you there.]

[SCREEN: Fade to black with Behike logo]

---

## FULL SCRIPT: LESSON 10

### Building a Real Project from Scratch
**Runtime: 10 minutes | ~1,200 words**

---

[SCREEN: Black screen with white text: "LESSON 10" then fade to "Building a Real Project from Scratch"]

[VOICE: This is the final lesson. We're going to combine everything. File operations, data analysis, web pages, MCP connections, custom commands, hooks. All of it. We're building a real tool that you can use every day. An invoice processing web app that your whole team can use.]

[SCREEN: Show the finished product briefly as a preview]

[VOICE: Here's what we're building. A web application where you drag and drop invoices. It processes them, extracts the data, shows you a table, and lets you download a report. Anyone on your local network can use it. No coding knowledge needed to operate it once it's built.]

[SCREEN: Create a new project folder:]

```
mkdir ~/Desktop/invoice-app
cd ~/Desktop/invoice-app
claude
```

[VOICE: I'm going to give Claude one detailed description and let it build the entire thing.]

[SCREEN: Type into Claude Code:]

```
Build a web application for invoice processing. Requirements:

UPLOAD:
- Drag-and-drop zone for uploading files
- Support PDF, JPG, PNG, and Excel files
- Process multiple files at once

PROCESSING:
- Extract from each invoice: invoice number, date, vendor name,
  line items, subtotal, tax, total
- Handle scanned images using OCR
- Show a progress bar during processing

DISPLAY:
- Show all extracted invoices in a clean table
- Let users edit any field if the extraction was wrong
- Color-code by vendor for easy scanning

EXPORT:
- "Download Excel" button for the consolidated data
- "Generate Report" button for a formatted PDF summary
- "Email Report" button (placeholder for now)

TECHNICAL:
- Use Python Flask for the backend
- Clean, modern UI (dark theme)
- Run on localhost:5000
```

[SCREEN: Claude Code starts building. Show files being created in sequence:]

```
Creating project structure...

  invoice-app/
    app.py              - Flask backend
    requirements.txt    - Python dependencies
    templates/
      index.html        - Main interface
    static/
      style.css         - Dark theme styling
      app.js            - Frontend logic
    processors/
      pdf_processor.py  - PDF extraction
      image_processor.py - OCR for images
      excel_processor.py - Excel parsing
    utils/
      report_generator.py - PDF report generation
```

[VOICE: Claude is building the entire application. Backend, frontend, processors for each file type, report generation. Let it work.]

[SCREEN: Time-lapse of Claude building, showing progress. Then the final output:]

```
Invoice Processing App built successfully.

To start the app:
  1. Install dependencies: pip install -r requirements.txt
  2. Run the app: python app.py
  3. Open http://localhost:5000 in your browser

Features implemented:
  ✓ Drag-and-drop file upload
  ✓ PDF, image, and Excel processing
  ✓ Editable results table
  ✓ Excel export
  ✓ PDF report generation
  ✓ Dark theme UI
```

[VOICE: Let's start it up.]

[SCREEN: Terminal showing:]

```
pip install -r requirements.txt
python app.py
```

```
 * Running on http://localhost:5000
 * Debug mode: on
```

[SCREEN: Open browser to localhost:5000, showing the app interface]

[VOICE: There it is. A full invoice processing application. Let me upload some test invoices.]

[SCREEN: Drag and drop 5 invoice files. Show the progress bar. Then the results table appears:]

```
Invoice #  | Date       | Vendor        | Total
-----------+------------+---------------+--------
4521       | 2026-03-01 | Acme Corp     | $2,340
H-2026-03  | 2026-03-05 | DigitalOcean  | $48
891        | 2026-03-12 | Office Depot  | $127
1089       | 2026-03-15 | FedEx         | $89.50
SW-445     | 2026-03-18 | Adobe         | $54.99
```

[VOICE: Five invoices, three different formats, all processed. The data is in a table I can edit. Let me click on a field.]

[SCREEN: Click on "Office Depot" and change it to "Office Depot (March)"]

[VOICE: Editable. If the OCR missed something, you just click and fix it. Now let me download the Excel file.]

[SCREEN: Click "Download Excel" button, show the downloaded file]

[VOICE: And the PDF report.]

[SCREEN: Click "Generate Report", show the PDF]

[VOICE: That's a working application built from a text description. Now, let me make this even more powerful by connecting it to our MCP setup from Lesson 7.]

[SCREEN: Type into Claude Code:]

```
Add a feature to the app: after processing invoices, automatically
save the data to my Notion database called "Expense Tracker".
Use the Zapier MCP connection we set up earlier.
```

[SCREEN: Claude Code updates the app:]

```
Updated app.py with Notion integration.

New button added: "Save to Notion"
When clicked, all processed invoice data is sent to your
Notion "Expense Tracker" database.
```

[VOICE: Now your invoice app talks to Notion. Upload invoices, process them, click one button, and everything lands in your Notion database. No manual data entry ever again.]

[VOICE: Last thing. Let's make this entire workflow a custom command so you never have to type all of this again.]

[SCREEN: Type into Claude Code:]

```
Create a custom command called "start-invoices" that starts the
invoice app, opens the browser to localhost:5000, and shows a
notification when it's ready.
```

[SCREEN: Claude Code creates the command:]

```
Created: .claude/commands/start-invoices.md

Usage: /start-invoices
This will start the Flask server and open your browser.
```

[VOICE: From now on, you type /start-invoices and your entire invoice processing system launches. That's the arc of this course. You went from not knowing what a terminal is to building a real application with integrations and custom commands.]

[SCREEN: Clean summary slide showing the full course progression:]

```
YOUR JOURNEY:
  Lesson 1:  Opened a terminal for the first time
  Lesson 2:  Gave your computer instructions in English
  Lesson 3:  Organized files intelligently
  Lesson 4:  Analyzed data and built presentations
  Lesson 5:  Automated repetitive tasks
  Lesson 6:  Built websites by describing them
  Lesson 7:  Connected to Notion, Calendar, Gmail
  Lesson 8:  Processed business documents
  Lesson 9:  Created custom commands and hooks
  Lesson 10: Built a full application from scratch
```

[VOICE: You started this course not knowing what a terminal was. Now you have custom commands, MCP connections, automated workflows, and a working web application. The tool is installed. The knowledge is yours. The only thing left is to use it. Pick one task you do every week that takes too long. Open Claude Code. Describe that task. And let it build the automation for you. That's how you start. One task at a time.]

**Common Mistakes in Lesson 10:**

1. **Building too much at once.** Start with a basic version. Get it working. Then add features one at a time. If you ask for 20 features at once, Claude might produce something that doesn't run.
2. **Not installing dependencies.** If Claude creates a requirements.txt file, you need to run `pip install -r requirements.txt` before starting the app. Missing this is the number one reason apps don't start.
3. **Port conflicts.** If you get an "address already in use" error, another app is using port 5000. Tell Claude to use a different port, like 5001 or 8080.
4. **Forgetting to test with real data.** The app works with test files, but your actual invoices might have different layouts. Test with a few real invoices early and ask Claude to handle any edge cases.

[SCREEN: Text on screen: "Course Complete. Go build something."]

[VOICE: Thanks for taking this course. If it was useful, leave a review. And check out the companion PDF that comes with this course. It has 50+ prompt templates, a cheat sheet, and a troubleshooting guide. Go build something. I'll see you out there.]

[SCREEN: Fade to black with Behike logo and "Copyright 2026 Behike"]

---

## COMPANION PDF: CLAUDE CODE FOR EVERYONE

### Command Reference, Prompt Templates, and Troubleshooting Guide

Copyright 2026 Behike. All rights reserved.

---

### SECTION 1: SETUP CHECKLIST

**System Requirements:**
- Mac (macOS 12+), Windows 10/11, or Linux
- Node.js 18+ (download from nodejs.org)
- 4GB RAM minimum
- Internet connection for Claude API access

**Installation Steps:**

1. Install Node.js from nodejs.org (LTS version)
2. Open terminal (Mac: Terminal.app or Warp / Windows: PowerShell or Warp)
3. Run: `npm install -g @anthropic-ai/claude-code`
4. Verify: `claude --version`
5. Start: `claude`
6. Sign in with your Anthropic account

**Recommended Terminal: Warp**
- Download from warp.dev
- Free tier available
- Built for AI-native workflows
- Works on Mac and Windows

**Anthropic Plans:**
- Startup ($25/mo): Light use, a few automations daily
- Max ($100/mo): Heavy daily use, recommended for this course
- Max Pro ($200/mo): High-volume professional use

---

### SECTION 2: ONE-PAGE CHEAT SHEET

```
CLAUDE CODE QUICK REFERENCE
============================

START/STOP:
  claude              Start Claude Code
  Ctrl+C (twice)      Exit Claude Code
  claude --resume     Resume last session

NAVIGATION:
  pwd                 Show current folder
  cd ~/Downloads      Move to Downloads folder
  ls                  List files in current folder

MODES:
  Shift+Tab           Toggle auto-accept edits
  /                   Access slash commands

MCP:
  claude mcp add      Add new MCP server
  claude mcp list     List connected servers
  claude mcp remove   Remove a server

CUSTOM COMMANDS:
  .claude/commands/   Project commands folder
  ~/.claude/commands/ Global commands folder
  $ARGUMENTS          Placeholder for dynamic input

KEYBOARD:
  Tab                 Accept suggestion
  Shift+Tab           Toggle accept mode
  Ctrl+C              Cancel current action
  Escape              Interrupt Claude
  Up/Down arrows      Scroll through history

TIPS:
  - Be specific: WHAT + WHERE + RESULT
  - Use numbered lists for multi-step tasks
  - Tell Claude to keep originals when modifying files
  - Verify numbers on financial data
  - Test on small sets before large batches
```

---

### SECTION 3: PROMPT TEMPLATES (50+)

#### File Organization (8 templates)

**1. Basic folder cleanup**
```
Organize all files in [FOLDER PATH] into subfolders by file type.
Keep original filenames. Create folders for: PDFs, Images,
Spreadsheets, Documents, Archives, and Other.
```

**2. Content-based sorting**
```
Read the content of all PDFs in [FOLDER PATH] and organize them
into subfolders based on what they are: invoices, contracts,
reports, and receipts. Put anything you can't classify into a
"Review" folder.
```

**3. Date-based organization**
```
Organize all files in [FOLDER PATH] into subfolders by month.
Use the format "2026-03-March" for folder names. Use the file's
modification date to determine the month.
```

**4. Project structure creator**
```
Create a project folder structure on my Desktop called
"[PROJECT NAME]" with these subfolders: [LIST FOLDERS].
Add a README.md in the root with the project name and today's date.
```

**5. Duplicate finder**
```
Scan [FOLDER PATH] for duplicate files. Compare by content, not
just filename. Move duplicates to a "duplicates" subfolder and
create a log file showing which files were duplicated.
```

**6. Archive old files**
```
Find all files in [FOLDER PATH] that haven't been modified in the
last [NUMBER] days. Move them to an "archive" subfolder. Create a
log of what was archived.
```

**7. Flatten nested folders**
```
Take all files from all subfolders inside [FOLDER PATH] and move
them into the root of that folder. Remove empty subfolders after.
Rename duplicates by adding a number suffix.
```

**8. Smart rename**
```
Rename all files in [FOLDER PATH] using this pattern:
[PREFIX]-[NUMBER].[EXTENSION]. Start numbering at 001. Sort by
original filename before numbering. Keep the original extension.
```

#### Data Analysis (8 templates)

**9. CSV summary**
```
Read [FILENAME] and give me a summary: how many rows, what columns
exist, and basic stats (min, max, average) for any numeric columns.
```

**10. Top N analysis**
```
Read [FILENAME] and find the top [NUMBER] items by [COLUMN NAME].
Show each item with its value and percentage of the total.
```

**11. Trend analysis**
```
Read [FILENAME] and analyze the [COLUMN NAME] over time. Is it
going up, down, or flat? What's the average monthly change? Flag
any months with unusual spikes or drops.
```

**12. Multi-file consolidation**
```
Read all [FILE TYPE] files in [FOLDER PATH]. Combine them into one
master spreadsheet. Add a "Source File" column so I know which file
each row came from. Save as [OUTPUT FILENAME].
```

**13. Comparison report**
```
Compare [FILE 1] and [FILE 2]. What's different? Which entries
exist in one but not the other? Create a summary of additions,
deletions, and changes.
```

**14. Outlier detection**
```
Read [FILENAME] and find any rows where [COLUMN NAME] is more
than 2 standard deviations from the mean. List them and explain
why they might be unusual.
```

**15. Pivot table**
```
Read [FILENAME] and create a pivot table: rows are [COLUMN 1],
columns are [COLUMN 2], values are the sum of [COLUMN 3]. Save
the result as a new spreadsheet.
```

**16. Data cleaning**
```
Read [FILENAME] and clean the data: remove duplicate rows,
standardize date formats to YYYY-MM-DD, trim whitespace from
text fields, and flag any rows with missing values. Save the
cleaned version as [OUTPUT FILENAME].
```

#### Batch Operations (6 templates)

**17. Batch rename with pattern**
```
Rename all [FILE TYPE] files in [FOLDER PATH] using the pattern:
[PREFIX]-[NUMBER].[EXT]. Start at 001. Sort by original name first.
```

**18. Batch resize images**
```
Resize all images in [FOLDER PATH] to [WIDTH]px wide. Keep the
aspect ratio. Save resized versions in a subfolder called
"resized". Don't modify the originals.
```

**19. Batch convert format**
```
Convert all [SOURCE FORMAT] files in [FOLDER PATH] to [TARGET
FORMAT]. Save converted files in a subfolder called "converted".
Keep the originals.
```

**20. Batch watermark**
```
Add a text watermark "[TEXT]" to all images in [FOLDER PATH].
Position it in the bottom-right corner, semi-transparent white
text. Save watermarked versions in a "watermarked" subfolder.
```

**21. Batch PDF merge**
```
Combine all PDF files in [FOLDER PATH] into one single PDF.
Order them alphabetically by filename. Save as [OUTPUT FILENAME].
```

**22. Batch metadata strip**
```
Remove all EXIF metadata from all images in [FOLDER PATH] for
privacy. Save cleaned versions in a "cleaned" subfolder. Keep
originals.
```

#### Web Page Creation (6 templates)

**23. Personal portfolio**
```
Build a personal portfolio website with: hero section with my name
"[NAME]" and tagline "[TAGLINE]", about section, portfolio grid
with [NUMBER] project placeholders, contact form. [THEME] theme,
modern, responsive.
```

**24. Product landing page**
```
Build a landing page for "[PRODUCT NAME]" priced at $[PRICE].
Include: hero with CTA button, [NUMBER] feature cards with
descriptions, pricing section, [NUMBER] testimonials (placeholder),
FAQ section. Link the buy button to [URL].
```

**25. Coming soon page**
```
Build a "coming soon" page for "[PROJECT NAME]". Include: large
title, countdown timer to [DATE], email signup field (just visual,
no backend), social media links. Minimal, clean design.
```

**26. Simple blog**
```
Build a simple blog with a home page listing 5 sample posts with
titles and dates. Each post should be clickable and open a full
article page. Include a sidebar with categories. Clean, readable
typography.
```

**27. Event page**
```
Build an event page for "[EVENT NAME]" on [DATE] at [LOCATION].
Include: event description, schedule/agenda, speaker bios
(placeholder), registration button linking to [URL], map embed
placeholder.
```

**28. Link in bio page**
```
Build a "link in bio" page for "@[USERNAME]". Include: profile
image placeholder, bio text, [NUMBER] link buttons with custom
labels. Mobile-optimized, dark theme, centered layout.
```

#### Document Processing (6 templates)

**29. Invoice extraction**
```
Process all invoices in [FOLDER PATH] (PDF, image, or Excel).
Extract: invoice number, date, vendor, line items, subtotal, tax,
total. Output everything to one Excel file called [FILENAME].
```

**30. Contract summarizer**
```
Read [CONTRACT FILE] and give me a plain-English summary: what
the agreement is about, key dates, payment terms, termination
conditions, and any unusual clauses I should know about.
```

**31. Receipt organizer**
```
Process all receipts in [FOLDER PATH]. Extract: date, store name,
total amount, payment method (if visible). Categorize each
(food, transport, office, etc.). Create a monthly summary spreadsheet.
```

**32. PDF text extraction**
```
Extract all text from [PDF FILE] and save it as a clean .txt file.
Preserve paragraph breaks. Remove headers, footers, and page
numbers.
```

**33. Document comparison**
```
Compare [FILE 1] and [FILE 2]. Highlight all differences:
additions, deletions, and changes. Create a summary showing what
changed between versions.
```

**34. Form data extraction**
```
Read all filled forms in [FOLDER PATH] (PDF or image). Extract the
field names and values from each form. Output to a spreadsheet with
one row per form.
```

#### MCP and Integrations (6 templates)

**35. Notion content pull**
```
Fetch all pages from my Notion database "[DATABASE NAME]" where
status is "[STATUS]". List the title, status, and last edited date
for each one.
```

**36. Notion article writer**
```
Fetch the first unstarted article from my Notion database
"[DATABASE NAME]". Research the topic, write a [LENGTH]-word
article, save it to the Notion page, and update the status to
"Done".
```

**37. Calendar summary**
```
Check my Google Calendar for [TIME PERIOD]. List all events with
times, durations, and attendees. Calculate my total meeting hours.
```

**38. Email draft**
```
Draft an email to [RECIPIENT] about [TOPIC]. Tone: [professional/
casual/friendly]. Keep it under [NUMBER] words. Include a clear
call to action. Save as a draft in Gmail.
```

**39. Meeting prep**
```
Check my calendar for my next meeting with [PERSON/COMPANY].
Search Notion for any related notes. Draft a prep doc with:
agenda items, open questions, and action items from last meeting.
```

**40. Daily briefing**
```
Give me a daily briefing:
1. List today's calendar events
2. Show unread important emails (last 12 hours)
3. Pull my "Due Today" tasks from Notion
4. Summarize it all in 5 bullet points
```

#### Content Creation (5 templates)

**41. Blog post from outline**
```
Write a [LENGTH]-word blog post on "[TOPIC]". Structure: hook
intro, [NUMBER] main sections with subheadings, practical examples,
conclusion with CTA. Tone: [DESCRIBE TONE]. Save to [LOCATION].
```

**42. Social media batch**
```
Take the article in [FILE] and create [NUMBER] social media posts
from it. Each post should highlight a different key point. Format
for [PLATFORM]. Include suggested hashtags.
```

**43. Newsletter draft**
```
Write a newsletter issue about [TOPIC]. Sections: intro hook,
main story (300 words), 3 quick links with one-line descriptions,
one tip of the week, sign-off. Save to [LOCATION].
```

**44. Product description**
```
Write a product description for "[PRODUCT]" priced at $[PRICE].
Include: one-line hook, 3 key benefits (not features), who it's
for, what's included, and a CTA. Max 200 words.
```

**45. Course outline**
```
Create a course outline for "[COURSE TITLE]". Include [NUMBER]
lessons. Each lesson needs: title, runtime estimate, 3 learning
objectives, and a practical exercise. Progressive difficulty.
```

#### Automation and Scripts (5 templates)

**46. Reusable script**
```
Take the workflow we just completed and save it as a reusable
bash script called [FILENAME]. It should be runnable with one
command. Add comments explaining each step.
```

**47. Scheduled cleanup**
```
Create a script that cleans my Downloads folder every Sunday.
Rules: move files older than 30 days to ~/Archive/[MONTH-YEAR]/,
delete .tmp files, organize remaining files by type. Log actions
to cleanup-log.txt.
```

**48. Backup script**
```
Create a script that backs up [FOLDER PATH] to [BACKUP LOCATION].
Include a timestamp in the backup folder name. Keep the last
[NUMBER] backups and delete older ones.
```

**49. File watcher**
```
Create a script that watches [FOLDER PATH] for new files. When a
new file appears, automatically [ACTION]. Log every action with
timestamp.
```

**50. Morning routine**
```
Create a custom command called /morning that:
1. Shows today's calendar events
2. Lists my top 3 priority tasks from Notion
3. Checks for unread emails from VIP contacts
4. Gives me a weather summary
5. Saves the briefing to ~/Documents/daily-briefs/
```

#### Advanced Templates (5 templates)

**51. Web scraper**
```
Write a Python script that visits [URL] and extracts [DATA
DESCRIPTION]. Save the results to a CSV file. Run it once and
show me the results.
```

**52. API connector**
```
Connect to the [SERVICE] API using my API key. Fetch [DATA
DESCRIPTION]. Format the results as a clean table. Save to
[FILENAME].
```

**53. Multi-file search**
```
Search all [FILE TYPE] files in [FOLDER PATH] for the text
"[SEARCH TERM]". List every file that contains it, with the
line number and surrounding context. Save results to search-results.md.
```

**54. Codebase analyzer**
```
Analyze all files in [FOLDER PATH]. Tell me: total files by type,
total lines of code, largest files, and any files that haven't
been modified in 6+ months. Create a health report.
```

**55. Presentation builder**
```
Create a PowerPoint presentation about "[TOPIC]" with [NUMBER]
slides. Include: title slide, agenda, [NUMBER] content slides with
bullet points, summary slide. Use a [LIGHT/DARK] theme. Add
placeholder charts where appropriate.
```

---

### SECTION 4: MCP SETUP GUIDE

#### What is MCP?

MCP (Model Context Protocol) connects Claude Code to external tools and services. Without it, Claude only works with local files. With it, Claude can read your Notion, check your calendar, draft emails, and more.

Think of it as plugging in a USB cable between Claude and your apps.

#### Setting Up Zapier MCP (Recommended Method)

**Step 1:** Go to mcp.zapier.com and sign in

**Step 2:** Click "New MCP Server"
- Client: Claude Code
- Name: whatever you want (e.g., "My Tools")

**Step 3:** Add tools for each service
- Click "Add Tools"
- Search for the service (Notion, Gmail, Google Calendar, etc.)
- Select the specific tools you want to enable
- Authorize the connection when prompted

**Step 4:** Copy the connection command
- Zapier provides a command like:
```
claude mcp add zapier -- npx -y @anthropic-ai/mcp-remote https://mcp.zapier.com/api/mcp/s/YOUR-KEY-HERE
```
- Paste it in your terminal and hit enter

**Step 5:** Verify the connection
```
claude mcp list
```
You should see your server with the number of tools available.

#### Connecting Notion

Tools to enable:
- Search pages and databases
- Read page content
- Create new pages
- Update page properties
- Add content to pages

Permissions to grant: Select only the workspaces and pages Claude needs access to. Don't share everything.

#### Connecting Google Calendar

Tools to enable:
- List calendars
- List events
- Create events
- Update events
- Find free time

#### Connecting Gmail

Tools to enable:
- Search messages
- Read messages
- Create drafts
- List labels

Note: We recommend "create drafts" not "send messages" so you always review before sending.

#### Troubleshooting MCP

**"Server not found"**: Re-run the `claude mcp add` command. Make sure you copied the full URL.

**"0 tools available"**: The authorization expired. Go back to Zapier and re-authorize the service.

**"Tool execution failed"**: The service might be temporarily down. Wait a few minutes and try again.

**Slow responses**: Too many MCP tools loaded. Remove servers you don't use with `claude mcp remove [name]`.

---

### SECTION 5: CUSTOM COMMANDS LIBRARY

#### How to Install a Command

1. Navigate to your project folder
2. Create the folder: `mkdir -p .claude/commands`
3. Create a new file: `[command-name].md`
4. Write your instructions in plain English
5. Restart Claude Code
6. Use with `/command-name`

For global commands (work in any project), put them in `~/.claude/commands/`

#### Ready-to-Use Commands

**1. /organize-downloads**
```markdown
Organize my ~/Downloads folder:
1. Create subfolders by file type (PDFs, Images, Spreadsheets,
   Documents, Archives, Other)
2. Move all files into their respective folders
3. Find and flag duplicate files
4. Create a log file with everything that was moved
5. Report the total files organized and space used
```

**2. /weekly-report**
```markdown
Generate a weekly report:
1. Read all files in ~/Documents/work-logs/ modified in the last 7 days
2. Summarize key accomplishments
3. List blockers and unfinished items
4. Format as: Accomplishments, In Progress, Blockers, Next Week
5. Save to ~/Documents/reports/weekly-report-YYYY-MM-DD.md
```

**3. /process-invoices**
```markdown
Process invoices in ~/Documents/invoices/:
1. Read all PDF, image, and Excel files
2. Extract: invoice number, date, vendor, total, tax
3. Create consolidated Excel file
4. Generate PDF summary report
5. Move processed files to ~/Documents/invoices/completed/
6. Report total amount and number of invoices processed
```

**4. /draft-email**
```markdown
Draft a professional email based on these details:
$ARGUMENTS

Requirements:
- Professional but friendly tone
- Under 200 words
- Clear call to action at the end
- Save to ~/Documents/email-drafts/ with a descriptive filename
```

**5. /meeting-prep**
```markdown
Prepare for a meeting about: $ARGUMENTS

1. Search my Notion for any related notes or documents
2. Check my calendar for the meeting details
3. Create a prep document with:
   - Meeting context and attendees
   - Key discussion points
   - Open questions to raise
   - Action items from previous meetings (if found)
4. Save to ~/Documents/meeting-prep/
```

**6. /photo-process**
```markdown
Process product photos:
1. Look in ~/Desktop/New-Products/ for new images
2. Rename sequentially: product-001, product-002, etc.
3. Create two versions:
   - "web" folder: 1080px wide, 80% quality JPG
   - "social" folder: 1080x1080px square crop, centered
4. Log original and new filenames
5. Report total files processed and space saved
```

**7. /content-pipeline**
```markdown
Run content pipeline:
1. Check Notion for articles with status "Not Started"
2. For each article:
   a. Research the topic
   b. Write a 1,000-word draft
   c. Save the draft to the Notion page
   d. Update status to "Draft Complete"
3. Report how many articles were processed
```

**8. /data-report**
```markdown
Generate a data report from: $ARGUMENTS

1. Read the specified file or all data files in the current folder
2. Provide: row count, column descriptions, basic statistics
3. Identify trends, outliers, and notable patterns
4. Create a summary with key findings
5. Generate a PowerPoint with charts if the data supports it
6. Save everything to ~/Documents/reports/
```

**9. /site-builder**
```markdown
Build a website based on this description: $ARGUMENTS

Requirements:
- Modern, responsive design
- Dark theme by default
- Mobile-friendly
- Working navigation
- Placeholder content where needed
- Save all files to ~/Desktop/websites/[project-name]/
- Provide instructions to preview it
```

**10. /backup**
```markdown
Run backup routine:
1. Create a timestamped backup folder in ~/Backups/
2. Copy these folders:
   - ~/Documents/work-logs/
   - ~/Documents/reports/
   - ~/Desktop/projects/
3. Compress the backup as a .zip file
4. Delete backups older than 30 days
5. Report backup size and number of files included
```

---

### SECTION 6: TROUBLESHOOTING GUIDE

#### Installation Problems

**"npm: command not found"**
Node.js isn't installed. Download it from nodejs.org (LTS version). After installing, close and reopen your terminal completely, then try again.

**"EACCES permission denied" during npm install**
On Mac/Linux, run:
```
sudo npm install -g @anthropic-ai/claude-code
```
Enter your computer password when prompted.

**"node: No such file or directory"**
Your Node.js installation is broken. Uninstall Node.js completely, restart your computer, and reinstall from nodejs.org.

#### Startup Problems

**Claude Code won't start / blank screen**
Try updating first:
```
npm update -g @anthropic-ai/claude-code
```
If that doesn't work, uninstall and reinstall:
```
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code
```

**"Authentication failed"**
Your session expired. Run `claude` again and re-authenticate with your Anthropic account. Check that your subscription is active at console.anthropic.com.

**"Rate limit reached"**
You've used too many tokens in your current billing period. Options:
- Wait for the limit to reset (usually hourly or daily depending on plan)
- Upgrade your plan for higher limits
- Use shorter, more specific prompts to reduce token usage

#### Runtime Problems

**"Permission denied" when accessing files**
On Mac, go to System Settings > Privacy & Security > Files and Folders. Grant your terminal app (Warp or Terminal) access to the folders Claude needs.

**Claude is slow or unresponsive**
- Close other heavy applications
- Use `Ctrl+C` to cancel and try a simpler prompt
- If you have many MCP servers, remove unused ones with `claude mcp remove [name]`
- Start a new session. Long conversations use more memory

**"File not found" errors**
Claude is looking in the wrong directory. Check where you are:
```
pwd
```
Navigate to the correct folder:
```
cd ~/the/correct/path
```

**Claude generates code that doesn't run**
Tell Claude the error:
```
That script threw this error: [paste the error message].
Fix it and try again.
```
Claude reads error messages and corrects its code. Usually takes one or two tries.

**MCP server connection failures**
1. Check the server is still connected: `claude mcp list`
2. If it shows 0 tools, remove and re-add it:
   ```
   claude mcp remove zapier
   ```
   Then re-run the add command from Zapier
3. Check your internet connection
4. Verify the service authorization hasn't expired in Zapier

#### Data and File Problems

**Claude modified the wrong file**
If the session is still open, say "undo that last change." If you closed the session, you'll need to restore from backup or manually fix the file.

**Numbers in generated reports look wrong**
Ask Claude to show its work:
```
Show me the calculation you used for the total revenue number.
Print the raw data for those rows.
```
Spot-check against the original file.

**Excel files won't open after Claude creates them**
Claude sometimes creates .xlsx files that older Excel versions can't read. Try opening with Google Sheets instead, or tell Claude to save as .csv format.

#### Performance Tips

- **Keep prompts focused.** One clear task per message gets better results than five tasks crammed together.
- **Start new sessions for new topics.** Long conversations degrade quality. If you switch from file organization to data analysis, start a fresh session.
- **Use /compact if your session gets long.** This reduces context size without losing key information.
- **Tell Claude to clean up after itself.** "Delete the temporary Python scripts you created" keeps your folders clean.

---

### SECTION 7: WHAT'S NEXT

#### Going Further with Claude Code

**Skills (Advanced Custom Commands)**
Skills are the evolution of custom commands. Instead of just instructions, skills include metadata that tells Claude when to use them automatically. Create a SKILL.md file in ~/.claude/skills/ with YAML frontmatter describing when the skill applies.

**Agent Teams**
For complex projects, Claude Code can run multiple instances that coordinate with each other. One Claude handles the frontend, another handles the backend, and they share progress. This is advanced territory but extremely powerful for large builds.

**Worktrees**
The `--worktree` flag lets you run Claude in isolated git branches. Perfect for trying experiments without risking your main project. Each worktree is a separate copy of your project.

**Local AI with Ollama**
Install Ollama (ollama.com) to run AI models locally, zero cloud dependency, zero monthly cost. Good for quick tasks where you don't need Claude's full capabilities. Claude Code can be configured to use local models for certain operations.

#### Community Resources

- Anthropic's official docs: code.claude.com/docs
- r/ClaudeAI on Reddit
- Claude Code Discord community
- Anthropic Academy courses (free)

#### From Behike

This course is the starting point. We're building more:
- Advanced Claude Code for Developers
- Building AI Agents with Claude
- Automation Systems for Small Business

Follow @behikeai on Instagram for updates.

---

*Copyright 2026 Behike. All rights reserved.*
*AI Disclosure: This course was created with the assistance of AI tools. All content has been reviewed, tested, and validated by a human author.*

---

## PRODUCTION NOTES

**Target audience:** Non-technical professionals, small business owners, freelancers, content creators, and anyone who uses a computer daily but has never touched the terminal.

**Tone:** Casual, clear, zero jargon. When technical terms must be used, define them immediately with a real-world analogy.

**Recording format:** Screen recording with voice narration. No face cam required (optional). 1080p minimum.

**Software needed for recording:** OBS Studio (free) or QuickTime (Mac). Warp terminal with font size increased to 16px+ for readability.

**Editing notes:** Cut pauses during Claude Code processing time. Add subtle zoom-ins when showing specific terminal output. Use consistent lower-third labels for section changes within lessons.

**Total word count:** ~14,000 words across all 10 lessons + companion PDF.
