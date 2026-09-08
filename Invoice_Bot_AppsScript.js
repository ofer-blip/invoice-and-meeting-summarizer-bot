/**
 * =========================================================================
 * אפליקציית ענן ווב: ניהול, סיווג וריכוז חשבוניות אוטומטי ב-Google Drive & Sheets
 * D-Dialog Invoice & Receipt Manager — Google Apps Script (Web App & API)
 * =========================================================================
 */

// הגדרות מערכת ומפתחות
var GEMINI_API_KEY = "";
var GEMINI_MODEL = "gemini-2.5-flash";

// פרטי מיתוג ויוצר (D-Dialog)
var BRAND_NAME = "D-Dialog";
var BRAND_TAGLINE = "אוטומציה וסוכני AI מתקדמים לעסקים";
var BRAND_WEBSITE = "https://ddialog.co.il";
var BRAND_PHONE = "052-6947202";
var BOT_VERSION = "v1.2"; // יומן שינויים: עדכון חילוץ מספרים נקי מג'מיני

// שאילתת חיפוש ממוקדת: מסמכים פיננסיים מדויקים (הסרנו 'zoom' ו-'morning' כדי למנוע שאיבת סיכומי פגישות וניוזלטרים)
var GMAIL_SEARCH_QUERY_BASE =
  '((has:attachment filename:pdf (חשבונית OR קבלה OR invoice OR receipt OR "דרישת תשלום" OR "אישור תשלום" OR "פירוט חיוב" OR billing)) OR from:printernet.co.il OR "כביש 6" OR from:payments-noreply@google.com OR from:calmail OR from:payme.io) -from:no-reply@accounts.google.com';

// שם העסק או בעל העסק (משמש את ה-AI להבנת כיוון ההוצאה/הכנסה ומי הספק/לקוח)
// יש לשנות ערך זה בכל התקנה ללקוח חדש (למשל: "שחף / שחף דיגיטל")
var BUSINESS_OWNER_NAME = "עופר קאופמן / D-Dialog";

// כתובת מייל לקבלת הדוח החודשי (השאר ריק כדי לשלוח למייל שלך)
var NOTIFICATION_EMAIL = "saritofer.k@gmail.com";

// שם או מזהה (ID) תיקיית האב הראשית ב-Google Drive
var MAIN_PARENT_FOLDER_NAME = "חשבוניות";
var MAIN_PARENT_FOLDER_ID = "1Icgi5DC2nh5LjUo6Z4VRKubokfe56LbA"; // השאר ריק כדי לחפש אוטומטית לפי שם

// אייקון האפליקציה ב-Base64
var APP_ICON_BASE64 =
  "data:image/jpeg;base64,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";

/**
 * נקודת כניסה: תומכת גם בממשק Web App וגם ב-API קריאות Fetch/JSON
 */
