/**
 * =========================================================================
 * מנוע סיכום פגישות AI - D-Dialog (Engine.gs)
 * קובץ זה מכיל את מנוע המערכת והלוגיקה בלבד.
 * קובץ זה משותף וזהה ב-100% לכל הלקוחות (אינו מכיל מפתחות פרטיים).
 * כל הגדרות הלקוח והמפתחות מוגדרים אך ורק בקובץ Config.gs.
 * =========================================================================
 */

// בדיקת משתני קונפיגורציה מקובץ Config.gs
if (typeof GEMINI_API_KEY === 'undefined') {
  var GEMINI_API_KEY = ""; // יוגדר בקובץ Config.gs
}
if (typeof GEMINI_MODEL === 'undefined') {
  var GEMINI_MODEL = "gemini-2.5-flash";
}
if (typeof FOLDER_INPUT_NAME === 'undefined') {
  var FOLDER_INPUT_NAME = "הקלטות לפגישות";
}
if (typeof FOLDER_OUTPUT_NAME === 'undefined') {
  var FOLDER_OUTPUT_NAME = "סיכומי פגישות";
}
if (typeof FOLDER_ARCHIVE_NAME === 'undefined') {
  var FOLDER_ARCHIVE_NAME = "הקלטות שעובדו";
}
if (typeof NOTIFICATION_EMAIL === 'undefined') {
  var NOTIFICATION_EMAIL = "";
}
if (typeof BRAND_NAME === 'undefined') {
  var BRAND_NAME = "D-Dialog";
}
if (typeof BRAND_TAGLINE === 'undefined') {
  var BRAND_TAGLINE = "אוטומציה וסוכני AI מתקדמים לעסקים";
}
if (typeof BRAND_WEBSITE === 'undefined') {
  var BRAND_WEBSITE = "https://ddialog.co.il";
}
if (typeof BRAND_PHONE === 'undefined') {
  var BRAND_PHONE = "052-6947202";
}
if (typeof DEFAULT_CATEGORIES === 'undefined') {
  var DEFAULT_CATEGORIES = ["עסקים", "גפ\"ן"];
}

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


// פרטי גרסה
var APP_VERSION = "v2.4";

// כתובות אייקון רשמיות וציבוריות (להתקנת PWA, אייקון למסך בית באנדרואיד ו-Favicon במעטפת גוגל)
var APP_ICON_URL = "https://raw.githubusercontent.com/ofer-blip/invoice-and-meeting-summarizer-bot/main/pwa_meeting/icon-192.png";
var APP_ICON_512_URL = "https://raw.githubusercontent.com/ofer-blip/invoice-and-meeting-summarizer-bot/main/pwa_meeting/icon-512.png";

// אייקון האפליקציה ב-PNG Base64 (לאייקון מסך בית בנייד ו-Favicon)
var APP_ICON_PNG_B64 = "data:image/png;base64,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";

