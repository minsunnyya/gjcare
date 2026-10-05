/**
 * 경기광주 재가복지센터 상담 신청 → 구글 시트 저장
 * 구글 시트 > 확장 프로그램 > Apps Script 에 붙여넣고 "웹 앱"으로 배포하세요.
 * (실행: 나 / 액세스: 모든 사용자)
 *
 * 새 신청이 들어오면 메일로도 알려 주려면 NOTIFY_EMAIL에 주소를 넣으세요.
 */
var NOTIFY_EMAIL = "";

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(["접수 시각", "성함", "연락처", "관계", "지역", "등급", "통화 시간", "궁금한 점", "접수 페이지"]);
  }
  var p = e.parameter || {};
  var row = [new Date(), p.name, p.phone, p.rel, p.area, p.grade, p.time, p.msg, p.page];
  sheet.appendRow(row);

  if (NOTIFY_EMAIL) {
    MailApp.sendEmail(
      NOTIFY_EMAIL,
      "[상담 신청] " + (p.name || "") + " · " + (p.phone || ""),
      "관계: " + p.rel + "\n지역: " + p.area + "\n등급: " + p.grade + "\n통화 시간: " + p.time + "\n\n" + (p.msg || "")
    );
  }
  return ContentService.createTextOutput("ok");
}
