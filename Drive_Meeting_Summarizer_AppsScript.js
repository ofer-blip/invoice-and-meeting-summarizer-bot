/**
 * =========================================================================
 * סקריפט אוטומציה בענן: סיכום פגישות ישיר מ-Google Drive ומייל
 * D-Dialog Meeting Summarizer — Google Apps Script (Cloud)
 * =========================================================================
 * 
 * הוראות התקנה מהירות (2 דקות):
 * 1. היכנס לכתובת: https://script.google.com
 * 2. לחץ על "פרויקט חדש" (New Project).
 * 3. מחק את מה שכתוב שם, הדבק את כל תוכן הקובץ הזה, ושמור (Ctrl+S).
 * 4. לחץ על "הפעל" (Run) בפונקציה checkAndSummarizeMeetings פעם ראשונה כדי לאשר הרשאות.
 * 5. בתפריט צד שמאל לחץ על "טריגרים" (Triggers / סמל השעון) ⬅ "הוסף טריגר":
 *    - בחר פונקציה: checkAndSummarizeMeetings
 *    - מקור אירוע: מבוסס זמן (Time-driven) ⬅ כל 5 או 10 דקות (או לפי הצורך).
 * 
 * זהו! מעכשיו כל הקלטה שתעלה מהטלפון לתיקיית 'הקלטות לפגישות' תעובד אוטומטית,
 * והסיכום יישלח אליך למייל ויישמר ב-Drive גם כשהמחשב מכובה לחלוטין!
 */

// הגדרות מערכת ומפתחות
var GEMINI_API_KEY = "AQ.Ab8RN6IL8JL8EC1V4LyOTMwZakgkenawg4RFmX7-0A5YMA0Gyg";
var GEMINI_MODEL = "gemini-2.5-flash";

// שמות התיקיות ב-Google Drive
var FOLDER_INPUT_NAME = "הקלטות לפגישות";
var FOLDER_OUTPUT_NAME = "סיכומי פגישות";
var FOLDER_ARCHIVE_NAME = "הקלטות שעובדו";

// כתובת מייל לקבלת הסיכום (השאר ריק כדי לשלוח אוטומטית למייל שלך)
var NOTIFICATION_EMAIL = "";

var PROMPT_MEETING_SUMMARY = 
  "אתה עוזר מקצועי לניהול, תמלול וסיכום פגישות עסקיות ואסטרטגיות בעברית.\n" +
  "האזן היטב לקובץ השמע המצורף של הפגישה/השיחה, והפק סיכום מקיף, תכליתי ומסודר היטב בעברית טבעית ורהוטה.\n\n" +
  "חשוב מאוד: הקפד על חלוקה מרווחת וקריאה, שבה כל נושא, החלטה ותובנה מופיעים בשורה נפרדת (ולא כגוש טקסט רציף).\n\n" +
  "אנא בנה את הסיכום לפי המבנה המדויק הבא:\n\n" +
  "# סיכום פגישה: [נושא הפגישה המרכזי]\n\n" +
  "**תאריך ושעה משוערת:** [אם מוזכר בשיחה, אחרת רשום תאריך נוכחי]\n" +
  "**משתתפים/דוברים שזוהו:** [שמות הדוברים או תפקידים שזוהו במהלך השיחה]\n" +
  "**נושא מרכזי:** [משפט אחד שמסביר את מהות הפגישה]\n\n" +
  "---\n\n" +
  "## 1. תקציר מנהלים (Executive Summary)\n" +
  "[2-3 פסקאות קצרות וממוקדות שמסבירות את הרקע, הצורך והכיוונים המרכזיים].\n\n" +
  "## 2. נקודות מפתח ונושאים שנדונו\n" +
  "(הקפד לרשום כל נושא כנקודה נפרדת בשורה משלו עם כותרת מודגשת):\n" +
  "* **[נושא 1]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]\n" +
  "* **[נושא 2]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]\n" +
  "* **[נושא 3]:** [פירוט תמציתי של מה שנדון, עמדות הצדדים ומשמעויות]\n\n" +
  "## 3. החלטות שהתקבלו\n" +
  "(רשימה ממוספרת שבה כל החלטה מופיעה בשורה נפרדת לחלוטין ללא טקסט רציף):\n" +
  "1. **[החלטה ראשונה]:** [פירוט קצר של מה שהוחלט וסוכם]\n" +
  "2. **[החלטה שנייה]:** [פירוט קצר של מה שהוחלט וסוכם]\n" +
  "3. **[החלטה שלישית]:** [פירוט קצר של מה שהוחלט וסוכם]\n\n" +
  "## 4. משימות לביצוע ותוכנית פעולה (Action Items)\n" +
  "- [ ] **משימה 1:** [תיאור המשימה] | **אחראי:** [שם/תפקיד] | **יעד:** [אם מוזכר]\n" +
  "- [ ] **משימה 2:** [תיאור המשימה] | **אחראי:** [שם/תפקיד] | **יעד:** [אם מוזכר]\n\n" +
  "## 5. תובנות ודגשים להמשך\n" +
  "(הקפד שכל תובנה תהיה בנקודה נפרדת בשורה משלה):\n" +
  "* **[תובנה 1]:** [דגש, הזדמנות או נושא למעקב]\n" +
  "* **[תובנה 2]:** [דגש, הזדמנות או נושא למעקב]\n\n" +
  "---\n" +
  "*הערה: שמור על עברית טבעית, מקצועית וברורה, תוך שמירה על הקשר עסקי מדויק וריווח מלא בין פסקאות.*";

