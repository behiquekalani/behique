# Study Buddy: The Complete Guide

**For ADHD learners who are done pretending the old way works.**

---

## What This Is

I built Study Buddy because I was tired of apps that assumed studying was a willpower problem.

It is not a willpower problem. When you have ADHD, the part of your brain that handles sustained attention works differently. It is not broken. It is just not optimized for sitting still with a textbook for two hours while nothing interesting happens.

Study Buddy is a standalone web app. No account. No subscription. No ads. Open it in a browser, and it works. It combines a Pomodoro timer, a task queue, gamification, a distraction log, and session history into one interface designed around how ADHD brains actually function.

The goal is not to make you study harder. The goal is to make studying feel like something your brain wants to do.

---

## The Neuroscience (Brief, Practical)

The Pomodoro technique was invented by Francesco Cirillo in the late 1980s. You work for 25 minutes, take a 5-minute break, repeat. After four blocks, take a longer break of 15 to 20 minutes.

For neurotypical people, this is a nice productivity trick. For ADHD brains, it is closer to a structural requirement.

Here is why.

The ADHD brain struggles with what researchers call "time blindness." Long tasks with distant deadlines register as vague and unimportant. A two-hour study session is hard to start because the brain cannot feel the urgency. Twenty-five minutes is concrete. Your brain can see the end. That makes it easier to begin.

The break is equally important. ADHD brains are not bad at focusing. They are bad at sustained focus without adequate dopamine. The break is a reset. It prevents the cognitive fatigue that turns studying into staring.

The gamification part targets dopamine directly. Earning XP, leveling up, watching a progress bar fill: these are not tricks. They are real dopamine signals. The ADHD brain responds to immediate rewards more strongly than delayed ones. Study Buddy makes every completed task and every finished Pomodoro an immediate reward.

The distraction log addresses the other side of the coin. ADHD brains do not just struggle to focus. They also hyperfocus on the wrong things. Logging distractions takes the mental energy of fighting them and channels it into a useful record. You see patterns. You learn what your specific triggers are. That awareness is the first step to addressing them.

---

## How to Use Each Feature

### Subject Input

At the top of the left panel, there is a text field labeled "Estudiando." Type in what you are working on.

Be specific. "Estudiar" is too vague. "Calculo II, Capitulo 3, integrales por partes" is specific. Your brain responds to concrete tasks. The subject field is displayed in your session summary at the end, so it also helps you track what you actually studied each day.

### Session Timer

The timer sits at the center of the screen. It counts down from 25:00 in large text. Press "Comenzar" to start.

The dots below the timer show where you are in your current cycle. Four dots, four Pomodoros. When a dot is amber, the block is in progress. When it turns blue, the block is done. After four blocks, the cycle resets and you earn a long break.

When a focus block ends, the app plays a three-tone alarm and automatically switches to break mode. The timer changes color to green. The mode label changes to "DESCANSO." Start the break timer when you are ready.

During the break: stand up. Get water. Step outside for 30 seconds. Do not open another tab and start scrolling. That is how breaks become 40 minutes.

### Break Mode

Short breaks are 5 minutes. Long breaks (after four blocks) are 15 minutes.

The app does not force you to take the break. You press "Comenzar" when you want to start the break countdown. Some people prefer to take a break without a timer and only start the countdown when they are about to return to work. Either approach works.

The color scheme shifts to green during breaks. This is intentional. It creates a visual signal to your brain that the rules have changed. Work mode is blue. Rest mode is green.

### Focus Mode

The "Modo Focus" button activates focus mode.

In focus mode, everything except the timer fades to near-invisible. The task queue, the distraction log, the notes field, the header: all of it drops to 8% opacity. The timer stays fully visible.

This is for the moments when the interface itself becomes a distraction. Sometimes you need the smallest possible surface to look at. Click the button again, or press "Salir Focus," to exit.

### Task Queue

The right panel contains your task queue. Add tasks before you start studying. One task per line, added with the plus button or the Enter key.

The task at the top of the queue is displayed prominently in the left panel under "Tarea actual." That is the one task you are supposed to be working on during this Pomodoro.

When you finish a task, press "Completada." It moves from the queue to the completed list below, and you earn 10 XP. The next task in the queue automatically becomes the current task.

If you finish a Pomodoro and still have the same task, that is fine. Complex tasks take multiple Pomodoros. The task stays at the top until you mark it done.

The completed list shows everything you finished in the current session. Looking at this list at the end of a study session is more useful than you would expect. Your brain tends to remember what you did not finish. The completed list forces it to also acknowledge what you did.

### XP System

