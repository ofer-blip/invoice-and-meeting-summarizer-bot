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

// אייקון האפליקציה (מומלץ להשתמש בקישור ישיר לתמונה כדי שיופיע תקין בנייד)
var APP_ICON_URL = "https://i.imgur.com/your-icon.png"; // <-- החלף לקישור האייקון שלך

// קוד גישה לאפליקציה למניעת שימוש לא מורשה
var ACCESS_PIN = "1234"; // <-- שנה לקוד ה-PIN שתרצה
