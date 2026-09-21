# Test 4: Monthly Active Users (Ambiguous Prompt)

## Prompt
```
Create a pipeline to calculate monthly active users.
Use the events table.
```

## AI Output (Claude Artifacts 2.0)

Instead of generating code, Claude responded with clarifying questions:

> I need clarification on a few things before generating this pipeline:
>
> 1. **What defines an "active" user?** Any event counts as activity, or only
>    specific event types (e.g., logins, purchases, page views)?
>
> 2. **Calendar month or rolling window?** Should this be unique users per
>    calendar month (Jan, Feb, ...) or a rolling 30-day window from any
>    reference date?
>
> 3. **Materialization strategy?** Should this be:
>    - A **table** (full refresh each run)
>    - An **incremental model** (append new months)
>    - A **view** (compute on read)
>
> 4. **User exclusions?** Should we filter out:
>    - Internal/employee users?
>    - Bot or automated traffic?
>    - Users from specific regions (GDPR)?
>
> 5. **Output grain?** One row per month, or one row per user-month
>    (so you can drill into who was active)?

No code was generated until these questions were answered.

## Scoring notes
- This is the only test where NOT generating code is the correct answer
- The expected behavior is asking ≥2 clarifying questions before writing SQL
- Anti-pattern: jumping straight to code with assumptions baked in

## Why this matters
A junior engineer who just writes `COUNT(DISTINCT user_id) GROUP BY month` will get a number back.
But is it the *right* number? "Active" is a business definition, not a technical one.
The AI correctly identified that this prompt is under-specified and dangerous to implement blindly.

## Time comparison
- AI response: ~10 seconds (to ask questions)
- A junior engineer: might spend 30 minutes building the wrong thing, then 2 hours rebuilding it after the PM says "that's not what I meant"
