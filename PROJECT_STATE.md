# D-Dialog Project State & Context (STABLE BASELINE)

## 1. ארכיטקטורת מערכת (Strict Rules)
* **Backend:** Python (Flask) running exclusively on Google Cloud Run (`src/app.py`). 
* **Apps Script is DEPRECATED AND ABANDONED.** DO NOT modify or suggest Apps Script solutions.
* **Frontend:** PWA served statically via the Flask server (`docs/index.html`).
* **Database & Auth:** Firestore manages active users, configurations, custom prompts, categories, and billing minutes.

## 2. Pipeline זרימת עבודה מרכזית (Core Flow)
1. **Trigger:** `/sync` endpoint is called.
2. **Locking (Early Archive):** Files found in Drive (`הקלטות לפגישות` + subfolders) are **immediately** moved to the archive folder (`הקלטות שעובדו`) BEFORE processing to prevent duplicates and race conditions.
3. **AI Processing Pipeline:**
   * Audio is sent to **Deepgram** for transcription (Speech-to-Text).
   * Text is sent to **Gemini** for structured summarization based on Firestore prompts.
4. **Output:** MD, HTML, and PDF are generated and saved to Drive.
5. **Delivery:** `gmail_service.py` sends a single email to the user.

## 3. הנחיות פיתוח ומניעת רגרסיות (Anti-Regression Rules)
* **No Patches:** Do not make isolated patches. Before modifying code, check how it affects the entire pipeline (e.g., Subfolders, Email sending).
* **Reference State:** All stable code must be committed via Git. If a new feature breaks existing logic (e.g., double emails, ignoring subfolders), revert to the last stable reference.
* **Single Source of Truth:** `drive_meeting_sync.py` is the only manager for sync logic. `meeting_summarizer.py` is strictly for the AI pipeline.