Every completed Pomodoro earns 25 XP. Every completed task earns 10 XP.

XP accumulates across sessions. It is stored in your browser's localStorage, so it persists between visits on the same device. You start at Level 1 and level up every 100 XP. The level badge in the top right flashes amber when you level up.

There is no functional difference between Level 1 and Level 10. The levels are not unlocks. They are records. They tell you how much work you have put in. Over time, watching your level grow creates a real sense of accumulated effort, which is something ADHD brains often lose track of.

The XP bar below the level badge shows how far you are through the current level. When it fills, you level up.

### Distraction Log

The "Me distrae..." button is in the left panel, below the current task.

When you notice yourself about to get distracted, click it. A text field appears. Type what is pulling your attention. The input is saved for the session.

At the end of the session, the session summary shows your distraction count.

Why this works: fighting a distraction directly uses willpower, which is a limited resource. Acknowledging it and logging it uses a different mechanism. You are not suppressing the distraction. You are capturing it. Your brain gets the small satisfaction of doing something with the intrusive thought, and then you return to work.

Over multiple sessions, your logs reveal patterns. If you keep logging the same source of distraction, that tells you something specific about your environment or habits that you can change.

### Session Notes

At the bottom of the left panel is a text area for notes. These auto-save to localStorage with a debounce, so you will not lose anything.

Use this during the session, not just at the end. When you figure something out mid-Pomodoro, write it down immediately. When you have a question you want to look up later, write it down. When something clicks, note it.

The notes field is persistent between page loads. If you close the tab and return, your notes are still there. Clear them manually when you start a new topic.

### History

The bottom of the right panel shows your last 7 sessions. Each entry shows the date, the subject, the number of Pomodoros, the number of tasks completed, and the XP earned.

This is not just data. It is evidence. On the days when you feel like you never study, look at the history. You probably study more than you think. The ADHD brain discounts past effort. The history panel fights that distortion.

---

## The XP System Explained

Gamification gets dismissed as gimmicky. It is not, for ADHD brains.

The core problem in ADHD is not attention. It is motivation regulation. The brain struggles to generate the internal drive to work on things that are not immediately rewarding. School is full of tasks where the reward (the grade, the knowledge, the career) is weeks or months away. The ADHD brain does not feel that reward as a motivator in the present moment.

XP changes the reward structure. Every 25-minute block becomes a task with an immediate payoff. Instead of studying "because you should," you are studying because there is a concrete thing that happens when you finish. The XP bar fills. The number goes up. The level badge changes.

This is not a trick that fools you into studying. It is a scaffold that gives your reward system something to attach to in the short term while you do the long-term work.

The leveling system also creates identity. "I am Level 12" is a real record of effort. It means you have completed over 400 XP worth of work. That number represents actual hours. Making that visible and permanent creates a sense of accumulated identity as someone who studies. That identity matters.

---

## Study Strategies by Subject Type

Different subjects have different rhythm requirements. Knowing which type you are studying helps you plan your sessions.

**Problem-based subjects (Math, Physics, Engineering)**

These require active engagement. You cannot just read the textbook. Work problems during each Pomodoro. The task queue should list specific problem sets, not chapters. "Ejercicios 3.1 a 3.5" is better than "estudiar derivadas." Do one problem type per Pomodoro when learning new material, and increase variety as you review.

**Reading-heavy subjects (History, Literature, Law, Social Sciences)**

These are deceptively easy to fake. You can read for 25 minutes and retain nothing. Use the notes field aggressively. At the end of each Pomodoro, write one to three sentences summarizing what you just read without looking at the source. This is the simplest active recall technique. It forces the material into memory instead of letting it slide past.

**Language learning**

Alternate between receptive skills (reading, listening) and productive skills (writing, speaking) across Pomodoros. Reading for two blocks, then writing from memory for one block, is more effective than four blocks of passive reading. Use the task queue to track vocabulary sets, grammar topics, and practice exercises separately.

**Programming and technical subjects**

Do not just read tutorials. Type the code. Every Pomodoro should end with something that runs. Use the task queue to list specific functions or concepts to implement. The notes field is useful for capturing what broke and why.

**Memorization-heavy subjects (Anatomy, Chemistry formulas, Dates)**

Space your study sessions. Two 25-minute blocks spread across two days are more effective than four blocks in one night. This is the spacing effect. Use the session history to track how often you are returning to the same material. If you only study anatomy the night before the exam, Study Buddy will show you that gap in the history.

---

## Recommended Study Environments

Study Buddy handles the internal structure. Your environment handles the external one. Both matter.

**Sound**

