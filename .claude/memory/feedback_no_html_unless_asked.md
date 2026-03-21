---
name: No HTML exports unless asked
description: Do not create HTML versions of documents unless the user explicitly requests it
type: feedback
---

Do not create `.html` exports of documents (briefs, reports, copy docs, etc.) unless the user explicitly asks for it.

**Why:** User only wants HTML when they specifically need it. Creating it by default adds noise.

**How to apply:** When exporting documents, default to `.md` and `.docx` only. Skip the HTML step unless the user says "give me this as HTML" or similar.