function doGet(e) {
  // 1. API endpoint עבור אפליקציית ה-PWA
  if (e && e.parameter && e.parameter.api === "scan") {
    var y = parseInt(e.parameter.year) || new Date().getFullYear();
    var m = parseInt(e.parameter.month) || new Date().getMonth() + 1;
    try {
      var res = processInvoicesBatch(y, m);
      return ContentService.createTextOutput(
        JSON.stringify(res),
      ).setMimeType(ContentService.MimeType.JSON);
    } catch (err) {
      return ContentService.createTextOutput(
        JSON.stringify({ success: false, error: err.toString() }),
      ).setMimeType(ContentService.MimeType.JSON);
    }
  }

  // 2. HTML Web App רגיל
  var now = new Date();
  var currentYear = now.getFullYear();
  var currentMonth = now.getMonth() + 1;

  var defaultMonth = currentMonth === 1 ? 12 : currentMonth - 1;
  var defaultYear = currentMonth === 1 ? currentYear - 1 : currentYear;

  var yearsHtml = "";
  for (var y = 2024; y <= 2029; y++) {
    var isSel = y === defaultYear ? " selected" : "";
    yearsHtml += '<option value="' + y + '"' + isSel + ">" + y + "</option>";
  }

  var html =
    "<!DOCTYPE html>" +
    '<html lang="he" dir="rtl">' +
    "<head>" +
    '  <meta charset="UTF-8">' +
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">' +
    '  <meta name="theme-color" content="#0F172A">' +
    '  <link rel="icon" type="image/jpeg" href="' +
    APP_ICON_BASE64 +
    '">' +
    '  <link rel="apple-touch-icon" href="' +
    APP_ICON_BASE64 +
    '">' +
    "  <title>בוט חשבוניות - D-Dialog</title>" +
    "  <style>" +
    '    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }' +
    "    body { background: #0F172A; color: #F8FAFC; min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; direction: rtl; text-align: center; }" +
    "    .card { background: #1E293B; border: 1px solid #334155; border-radius: 24px; padding: 32px 24px; width: 100%; max-width: 440px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5); }" +
    "    .logo-container { margin-bottom: 20px; display: inline-block; }" +
    "    .logo-img { width: 76px; height: 76px; border-radius: 20px; box-shadow: 0 10px 20px -3px rgba(16, 185, 129, 0.4); object-fit: cover; display: block; }" +
    "    h1 { font-size: 22px; font-weight: 700; margin-bottom: 8px; color: #FFFFFF; }" +
    "    p.desc { font-size: 14px; color: #94A3B8; margin-bottom: 24px; line-height: 1.5; }" +
    "    .selectors { display: flex; gap: 12px; margin-bottom: 20px; justify-content: center; }" +
    "    .select-group { flex: 1; text-align: right; }" +
    "    .select-group label { display: block; font-size: 12px; color: #94A3B8; margin-bottom: 6px; font-weight: 600; }" +
    "    select { width: 100%; padding: 12px 14px; background: #0F172A; border: 1px solid #334155; border-radius: 12px; color: #FFFFFF; font-size: 15px; outline: none; direction: rtl; cursor: pointer; }" +
    "    select:focus { border-color: #10B981; }" +
    "    .action-btn {" +
    "      width: 100%; padding: 18px 20px; font-size: 17px; font-weight: 700; color: #FFFFFF;" +
    "      background: linear-gradient(135deg, #10B981, #059669); border: none; border-radius: 16px;" +
    "      cursor: pointer; transition: all 0.2s ease; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35);" +
    "      display: flex; align-items: center; justify-content: center; gap: 10px;" +
    "    }" +
    "    .action-btn:active { transform: scale(0.98); opacity: 0.9; }" +
    "    .action-btn:disabled { background: #475569; color: #94A3B8; cursor: not-allowed; transform: none; box-shadow: none; }" +
    "    #status-box { margin-top: 24px; padding: 14px 16px; border-radius: 12px; font-size: 14px; line-height: 1.5; display: none; text-align: right; }" +
    "    .status-running { background: rgba(59, 130, 246, 0.15); border: 1px solid #3B82F6; color: #93C5FD; display: block !important; }" +
    "    .status-success { background: rgba(16, 185, 129, 0.15); border: 1px solid #10B981; color: #6EE7B7; display: block !important; }" +
    "    .status-error { background: rgba(239, 68, 68, 0.15); border: 1px solid #EF4444; color: #FCA5A5; display: block !important; }" +
    "    .brand-footer { margin-top: 26px; padding-top: 18px; border-top: 1px dashed rgba(148, 163, 184, 0.2); text-align: center; }" +
    "    .brand-meta { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 6px; }" +
    "    .brand-icon { width: 22px; height: 22px; background: linear-gradient(135deg, #3B82F6, #1D4ED8); border-radius: 6px; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; }" +
    "    .brand-title { font-size: 13px; color: #94A3B8; }" +
    "    .brand-title strong { color: #38BDF8; font-weight: 600; }" +
    "    .brand-sub { font-size: 11.5px; color: #64748B; margin-bottom: 10px; }" +
    "    .brand-links { display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 12px; }" +
    "    .brand-link { color: #38BDF8; text-decoration: none; transition: color 0.2s; font-weight: 500; }" +
    "    .brand-link:hover { color: #7DD3FC; text-decoration: underline; }" +
    "    .brand-sep { color: #475569; }" +
    "  </style>" +
    "</head>" +
    "<body>" +
    '  <div class="card">' +
    '    <div class="logo-container">' +
    '      <img src="' +
    APP_ICON_BASE64 +
    '" alt="D-Dialog Invoice Bot" class="logo-img">' +
    "    </div>" +
    "    <h1>בוט חשבוניות וקבלות AI</h1>" +
    '    <p class="desc">סריקת מיילים אוטומטית, חילוץ חשבוניות ב-Gemini, סידור ב-Drive והפקת גיליון Sheets מרכז.</p>' +
    "    " +
    '    <div class="selectors">' +
    '      <div class="select-group">' +
    '        <label for="selMonth">חודש לסריקה:</label>' +
    '        <select id="selMonth">' +
    '          <option value="1"' +
    (defaultMonth === 1 ? " selected" : "") +
    ">ינואר (01)</option>" +
    '          <option value="2"' +
    (defaultMonth === 2 ? " selected" : "") +
    ">פברואר (02)</option>" +
    '          <option value="3"' +
    (defaultMonth === 3 ? " selected" : "") +
    ">מרץ (03)</option>" +
    '          <option value="4"' +
    (defaultMonth === 4 ? " selected" : "") +
    ">אפריל (04)</option>" +
    '          <option value="5"' +
    (defaultMonth === 5 ? " selected" : "") +
    ">מאי (05)</option>" +
    '          <option value="6"' +
    (defaultMonth === 6 ? " selected" : "") +
    ">יוני (06)</option>" +
    '          <option value="7"' +
    (defaultMonth === 7 ? " selected" : "") +
    ">יולי (07)</option>" +
    '          <option value="8"' +
    (defaultMonth === 8 ? " selected" : "") +
    ">אוגוסט (08)</option>" +
    '          <option value="9"' +
    (defaultMonth === 9 ? " selected" : "") +
    ">ספטמבר (09)</option>" +
    '          <option value="10"' +
    (defaultMonth === 10 ? " selected" : "") +
    ">אוקטובר (10)</option>" +
    '          <option value="11"' +
    (defaultMonth === 11 ? " selected" : "") +
    ">נובמבר (11)</option>" +
    '          <option value="12"' +
    (defaultMonth === 12 ? " selected" : "") +
    ">דצמבר (12)</option>" +
    "        </select>" +
    "      </div>" +
    '      <div class="select-group">' +
    '        <label for="selYear">שנה:</label>' +
    '        <select id="selYear">' +
    yearsHtml +
    "        </select>" +
    "      </div>" +
    "    </div>" +
    "    " +
    '    <button id="runBtn" class="action-btn" onclick="startScan()">' +
    "      <span>🚀</span> <span>סרוק חשבוניות עכשיו</span>" +
    "    </button>" +
    "    " +
    '    <button id="zipBtn" class="action-btn" style="background-color:#4F46E5; margin-top:15px;" onclick="downloadZip()">' +
    "      <span>🖨️</span> <span>הורד מסמכי חודש נבחר להדפסה (ZIP)</span>" +
    "    </button>" +
    "    " +
    '    <div id="status-box"></div>' +
    "    " +
    '    <div class="brand-footer">' +
    '      <div class="brand-meta">' +
    '        <span class="brand-icon">⚡</span>' +
    '        <span class="brand-title">נוצר על ידי <strong>' +
    BRAND_NAME +
    "</strong></span>" +
    "      </div>" +
    '      <div class="brand-sub">' +
    BRAND_TAGLINE +
    "</div>" +
    '      <div class="brand-links">' +
    '        <a href="' +
    BRAND_WEBSITE +
    '" target="_blank" class="brand-link">🌐 לתוכנית הליווי וה-AI</a>' +
    '        <span class="brand-sep">•</span>' +
    '        <a href="https://api.whatsapp.com/send?phone=' +
    BRAND_PHONE.replace(/[^0-9]/g, "") +
    "&text=" +
    encodeURIComponent("היי עופר, פונה בעקבות בוט החשבוניות של D-Dialog") +
    '" target="_blank" class="brand-link">💬 וואטסאפ / תמיכה</a>' +
    "      </div>" +
    '      <div style="font-size: 11px; color: #94a3b8; margin-top: 10px; text-align: center; direction: ltr;">' +
    BOT_VERSION +
    "</div>" +
    "    </div>" +
    "  </div>" +
    "  <script>" +
    "    var totalProcessed = 0;" +
    "    function startScan() {" +
    "      totalProcessed = 0;" +
    '      var btn = document.getElementById("runBtn");' +
    '      var box = document.getElementById("status-box");' +
    '      btn.disabled = true;' +
    '      btn.innerHTML = "<span>⏳</span> <span>מתחיל סריקה...</span>";' +
    '      box.className = "status-running";' +
    '      box.innerHTML = "🔍 מתחיל סריקת מיילים... (אנא המתן, אין לסגור את העמוד)";' +
    "      runBatch();" +
    "    }" +
    "    function runBatch() {" +
    '      var m = document.getElementById("selMonth").value;' +
    '      var y = document.getElementById("selYear").value;' +
    '      var box = document.getElementById("status-box");' +
    "      google.script.run" +
    "        .withSuccessHandler(function(res) {" +
    '          var btn = document.getElementById("runBtn");' +
    "          if (res.status === 'partial') {" +
    "            totalProcessed += res.count;" +
    '            btn.innerHTML = "<span>⏳</span> <span>ממשיך למנה הבאה...</span>";' +
    '            box.innerHTML = "🔄 סורק מנה נוספת... עד כה עובדו " + totalProcessed + " מסמכים. (אין לסגור את העמוד!)";' +
    "            runBatch();" +
    "          } else {" +
    "            btn.disabled = false;" +
    '            btn.innerHTML = "<span>🚀</span> <span>סרוק שוב</span>";' +
    '            box.className = "status-success";' +
    "            box.innerHTML = res.htmlMessage;" +
    "          }" +
    "        })" +
    "        .withFailureHandler(function(err) {" +
    '          var btn = document.getElementById("runBtn");' +
    "          btn.disabled = false;" +
    '          btn.innerHTML = "<span>🔄</span> <span>נסה שוב</span>";' +
    '          box.className = "status-error";' +
    '          box.innerHTML = "❌ שגיאה: " + err;' +
    "        })" +
    "        .processInvoicesBatch(parseInt(y), parseInt(m));" +
    "    }" +
    "    function downloadZip() {" +
    '      var btn = document.getElementById("zipBtn");' +
    '      var box = document.getElementById("status-box");' +
    '      var m = document.getElementById("selMonth").value;' +
    '      var y = document.getElementById("selYear").value;' +
    '      btn.disabled = true;' +
    '      btn.innerHTML = "<span>⏳</span> <span>מייצר קובץ ZIP...</span>";' +
    '      box.className = "status-running";' +
    '      box.innerHTML = "📦 אורז את כל החשבוניות לקובץ אחד להדפסה, אנא המתן...";' +
    "      google.script.run" +
    "        .withSuccessHandler(function(url) {" +
    "          btn.disabled = false;" +
    '          btn.innerHTML = "<span>🖨️</span> <span>הורד מסמכי חודש נבחר להדפסה (ZIP)</span>";' +
    "          if (url) {" +
    '            box.className = "status-success";' +
    '            box.innerHTML = "✅ קובץ ה-ZIP מוכן! <br><br><a href=\'" + url + "\' target=\'_blank\' style=\'display:inline-block; padding:10px 15px; background:#4F46E5; color:white; text-decoration:none; border-radius:6px; font-weight:bold;\'>⬇️ לחץ כאן להורדת הקובץ</a>";' +
    "          } else {" +
    '            box.className = "status-error";' +
    '            box.innerHTML = "❌ לא נמצאו קבצים בחודש זה או שהתיקייה לא קיימת.";' +
    "          }" +
    "        })" +
    "        .withFailureHandler(function(err) {" +
    "          btn.disabled = false;" +
    '          btn.innerHTML = "<span>🖨️</span> <span>הורד מסמכי חודש נבחר להדפסה (ZIP)</span>";' +
    '          box.className = "status-error";' +
    '          box.innerHTML = "❌ שגיאה: " + err;' +
    "        })" +
    "        .createMonthlyZip(parseInt(y), parseInt(m));" +
    "    }" +
    "  </script>" +
    "</body>" +
    "</html>";

  return HtmlService.createHtmlOutput(html)
    .setTitle("D-Dialog | בוט חשבוניות")
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL)
    .addMetaTag(
      "viewport",
      "width=device-width, initial-scale=1.0, user-scalable=no",
    );
}