Some ADHD brains focus better with background noise. Brown noise, lo-fi music, or ambient coffee shop sounds work for many people. Silence works for others. Lyrics almost always hurt. If you are going to play music while using Study Buddy, use instrumentals only and keep the volume moderate. The goal is masking unpredictable sounds, not adding stimulation.

**Space**

Your study space should have one job. If you study in the same place you watch videos, your brain has a mixed association with that space. If possible, have a dedicated spot. This does not need to be a desk. It can be a specific chair, a particular corner, anywhere that becomes consistently associated with focused work.

**Phone**

Put it face down, across the room, on Do Not Disturb. Not on your desk. Not on silent with vibration on. Across the room. The mere presence of a smartphone on a desk reduces cognitive performance even when it is turned off. That is a documented finding. Move it.

**Notifications**

Close email. Close Slack. Close Discord. You cannot use focus mode in Study Buddy and your notification center at the same time. Pick one. The Pomodoro is 25 minutes. Nothing sent in those 25 minutes requires an immediate response.

---

## Combining Study Buddy with Physical Note-Taking

The research on handwritten notes is consistent: writing by hand improves retention compared to typing. You are processing the information to summarize it, not transcribing it verbatim.

Study Buddy and paper notes work together well. Use the app for timing and task management. Use paper for the actual note-taking during each block.

A recommended structure:

During the Pomodoro: handwrite notes, summaries, and diagrams. Do not type them. Do not try to make them perfect. Capture the content.

At the end of the Pomodoro, before you start the break: open the notes field in Study Buddy and write two or three sentences about what you just learned. This is your recall check. If you cannot write it without looking, you did not learn it yet. That tells you something important.

After the session: the Study Buddy notes field has your recall attempts from each block. Your handwritten notes have the detail. Together they give you the full picture of the session.

---

## Troubleshooting

**"I start the timer but I still cannot focus."**

That is common. The timer itself does not produce focus. It creates a container for it. If you are staring at the countdown for five minutes without engaging the material, pause the timer. Write down in the notes field what is blocking you. Sometimes the block is unclear task definition. You have "estudiar para el examen" on your task queue but no idea what that actually means. Break it down. "Leer seccion 4.2" is workable. "Estudiar" is not.

Other times the block is environment. Check your phone first. Physically remove it if needed.

Other times the block is state. You are tired, hungry, or in a bad emotional place. Those are real obstacles. Trying to force a Pomodoro when your nervous system is not available is a bad use of energy. Log a distraction called "estoy agotado" and close the app. Rest is part of the system.

**"I get through the Pomodoro but I feel like I learned nothing."**

Try the recall test. At the end of every block, without looking at your notes or the textbook, write what you just studied. If you can write a paragraph, you learned it. If you cannot write a sentence, you were present in your body but absent from the material. This is extremely common and extremely fixable. Active engagement during the block, not passive reading, is the difference.

**"I keep adding to the task queue but never finishing anything."**

Your tasks are probably too large. "Terminar el capitulo" is a project, not a task. A task is something you can finish in one Pomodoro. Break every queue item to that size. If you cannot finish it in 25 minutes, it needs to be split.

**"The distraction log is just showing me the same three things every session."**

That is valuable. Those three things are your specific weak points. For each one, design a countermeasure. If it is your phone, it leaves the room next session. If it is hunger, you eat before you sit down. If it is a recurring thought, keep a physical notepad next to you just for that. Capture it on paper and return. Study Buddy logs the pattern. You solve it.

**"I feel overwhelmed before I even start."**

Open Study Buddy. Add one task. Set the subject. Press Comenzar. Do not plan the whole session. Do not organize your materials. Do not make a study schedule. Just start the one task.

Everything else can wait until the first Pomodoro ends.

---

## A Note on ADHD and Studying

ADHD is not a deficiency in intelligence or capability. Research consistently shows that ADHD brains have higher than average divergent thinking, pattern recognition, and creative problem-solving. The challenge is not capacity. It is access.

Standard study methods were not designed for the ADHD brain. They were designed for sustained, self-directed attention in quiet environments with delayed rewards. That description is the opposite of what ADHD brains do well.

Study Buddy does not try to make you neurotypical. It builds a structure around how your brain actually works: short bursts, immediate rewards, concrete tasks, awareness of distractions rather than suppression of them.

The goal is not perfect productivity. The goal is showing up consistently. Twenty-five minutes of real engagement every day outperforms three-hour marathon sessions the night before an exam. Every time.

You already have what it takes. This is just a tool that gets out of the way and lets you use it.

---

*Built by Behike. Para cerebros que piensan diferente.*
