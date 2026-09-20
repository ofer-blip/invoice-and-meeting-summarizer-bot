# D-Dialog Project State & Context

### Current Focus (Updated: September 2026)
We are currently developing and iterating on the **Meeting Summarizer backend using Python and Google Cloud Run**. 

### Architecture Flexibility
This project uses a hybrid approach. We have Apps Script components and Cloud Run components. 
*Currently*, our active work is on the Cloud Run (Python) service located in the src/ directory.

### Last Session Handoff
- Deployed a fix for the dashboard UI (Spinner CSS).
- Updated the Drive meeting sync to track user quotas (minutes used & number of uses).
- Configured Cloud Scheduler to run every 5 minutes.
- **Next Steps:** We were discussing folder configurations (e.g., making sure the 'בדיקות' folder is added to the user's dashboard with transcription enabled so it processes correctly).
