# AI Pipeline

The local MVP uses deterministic mock AI so the full demo works without paid external services.

Pipeline:

1. Trigger matching scores the incoming message.
2. AI classification returns structured intent, confidence, reason, and action.
3. The decision engine creates an opportunity.
4. AI drafts a transparent permission request.
5. Safety validation blocks product promotion before consent.
6. After consent, AI generates a grounded product response from enabled product fields.

Production provider:

- `AI_PROVIDER=vertex`
- `VERTEX_PROJECT_ID`
- `VERTEX_LOCATION`
- `VERTEX_MODEL`
- platform Google credentials through `GOOGLE_APPLICATION_CREDENTIALS` or workload identity

The system stores concise audit explanations, not hidden chain-of-thought.
