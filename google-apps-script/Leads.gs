/**
 * Graphene lead form -> Google Sheet
 *
 * SETUP (bound script recommended)
 * 1. Create or open a Google Sheet. Add a tab named "Leads" (or let the script create it).
 * 2. Extensions > Apps Script. Paste this file. Save.
 * 3. Run setupLeadsSheet once from the editor (select function, Run). Authorize.
 * 4. Deploy > New deployment > Type: Web app
 *    - Execute as: Me
 *    - Who has access: Anyone
 * 5. Copy the Web app URL (ends in /exec) into index.html as GAS_WEB_APP_URL.
 *
 * POST fields: email, full_name, company, title, website (honeypot, must be empty).
 * New sheet header: Timestamp, Email, Name, Company, Title, Source.
 * If upgrading an old sheet, add Name column after Email and align headers with appendRow order.
 */

var SHEET_NAME = 'Leads';

/** If the web app ever sees no active spreadsheet, paste your Sheet ID from the URL here. */
var SPREADSHEET_ID = '';

function getSpreadsheet() {
  if (SPREADSHEET_ID) {
    return SpreadsheetApp.openById(SPREADSHEET_ID);
  }
  return SpreadsheetApp.getActiveSpreadsheet();
}

function setupLeadsSheet() {
  var ss = getSpreadsheet();
  if (!ss) {
    throw new Error('No spreadsheet: bind this project to a Sheet (Extensions > Apps Script from the Sheet), or set SPREADSHEET_ID in Leads.gs');
  }
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
  }
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Timestamp', 'Email', 'Name', 'Company', 'Title', 'Source']);
    sheet.getRange(1, 1, 1, 6).setFontWeight('bold');
  }
}

function doGet() {
  return ContentService.createTextOutput('Graphene leads endpoint OK').setMimeType(ContentService.MimeType.TEXT);
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(15000);
    var p = e.parameter || {};
    // Honeypot: bots often fill every field
    if (p.website) {
      return ContentService.createTextOutput('ok').setMimeType(ContentService.MimeType.TEXT);
    }
    var email = String(p.email || '').trim();
    var fullName = String(p.full_name || '').trim();
    var company = String(p.company || '').trim();
    var title = String(p.title || '').trim();
    if (!email) {
      return ContentService.createTextOutput('missing email').setMimeType(ContentService.MimeType.TEXT);
    }
    setupLeadsSheet();
    var sheet = getSpreadsheet().getSheetByName(SHEET_NAME);
    sheet.appendRow([new Date(), email, fullName, company, title, 'trygraphene.dev']);
    return ContentService.createTextOutput('ok').setMimeType(ContentService.MimeType.TEXT);
  } catch (err) {
    return ContentService.createTextOutput('error').setMimeType(ContentService.MimeType.TEXT);
  } finally {
    try {
      lock.releaseLock();
    } catch (ignore) {}
  }
}