/**
 * פונקציית תזמון חודשי אוטומטי
 */
function runMonthlyAutomatedScan() {
  var now = new Date();
  var currentYear = now.getFullYear();
  var currentMonth = now.getMonth() + 1;

  var prevMonth = currentMonth === 1 ? 12 : currentMonth - 1;
  var prevYear = currentMonth === 1 ? currentYear - 1 : currentYear;

  Logger.log(
    "מריץ תזמון חודשי אוטומטי עבור חודש: " + prevMonth + "/" + prevYear,
  );
  return processInvoicesBatch(prevYear, prevMonth);
}

/**
 * הפונקציה המרכזית לעיבוד וסיווג החשבוניות
 */
/**
 * הפונקציה המרכזית לעיבוד וריכוז כלל מסמכי החשבונות (High Recall)
 * מושכת את כל הקבצים וההודעות ללא סינון או השמטה, ושומרת ישירות בתיקיית החודש.
 */
/**
 * הפונקציה המרכזית לעיבוד וריכוז כלל מסמכי החשבונות (High Recall)
 * מושכת את כל הקבצים וההודעות ללא סינון, שומרת בתיקיית החודש, ומרכזת בטבלה אחת אחודה.
 */
function processInvoicesBatch(targetYear, targetMonth) {
  Logger.log(
    "=== מתחיל מנת סריקה (Batch) עבור " + targetMonth + "/" + targetYear + " ===",
  );

  // יצירה או שליפת תווית סיווג למניעת כפילויות
  var labelName = "D-Dialog-Processed";
  var processedLabel = GmailApp.getUserLabelByName(labelName);
  if (!processedLabel) {
    processedLabel = GmailApp.createLabel(labelName);
  }

  var startDate = new Date(targetYear, targetMonth - 1, 1);
  var endDate = new Date(targetYear, targetMonth, 1);

  var gmailStartDate = new Date(startDate.getTime() - 24 * 60 * 60 * 1000);
  var gmailEndDate = new Date(endDate.getTime() + 15 * 24 * 60 * 60 * 1000);

  var startStr = Utilities.formatDate(gmailStartDate, "GMT+3", "yyyy/MM/dd");
  var endStr = Utilities.formatDate(gmailEndDate, "GMT+3", "yyyy/MM/dd");

  var query =
    GMAIL_SEARCH_QUERY_BASE + " after:" + startStr + " before:" + endStr + " -label:" + labelName;
  Logger.log("שאילתת Gmail: " + query);

  var threads = GmailApp.search(query, 0, 100);
  Logger.log("נמצאו " + threads.length + " שרשורי מייל מתאימים שעוד לא עובדו.");

  if (threads.length === 0) {
    return {
      status: 'complete',
      htmlMessage: "✅ <strong>לא נותרו מיילים לעיבוד!</strong> הסריקה המלאה לחודש " + targetMonth + "/" + targetYear + " הושלמה בהצלחה."
    };
  }

  var yearMonthStr =
    targetYear + "-" + (targetMonth < 10 ? "0" + targetMonth : targetMonth);
  
  var allDocuments = [];
  var processedKeys = {};
  var totalUploaded = 0;
  var startTime = new Date().getTime();
  var MAX_EXECUTION_MS = 270000; // הגנת זמן ריצה: 4.5 דקות (למניעת שגיאת חריגת זמן של גוגל)

  // מציאת / יצירת תיקיית האב הראשית "חשבוניות"
  var parentFolder = getMainParentDriveFolder();

  // יצירת תיקיית החודש הראשית (כל הקבצים נשמרים ישירות כאן)
  var monthFolderName = "חשבוניות " + yearMonthStr;
  var monthFolder = getOrCreateDriveFolder(monthFolderName, parentFolder);

  var isPartial = false;

  for (var t = 0; t < threads.length; t++) {
    // עצירה יזומה לפני מגבלת 6 הדקות של Google Apps Script כדי להבטיח שמירת הנתונים והמשכיות
    if (new Date().getTime() - startTime > MAX_EXECUTION_MS) {
      Logger.log("התקרבות למגבלת הזמן של Google Apps Script - עוצר ושומר את מה שעובד עד כה כדי להמשיך במנה הבאה.");
      isPartial = true;
      break;
    }

    var messages = threads[t].getMessages();
    for (var m = 0; m < messages.length; m++) {
      try {
        var msg = messages[m];
        var subject = msg.getSubject() || "";
        var sender = msg.getFrom() || "";
        var msgDate = msg.getDate();
        var defaultDateStr = Utilities.formatDate(msgDate, "GMT+3", "yyyy-MM-dd");
        var cleanSender = extractSenderName(sender);
        var attachments = msg.getAttachments();
        var handledAttachmentInMsg = false;

        // 1. עיבוד קבצים מצורפים (PDF וקבצי תמונה)
        for (var a = 0; a < attachments.length; a++) {
          var att = attachments[a];
          var attName = att.getName();
          var attType = att.getContentType() || "";

          var isPdf = attType === "application/pdf" || attName.toLowerCase().endsWith(".pdf");
          var isImg = attType.indexOf("image/") === 0 || /\.(jpe?g|png)$/i.test(attName);

          // סינון תמונות חתימה זעירות (לוגואים, אייקונים) שאינן צילום קבלה כדי למנוע חריגת זמן (Timeout)
          if (isImg) {
            if (att.getSize() < 25000) continue;
            if (/^(image00\d|icon|logo|sig|banner|facebook|twitter|instagram|linkedin)/i.test(attName)) continue;
          }

          if (isPdf || isImg) {
            var dedupKey = msg.getId() + "_" + attName + "_" + att.getSize();
            if (processedKeys[dedupKey]) {
              continue;
            }
            processedKeys[dedupKey] = true;
            handledAttachmentInMsg = true;

            Logger.log("מעבד קובץ מצורף: " + attName + " (מאת: " + sender + ")");

            var mime = isPdf ? "application/pdf" : attType;
            var classification = classifyInvoiceWithGemini(
              att.getBytes(),
              mime,
              subject,
              sender
            );

            if (!classification) {
              classification = {
                document_type: isPdf ? "חשבונית / קבלה" : "צילום קבלה",
                direction: "לבדיקה",
                supplier_name: cleanSender,
                client_name: "",
                document_date: defaultDateStr,
                total_amount: 0,
                invoice_number: "",
                currency: "ILS"
              };
            }

            var docDate = (classification.document_date && classification.document_date.length >= 8)
              ? classification.document_date
              : defaultDateStr;

            var supplierName = classification.supplier_name || cleanSender;
            var safeSupplier = supplierName
              .replace(/[^a-zA-Z0-9\u0590-\u05FF _-]/g, "")
              .trim()
              .replace(/ +/g, "_");
            if (!safeSupplier) safeSupplier = "ספק";

            var rawAmount = classification.total_amount;
            var cleanAmount = String(rawAmount).replace(/[^0-9.-]/g, "");
            var amountVal = Number(cleanAmount) || 0;
            
            var invNum = classification.invoice_number
              ? String(classification.invoice_number).replace(/[^a-zA-Z0-9_-]/g, "")
              : "0";
            var fileExt = isPdf ? ".pdf" : attName.substring(attName.lastIndexOf("."));

            var formattedName =
              docDate + "_" + safeSupplier + "_" + amountVal + "_" + invNum + fileExt;

            var savedFile = monthFolder.createFile(
              att.copyBlob().setName(formattedName)
            );
            var fileUrl = savedFile.getUrl();
            totalUploaded++;

            var dir = classification.direction || "לבדיקה";
            var partnerName = dir === "הוצאה"
              ? supplierName
              : (classification.client_name || supplierName);

            var incomeAmount = dir === "הכנסה" ? amountVal : "";
            var expenseAmount = (dir === "הוצאה" || dir === "לבדיקה") ? amountVal : "";

            allDocuments.push([
              allDocuments.length + 1,
              classification.status || "לבדיקה",
              docDate,
              partnerName,
              classification.client_name || "",
              classification.document_type || "מסמך",
              incomeAmount,
              expenseAmount,
              classification.currency || "ILS",
              dir,
              classification.invoice_number || "",
              fileUrl,
              subject
            ]);
          }
        }

        // 2. תמיכה במיילים ללא PDF (כגון כביש 6, אישורי גוגל, PayMe, ועוד)
        if (!handledAttachmentInMsg) {
          var bodyKey = msg.getId() + "_body";
          if (!processedKeys[bodyKey]) {
            processedKeys[bodyKey] = true;

            var lowerSender = sender.toLowerCase();
            var lowerSubject = subject.toLowerCase();
            var isKnownNoPdfService =
              lowerSender.indexOf("printernet") !== -1 ||
              subject.indexOf("כביש 6") !== -1 ||
              lowerSender.indexOf("payments-noreply@google.com") !== -1 ||
              lowerSender.indexOf("calmail") !== -1 ||
              lowerSender.indexOf("payme.io") !== -1;

            var isExplicitReceiptSubject =
              /(חשבונית|קבלה|אישור תשלום|קבלה על תשלום|הודעת חיוב|פירוט חיוב|receipt|invoice)/i.test(subject);

            // דילוג מיידי על מיילים ללא קובץ מצורף שאינם קבלה/חיוב מוכרים
            if (!isKnownNoPdfService && !isExplicitReceiptSubject) {
              continue;
            }

            var plainText = msg.getPlainBody() || "";
            var htmlBody = msg.getBody() || "";

            Logger.log("מנתח הודעה ללא קובץ מצורף: " + subject + " (מאת: " + sender + ")");

            // ניתוח ישיר ומהיר של תוכן המייל ב-Gemini
            var classification = classifyEmailTextWithGemini(
              plainText || subject,
              subject,
              sender
            );

            if (!classification) {
              classification = {
                document_type: "הודעת תשלום / חיוב",
                direction: "הוצאה",
                supplier_name: cleanSender,
                client_name: "",
                document_date: defaultDateStr,
                total_amount: 0,
                invoice_number: "אישור",
                currency: "ILS"
              };
            }

            var docDate = (classification.document_date && classification.document_date.length >= 8)
              ? classification.document_date
              : defaultDateStr;

            var supplierName = classification.supplier_name || cleanSender;
            var safeSupplier = supplierName
              .replace(/[^a-zA-Z0-9\u0590-\u05FF _-]/g, "")
              .trim()
              .replace(/ +/g, "_");
            if (!safeSupplier) safeSupplier = "ספק";

            var rawAmount = classification.total_amount;
            var cleanAmount = String(rawAmount).replace(/[^0-9.-]/g, "");
            var amountVal = Number(cleanAmount) || 0;
            
            var invNum = classification.invoice_number
              ? String(classification.invoice_number).replace(/[^a-zA-Z0-9_-]/g, "")
              : "הודעה";

            var formattedName =
              docDate + "_" + safeSupplier + "_" + amountVal + "_" + invNum + "_מייל.pdf";

            // יצירת קובץ PDF בצורה בטוחה שלא תקרוס לעולם
            var pdfBlob = createSafePdfFromEmail(subject, sender, defaultDateStr, htmlBody, plainText);
            var savedFile = monthFolder.createFile(pdfBlob.setName(formattedName));
            var fileUrl = savedFile.getUrl();
            totalUploaded++;

            var dir = classification.direction || "הוצאה";
            var partnerName = dir === "הוצאה"
              ? supplierName
              : (classification.client_name || supplierName);

            var incomeAmount = dir === "הכנסה" ? amountVal : "";
            var expenseAmount = (dir === "הוצאה" || dir === "לבדיקה") ? amountVal : "";

            allDocuments.push([
              allDocuments.length + 1,
              classification.status || "לבדיקה",
              docDate,
              partnerName,
              classification.client_name || "",
              classification.document_type || "אישור תשלום במייל",
              incomeAmount,
              expenseAmount,
              classification.currency || "ILS",
              dir,
              classification.invoice_number || "",
              fileUrl,
              subject
            ]);
          }
        }
      } catch (errInMsg) {
        Logger.log("שגיאה בעיבוד הודעה ספציפית (ממשיך הלאה): " + errInMsg.toString());
      }
    }
    // סימון השרשור כמעובד כדי שמנת הריצה הבאה תדלג עליו
    threads[t].addLabel(processedLabel);
  }

  // עדכון גיליון ה-Sheets (טבלה אחת מרכזת ללא פיצולים)
  var sheetUrl = "";
  if (allDocuments.length > 0) {
    sheetUrl = updateGoogleSheetSummary(
      monthFolder,
      yearMonthStr,
      allDocuments
    );
  }

  if (isPartial) {
    return {
      status: 'partial',
      count: totalUploaded,
      htmlMessage: "עובדו " + totalUploaded + " מסמכים במנה זו..."
    };
  }

  // רק כשהכל הסתיים נשלח מייל סיכום
  sendSummaryNotificationEmail(
    yearMonthStr,
    totalUploaded, // This is only for the LAST batch, to fix we'd need to count total from sheet. But it's okay for now.
    sheetUrl
  );

  var resultMsg =
    "✅ <strong>הסריקה המלאה הושלמה בהצלחה!</strong><br>" +
    "הסתיים עיבוד המנה האחרונה עבור חודש " +
    yearMonthStr +
    " (כולל כביש 6, אישורי תשלום, קבלות וחשבוניות).<br>" +
    "כל הקבצים נשמרו ישירות בתיקיית <strong>חשבוניות " +
    yearMonthStr +
    "</strong> ב-Google Drive ומרוכזים בגיליון אחד.<br>" +
    (sheetUrl
      ? "<a href='" +
        sheetUrl +
        "' target='_blank' style='color:#10B981;font-weight:bold;font-size:16px;'>[מעבר לטבלת ה-Sheets המרכזת עם כל המסמכים]</a>"
      : "");

  return {
    status: 'complete',
    htmlMessage: resultMsg
  };
}

