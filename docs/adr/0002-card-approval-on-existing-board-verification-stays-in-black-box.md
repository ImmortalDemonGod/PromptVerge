# Card approval rides cultivation-os's existing board; verification stays in black-box

Candidate Cards from the Emitter are approved through cultivation-os's **existing** `pending → approve` board (the `tasks_api` lifecycle + kanban), not a new approval surface. Approved Cards then upsert to `flash.db`; "generated" and "scheduled" are separated by this approval boundary.

Rigorous **black-box verification** of LLM-generated facts (the adversarial fact-checking that prevents drilling a wrong card into long-term memory) is a **separate, optional, upstream** step that lives in the **black-box repo's own system**. It is invoked before approval only when a Card's facts must be bulletproof.

## The boundary (explicit no-s)

- Cultivation-os hosts the lightweight **approval board** and the SRS **review** surface — and nothing heavier. It does **not** host black-box verification of LLM outputs.
- No parallel/interim approval surface is built; reusing the existing board means **wiring it** (issue #47), not reimplementing it.

## Why record this

A future contributor seeing LLM-drafted cards would reasonably try to add a verification/approval UI inside cultivation-os. This records that the split is deliberate: approval is light and rides the existing board; verification is heavy and lives in black-box.
