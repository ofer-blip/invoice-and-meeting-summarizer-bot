# D-Dialog Agent Autonomy & AI Strategy

When working with Ofer on coding tasks:
1. **Proactive Model Routing**: At the start of a task, or when switching task complexity, PROACTIVELY recommend which model Ofer should use. Suggest Heavy models (Pro/Opus) for deep logic/reasoning/parsing, and Light models (Flash) for simple code fixes or text classification.
2. **High Autonomy**: Do not stop to ask for permission on minor bug fixes or trivial implementation details. Implement them and summarize afterward. 
3. **Data Formatting**: When extracting AI data for systems (like invoices), enforce JSON/Table output. When generating text for humans (like summaries), enforce Bullet points.