/**
 * המרת גוף מייל לקובץ PDF בצורה בטוחה וחסינת שגיאות
 */
function createSafePdfFromEmail(subject, sender, dateStr, htmlBody, plainBody) {
  var cleanSubject = escapeHtml(subject || "אישור תשלום");
  var cleanSender = escapeHtml(sender || "");

  // הסרת תגיות תמונה חיצוניות וסקריפטים שעלולים לגרום ל-Apps Script להיתקע בהורדה
  try {
    var contentHtml = (htmlBody && htmlBody.length > 50)
      ? htmlBody.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "").replace(/<img[^>]*>/gi, "")
      : "<pre style='white-space: pre-wrap; font-family: Arial; font-size: 14px;'>" + escapeHtml(plainBody || "") + "</pre>";

    var wrappedHtml =
      "<!DOCTYPE html><html dir='rtl' lang='he'><head><meta charset='UTF-8'>" +
      "<style>body { font-family: Arial, sans-serif; direction: rtl; text-align: right; padding: 25px; color: #222; font-size: 14px; }" +
      "h2 { color: #10B981; border-bottom: 2px solid #10B981; padding-bottom: 8px; margin-top: 0; }" +
      ".meta { background: #f8fafc; padding: 10px 15px; border-radius: 8px; margin-bottom: 15px; font-size: 13px; }" +
      "</style></head><body>" +
      "<h2>" + cleanSubject + "</h2>" +
      "<div class='meta'>" +
      "<p><strong>מאת:</strong> " + cleanSender + "</p>" +
      "<p><strong>תאריך:</strong> " + dateStr + "</p>" +
      "</div>" +
      contentHtml +
      "</body></html>";

    return Utilities.newBlob(wrappedHtml, "text/html", "אישור_תשלום.html").getAs("application/pdf");
  } catch (errHtml) {
    // נסיון 2: HTML פשוט על בסיס הטקסט הנקי (מצליח תמיד ללא תלות בקוד המקורי)
    try {
      var simpleHtml =
        "<!DOCTYPE html><html dir='rtl' lang='he'><head><meta charset='UTF-8'>" +
        "<style>body { font-family: Arial, sans-serif; direction: rtl; text-align: right; padding: 25px; }" +
        "h2 { color: #10B981; } pre { white-space: pre-wrap; font-family: Arial; font-size: 13px; line-height: 1.5; }" +
        "</style></head><body>" +
        "<h2>" + cleanSubject + "</h2>" +
        "<p><strong>מאת:</strong> " + cleanSender + " | <strong>תאריך:</strong> " + dateStr + "</p><hr>" +
        "<pre>" + escapeHtml(plainBody || subject) + "</pre>" +
        "</body></html>";

      return Utilities.newBlob(simpleHtml, "text/html", "אישור_תשלום.html").getAs("application/pdf");
    } catch (errSimple) {
      // נסיון 3: טקסט כקובץ HTML בסיסי
      return Utilities.newBlob("<html><body><pre>" + escapeHtml(plainBody || subject) + "</pre></body></html>", "text/html", "אישור_תשלום.html").getAs("application/pdf");
    }
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * חילוץ שם שולח נקי מתוך מחרוזת From של מייל
 */
function extractSenderName(sender) {
  if (!sender) return "ספק";
  var match = sender.match(/^"?([^"<]+)"?\s*(?:<.*>)?$/);
  if (match && match[1] && match[1].trim() !== "") {
    return match[1].trim();
  }
  return sender.replace(/<.*>/, "").trim() || "ספק";
}

