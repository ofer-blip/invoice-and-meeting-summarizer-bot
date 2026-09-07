/**
 * =========================================================================
 * קובץ הגדרות לקוח - D-Dialog Meeting Summarizer
 * קובץ זה מכיל אך ורק את הגדרות הלקוח הספציפיות.
 * אין צורך לשנות קובץ זה כאשר מעדכנים את מנוע המערכת (Engine.gs).
 * =========================================================================
 */

// 1. מפתח Gemini API של הלקוח
var GEMINI_API_KEY = "AQ.Ab8RN6IL8JL8EC1V4LyOTMwZakgkenawg4RFmX7-0A5YMA0Gyg";

// 2. כתובת מייל לקבלת הסיכומים (השאר ריק "" כדי לשלוח אוטומטית למייל בעל החשבון)
var NOTIFICATION_EMAIL = "";

// 3. שמות תיקיות הבסיס ב-Google Drive
var FOLDER_INPUT_NAME = "הקלטות לפגישות";
var FOLDER_OUTPUT_NAME = "סיכומי פגישות";
var FOLDER_ARCHIVE_NAME = "הקלטות שעובדו";

// 4. תיקיות ראשוניות ברירת מחדל (יווצרו בדרייב בהפעלה ראשונה)
// כל תיקייה נוספת שהלקוח ייצור ב-Drive תופיע אוטומטית בתפריט האפליקציה!
var DEFAULT_CATEGORIES = ["עסקים", "גפ\"ן"];

// 5. מיתוג ופרטי התקשרות
var BRAND_NAME = "D-Dialog";
var BRAND_TAGLINE = "אוטומציה וסוכני AI מתקדמים לעסקים";
var BRAND_WEBSITE = "https://ddialog.co.il";
var BRAND_PHONE = "052-6947202";
