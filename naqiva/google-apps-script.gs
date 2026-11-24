/**
 * Naqiva – كيسجل الناس اللي عمرو الفورمولير فـ Google Sheet.
 * الطريقة: شوف README.md (الخطوة 2).
 */
var HEADERS = ["date", "name", "phone", "city", "address", "qty", "total", "concern", "variant",
  "utm_source", "utm_medium", "utm_campaign", "utm_content", "quiz_score", "page"];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Leads")
      || SpreadsheetApp.getActiveSpreadsheet().insertSheet("Leads");
    if (sheet.getLastRow() === 0) sheet.appendRow(HEADERS);
    var p = (e && e.parameter) || {};
    sheet.appendRow(HEADERS.map(function (h) {
      var v = String(p[h] || "").slice(0, 300);
      // يمنع Google Sheets يقرا القيمة كـ formule
      return /^[=+\-@]/.test(v) ? "'" + v : v;
    }));
    return ContentService.createTextOutput("ok");
  } finally {
    lock.releaseLock();
  }
}