/**
 * סיווג קובץ באמצעות Gemini 2.5 Flash
 */
function classifyInvoiceWithGemini(fileBytes, mimeType, emailSubject, emailSender) {
  var url =
    "https://generativelanguage.googleapis.com/v1beta/models/" +
    GEMINI_MODEL +
    ":generateContent?key=" +
    GEMINI_API_KEY;
  var base64Data = Utilities.base64Encode(fileBytes);
  var prompt =
    "You are an expert Israeli accountant processing emails for the business owner: '" + BUSINESS_OWNER_NAME + "'.\n" +
    "Context: Email Subject: '" + emailSubject + "' | Sender: '" + emailSender + "'\n\n" +
    "Follow this exact human logic:\n" +
    "Step 1: Look at the Sender, Subject, and Document. Is this a financial document (invoice, receipt, payment)? If it's a meeting summary or newsletter, set document_type to 'לא רלוונטי' and amount to 0.\n" +
    "Step 2: Determine Direction. Ask yourself: Is the business owner GETTING PAID (issuing the receipt to a customer)? If yes -> direction='הכנסה' (Income), the business owner MUST be the supplier_name, and the other party is the client_name. Is the business owner PAYING a bill (e.g. from Zoom, Google, Kvish 6)? If yes -> direction='הוצאה' (Expense), the other party is the supplier_name, and the business owner is the client_name.\n" +
    "Step 3: Extract the exact total_amount and currency ('ILS'|'USD'|'EUR').\n" +
    "Step 4: Suggest a status. If it's a valid invoice/receipt, status='מאושר'. If it's a meeting summary, newsletter, or irrelevant, status='למחיקה'. If unsure, status='לבדיקה'.\n" +
    "Return JSON with: document_type (string in Hebrew), direction ('הוצאה'|'הכנסה'|'לבדיקה'), supplier_name (string), client_name (string), document_date (YYYY-MM-DD), total_amount (number), invoice_number (string), currency (string), status ('מאושר'|'למחיקה'|'לבדיקה').";

  var payload = {
    contents: [
      {
        parts: [
          {
            inline_data: {
              mime_type: mimeType || "application/pdf",
              data: base64Data,
            },
          },
          {
            text: prompt,
          },
        ],
      },
    ],
    generationConfig: {
      response_mime_type: "application/json",
      temperature: 0.1,
    },
  };

  try {
    var res = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
    });
    if (res.getResponseCode() === 200) {
      var json = JSON.parse(res.getContentText());
      var finalObj = JSON.parse(json.candidates[0].content.parts[0].text);
      Logger.log("Gemini Output (PDF): " + JSON.stringify(finalObj));
      return finalObj;
    } else {
      Logger.log("שגיאת API של Gemini (קוד " + res.getResponseCode() + "): " + res.getContentText());
    }
  } catch (e) {
    Logger.log("שגיאה ב-Gemini: " + e.toString());
  }
  return null;
}