// Webhook Endpoints: מאפשר הפעלה מיידית מכל מקום בלחיצת קישור או Webhook
function doGet(e) {
  checkAndSummarizeMeetings();
  return ContentService.createTextOutput("✓ סנכרון וסיכום הפגישות בוצע בהצלחה!").setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  checkAndSummarizeMeetings();
  return ContentService.createTextOutput("✓ סנכרון וסיכום הפגישות בוצע בהצלחה!").setMimeType(ContentService.MimeType.TEXT);
}

function checkAndSummarizeMeetings() {
  Logger.log("מתחיל בדיקת הקלטות חדשות ב-Google Drive...");
  
  var inputFolder = getOrCreateFolder(FOLDER_INPUT_NAME);
  var outputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
  var archiveFolder = getOrCreateFolder(FOLDER_ARCHIVE_NAME);
  
  var files = inputFolder.getFiles();
  var processedCount = 0;
  
  while (files.hasNext()) {
    var file = files.next();
    var fileName = file.getName();
    var mimeType = file.getMimeType();
    
    // Check if it's an audio or video file
    var lowerName = fileName.toLowerCase();
    var isAudio = lowerName.endsWith('.m4a') || lowerName.endsWith('.mp3') || lowerName.endsWith('.wav') || 
                  lowerName.endsWith('.aac') || lowerName.endsWith('.ogg') || lowerName.endsWith('.mp4') || 
                  mimeType.indexOf('audio') !== -1 || mimeType.indexOf('video') !== -1;
                  
    if (!isAudio) {
      continue;
    }
    
    Logger.log("מעבד הקלטה: " + fileName + " (" + (file.getSize() / (1024*1024)).toFixed(2) + " MB)");
    
    try {
      // 1. Prepare Base64 audio payload for Gemini
      var blob = file.getBlob();
      var audioBase64 = Utilities.base64Encode(blob.getBytes());
      var audioMime = mimeType;
      if (lowerName.endsWith('.m4a') || (lowerName.endsWith('.mp4') && lowerName.indexOf('audio') !== -1)) {
        audioMime = "audio/mp4";
      } else if (lowerName.endsWith('.mp3')) {
        audioMime = "audio/mp3";
      } else if (lowerName.endsWith('.wav')) {
        audioMime = "audio/wav";
      }
      
      // 2. Call Gemini API
      var url = "https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL + ":generateContent?key=" + GEMINI_API_KEY;
      
      var payload = {
        "contents": [
          {
            "parts": [
              {
                "inline_data": {
                  "mime_type": audioMime,
                  "data": audioBase64
                }
              },
              {
                "text": PROMPT_MEETING_SUMMARY + "\n\nשם קובץ ההקלטה המקורי: " + fileName
              }
            ]
          }
        ]
      };
      
      var options = {
        "method": "post",
        "contentType": "application/json",
        "payload": JSON.stringify(payload),
        "muteHttpExceptions": true
      };
      
      var response = UrlFetchApp.fetch(url, options);
      var responseCode = response.getResponseCode();
      
      if (responseCode !== 200) {
        Logger.log("שגיאה מ-Gemini API: " + response.getContentText());
        continue;
      }
      
      var json = JSON.parse(response.getContentText());
      var summaryText = json.candidates[0].content.parts[0].text;
      
      // 3. Build HTML Output with RTL
      var htmlContent = buildHtmlDocument(summaryText, fileName);
      
      // 4. Save to Drive Output Folder
      var dateStr = Utilities.formatDate(new Date(), "GMT+3", "yyyy-MM-dd_HH-mm");
      var baseName = "סיכום_פגישה_" + dateStr + "_" + fileName.replace(/\.[^/.]+$/, "");
      
      outputFolder.createFile(baseName + ".html", htmlContent, MimeType.HTML);
      outputFolder.createFile(baseName + ".md", summaryText, MimeType.PLAIN_TEXT);
      
      // 5. Move original recording to Archive folder
      file.moveTo(archiveFolder);
      
      // 6. Send Summary Email
      var recipient = NOTIFICATION_EMAIL || Session.getActiveUser().getEmail();
      var subject = "סיכום פגישה: " + fileName.replace(/\.[^/.]+$/, "");
      
      GmailApp.sendEmail(recipient, subject, summaryText, {
        htmlBody: htmlContent,
        name: "סיכום פגישות AI"
      });
      
      Logger.log("✓ סיום בהצלחה עבור: " + fileName + ". המייל נשלח אל: " + recipient);
      processedCount++;
      
    } catch (e) {
      Logger.log("❌ שגיאה בעיבוד " + fileName + ": " + e.toString());
    }
  }
  
  Logger.log("סיום ריצה: עובדו " + processedCount + " הקלטות.");
}

