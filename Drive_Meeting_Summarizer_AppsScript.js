/**
 * =========================================================================
 * אפליקציית ענן ווב: סיכום פגישות ישיר מ-Google Drive ומייל
 * D-Dialog Meeting Summarizer — Google Apps Script (Web App)
 * =========================================================================
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

/**
 * מציג ממשק ווב יפהפה ואסתטי לטלפון עם כפתור הפעלה
 */
function doGet(e) {
  var html = '<!DOCTYPE html>' +
    '<html lang="he" dir="rtl">' +
    '<head>' +
    '  <meta charset="UTF-8">' +
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">' +
    '  <title>סיכום פגישות - D-Dialog</title>' +
    '  <style>' +
    '    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }' +
    '    body { background: #0F172A; color: #F8FAFC; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; direction: rtl; text-align: center; }' +
    '    .card { background: #1E293B; border: 1px solid #334155; border-radius: 24px; padding: 32px 24px; width: 100%; max-width: 420px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }' +
    '    .logo-badge { width: 64px; height: 64px; background: linear-gradient(135deg, #3B82F6, #1D4ED8); border-radius: 20px; display: inline-flex; align-items: center; justify-content: center; font-size: 30px; margin-bottom: 20px; box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.4); }' +
    '    h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #FFFFFF; }' +
    '    p.desc { font-size: 14px; color: #94A3B8; margin-bottom: 28px; line-height: 1.5; }' +
    '    .action-btn {' +
    '      width: 100%; padding: 18px 20px; font-size: 18px; font-weight: 700; color: #FFFFFF;' +
    '      background: linear-gradient(135deg, #2563EB, #1D4ED8); border: none; border-radius: 16px;' +
    '      cursor: pointer; transition: all 0.2s ease; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.35);' +
    '      display: flex; align-items: center; justify-content: center; gap: 10px;' +
    '    }' +
    '    .action-btn:active { transform: scale(0.98); opacity: 0.9; }' +
    '    .action-btn:disabled { background: #475569; color: #94A3B8; cursor: not-allowed; transform: none; box-shadow: none; }' +
    '    #status-box { margin-top: 24px; padding: 14px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; display: none; }' +
    '    .status-running { background: rgba(59, 130, 246, 0.15); border: 1px solid #3B82F6; color: #93C5FD; display: block !important; }' +
    '    .status-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #6EE7B7; display: block !important; }' +
    '    .status-error { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #FCA5A5; display: block !important; }' +
    '    .steps { margin-top: 28px; padding-top: 20px; border-top: 1px solid #334155; text-align: right; }' +
    '    .steps h3 { font-size: 13px; color: #64748B; margin-bottom: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }' +
    '    .step-item { font-size: 13px; color: #CBD5E1; margin-bottom: 8px; display: flex; align-items: flex-start; gap: 8px; }' +
    '    .step-num { width: 18px; height: 18px; background: #334155; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; color: #94A3B8; flex-shrink: 0; margin-top: 2px; }' +
    '  </style>' +
    '</head>' +
    '<body>' +
    '  <div class="card">' +
    '    <div class="logo-badge">🎙️</div>' +
    '    <h1>סיכום פגישות AI</h1>' +
    '    <p class="desc">סנכרון הקלטות מ-Google Drive, הפקת סיכום מובנה ושליחה ישירה למייל.</p>' +
    '    ' +
    '    <button id="runBtn" class="action-btn" onclick="startProcess()">' +
    '      <span>🎙️</span> <span>סכם פגישות עכשיו</span>' +
    '    </button>' +
    '    ' +
    '    <div id="status-box"></div>' +
    '    ' +
    '    <div class="steps">' +
    '      <h3>איך זה עובד?</h3>' +
    '      <div class="step-item"><span class="step-num">1</span> <span>מעלים הקלטה מהטלפון לתיקיית <strong>"הקלטות לפגישות"</strong> ב-Drive.</span></div>' +
    '      <div class="step-item"><span class="step-num">2</span> <span>לוחצים על הכפתור הכחול למעלה.</span></div>' +
    '      <div class="step-item"><span class="step-num">3</span> <span>הסיכום המלא נוחת אצלך במייל וב-Drive תוך שניות!</span></div>' +
    '    </div>' +
    '  </div>' +
    '  <script>' +
    '    function startProcess() {' +
    '      var btn = document.getElementById("runBtn");' +
    '      var box = document.getElementById("status-box");' +
    '      btn.disabled = true;' +
    '      btn.innerHTML = "<span>⏳</span> <span>מעבד הקלטות... אנא המתן</span>";' +
    '      box.className = "status-running";' +
    '      box.innerHTML = "🔍 סורק את Google Drive ומעבד את ההקלטה ב-Gemini... (אורך כ-30 שניות)";' +
    '      ' +
    '      google.script.run' +
    '        .withSuccessHandler(function(res) {' +
    '          btn.disabled = false;' +
    '          btn.innerHTML = "<span>🎙️</span> <span>סכם פגישות שוב</span>";' +
    '          box.className = "status-success";' +
    '          box.innerHTML = "✅ " + res;' +
    '        })' +
    '        .withFailureHandler(function(err) {' +
    '          btn.disabled = false;' +
    '          btn.innerHTML = "<span>🔄</span> <span>נסה שוב</span>";' +
    '          box.className = "status-error";' +
    '          box.innerHTML = "❌ שגיאה: " + err;' +
    '        })' +
    '        .checkAndSummarizeMeetings();' +
    '    }' +
    '  </script>' +
    '</body>' +
    '</html>';
    
  return HtmlService.createHtmlOutput(html)
    .setTitle("D-Dialog | סיכום פגישות")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, user-scalable=no');
}

function doPost(e) {
  var result = checkAndSummarizeMeetings();
  return ContentService.createTextOutput(result).setMimeType(ContentService.MimeType.TEXT);
}

function checkAndSummarizeMeetings() {
  Logger.log("מתחיל בדיקת הקלטות חדשות ב-Google Drive...");
  
  var inputFolder = getOrCreateFolder(FOLDER_INPUT_NAME);
  var outputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
  var archiveFolder = getOrCreateFolder(FOLDER_ARCHIVE_NAME);
  
  var files = inputFolder.getFiles();
  var processedCount = 0;
  var lastFileName = "";
  
  while (files.hasNext()) {
    var file = files.next();
    var fileName = file.getName();
    var mimeType = file.getMimeType();
    
    var lowerName = fileName.toLowerCase();
    var isAudio = lowerName.endsWith('.m4a') || lowerName.endsWith('.mp3') || lowerName.endsWith('.wav') || 
                  lowerName.endsWith('.aac') || lowerName.endsWith('.ogg') || lowerName.endsWith('.mp4') || 
                  mimeType.indexOf('audio') !== -1 || mimeType.indexOf('video') !== -1;
                  
    if (!isAudio) {
      continue;
    }
    
    Logger.log("מעבד הקלטה: " + fileName + " (" + (file.getSize() / (1024*1024)).toFixed(2) + " MB)");
    lastFileName = fileName;
    
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
      return "שגיאה בעיבוד הקובץ: " + e.toString();
    }
  }
  
  if (processedCount === 0) {
    return "לא נמצאו הקלטות חדשות בתיקיית 'הקלטות לפגישות'. אנא העלה הקלטה ל-Drive ולחץ שוב.";
  }
  
  return "הסנכרון הושלם בהצלחה! עובדו " + processedCount + " הקלטות. הסיכום נשלח למייל ונשמר ב-Drive.";
}

function buildHtmlDocument(markdown, fileName) {
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