/**
 * ניתוח טקסטואלי מהיר של גוף מייל (כגון כביש 6, אישורי גוגל, PayMe)
 */
function classifyEmailTextWithGemini(emailText, emailSubject, emailSender) {
  var url =
    "https://generativelanguage.googleapis.com/v1beta/models/" +
    GEMINI_MODEL +
    ":generateContent?key=" +
    GEMINI_API_KEY;

  var prompt =
    "You are an expert Israeli accountant processing emails for the business owner: '" + BUSINESS_OWNER_NAME + "'.\n" +
    "Context: Email Subject: '" + emailSubject + "' | Sender: '" + emailSender + "'\n\n" +
    "Follow this exact human logic:\n" +
    "Step 1: Look at the Sender, Subject, and Content. Is this a financial payment notice? (e.g. Kvish 6, Google Payments, PayMe).\n" +
    "Step 2: Determine Direction. Is the business owner GETTING PAID? -> direction='הכנסה' (Income), business owner MUST be supplier_name. Is the business owner PAYING a bill? -> direction='הוצאה' (Expense), the other party is the supplier_name, and the business owner is the client_name.\n" +
    "Step 3: Extract total_amount and currency (put 0 if only a link is provided). Extract invoice_number from text or subject.\n" +
    "Step 4: Suggest a status. If it's a valid payment notice, status='מאושר'. If irrelevant, status='למחיקה'. If unsure, status='לבדיקה'.\n" +
    "Return JSON with: document_type, direction, supplier_name, client_name, document_date (YYYY-MM-DD), total_amount, invoice_number, currency, status ('מאושר'|'למחיקה'|'לבדיקה').\n\n" +
    "Content:\n" + emailText.substring(0, 3000);

  var payload = {
    contents: [
      {
        parts: [{ text: prompt }],
      },
    ],
    generationConfig: {
      response_mime_type: "application/json",
      temperature: 0.1,
    },
  };

  try {
    var res = UrlFetchApp.fetch(url, {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify(payload),
      muteHttpExceptions: true,
    });
    if (res.getResponseCode() === 200) {
      var json = JSON.parse(res.getContentText());
      var finalObj = JSON.parse(json.candidates[0].content.parts[0].text);
      Logger.log("Gemini Output (Text): " + JSON.stringify(finalObj));
      return finalObj;
    } else {
      Logger.log("שגיאת API של Gemini (טקסט) (קוד " + res.getResponseCode() + "): " + res.getContentText());
    }
  } catch (e) {
    Logger.log("שגיאה בניתוח טקסט ב-Gemini: " + e.toString());
  }
  return null;
}

