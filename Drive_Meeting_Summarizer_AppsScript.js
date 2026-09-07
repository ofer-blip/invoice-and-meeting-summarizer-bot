/**
 * =========================================================================
 * אפליקציית ענן ווב: סיכום פגישות ישיר מ-Google Drive ומייל
 * D-Dialog Meeting Summarizer — Google Apps Script (Web App)
 * =========================================================================
 */

// הגדרות מערכת ומפתחות
var GEMINI_API_KEY = "AQ.Ab8RN6IL8JL8EC1V4LyOTMwZakgkenawg4RFmX7-0A5YMA0Gyg";
var GEMINI_MODEL = "gemini-2.5-flash";

/// שמות התיקיות ותיקיות המשנה ב-Google Drive
var FOLDER_INPUT_NAME = "הקלטות לפגישות";
var FOLDER_OUTPUT_NAME = "סיכומי פגישות";
var FOLDER_ARCHIVE_NAME = "הקלטות שעובדו";
var FOLDER_SUB_BUSINESS = "עסקים";
var FOLDER_SUB_GEFEN = "גפ\"ן";

// שמות מסמכי הריכוז המרכזיים ב-Google Drive
var MASTER_DOC_BUSINESS_NAME = "💼 ריכוז סיכומי פגישות עסקיות";
var MASTER_DOC_GEFEN_NAME = "📋 ריכוז סיכומי פגישות גפ\"ן";

// כתובת מייל לקבלת הסיכום (השאר ריק כדי לשלוח אוטומטית למייל שלך)
var NOTIFICATION_EMAIL = "";

// פרומפט מותאם אישית למודל השפה
var PROMPT_MEETING_SUMMARY = "אתה עוזר מקצועי לניהול, תמלול וסיכום פגישות עסקיות, פדגוגיות ואסטרטגיות בעברית.\n" +
"האזן היטב לקובץ השמע המצורף של הפגישה/השיחה, והפק סיכום מקיף, תכליתי ומסודר היטב בעברית טבעית ורהוטה.\n\n" +
"חשוב מאוד:\n" +
"1. הקפד על חלוקה מרווחת וקריאה, שבה כל נושא, החלטה ותובנה מופיעים בשורה נפרדת (ולא כגוש טקסט רציף).\n" +
"2. סווג את הפגישה במדויק בשדה הקטגוריה: 'עסקים' או 'גפ\"ן'.\n\n" +
"אנא בנה את הסיכום לפי המבנה המדויק הבא:\n\n" +
"# סיכום פגישה: [נושא הפגישה המרכזי]\n\n" +
"**תאריך ושעה:** [תאריך ושעת הפגישה]\n" +
"**קטגוריה:** [עסקים / גפ\"ן]\n" +
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
"*הערה: שמור על עברית טבעית, מקצועית וברורה, תוך שמירה על הקשר מדויק וריווח מלא בין פסקאות.*";

// פרטי מיתוג וגרסה (D-Dialog)
var APP_VERSION = "v2.4";
var BRAND_NAME = "D-Dialog";
var BRAND_TAGLINE = "אוטומציה וסוכני AI מתקדמים לעסקים";
var BRAND_WEBSITE = "https://ddialog.co.il";
var BRAND_PHONE = "052-6947202";

// קטגוריות ראשוניות ברירת מחדל (יווצרו בדרייב אם התיקייה ריקה)
var DEFAULT_CATEGORIES = ["עסקים", "גפ\"ן"];

// כתובת ישירה של האייקון ברשת (עבור הוספה למסך הבית בנייד)
var APP_ICON_URL = "https://raw.githubusercontent.com/ofer-blip/invoice-and-meeting-summarizer-bot/main/icon_ddialog_meeting.jpg";

// אייקון האפליקציה ב-Base64 (למסמכי Google Doc וגיבוי)
var APP_ICON_BASE64 = "data:image/jpeg;base64,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";

/**
 * סורק את תיקיית "סיכומי פגישות" ב-Google Drive ומחזיר את כל שמות התיקיות
 */
function getAvailableCategoriesFromDrive() {
  var categories = [];
  try {
    var outputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
    var subFolders = outputFolder.getFolders();
    while (subFolders.hasNext()) {
      var subFolder = subFolders.next();
      var folderName = subFolder.getName();
      if (categories.indexOf(folderName) === -1) {
        categories.push(folderName);
      }
    }
  } catch (e) {
    Logger.log("שגיאה בסריקת תיקיות מ-Drive: " + e.toString());
  }
  
  // אם אין עדיין תיקיות בדרייב, צור את תיקיות ברירת המחדל
  if (categories.length === 0) {
    var defaults = (typeof DEFAULT_CATEGORIES !== 'undefined' && DEFAULT_CATEGORIES.length > 0) ? 
      DEFAULT_CATEGORIES : ["עסקים", "גפ\"ן"];
    try {
      var outputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
      for (var i = 0; i < defaults.length; i++) {
        getOrCreateSubFolder(outputFolder, defaults[i]);
        categories.push(defaults[i]);
      }
    } catch (e) {
      categories = defaults;
    }
  }
  return categories;
}

