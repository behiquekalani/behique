---
title: "AI Safety Checklist"
type: lead-magnet
tags: [security, ai-safety, lead-magnet, free]
created: 2026-03-22
price: FREE
---

# The AI Safety Checklist
## 15 Things to Check Before You Let AI Touch Your Business

By Kalani Andre / Behike

---

## Why This Exists

You've heard the horror stories. AI agents going rogue. Data leaking to unknown servers. Prompt injection attacks hijacking AI systems. Companies losing money because an AI tool did something it shouldn't have.

Most of these stories are real. But they're also preventable.

This checklist is the 15-item security audit I run on every AI tool and agent before I deploy it in my business. I run 6 AI agents across 3 computers. If any of them got compromised, my entire operation would be at risk.

These checks keep that from happening.

Print this. Tape it to your monitor. Run through it every time you add a new AI tool or give an AI agent new permissions.

---

## Before You Install Any AI Tool

- [ ] **1. Check what data it accesses.** Read the permissions list. Does this tool need access to your files, emails, browser, or contacts? If it asks for more than it needs, that's a red flag.

- [ ] **2. Check where your data goes.** Does the tool process everything locally or send data to a cloud server? For sensitive work, prefer local tools like Ollama that never send data off your machine.

- [ ] **3. Check the company behind it.** Is it a known company with a privacy policy? Or a random GitHub repo with no documentation? Open-source is fine, but verify it has active maintainers and a real community.

- [ ] **4. Check for API key exposure.** If the tool requires API keys, where does it store them? They should be in environment variables or a secure config file, never hardcoded in scripts or committed to git.

- [ ] **5. Check the .gitignore.** If you're writing code with AI, make sure .env files, credential files, and API keys are in .gitignore BEFORE your first commit. One accidental push can expose everything.

---

## Before You Give AI Access to Anything

- [ ] **6. Apply least privilege.** Only give the AI tool access to what it absolutely needs. If it just needs to read files, don't give it write access. If it needs one folder, don't give it your entire drive.

- [ ] **7. Set up a sandbox.** Test new AI tools in an isolated environment first. A separate user account, a virtual machine, or a container. Never test unknown tools on your production system.

- [ ] **8. Never let AI handle money unsupervised.** If an AI agent can make purchases, send payments, or access financial accounts, require manual approval for every transaction. No exceptions. Ever.

- [ ] **9. Review AI-generated code before running it.** AI can write malicious code just like it writes good code. Never run code from an AI tool without reading it first. Especially scripts that access the network, modify system files, or handle credentials.

- [ ] **10. Set up logging.** Every action your AI agent takes should be logged somewhere you can review. If you can't see what it did, you can't catch problems early.

---

## Ongoing Security Practices

- [ ] **11. Watch for prompt injection.** If your AI processes external content (emails, web pages, documents), that content can contain hidden instructions. Always treat external content as untrusted data. Never let your AI follow instructions from content it reads.

- [ ] **12. Rotate your API keys.** If you use AI APIs, change your keys every 30-90 days. If a key is compromised, the window of exposure is limited.

- [ ] **13. Monitor for unusual behavior.** If your AI agent suddenly starts doing things it normally doesn't, accessing files it shouldn't, making requests to unknown servers, that's a signal. Investigate immediately.

- [ ] **14. Keep everything updated.** AI tools get security patches just like any software. Update regularly. Old versions have known vulnerabilities that attackers can exploit.

- [ ] **15. Have a kill switch.** Know how to shut down every AI agent you run. Immediately. If something goes wrong, you need to be able to stop it in seconds, not minutes.

---

## The 30-Second Security Audit

When you don't have time for the full checklist, ask these three questions:

1. **What data can this AI see?** If it can see more than it needs, restrict access.
2. **What actions can this AI take?** If it can do more than it should, reduce permissions.
3. **Can I shut it down right now?** If you don't know how, figure that out before anything else.

---

## What To Do If Something Goes Wrong

1. **Stop the agent immediately.** Kill the process, revoke access, disconnect from the network.
2. **Change your passwords and API keys.** All of them. Start with financial accounts.
3. **Check your logs.** See what the agent accessed and when. This tells you the scope of the problem.
4. **Check your git history.** If you're a developer, verify no credentials were committed.
5. **Report the issue.** If it's a third-party tool, report the vulnerability. If it's your own system, document what happened so you can prevent it next time.

---

## Want the Full Guide?

This checklist covers the basics. The full **AI Agent Security Guide** ($14.99) goes deep:

- 8 chapters covering every real AI security threat
- Prompt injection defense strategies with real examples
- How to protect your data when using AI tools
- Financial safety rules for AI agents
- How to secure your entire AI stack (API keys, network, code)
- The complete AI Security Playbook (one-page reference)

Available on Gumroad. Link in bio.

---

## About Behike

Behike builds AI systems that work. Founded by Kalani Andre, a computer engineering student in Puerto Rico who runs 6 AI agents across 3 networked computers. Every security practice in this checklist comes from real experience securing a live system, not from theory.

Follow @behikeai on Instagram for AI automation tips, security updates, and build-in-public content.