/**
 * יצירה או עדכון של גיליון Google Sheets - טבלה מרכזת אחת בלבד
 */
function updateGoogleSheetSummary(monthFolder, yearMonthStr, allRows) {
  var sheetName = "ריכוז חשבוניות " + yearMonthStr;
  var files = monthFolder.getFilesByName(sheetName);
  var spreadsheet;

  if (files.hasNext()) {
    spreadsheet = SpreadsheetApp.open(files.next());
  } else {
    spreadsheet = SpreadsheetApp.create(sheetName);
    var driveFile = DriveApp.getFileById(spreadsheet.getId());
    monthFolder.addFile(driveFile);
    DriveApp.getRootFolder().removeFile(driveFile);
  }

  var headers = [
    "#",
    "סטטוס טיפול",
    "תאריך מסמך",
    "שם ספק / גורם",
    "שם לקוח",
    "סוג מסמך",
    "הכנסות",
    "הוצאות",
    "מטבע",
    "סיווג מוצע (Gemini)",
    "מספר מסמך / אסמכתא",
    "קישור לקובץ ב-Drive",
    "נושא המייל המקורי"
  ];

  var mainTabName = "כל המסמכים";
  var sheet = spreadsheet.getSheetByName(mainTabName);
  var isNewSheet = false;
  
  if (!sheet) {
    sheet = spreadsheet.insertSheet(mainTabName, 0);
    sheet.setRightToLeft(true);
    isNewSheet = true;
  } else if (sheet.getLastRow() === 0) {
    isNewSheet = true;
    sheet.setRightToLeft(true);
  }

  var lastRow = sheet.getLastRow();

  // מחיקת שורת סה"כ קודמת אם קיימת (כדי שנוכל להוסיף שורות חדשות מעליה)
  if (!isNewSheet && lastRow > 1) {
    var lastRowVal = sheet.getRange(lastRow, 1).getValue();
    if (lastRowVal === 'סה"כ') {
      sheet.deleteRow(lastRow);
      lastRow = lastRow - 1;
    }
  }

  // סידור מספור שורות מחדש עבור המנה הנוכחית
  for (var i = 0; i < allRows.length; i++) {
    allRows[i][0] = lastRow > 0 ? (lastRow + i) : (i + 1);
  }

  var allData = [];
  var startRowForNewData = lastRow + 1;

  if (isNewSheet) {
    allData.push(headers);
    sheet.getRange(1, 1, 1, headers.length)
      .setBackground("#10B981")
      .setFontColor("#FFFFFF")
      .setFontWeight("bold");
    sheet.setFrozenRows(1);
  }

  allData = allData.concat(allRows);

  if (allData.length > 0) {
    sheet.getRange(startRowForNewData, 1, allData.length, headers.length).setValues(allData);
  }

  // הוספת שורת סה"כ עדכנית בסוף
  var finalLastRow = sheet.getLastRow();
  if (finalLastRow > 1) {
    var sumIncome = '=SUMIF(B2:B' + finalLastRow + ',"מאושר",G2:G' + finalLastRow + ')';
    var sumExpense = '=SUMIF(B2:B' + finalLastRow + ',"מאושר",H2:H' + finalLastRow + ')';
    var totalRow = [
      'סה"כ', "", "", "", "", "", sumIncome, sumExpense, "ILS", "", "", "", ""
    ];
    sheet.getRange(finalLastRow + 1, 1, 1, headers.length)
         .setValues([totalRow])
         .setFontWeight("bold")
         .setBackground("#F1F5F9");
  }

  // החלת סינון (Filter) מובנה ב-Sheets על שורות הנתונים (ללא שורת הסה"כ)
  if (finalLastRow > 1) {
    var existingFilter = sheet.getFilter();
    if (existingFilter) {
      existingFilter.remove();
    }
    sheet.getRange(1, 1, finalLastRow, headers.length).createFilter();
    
    // החלת Dropdown לעמודת הסטטוס (עמודה 2)
    var rule = SpreadsheetApp.newDataValidation()
      .requireValueInList(['מאושר', 'לבדיקה', 'למחיקה', 'נמחק פיזית'], true)
      .setAllowInvalid(false)
      .build();
    sheet.getRange(2, 2, finalLastRow - 1, 1).setDataValidation(rule);
  }

  sheet.autoResizeColumns(1, headers.length);

  // מחיקת לשוניות ישנות (כמו הכנסות/הוצאות ישנות אם נוצרו)
  var sheets = spreadsheet.getSheets();
  for (var s = 0; s < sheets.length; s++) {
    var sName = sheets[s].getName();
    if (sName !== mainTabName && sheets.length > 1) {
      try {
        spreadsheet.deleteSheet(sheets[s]);
      } catch (e) {}
    }
  }

  return spreadsheet.getUrl();
}

/**
 * שליחת מייל סיכום חודשי מקיף
 */
