# CallBuddy MVP Landing Page

AI-powered phone calls for people with social anxiety.

## Run locally

```bash
cd ~/behique/callbuddy
python3 -m http.server 8094
```

Then open http://localhost:8094

## Structure

Single file: `index.html`. No dependencies, no frameworks, no build step.

## Waitlist

Email signups are stored in browser localStorage under the key `callbuddy_waitlist`. To view collected emails, open the browser console and run:

```js
JSON.parse(localStorage.getItem('callbuddy_waitlist'))
```

Replace with a real backend (Supabase, Airtable, etc.) before launch.
