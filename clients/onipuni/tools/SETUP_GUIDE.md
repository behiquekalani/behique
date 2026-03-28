# Oni-Puni AI Toolkit - Setup Guide

This guide will get you running a free, private AI on your own computer.
No monthly fees. No data sent to anyone. Everything stays on your machine.

The AI will help you write product descriptions, social media posts, and event materials
for your kawaii store. All you need is a computer and about 10 minutes.

---

## What You Are Installing

**Ollama** is a free program that runs AI models on your computer.
Think of it like having ChatGPT, but it lives on your machine and costs nothing.

The model we use is called **Llama 3.1** (made by Meta). It is free and open source.
It runs well on any computer made in the last 4-5 years.

---

## Step 1: Download Ollama

Go to: **https://ollama.com/download**

### On a Mac:
1. Click "Download for macOS"
2. Open the downloaded file
3. Drag Ollama to your Applications folder
4. Open Ollama from Applications
5. You will see a small llama icon in your menu bar at the top of the screen

### On Windows:
1. Click "Download for Windows"
2. Run the installer
3. Follow the prompts (just click Next, Next, Install)
4. Ollama will start automatically

---

## Step 2: Download the AI Model

Open **Terminal** (Mac) or **Command Prompt** (Windows).

**How to open Terminal on Mac:**
- Press Command + Space, type "Terminal", press Enter

**How to open Command Prompt on Windows:**
- Press the Windows key, type "cmd", press Enter

Now type this command and press Enter:

```
ollama pull llama3.1:8b
```

This downloads the AI model. It is about 4.7 GB, so it might take a few minutes
depending on your internet speed.

You will see a progress bar. Wait until it says "success".

---

## Step 3: Test That It Works

In the same Terminal or Command Prompt window, type:

```
ollama run llama3.1:8b
```

You should see a `>>>` prompt. Type something like:

```
Write a short product description for a cute bear plush toy.
```

If you get a response, everything is working. Type `/bye` to exit.

---

## Step 4: Install Python (if you do not have it)

### Check if Python is already installed:
Open Terminal or Command Prompt and type:

```
python3 --version
```

If you see something like "Python 3.11.5", you are good. Skip to Step 5.

### If Python is NOT installed:

**Mac:** Open Terminal and type:
```
xcode-select --install
```
Then install Python from https://www.python.org/downloads/

**Windows:** Go to https://www.python.org/downloads/ and download the installer.
IMPORTANT: Check the box that says "Add Python to PATH" during installation.

---

## Step 5: Install the requests library

In Terminal or Command Prompt, type:

```
pip3 install requests
```

This is the only extra library needed. Everything else uses built-in Python.

---

## Step 6: Test the Tools

Navigate to the tools folder and try:

```
python3 product_writer.py "Rilakkuma Plush" "San-X" "$25.99" "soft brown bear plush, 12 inches, new with tags"
```

You should see a product description, Instagram caption, and TikTok script appear.
The output also gets saved to a text file in the output/ folder.

---

## Troubleshooting

### "ollama: command not found"
- Make sure Ollama is running (look for the llama icon in your menu bar on Mac)
- On Windows, restart your computer after installing

### "connection refused" or "cannot connect"
- Ollama needs to be running in the background
- On Mac: Open Ollama from Applications
- On Windows: Search for Ollama in Start menu and open it

### "model not found"
- Run `ollama pull llama3.1:8b` again
- Make sure you typed the name exactly right (no spaces around the colon)

### The AI responses are slow
- This is normal on older computers. The 8b model is the smallest good model.
- Close other programs to free up memory.
- If it is unusably slow, your computer might need more RAM (at least 8 GB recommended).

### "python3: command not found"
- Try just `python` instead of `python3`
- On Windows, you may need to restart Command Prompt after installing Python

### Scripts work but output is generic (template mode)
- This means Ollama is not running. Start Ollama first, then run the script again.
- Template mode still works, it just uses pre-written templates instead of AI.

---

## Milwaukee Resources for Extra Help

If you get stuck or want hands-on help, these are all local and most are free:

### Tech Help

**Milwaukee Makerspace**
- Website: https://milwaukeemakerspace.org
- Community workshop with people who know tech. Good for getting help with setup.

**MATC (Milwaukee Area Technical College)**
- Free tech workshops throughout the year
- Website: https://www.matc.edu
- Check their continuing education catalog for computer basics classes

**Milwaukee Public Library**
- Free computer access at all branches
- Staff can help with basic tech questions
- Website: https://www.mpl.org

### Business Help

**Small Business Development Center at UW-Milwaukee**
- Free one-on-one business consulting
- Help with marketing, pricing, growth strategy
- Website: https://uwm.edu/sbdc
- Call to schedule: they are very friendly and used to working with small businesses

**SCORE Milwaukee**
- Free business mentorship from experienced business owners
- They pair you with a mentor who knows retail
- Website: https://www.score.org (search for Milwaukee chapter)

**Wisconsin Women's Business Initiative Corporation (WWBIC)**
- Microloans and small business grants
- Business education programs
- Website: https://www.wwbic.com
- Good resource if you need funding for inventory or booth fees

---

## Quick Reference Card

| What you want to do | Command |
|---|---|
| Start Ollama | Open the Ollama app |
| Download the AI model | `ollama pull llama3.1:8b` |
| Chat with AI directly | `ollama run llama3.1:8b` |
| Write a product description | `python3 product_writer.py "name" "brand" "price" "description"` |
| Generate a week of content | `python3 social_batch.py` |
| Prepare for an event | `python3 event_prep.py "Event Name" "Date" "Booth #"` |
| Exit AI chat | Type `/bye` |

---

## What is Next

Once you are comfortable with these tools, you can:
1. Add more products to sample_products.csv (just follow the same format)
2. Run social_batch.py every week to get fresh content ideas
3. Use event_prep.py before every con, market, or pop-up
4. The AI gets better the more specific your product descriptions are

Everything runs locally. No subscriptions. No data leaves your computer.