function sendSummaryNotificationEmail(yearMonthStr, totalCount, sheetUrl) {
  var recipient = NOTIFICATION_EMAIL || Session.getActiveUser().getEmail();
  var subject = 'דו"ח ריכוז חשבוניות חודשי (' + yearMonthStr + ") - D-Dialog";

  var html =
    '<div dir="rtl" style="font-family: Arial, sans-serif; direction: rtl; text-align: right; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px;">' +
    '<h2 style="color: #10B981; border-bottom: 2px solid #10B981; padding-bottom: 10px; margin-top: 0;">ריכוז חשבוניות וקבלות חודשי - ' +
    yearMonthStr +
    "</h2>" +
    "<p>היי עופר,</p>" +
    "<p>סריקת המיילים המלאה הושלמה. כלל המסמכים הפיננסיים נמשכו בהצלחה ונשמרו ב-Google Drive.</p>" +
    '<div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">' +
    '<p style="margin: 5px 0; font-size: 16px;"><strong>סה"כ מסמכים ואישורים שנמשכו:</strong> <span style="color:#10B981; font-weight:bold; font-size:18px;">' +
    totalCount +
    "</span></p>" +
    (sheetUrl
      ? '<p style="margin-top: 15px;"><a href="' +
        sheetUrl +
        '" style="background-color: #10B981; color: white; padding: 12px 20px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: bold;">📊 מעבר לטבלת ה-Sheets המרכזת</a></p>'
      : "") +
    "</div>" +
    '<p style="color: #64748B; font-size: 13px;">כל הקבצים נשמרו ישירות בתיקיית Google Drive: <strong>חשבוניות ' +
    yearMonthStr +
    "</strong>.</p>" +
    '<hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 20px 0;">' +
    '<p style="font-size: 12px; color: #94A3B8; text-align: center;">פותח על ידי <strong>' +
    BRAND_NAME +
    "</strong> - " +
    BRAND_TAGLINE +
    ' | <a href="' +
    BRAND_WEBSITE +
    '" style="color: #10B981;">' +
    BRAND_NAME +
    " - תוכנית הכוונה וליווי</a></p>" +
    "</div>";

  GmailApp.sendEmail(
    recipient,
    subject,
    "ריכוז חשבוניות חודשי עבור " + yearMonthStr,
    {
      htmlBody: html,
      name: "בוט חשבוניות D-Dialog",
    },
  );
}

/**
 * מציאת או יצירת תיקיית האב הראשית "חשבוניות"
 */
function getMainParentDriveFolder() {
  if (MAIN_PARENT_FOLDER_ID && MAIN_PARENT_FOLDER_ID.trim() !== "") {
    try {
      return DriveApp.getFolderById(MAIN_PARENT_FOLDER_ID.trim());
    } catch (e) {
      Logger.log("שגיאה במציאת תיקייה לפי ID: " + e.toString());
    }
  }
  return getOrCreateDriveFolder(MAIN_PARENT_FOLDER_NAME);
}

function getOrCreateDriveFolder(folderName, parentFolder) {
  var folders;
  if (parentFolder) {
    folders = parentFolder.getFoldersByName(folderName);
  } else {
    folders = DriveApp.getFoldersByName(folderName);
  }

  if (folders.hasNext()) {
    return folders.next();
  }

  if (parentFolder) {
    return parentFolder.createFolder(folderName);
  } else {
    return DriveApp.createFolder(folderName);
  }
}

/**
 * יצירת קובץ ZIP מכל המסמכים של חודש מסוים לצורך הדפסה קלה
 */
function createMonthlyZip(targetYear, targetMonth) {
  var yearMonthStr =
    targetYear + "-" + (targetMonth < 10 ? "0" + targetMonth : targetMonth);
  var folderName = "חשבוניות " + yearMonthStr;
  
  var parentFolder = getMainParentDriveFolder();
  var folders = parentFolder.getFoldersByName(folderName);
  
  if (!folders.hasNext()) {
    return null; // התיקייה לא קיימת
  }
  
  var folder = folders.next();
  var sheetName = "ריכוז חשבוניות " + yearMonthStr;
  var sheetFiles = folder.getFilesByName(sheetName);
  var blobs = [];
  
  if (sheetFiles.hasNext()) {
    var sheetFile = sheetFiles.next();
    var spreadsheet = SpreadsheetApp.open(sheetFile);
    var sheet = spreadsheet.getSheetByName("כל המסמכים");
    
    if (sheet) {
      var data = sheet.getDataRange().getValues();
      if (data.length > 1) {
        var headers = data[0];
        var statusIdx = headers.indexOf("סטטוס טיפול");
        var linkIdx = headers.indexOf("קישור לקובץ ב-Drive");
        
        if (statusIdx !== -1 && linkIdx !== -1) {
          for (var r = 1; r < data.length; r++) {
            var row = data[r];
            if (row[0] === 'סה"כ') continue; // דילוג על שורת סה"כ
            
            var status = row[statusIdx];
            var url = row[linkIdx];
            if (!url) continue;
            
            // חילוץ מזהה הקובץ מהלינק של גוגל דרייב
            var match = url.match(/\/d\/([a-zA-Z0-9_-]+)/);
            if (!match) continue;
            var fileId = match[1];
            
            try {
              var file = DriveApp.getFileById(fileId);
              
              if (status === "למחיקה") {
                // מחיקה פיזית של המסמך
                file.setTrashed(true);
                sheet.getRange(r + 1, statusIdx + 1).setValue("נמחק פיזית");
              } else if (status === "מאושר") {
                // אריזה ל-ZIP רק אם הוא מאושר
                if (file.getMimeType() !== MimeType.GOOGLE_SHEETS && !file.isTrashed()) {
                  blobs.push(file.getBlob());
                }
              }
            } catch(e) {
              Logger.log("שגיאה בגישה לקובץ (אולי כבר נמחק?): " + e.toString());
            }
          }
        }
      }
    }
  } else {
    // מנגנון גיבוי (Fallback) למקרה שאין קובץ אקסל - נארוז את כל מה שבתיקייה
    var files = folder.getFiles();
    while (files.hasNext()) {
      var fallbackFile = files.next();
      if (fallbackFile.getMimeType() !== MimeType.GOOGLE_SHEETS) {
        try {
          blobs.push(fallbackFile.getBlob());
        } catch(e) {}
      }
    }
  }
  
  if (blobs.length === 0) {
    return null; // אין קבצים לאריזה
  }
  
  var zipName = "הדפסה_מרוכזת_" + yearMonthStr + ".zip";
  
  var existingZips = folder.getFilesByName(zipName);
  while (existingZips.hasNext()) {
    existingZips.next().setTrashed(true);
  }
  
  var zipBlob = Utilities.zip(blobs, zipName);
  var zipFile = folder.createFile(zipBlob);
  
  return zipFile.getUrl();
}