function buildHtmlDocument(markdown, fileName) {
  // Convert Markdown syntax to styled HTML
  var html = markdown
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/^# (.+)$/gm, "<h1>$1</h1>")
    .replace(/^## (.+)$/gm, "<h2>$1</h2>")
    .replace(/^### (.+)$/gm, "<h3>$1</h3>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/^- \[ \] (.+)$/gm, "<div style='background:rgba(15,23,42,0.04);border:1px solid #E2E8F0;padding:8px 12px;border-radius:8px;margin-bottom:6px;'>⬜ $1</div>")
    .replace(/^- \[x\] (.+)$/gm, "<div style='background:rgba(16,185,129,0.08);border:1px solid #10B981;padding:8px 12px;border-radius:8px;margin-bottom:6px;'>✅ $1</div>")
    .replace(/^\* (.+)$/gm, "<li style='margin-bottom:8px;'>$1</li>")
    .replace(/^[0-9]+\. (.+)$/gm, "<li style='margin-bottom:8px;'>$1</li>")
    .replace(/^---$/gm, "<hr style='border:0;height:1px;background:#E2E8F0;margin:24px 0;'>");
    
  var paragraphs = html.split("\n\n");
  var formatted = [];
  for (var i = 0; i < paragraphs.length; i++) {
    var p = paragraphs[i].trim();
    if (!p) continue;
    if (p.indexOf("<h") === 0 || p.indexOf("<li") === 0 || p.indexOf("<hr") === 0 || p.indexOf("<div") === 0) {
      formatted.push(p);
    } else {
      formatted.push("<p style='margin-bottom:14px;line-height:1.7;'>" + p.replace(/\n/g, "<br>") + "</p>");
    }
  }
  
  var dateFormatted = Utilities.formatDate(new Date(), "GMT+3", "dd/MM/yyyy HH:mm");
  
  return "<!DOCTYPE html><html lang='he' dir='rtl'><head><meta charset='UTF-8'>" +
    "<style>" +
    "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; direction: rtl; text-align: right; background-color: #F8FAFC; color: #1E293B; padding: 20px; line-height: 1.7; }" +
    ".card { max-width: 800px; margin: 0 auto; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }" +
    "h1 { color: #0F172A; font-size: 1.8rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 12px; margin-bottom: 20px; }" +
    "h2 { color: #D97706; font-size: 1.3rem; margin-top: 28px; margin-bottom: 12px; }" +
    "h3 { color: #0284C7; font-size: 1.1rem; margin-top: 18px; }" +
    ".meta { background: #F1F5F9; border-radius: 8px; padding: 12px 16px; margin-bottom: 24px; font-size: 0.95rem; color: #64748B; }" +
    "</style></head><body><div class='card'>" +
    "<div class='meta'><div>קובץ מקור: <strong>" + fileName + "</strong></div><div>תאריך הפקה: <strong>" + dateFormatted + "</strong></div></div>" +
    formatted.join("\n") +
    "</div></body></html>";
}

function getOrCreateFolder(folderName) {
  if (!folderName) {
    folderName = FOLDER_INPUT_NAME;
  }
  var folders = DriveApp.getFoldersByName(folderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  return DriveApp.createFolder(folderName);
}
