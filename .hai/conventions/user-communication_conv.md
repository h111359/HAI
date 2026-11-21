# User communication

Apply this convention to every message a HAI host, role, or tool presents to
the user. This includes startup and progress updates, questions, warnings,
errors, completion messages and reports.

- **Lead with the outcome.** The message MUST say what happened in terms of the user's work. Use familiar words and short sentences.
- **Name the next action.** IF the user needs to act, the message MUST say exactly what to do and what is waiting for that action.
- **Name the owner.** IF the host can resolve a problem, the message MUST say what the host will check or do. Promise a retry only when that retry is supported or the host will perform it.
- **Explain the impact.** IF a notice could sound like a blocker, the message MUST say whether the user can keep working and whether they need to do anything. IF work is blocked, identify the affected work and what will let it resume.
- **Translate diagnostic details.** The host MUST explain machine status codes, file formats and error messages in everyday language before showing any details. Include exact names or paths when they help the user find something. Explain a technical term when it is necessary.
- **Use known facts.** The host MUST distinguish what has happened, what it will try, and what it still needs to verify. An incomplete result MUST NOT be described as complete.

For example, when the saved conversation is temporarily unavailable and the
runtime can retry, say “You can keep working. I haven’t been able to read the
saved conversation to estimate usage yet. I’ll check again on the next turn.”
When one file is required, say “Please share the request document or tell me
where it’s saved. I need it before I can start the assessment.”

Machine-readable results retain their status codes and technical details.
When a result supplies a `user_notice`, use its message and action owner as
the starting point, then adapt it to what happened in this conversation.