/**
 * מציג ממשק ווב יפהפה ואסתטי לטלפון עם כפתור הפעלה
 */
function doGet(e) {
  // ---------------------------------------------------------
  // API Endpoint לסנכרון מקומי (משיכת קבצי MD)
  // ---------------------------------------------------------
  if (e && e.parameter && e.parameter.action === 'sync') {
    try {
      var outputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
      var result = [];
      
      // Get files in root folder
      var files = outputFolder.getFilesByType(MimeType.PLAIN_TEXT);
      while (files.hasNext()) {
        var file = files.next();
        if (file.getName().endsWith('.md')) {
          result.push({ name: file.getName(), content: file.getBlob().getDataAsString(), category: 'D-Dialog' });
        }
      }
      
      // Get files in subfolders
      var subFolders = outputFolder.getFolders();
      while (subFolders.hasNext()) {
        var subFolder = subFolders.next();
        var catName = subFolder.getName();
        var subFiles = subFolder.getFilesByType(MimeType.PLAIN_TEXT);
        while (subFiles.hasNext()) {
          var sFile = subFiles.next();
          if (sFile.getName().endsWith('.md')) {
            result.push({ name: sFile.getName(), content: sFile.getBlob().getDataAsString(), category: catName });
          }
        }
      }
      
      return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
    } catch (err) {
      return ContentService.createTextOutput(JSON.stringify({error: err.toString()})).setMimeType(ContentService.MimeType.JSON);
    }
  }

  // ---------------------------------------------------------
  // יצירת אפשרויות התפריט הנפתח דינמית מתוך תיקיות ה-Drive
  // ---------------------------------------------------------
  var categories = getAvailableCategoriesFromDrive();
  var optionsHtml = '<option value="auto">✨ סיווג אוטומטי (AI)</option>';
  for (var i = 0; i < categories.length; i++) {
    var cat = categories[i];
    var icon = "📁";
    if (cat.indexOf("עסק") !== -1) icon = "🏢";
    else if (cat.indexOf("גפ") !== -1 || cat.indexOf("חינוך") !== -1 || cat.indexOf("כית") !== -1 || cat.indexOf("לילך") !== -1) icon = "🏫";
    else if (cat.indexOf("גוונ") !== -1) icon = "🎨";
    optionsHtml += '<option value="' + cat.replace(/"/g, '&quot;') + '">' + icon + ' ' + cat + '</option>';
  }

  // ---------------------------------------------------------
  // ממשק המשתמש הרגיל לטלפון
  // ---------------------------------------------------------
  var html = '<!DOCTYPE html>' +
    '<html lang="he" dir="rtl">' +
    '<head>' +
    '  <meta charset="UTF-8">' +
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">' +
    '  <meta name="theme-color" content="#0F172A">' +
    '  <link rel="icon" type="image/jpeg" href="' + APP_ICON_URL + '">' +
    '  <link rel="shortcut icon" href="' + APP_ICON_URL + '">' +
    '  <link rel="apple-touch-icon" href="' + APP_ICON_URL + '">' +
    '  <meta property="og:image" content="' + APP_ICON_URL + '">' +
    '  <title>סיכום פגישות - D-Dialog</title>' +
    '  <style>' +
    '    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }' +
    '    body { background: #0F172A; color: #F8FAFC; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; direction: rtl; text-align: center; }' +
    '    .card { background: #1E293B; border: 1px solid #334155; border-radius: 24px; padding: 32px 24px; width: 100%; max-width: 440px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }' +
    '    .logo-container { margin-bottom: 20px; display: inline-block; }' +
    '    .logo-img { width: 76px; height: 76px; border-radius: 20px; box-shadow: 0 10px 22px -3px rgba(14, 165, 233, 0.45); object-fit: cover; display: block; }' +
    '    h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #FFFFFF; }' +
    '    p.desc { font-size: 14px; color: #94A3B8; margin-bottom: 26px; line-height: 1.5; }' +
    '    .action-btn {' +
    '      width: 100%; padding: 18px 20px; font-size: 17px; font-weight: 700; color: #FFFFFF;' +
    '      background: linear-gradient(135deg, #0EA5E9, #2563EB); border: none; border-radius: 16px;' +
    '      cursor: pointer; transition: all 0.2s ease; box-shadow: 0 8px 20px rgba(14, 165, 233, 0.35);' +
    '      display: flex; align-items: center; justify-content: center; gap: 10px;' +
    '    }' +
    '    .action-btn:active { transform: scale(0.98); opacity: 0.9; }' +
    '    .action-btn:disabled { background: #475569; color: #94A3B8; cursor: not-allowed; transform: none; box-shadow: none; }' +
    '    #status-box { margin-top: 24px; padding: 14px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; display: none; text-align: right; }' +
    '    .status-running { background: rgba(14, 165, 233, 0.15); border: 1px solid #0EA5E9; color: #7DD3FC; display: block !important; }' +
    '    .status-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #6EE7B7; display: block !important; }' +
    '    .status-error { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #FCA5A5; display: block !important; }' +
    '    .steps { margin-top: 26px; padding-top: 20px; border-top: 1px dashed rgba(148, 163, 184, 0.2); text-align: right; }' +
    '    .steps h3 { font-size: 13px; color: #64748B; margin-bottom: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }' +
    '    .step-item { font-size: 13px; color: #CBD5E1; margin-bottom: 10px; display: flex; align-items: flex-start; gap: 10px; line-height: 1.4; }' +
    '    .step-num { width: 20px; height: 20px; background: #334155; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; color: #38BDF8; font-weight: 700; flex-shrink: 0; margin-top: 1px; }' +
    '    .brand-footer { margin-top: 26px; padding-top: 18px; border-top: 1px dashed rgba(148, 163, 184, 0.2); text-align: center; }' +
    '    .brand-meta { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }' +
    '    .brand-icon { width: 22px; height: 22px; background: linear-gradient(135deg, #0EA5E9, #2563EB); border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }' +
    '    .brand-title { font-size: 13px; color: #94A3B8; }' +
    '    .brand-title strong { color: #38BDF8; font-weight: 600; }' +
    '    .brand-sub { font-size: 11.5px; color: #64748B; margin-bottom: 10px; }' +
    '    .brand-links { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 12px; }' +
    '    .brand-link { color: #38BDF8; text-decoration: none; transition: color 0.2s; font-weight: 500; }' +
    '    .brand-link:hover { color: #7DD3FC; text-decoration: underline; }' +
    '    .brand-sep { color: #475569; }' +
    '    .client-select { width: 100%; padding: 14px 16px; margin-bottom: 20px; border-radius: 12px; background: #334155; border: 1px solid #475569; color: #F8FAFC; font-size: 15px; outline: none; }' +
    '  </style>' +
    '</head>' +
    '<body>' +
    '  <div class="card">' +
    '    <div class="logo-container">' +
    '      <img src="' + APP_ICON_BASE64 + '" alt="D-Dialog Meeting AI" class="logo-img">' +
    '    </div>' +
    '    <h1>בוט סיכום פגישות AI <span style="font-size:11px;background:#0284C7;color:#FFFFFF;padding:3px 8px;border-radius:10px;vertical-align:middle;font-weight:600;margin-right:6px;">' + APP_VERSION + '</span></h1>' +
    '    <p class="desc">סנכרון הקלטות מ-Google Drive, תמלול חכם ב-Gemini והפקת סיכום מנהלים מובנה ישירות למייל.</p>' +
    '    ' +
    '    <select id="clientSelect" class="client-select">' +
    '      ' + optionsHtml +
    '    </select>' +
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
    '      <div class="step-item"><span class="step-num">2</span> <span>לוחצים על כפתור הסיכום למעלה.</span></div>' +
    '      <div class="step-item"><span class="step-num">3</span> <span>הסיכום המלא נוחת אצלך במייל וב-Drive תוך שניות!</span></div>' +
    '    </div>' +
    '    ' +
    '    <div class="brand-footer">' +
    '      <div class="brand-meta">' +
    '        <div class="brand-icon">⚡</div>' +
    '        <div class="brand-title">פותח על ידי <strong>' + BRAND_NAME + '</strong> <span style="color:#64748B;font-size:11px;">(' + APP_VERSION + ')</span></div>' +
    '      </div>' +
    '      <div class="brand-sub">' + BRAND_TAGLINE + '</div>' +
    '      <div class="brand-links">' +
    '        <a href="' + BRAND_WEBSITE + '" target="_blank" class="brand-link">אתר הבית</a>' +
    '        <span class="brand-sep">•</span>' +
    '        <a href="tel:' + BRAND_PHONE + '" class="brand-link">' + BRAND_PHONE + '</a>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '  <script>' +
    '    function startProcess() {' +
    '      var client = document.getElementById("clientSelect").value;' +
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
    '        .checkAndSummarizeMeetings(client);' +
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

function checkAndSummarizeMeetings(clientCategory) {
  Logger.log("מתחיל בדיקת הקלטות חדשות ב-Google Drive... " + (clientCategory ? "(" + clientCategory + ")" : ""));
  
  var inputFolder = getOrCreateFolder(FOLDER_INPUT_NAME);
  
  // Output and Archive folders based on category
  var baseOutputFolder = getOrCreateFolder(FOLDER_OUTPUT_NAME);
  var baseArchiveFolder = getOrCreateFolder(FOLDER_ARCHIVE_NAME);
  
  var outputFolder = baseOutputFolder;
  var archiveFolder = baseArchiveFolder;
  
  if (clientCategory && clientCategory.trim() !== "") {
    outputFolder = getOrCreateSubFolder(baseOutputFolder, clientCategory);
    archiveFolder = getOrCreateSubFolder(baseArchiveFolder, clientCategory);
  }
  
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
      // 1. Identify audio MIME type
      var audioMime = mimeType;
      if (lowerName.endsWith('.m4a') || lowerName.endsWith('.mp4')) {
        audioMime = "audio/mp4";
      } else if (lowerName.endsWith('.mp3')) {
        audioMime = "audio/mp3";
      } else if (lowerName.endsWith('.wav')) {
        audioMime = "audio/wav";
      }
      
      // 2. Call Gemini API (Handles both small and large audio files)
      var extractedDate = extractDateFromFileName(fileName);
      var dynamicPrompt = PROMPT_MEETING_SUMMARY + "\n\nהקשר נוסף שנמצא:\n- שם קובץ ההקלטה המקורי: " + fileName + "\n- תאריך ושעה שחולצו מקובץ ההקלטה: " + extractedDate + " (השתמש בתאריך זה בשדה התאריך אלא אם צוין תאריך אחר מפורשות בשיחה).";
      
      var summaryText = callGeminiWithAudio(file, audioMime, dynamicPrompt);
      if (!summaryText) {
        Logger.log("לא התקבל סיכום עבור " + fileName);
        continue;
      }
      
      var category = "גפ\"ן";
      if (clientCategory && clientCategory !== "auto" && clientCategory !== "D-Dialog") {
        category = clientCategory;
      } else {
        category = extractCategoryFromText(summaryText);
      }
      var targetFolder = getOrCreateSubFolder(baseOutputFolder, category);
      
      Logger.log("📊 סיווג פגישה: " + category + " | תיקיית יעד: " + baseOutputFolder.getName() + "/" + category);
      
      // 3. Extract metadata
      var meetingTitle = extractMeetingTitleFromSummary(summaryText, fileName);
      var recordingDate = extractDateFromFileName(fileName) || Utilities.formatDate(new Date(), "GMT+3", "dd/MM/yyyy");
      
      // 4. Build HTML Output with RTL
      var htmlContent = buildHtmlDocument(summaryText, fileName);
      
      // 5. Save individual files to Drive Output Folder (Inside Category Subfolder)
      var dateStr = Utilities.formatDate(new Date(), "GMT+3", "yyyy-MM-dd_HH-mm");
      var baseName = "סיכום_פגישה_" + dateStr + "_" + fileName.replace(/\.[^/.]+$/, "");
      
      targetFolder.createFile(baseName + ".html", htmlContent, MimeType.HTML);
      targetFolder.createFile(baseName + ".md", summaryText, MimeType.PLAIN_TEXT);
      
      // Create a native Google Doc for this individual meeting
      var docFile = convertMarkdownToGoogleDoc(summaryText, baseName, targetFolder);
      var docUrl = docFile.getUrl();
      
      // 6. Append to Master Google Doc in Drive
      var masterDocFile = appendToMasterGoogleDoc(summaryText, category, meetingTitle, recordingDate, targetFolder);
      var masterDocUrl = masterDocFile ? masterDocFile.getUrl() : "";
      var masterDocLabel = (category === "עסקים") ? "💼 פתח ריכוז פגישות עסקיות" : "📋 פתח ריכוז פגישות גפ\"ן";
      
      // 7. Move original recording to Archive folder
      file.moveTo(archiveFolder);
      
      // 8. Send Summary Email
      var recipient = NOTIFICATION_EMAIL || Session.getActiveUser().getEmail();
      var subject = "סיכום פגישה (" + category + "): " + fileName.replace(/\.[^/.]+$/, "");
      
      var emailActionsHtml = "<div style='margin-bottom: 24px; display: flex; gap: 12px; flex-wrap: wrap;'>" +
        "<a href='" + docUrl + "' style='background-color:#0EA5E9;color:white;padding:12px 20px;text-decoration:none;border-radius:10px;font-weight:bold;display:inline-block;'>📄 פתח סיכום פגישה ב-Google Docs</a>" +
        (masterDocUrl ? " <a href='" + masterDocUrl + "' style='background-color:#059669;color:white;padding:12px 20px;text-decoration:none;border-radius:10px;font-weight:bold;display:inline-block;'>" + masterDocLabel + "</a>" : "") +
        "</div>";
        
      var emailHtml = htmlContent.replace(
        "<div class='meta'>", 
        emailActionsHtml + "<div class='meta'>"
      );
      
      // Generate PDF, name it correctly, save to Drive and attach
      var pdfBlob = docFile.getAs(MimeType.PDF);
      pdfBlob.setName(baseName + ".pdf");
      targetFolder.createFile(pdfBlob);
      
      GmailApp.sendEmail(recipient, subject, summaryText, {
        htmlBody: emailHtml,
        name: "סיכום פגישות AI (" + BRAND_NAME + ")",
        attachments: [pdfBlob]
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
    "</style></head><body><div class='card' dir='rtl' style='direction: rtl; text-align: right;'>" +
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

function getOrCreateSubFolder(parentFolder, subFolderName) {
  var folders = parentFolder.getFoldersByName(subFolderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  return parentFolder.createFolder(subFolderName);
}

function convertMarkdownToGoogleDoc(markdown, title, folder) {
  var doc = DocumentApp.create(title);
  var body = doc.getBody();
  
  // Set RTL for the whole document
  var bodyStyle = {};
  bodyStyle[DocumentApp.Attribute.LEFT_TO_RIGHT] = false;
  body.setAttributes(bodyStyle);
  
  // Clear default empty paragraph
  body.clear();
  
  try {
    var base64Data = APP_ICON_BASE64.replace(/^data:image\/[a-z]+;base64,/, "");
    var imageBlob = Utilities.newBlob(Utilities.base64Decode(base64Data), MimeType.JPEG);
    var pLogo = body.appendParagraph("");
    pLogo.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
    var img = pLogo.appendInlineImage(imageBlob);
    img.setWidth(80).setHeight(80);
    body.appendParagraph("");
  } catch (e) {
    Logger.log("Logo Error: " + e.toString());
  }
  
  var lines = markdown.split('\n');
  
  for (var i = 0; i < lines.length; i++) {
    var line = lines[i].trim();
    if (line === '') continue;
    
    var p;
    if (line.indexOf('# ') === 0) {
      p = body.appendParagraph(line.substring(2));
      p.setHeading(DocumentApp.ParagraphHeading.HEADING1);
    } else if (line.indexOf('## ') === 0) {
      p = body.appendParagraph(line.substring(3));
      p.setHeading(DocumentApp.ParagraphHeading.HEADING2);
    } else if (line.indexOf('### ') === 0) {
      p = body.appendParagraph(line.substring(4));
      p.setHeading(DocumentApp.ParagraphHeading.HEADING3);
    } else if (line.indexOf('- [ ] ') === 0) {
      p = body.appendListItem("⬜ " + line.substring(6));
      p.setGlyphType(DocumentApp.GlyphType.BULLET);
    } else if (line.indexOf('- [x] ') === 0) {
      p = body.appendListItem("✅ " + line.substring(6));
      p.setGlyphType(DocumentApp.GlyphType.BULLET);
    } else if (line.indexOf('* ') === 0 || line.indexOf('- ') === 0) {
      p = body.appendListItem(line.substring(2));
      p.setGlyphType(DocumentApp.GlyphType.BULLET);
    } else if (line.match(/^[0-9]+\. /)) {
      var text = line.replace(/^[0-9]+\. /, '');
      p = body.appendListItem(text);
      p.setGlyphType(DocumentApp.GlyphType.NUMBER);
    } else if (line === '---') {
      body.appendHorizontalRule();
      continue;
    } else {
      p = body.appendParagraph(line);
    }
    
    // Set RTL for paragraph
    p.setLeftToRight(false);
    
    // Simple bold markdown parser (**text**)
    try {
      var textObj = p.editAsText();
      var textStr = textObj.getText();
      var regex = /\*\*(.*?)\*\*/g;
      var match;
      var matches = [];
      
      while ((match = regex.exec(textStr)) !== null) {
        matches.push({start: match.index, inner: match[1]});
      }
      
      for (var j = matches.length - 1; j >= 0; j--) {
        var m = matches[j];
        textObj.deleteText(m.start, m.start + 1); // Delete first **
        textObj.deleteText(m.start + m.inner.length, m.start + m.inner.length + 1); // Delete last **
        textObj.setBold(m.start, m.start + m.inner.length - 1, true);
      }
    } catch (e) {
      // Ignore if text processing fails
    }
  }
  
  doc.saveAndClose();
  
  // Move to folder
  var file = DriveApp.getFileById(doc.getId());
  file.moveTo(folder);
  
  return file;
}

function getOrCreateSubFolder(parentFolder, subFolderName) {
  var folders = parentFolder.getFoldersByName(subFolderName);
  if (folders.hasNext()) {
    return folders.next();
  }
  return parentFolder.createFolder(subFolderName);
}

function extractDateFromFileName(fileName) {
  var matchWa = fileName.match(/WhatsApp Audio (\d{4})-(\d{2})-(\d{2}) at (\d{2})\.(\d{2})/i);
  if (matchWa) {
    return matchWa[3] + "/" + matchWa[2] + "/" + matchWa[1] + " " + matchWa[4] + ":" + matchWa[5];
  }
  var matchPtt = fileName.match(/PTT-(\d{4})(\d{2})(\d{2})-WA/i);
  if (matchPtt) {
    return matchPtt[3] + "/" + matchPtt[2] + "/" + matchPtt[1];
  }
  var matchYmd = fileName.match(/(\d{4})[-_\.](\d{1,2})[-_\.](\d{1,2})/);
  if (matchYmd) {
    return ("0" + matchYmd[3]).slice(-2) + "/" + ("0" + matchYmd[2]).slice(-2) + "/" + matchYmd[1];
  }
  var matchDmy = fileName.match(/(\d{1,2})[-_\.](\d{1,2})[-_\.](\d{4})/);
  if (matchDmy) {
    return ("0" + matchDmy[1]).slice(-2) + "/" + ("0" + matchDmy[2]).slice(-2) + "/" + matchDmy[3];
  }
  var matchDmy2 = fileName.match(/(\d{1,2})[-_\.](\d{1,2})[-_\.](\d{2})\b/);
  if (matchDmy2) {
    return ("0" + matchDmy2[1]).slice(-2) + "/" + ("0" + matchDmy2[2]).slice(-2) + "/20" + matchDmy2[3];
  }
  var matchCompact = fileName.match(/\b(\d{2})(\d{2})(\d{2})\b/);
  if (matchCompact) {
    if (parseInt(matchCompact[1]) <= 31 && parseInt(matchCompact[2]) <= 12) {
      return matchCompact[1] + "/" + matchCompact[2] + "/20" + matchCompact[3];
    }
  }
  return Utilities.formatDate(new Date(), "GMT+3", "dd/MM/yyyy");
}

function extractCategoryFromText(summaryText) {
  var lines = summaryText.split("\n");
  for (var i = 0; i < lines.length; i++) {
    if (lines[i].indexOf("**קטגוריה:**") !== -1) {
      if (lines[i].indexOf("עסק") !== -1) {
        return "עסקים";
      } else if (lines[i].indexOf("גפ") !== -1 || lines[i].indexOf("חינוך") !== -1) {
        return "גפ\"ן";
      }
    }
  }
  var textLower = summaryText.toLowerCase();
  var businessScore = (textLower.match(/עסק|שחף|חשבונית|invoice|סוכן|פיתוח|לקוח|חברה|hubayta/g) || []).length;
  var gefenScore = (textLower.match(/גפ"ן|גפן|בית ספר|מורה|מורות|חינוך|תל"א|גוונים|רננים|אלומות|אורי/g) || []).length;
  return businessScore > gefenScore ? "עסקים" : "גפ\"ן";
}

function extractMeetingTitleFromSummary(summaryText, fallbackName) {
  var m = summaryText.match(/^# סיכום פגישה:\s*(.+)$/m);
  if (m && m[1]) {
    return m[1].replace(/[\[\]]/g, "").trim();
  }
  return fallbackName.replace(/\.[^/.]+$/, "");
}

function appendToMasterGoogleDoc(summaryText, category, meetingTitle, dateStr, folder) {
  try {
    var masterDocName = "📋 ריכוז סיכומי פגישות - " + category;
    if (category === "עסקים") {
      masterDocName = "💼 ריכוז סיכומי פגישות עסקיות";
    } else if (category === "גפ\"ן" || category === "גפן") {
      masterDocName = "📋 ריכוז סיכומי פגישות גפ\"ן";
    }
    
    // Find or create Master Google Doc in folder
    var files = folder.getFilesByName(masterDocName);
    var doc;
    var isNew = false;
    
    if (files.hasNext()) {
      var file = files.next();
      doc = DocumentApp.openById(file.getId());
    } else {
      isNew = true;
      doc = DocumentApp.create(masterDocName);
      var docFile = DriveApp.getFileById(doc.getId());
      docFile.moveTo(folder);
      
      var body = doc.getBody();
      var bodyStyle = {};
      bodyStyle[DocumentApp.Attribute.LEFT_TO_RIGHT] = false;
      body.setAttributes(bodyStyle);
      body.clear();
      
      // Add Cover Header
      try {
        var base64Data = APP_ICON_BASE64.replace(/^data:image\/[a-z]+;base64,/, "");
        var imageBlob = Utilities.newBlob(Utilities.base64Decode(base64Data), MimeType.JPEG);
        var pLogo = body.appendParagraph("");
        pLogo.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
        var img = pLogo.appendInlineImage(imageBlob);
        img.setWidth(70).setHeight(70);
      } catch (e) {}
      
      var pTitle = body.appendParagraph(masterDocName);
      pTitle.setHeading(DocumentApp.ParagraphHeading.HEADING1);
      pTitle.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
      pTitle.setLeftToRight(false);
      
      var pSub = body.appendParagraph("מסמך זה מאגד את כלל סיכומי פגישות העבודה, הפרוטוקולים וההחלטות עבור " + category + ".");
      pSub.setAlignment(DocumentApp.HorizontalAlignment.CENTER);
      pSub.setLeftToRight(false);
      
      body.appendHorizontalRule();
    }
    
    var body = doc.getBody();
    
    // Check if this meeting is already recorded in the document to prevent duplicates
    var fullText = body.getText();
    var checkTitle = meetingTitle || "";
    if (checkTitle && fullText.indexOf(checkTitle) !== -1 && dateStr && fullText.indexOf(dateStr) !== -1) {
      Logger.log("ℹ️ הפגישה כבר קיימת במסמך הריכוז: " + checkTitle);
      return DriveApp.getFileById(doc.getId());
    }
    
    // Add spacing before new entry if not brand new
    if (!isNew) {
      body.appendParagraph("");
      body.appendHorizontalRule();
      body.appendParagraph("");
    }
    
    // Append formatted markdown lines
    var lines = summaryText.split('\n');
    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line === '') continue;
      
      var p;
      if (line.indexOf('# ') === 0) {
        p = body.appendParagraph(line.substring(2));
        p.setHeading(DocumentApp.ParagraphHeading.HEADING1);
      } else if (line.indexOf('## ') === 0) {
        p = body.appendParagraph(line.substring(3));
        p.setHeading(DocumentApp.ParagraphHeading.HEADING2);
      } else if (line.indexOf('### ') === 0) {
        p = body.appendParagraph(line.substring(4));
        p.setHeading(DocumentApp.ParagraphHeading.HEADING3);
      } else if (line.indexOf('- [ ] ') === 0) {
        p = body.appendListItem("⬜ " + line.substring(6));
        p.setGlyphType(DocumentApp.GlyphType.BULLET);
      } else if (line.indexOf('- [x] ') === 0) {
        p = body.appendListItem("✅ " + line.substring(6));
        p.setGlyphType(DocumentApp.GlyphType.BULLET);
      } else if (line.indexOf('* ') === 0 || line.indexOf('- ') === 0) {
        p = body.appendListItem(line.substring(2));
        p.setGlyphType(DocumentApp.GlyphType.BULLET);
      } else if (line.match(/^[0-9]+\. /)) {
        var text = line.replace(/^[0-9]+\. /, '');
        p = body.appendListItem(text);
        p.setGlyphType(DocumentApp.GlyphType.NUMBER);
      } else if (line === '---') {
        body.appendHorizontalRule();
        continue;
      } else {
        p = body.appendParagraph(line);
      }
      
      p.setLeftToRight(false);
      
      // Bold parser
      try {
        var textObj = p.editAsText();
        var textStr = textObj.getText();
        var regex = /\*\*(.*?)\*\*/g;
        var match;
        var matches = [];
        while ((match = regex.exec(textStr)) !== null) {
          matches.push({start: match.index, inner: match[1]});
        }
        for (var j = matches.length - 1; j >= 0; j--) {
          var m = matches[j];
          textObj.deleteText(m.start, m.start + 1);
          textObj.deleteText(m.start + m.inner.length, m.start + m.inner.length + 1);
          textObj.setBold(m.start, m.start + m.inner.length - 1, true);
        }
      } catch (e) {}
    }
    
    doc.saveAndClose();
    Logger.log("✓ הפגישה נוספה בהצלחה למסמך הריכוז: " + masterDocName);
    return DriveApp.getFileById(doc.getId());
  } catch (err) {
    Logger.log("⚠️ שגיאה בהוספה למסמך ריכוז: " + err.toString());
    return null;
  }
}

/**
 * מפעיל את מודל Gemini עבור קובץ שמע.
 * תומך בקבצים קטנים וגדולים ללא שגיאת מגבלת Payload של URLFetch.
 */
function callGeminiWithAudio(file, audioMime, dynamicPrompt) {
  var fileSize = file.getSize();
  var blob = file.getBlob();
  var fileName = file.getName();
  
  // לקבצים קטנים מ-4MB - שימוש ב-Inline Base64 מהיר
  if (fileSize < 4 * 1024 * 1024) {
    Logger.log("⚡ קובץ קל (" + (fileSize / (1024*1024)).toFixed(2) + " MB) - מעבד ב-Inline Base64...");
    var audioBase64 = Utilities.base64Encode(blob.getBytes());
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
              "text": dynamicPrompt
            }
          ]
        }
      ]
    };
    
    var response = UrlFetchApp.fetch(url, {
      "method": "post",
      "contentType": "application/json",
      "payload": JSON.stringify(payload),
      "muteHttpExceptions": true
    });
    
    if (response.getResponseCode() !== 200) {
      throw new Error("שגיאה מ-Gemini API: " + response.getContentText());
    }
    
    var json = JSON.parse(response.getContentText());
    return json.candidates[0].content.parts[0].text;
  }
  
  // לקבצים גדולים (4MB ומעלה) - שימוש ב-Gemini Files API להעלאת קובץ בינארי מלא
  Logger.log("📁 קובץ גדול מזוהה (" + (fileSize / (1024*1024)).toFixed(2) + " MB) - מעלה ישירות ל-Gemini Files API...");
  
  var initUrl = "https://generativelanguage.googleapis.com/upload/v1beta/files?key=" + GEMINI_API_KEY;
  var initHeaders = {
    "X-Goog-Upload-Protocol": "resumable",
    "X-Goog-Upload-Command": "start",
    "X-Goog-Upload-Header-Content-Length": fileSize.toString(),
    "X-Goog-Upload-Header-Content-Type": audioMime,
    "Content-Type": "application/json"
  };
  
  var initResponse = UrlFetchApp.fetch(initUrl, {
    "method": "post",
    "headers": initHeaders,
    "payload": JSON.stringify({ "file": { "display_name": fileName } }),
    "muteHttpExceptions": true
  });
  
  var headers = initResponse.getAllHeaders();
  var uploadUrl = headers["X-Goog-Upload-URL"] || headers["x-goog-upload-url"] || headers["X-Goog-Upload-Url"];
  if (!uploadUrl) {
    throw new Error("לא ניתן היה לאתחל העלאה ל-Gemini Files API: " + initResponse.getContentText());
  }
  
  // העלאת הקובץ הבינארי ישירות לשרתי גוגל
  var uploadResponse = UrlFetchApp.fetch(uploadUrl, {
    "method": "post",
    "headers": {
      "Content-Length": fileSize.toString(),
      "X-Goog-Upload-Offset": "0",
      "X-Goog-Upload-Command": "upload, finalize"
    },
    "payload": blob.getBytes(),
    "muteHttpExceptions": true
  });
  
  if (uploadResponse.getResponseCode() !== 200) {
    throw new Error("שגיאה בהעלאת קובץ ל-Gemini Files API: " + uploadResponse.getContentText());
  }
  
  var fileInfo = JSON.parse(uploadResponse.getContentText());
  var fileUri = fileInfo.file.uri;
  Logger.log("✓ הקובץ הועלה ל-Gemini בהצלחה: " + fileUri);
  
  // הפקת הסיכום באמצעות ה-URI של הקובץ שהועלה
  var genUrl = "https://generativelanguage.googleapis.com/v1beta/models/" + GEMINI_MODEL + ":generateContent?key=" + GEMINI_API_KEY;
  var genPayload = {
    "contents": [
      {
        "parts": [
          {
            "file_data": {
              "mime_type": audioMime,
              "file_uri": fileUri
            }
          },
          {
            "text": dynamicPrompt
          }
        ]
      }
    ]
  };
  
  var genResponse = UrlFetchApp.fetch(genUrl, {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(genPayload),
    "muteHttpExceptions": true
  });
  
  if (genResponse.getResponseCode() !== 200) {
    throw new Error("שגיאה מ-Gemini בעת הפקת הסיכום: " + genResponse.getContentText());
  }
  
  var genJson = JSON.parse(genResponse.getContentText());
  return genJson.candidates[0].content.parts[0].text;
}