// אייקון האפליקציה ב-Base64 (לשיבוץ במסמכי Google Doc)
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
  // פונקציית אימות קוד אבטחה (PIN)
  // ---------------------------------------------------------
  function isPinAuthorized(req) {
    if (typeof ACCESS_PIN === 'undefined' || !ACCESS_PIN || ACCESS_PIN.toString().trim() === '') {
      return true; // ללא קוד סודי = פתוח
    }
    var providedPin = (req && req.parameter && req.parameter.pin) ? req.parameter.pin.toString().trim() : '';
    return providedPin === ACCESS_PIN.toString().trim();
  }

  // ---------------------------------------------------------
  // API Endpoint לסנכרון מקומי (משיכת קבצי MD)
  // ---------------------------------------------------------
  if (e && e.parameter && e.parameter.action === 'sync') {
    if (!isPinAuthorized(e)) {
      return ContentService.createTextOutput(JSON.stringify({ error: 'קוד אבטחה (PIN) שגוי או חסר' })).setMimeType(ContentService.MimeType.JSON);
    }
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
  // API Endpoint עבור אפליקציית ה-PWA ברשת (הפעלת סיכום פגישות)
  // ---------------------------------------------------------
  if (e && e.parameter && (e.parameter.api === 'summarize' || e.parameter.action === 'summarize')) {
    if (!isPinAuthorized(e)) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: "קוד אבטחה (PIN) שגוי או חסר. הגישה נדחתה."
      })).setMimeType(ContentService.MimeType.JSON);
    }
    var cat = e.parameter.category || "";
    if (cat === "auto") cat = "";
    try {
      var summaryResult = checkAndSummarizeMeetings(cat);
      var responsePayload = {
        success: true,
        message: summaryResult
      };
      return ContentService.createTextOutput(JSON.stringify(responsePayload))
        .setMimeType(ContentService.MimeType.JSON);
    } catch (err) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: err.toString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }

  // ---------------------------------------------------------
  // API Endpoint עבור קבלת רשימת קטגוריות זמינות מ-Drive
  // ---------------------------------------------------------
  if (e && e.parameter && e.parameter.api === 'categories') {
    if (!isPinAuthorized(e)) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: "קוד אבטחה (PIN) שגוי או חסר."
      })).setMimeType(ContentService.MimeType.JSON);
    }
    try {
      var cats = getAvailableCategoriesFromDrive();
      return ContentService.createTextOutput(JSON.stringify({
        success: true,
        categories: cats
      })).setMimeType(ContentService.MimeType.JSON);
    } catch (err) {
      return ContentService.createTextOutput(JSON.stringify({
        success: false,
        error: err.toString()
      })).setMimeType(ContentService.MimeType.JSON);
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
  var logoSvg = '<svg class="logo-svg" viewBox="0 0 100 100" width="80" height="80" xmlns="http://www.w3.org/2000/svg">' +
    '  <defs>' +
    '    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">' +
    '      <stop offset="0%" stop-color="#0284C7" />' +
    '      <stop offset="50%" stop-color="#0EA5E9" />' +
    '      <stop offset="100%" stop-color="#2563EB" />' +
    '    </linearGradient>' +
    '    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">' +
    '      <feGaussianBlur stdDeviation="2" result="blur" />' +
    '      <feComposite in="SourceGraphic" in2="blur" operator="over" />' +
    '    </filter>' +
    '  </defs>' +
    '  <rect x="3" y="3" width="94" height="94" rx="22" fill="url(#bgGrad)" stroke="#38BDF8" stroke-width="2" />' +
    '  <path d="M 18 42 Q 14 50 18 58" stroke="#BAE6FD" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.8" />' +
    '  <path d="M 25 36 Q 20 50 25 64" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" fill="none" opacity="0.9" />' +
    '  <path d="M 82 42 Q 86 50 82 58" stroke="#BAE6FD" stroke-width="3" stroke-linecap="round" fill="none" opacity="0.8" />' +
    '  <path d="M 75 36 Q 80 50 75 64" stroke="#FFFFFF" stroke-width="3.5" stroke-linecap="round" fill="none" opacity="0.9" />' +
    '  <rect x="41" y="24" width="18" height="32" rx="9" fill="#FFFFFF" filter="url(#glow)" />' +
    '  <path d="M 33 46 C 33 60 67 60 67 46" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" fill="none" />' +
    '  <line x1="50" y1="60" x2="50" y2="72" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" />' +
    '  <line x1="38" y1="72" x2="62" y2="72" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round" />' +
    '  <path d="M 68 18 L 70 23 L 75 25 L 70 27 L 68 32 L 66 27 L 61 25 L 66 23 Z" fill="#FDE047" />' +
    '</svg>';

  var manifestObj = {
    name: "סיכום פגישות - " + BRAND_NAME,
    short_name: "סיכום פגישות",
    start_url: ".",
    display: "standalone",
    background_color: "#0F172A",
    theme_color: "#0F172A",
    icons: [
      {
        src: APP_ICON_URL,
        sizes: "192x192",
        type: "image/png",
        purpose: "any maskable"
      },
      {
        src: APP_ICON_512_URL,
        sizes: "512x512",
        type: "image/png",
        purpose: "any maskable"
      }
    ]
  };
  var manifestDataUri = "data:application/manifest+json;charset=utf-8," + encodeURIComponent(JSON.stringify(manifestObj));

  var html = '<!DOCTYPE html>' +
    '<html lang="he" dir="rtl">' +
    '<head>' +
    '  <meta charset="UTF-8">' +
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">' +
    '  <meta name="theme-color" content="#0F172A">' +
    '  <meta name="apple-mobile-web-app-capable" content="yes">' +
    '  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">' +
    '  <meta name="apple-mobile-web-app-title" content="סיכום פגישות">' +
    '  <meta name="mobile-web-app-capable" content="yes">' +
    '  <meta name="application-name" content="סיכום פגישות">' +
    '  <link rel="manifest" href="' + manifestDataUri + '">' +
    '  <link rel="icon" type="image/png" sizes="192x192" href="' + APP_ICON_URL + '">' +
    '  <link rel="shortcut icon" href="' + APP_ICON_URL + '">' +
    '  <link rel="apple-touch-icon" href="' + APP_ICON_URL + '">' +
    '  <link rel="apple-touch-icon" sizes="192x192" href="' + APP_ICON_URL + '">' +
    '  <link rel="apple-touch-icon-precomposed" href="' + APP_ICON_URL + '">' +
    '  <meta property="og:image" content="' + APP_ICON_URL + '">' +
    '  <title>סיכום פגישות - ' + BRAND_NAME + '</title>' +
    '  <style>' +
    '    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }' +
    '    body { background: #0F172A; color: #F8FAFC; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; direction: rtl; text-align: center; }' +
    '    .card { background: #1E293B; border: 1px solid #334155; border-radius: 24px; padding: 32px 24px; width: 100%; max-width: 440px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }' +
    '    .logo-container { margin-bottom: 18px; display: inline-block; }' +
    '    .logo-svg { width: 80px; height: 80px; border-radius: 22px; box-shadow: 0 10px 25px -3px rgba(14, 165, 233, 0.5); display: block; margin: 0 auto; }' +
    '    h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #FFFFFF; }' +
    '    p.desc { font-size: 14px; color: #94A3B8; margin-bottom: 24px; line-height: 1.5; }' +
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
    '      ' + logoSvg +
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
    '      <div class="step-item"><span class="step-num">1</span> <span>מעלים הקלטה מהטלפון לתיקיית <strong>"' + FOLDER_INPUT_NAME + '"</strong> ב-Drive.</span></div>' +
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

  var output = HtmlService.createHtmlOutput(html)
    .setTitle("סיכום פגישות - " + BRAND_NAME)
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, user-scalable=no');
    
  try {
    output.setFaviconUrl(APP_ICON_URL);
  } catch (err) {
    Logger.log("Favicon notice: " + err.toString());
  }
    
  return output;
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
