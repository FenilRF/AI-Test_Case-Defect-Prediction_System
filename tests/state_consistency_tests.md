# State Consistency Testing — Test Cases
> **Scope:** Verify that after deletion operations, the entire stack (UI, sessionStorage, database, cache) reflects a consistent, clean state with no ghost data.
> **Date Generated:** 2026-02-28
> **Project:** AI-TestCase-Defect-Prediction-System

---

## Module Legend

| ID Prefix | Module |
|---|---|
| `SC-DEL` | Deleting All Test Cases |
| `SC-DB`  | Verifying DB Deletion |
| `SC-CAC` | Verifying Cache Invalidation |
| `SC-SES` | Verifying Session Clearing |
| `SC-ARG` | Verifying No Auto-Regeneration |
| `SC-REF` | Verifying Refresh Loads Correct State |
| `SC-GHO` | Verifying No Ghost Records |
| `SC-STL` | Verifying No Stale Memory Restoration |

---

## 1 · Deleting All Test Cases (`SC-DEL`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-DEL-001 | "Clear Entire Test Case List" removes all entries from UI | ≥5 test cases visible on Test Cases page | 1. Navigate to Test Cases page 2. Click "Clear Entire Test Case List" 3. Confirm deletion in modal | Table shows "No test cases found" empty state; count reads 0 | Critical | 2 |
| SC-DEL-002 | Clear all with active type filter removes ALL, not just filtered | 10 test cases exist; type filter set to "positive" showing 4 | 1. Set filter to "positive" 2. Click "Clear Entire Test Case List" 3. Confirm 4. Remove filter | ALL test cases are removed — not just the 4 filtered ones; empty state shown | Critical | 3 |
| SC-DEL-003 | Clear all with active level filter removes ALL | Level filter set to "Unit" showing subset | 1. Set level filter to "Unit" 2. Click "Clear Entire Test Case List" 3. Confirm 4. Clear level filter | All test cases (all levels) are removed; empty state | Critical | 3 |
| SC-DEL-004 | Clear all with active search term removes ALL | Search term narrows list to 2 items | 1. Type search term matching 2 items 2. Click "Clear Entire Test Case List" 3. Confirm 4. Clear search | All test cases are gone — not just the 2 matched; empty state | Critical | 3 |
| SC-DEL-005 | Delete selected removes exactly the checked items | 10 test cases; 3 selected via checkbox | 1. Check 3 test case rows 2. Click "Remove Selected" 3. Confirm | Exactly 3 selected items removed; 7 remain; selected count resets to 0 | Critical | 3 |
| SC-DEL-006 | Delete single via row action button | ≥3 test cases visible | 1. Click trash icon on one specific row 2. Confirm deletion in modal | Only that single row is removed; all others remain unchanged | High | 2 |
| SC-DEL-007 | Cancel delete modal does NOT remove any data | ≥5 test cases visible | 1. Click "Clear Entire Test Case List" 2. In modal, click "Cancel" | No test cases are removed; counts unchanged; modal closes | High | 2 |
| SC-DEL-008 | Rapid double-click on delete does not cause double-deletion | ≥5 test cases visible | 1. Click "Clear Entire Test Case List" 2. Rapidly double-click "Confirm Delete" in modal | Deletion runs once; no console errors; no race condition or repeated API calls | High | 4 |
| SC-DEL-009 | Delete all when list is already empty | 0 test cases on the page | 1. Observe "Clear Entire Test Case List" button state | Button should be hidden or disabled when test case list is empty; no error if somehow triggered | Medium | 2 |
| SC-DEL-010 | Select all → Delete selected acts same as Clear All | 8 test cases; select-all checkbox checked | 1. Check "select all" header checkbox 2. Click "Remove Selected" 3. Confirm | All 8 removed; empty state shown; same result as Clear All | High | 3 |

---

## 2 · Verifying DB Deletion (`SC-DB`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-DB-001 | Clear all removes records from database | ≥5 test cases in DB and visible on UI | 1. Click "Clear Entire Test Case List" and confirm 2. Call `GET /api/test-cases` directly via curl/Postman | API returns empty array `[]`; HTTP 200 | Critical | 3 |
| SC-DB-002 | Delete single removes record from database | Test case with known ID exists | 1. Delete single test case via UI trash icon 2. Call `GET /api/test-cases` 3. Search response for deleted ID | Deleted ID is absent from API response | Critical | 3 |
| SC-DB-003 | Delete selected removes only selected from DB | 10 test cases; IDs [1–10]; delete IDs [3, 5, 7] | 1. Select test cases 3, 5, 7 2. Delete selected 3. Call `GET /api/test-cases` | Response contains IDs [1,2,4,6,8,9,10]; IDs [3,5,7] absent | Critical | 3 |
| SC-DB-004 | Associated requirement record is NOT deleted when test cases cleared | Requirement #1 has 5 test cases | 1. Clear all test cases for Req #1 2. Call `GET /api/requirements/1` | Requirement still exists; only test cases removed | Critical | 4 |
| SC-DB-005 | DB record count matches UI count post-deletion | 10 TCs initially; delete 4 | 1. Delete 4 test cases 2. Count remaining in UI 3. Call `GET /api/test-cases` and count | Both UI and API return exactly 6 records | High | 3 |
| SC-DB-006 | No orphaned foreign keys after deletion | Test cases reference requirement_id | 1. Delete all test cases 2. Query DB for any orphaned FK references or join tables | No orphaned records; all FK references are clean | High | 4 |
| SC-DB-007 | Delete is idempotent — re-deleting same ID returns graceful error | Test case ID 42 already deleted | 1. Call `DELETE /api/test-cases/42` via API | Returns 404 "Not found"; no server crash or 500 | Medium | 3 |
| SC-DB-008 | Concurrent delete requests for overlapping IDs | IDs [1,2,3] exist | 1. Send two simultaneous `delete-selected` requests: one for [1,2], one for [2,3] 2. Observe responses | Both succeed or one returns partial success; ID 2 is not double-deleted; DB consistent | High | 5 |

---

## 3 · Verifying Cache Invalidation (`SC-CAC`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-CAC-001 | Dashboard stats update after deletion | Dashboard shows "Test Cases: 10" | 1. Navigate to Test Cases page 2. Clear all 3. Navigate to Dashboard | Dashboard "Test Cases" stat shows 0; not stale 10 | Critical | 3 |
| SC-CAC-002 | Test Cases page fetches fresh data on each mount | 10 TCs visible; navigate away; externally delete 3 via API | 1. View Test Cases page (10 shown) 2. Navigate to Dashboard 3. Delete 3 TCs via curl 4. Navigate back to Test Cases | Page shows 7 (fresh fetch), not cached 10 | Critical | 4 |
| SC-CAC-003 | Browser HTTP cache does not serve stale API responses | Test cases cleared | 1. Clear all TCs 2. Immediately navigate to Test Cases page 3. Inspect Network tab — is `GET /api/test-cases` a fresh request? | Request is not served from disk cache; response is `[]` | High | 3 |
| SC-CAC-004 | Export CSV/JSON/Excel after deletion exports empty or no data | All test cases deleted | 1. Delete all test cases 2. Attempt CSV export | Either export is disabled (button greyed out) or export file contains headers only with no data rows | High | 3 |
| SC-CAC-005 | Requirement dropdown in Upload Design reflects deleted TCs | TCs for Req #1 deleted | 1. Delete all TCs for Req #1 2. Go to Upload Design page → select Req #1 3. Check if any old TC count metadata is shown | No stale TC count associated with Req #1; data reflects deletion | Medium | 3 |
| SC-CAC-006 | Level summary pills update after partial deletion | 10 TCs: 4 Unit, 3 Integration, 2 System, 1 UAT | 1. Delete all 4 Unit test cases 2. Check level pills | Unit pill shows 0; other pills unchanged; total now 6 | High | 3 |
| SC-CAC-007 | Browser back button after deletion does not show cached page | Viewed Test Cases (10 items) → deleted all → navigated to Dashboard | 1. Press browser Back button to return to Test Cases | Page re-renders with fresh data (empty list), NOT the cached view of 10 items | High | 4 |

---

## 4 · Verifying Session Clearing (`SC-SES`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-SES-001 | sessionStorage `upload_req_result` cleared after Clear All | Generated TCs on Upload Requirement page (result stored in session) | 1. Go to Test Cases → Clear All 2. Open DevTools → Application → sessionStorage 3. Check `upload_req_result` key | `upload_req_result` should either be null or cleared; navigating back to Upload Requirement shows no stale results | Critical | 3 |
| SC-SES-002 | sessionStorage `upload_design_result` cleared after Clear All | Generated TCs on Upload Design page (result stored in session) | 1. Clear all test cases 2. Check sessionStorage for `upload_design_result` | Key either cleared or its `test_cases` array is empty; no stale design results shown | Critical | 3 |
| SC-SES-003 | Manual sessionStorage.clear() via DevTools results in clean state | Active session with stored results | 1. Open DevTools Console 2. Run `sessionStorage.clear()` 3. Navigate to Upload Requirement page | Page shows empty form; no errors; no crashed components | High | 3 |
| SC-SES-004 | Corrupt sessionStorage JSON does not crash the app | sessionStorage contains invalid JSON for a key | 1. Run `sessionStorage.setItem('upload_req_result', '{invalid json}')` 2. Navigate to Upload Requirement page | App falls back to default state (null); no white screen or crash | Critical | 4 |
| SC-SES-005 | Session keys remain isolated per feature after deletion | Delete TCs from Upload Requirement; Upload Design has its own result | 1. Generate TCs on both Upload Requirement and Upload Design pages 2. Clear all TCs from the Test Cases page 3. Check both sessionStorage keys | Each key is independently managed; clearing test cases on one page does not corrupt the other's session data | High | 4 |
| SC-SES-006 | Deleting single TC does not clear entire session result | User generated 10 TCs; one deleted by row action | 1. Delete single TC via trash icon on Test Cases page 2. Navigate to Upload Requirement 3. Check if full result set is still in session | Session result reflects original generation (10 TCs); the Test Cases page list shows 9 (fresh API fetch) | Medium | 3 |
| SC-SES-007 | Tab close after deletion clears all session state | All TCs deleted; session keys reflect empty state | 1. Close the browser tab 2. Open new tab → navigate to app | sessionStorage is empty (tab-scoped); app shows clean login/empty state | High | 2 |

---

## 5 · Verifying No Auto-Regeneration (`SC-ARG`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-ARG-001 | Clearing all TCs does not trigger automatic regeneration | 10 test cases exist; requirement text is still in session | 1. Clear all TCs on Test Cases page 2. Wait 30 seconds 3. Inspect Network tab for any `POST /api/generate-*` calls | No auto-generation API calls are made; list remains empty | Critical | 2 |
| SC-ARG-002 | Navigating to Upload Requirement after deletion does not auto-generate | All TCs cleared; session still has `upload_req_text` | 1. Clear all TCs 2. Navigate to Upload Requirement 3. Observe: does the Generate button auto-trigger? 4. Monitor Network tab | Generate button is NOT auto-clicked; no spinner; no API call; user must explicitly click Generate | Critical | 3 |
| SC-ARG-003 | Page refresh after deletion does not auto-generate | All TCs cleared; requirement text in session | 1. Clear all TCs 2. Press F5 to refresh 3. Navigate to Upload Requirement | Form shows previous text (from session) but results area is empty; no auto-generation | Critical | 3 |
| SC-ARG-004 | useEffect does not trigger generation on mount | Upload Requirement page with text in session but no result | 1. Clear `upload_req_result` from sessionStorage 2. Navigate to Upload Requirement | Page renders with text in textarea; no API call fires; user must click Generate | High | 3 |
| SC-ARG-005 | Multiple rapid navigations to Upload Requirement do not accumulate API calls | Click sidebar rapidly 5 times | 1. Click Upload Requirement sidebar link 5 times rapidly 2. Monitor Network tab for generation calls | Zero `POST /api/generate-*` calls; only potential `GET` fetches (if any) | Medium | 3 |
| SC-ARG-006 | Timer-based or interval-based auto-generation does not exist | Freshly loaded app | 1. Open Network tab 2. Leave app idle for 5 minutes 3. Check for any `POST /api/generate-*` requests | No periodic generation calls; app is silent unless user triggers action | Medium | 2 |

---

## 6 · Verifying Refresh Loads Correct State (`SC-REF`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-REF-001 | F5 refresh after clearing all shows empty list | All TCs cleared; on Test Cases page | 1. Clear all test cases 2. Press F5 3. Wait for page load | "No test cases found" empty state renders; API returns `[]` | Critical | 2 |
| SC-REF-002 | F5 refresh after deleting selected shows remaining items | 10 TCs; deleted 3; 7 remaining | 1. Delete 3 selected TCs 2. Press F5 | Page reloads showing exactly 7 TCs; correct IDs; counts match | Critical | 3 |
| SC-REF-003 | Hard refresh (Ctrl+Shift+R) shows same correct state | 7 TCs remaining after deletion | 1. Press Ctrl+Shift+R 2. Wait for page load | Same 7 TCs as before; no cache-induced discrepancy | High | 2 |
| SC-REF-004 | Refresh on Upload Requirement shows session-persisted text but no stale results | Generated TCs; then cleared all from Test Cases page | 1. Generate TCs on Upload Requirement 2. Go to Test Cases → Clear All 3. Go back to Upload Requirement 4. Press F5 | Textarea has the persisted text (from sessionStorage); result table may show old generation result (session-stored) unless session was cleaned | High | 4 |
| SC-REF-005 | Refresh on Dashboard shows updated zero counts | All TCs cleared | 1. Clear all TCs 2. Navigate to Dashboard 3. Press F5 | Dashboard stats show 0 Test Cases; risk chart reflects no data | High | 3 |
| SC-REF-006 | Refresh during deletion (race condition) | User clicks "Clear All" → modal confirms → immediately presses F5 | 1. Click Clear All → Confirm 2. Immediately press F5 before UI update completes | After refresh, page shows consistent state — either all deleted (if API completed) or all present (if API didn't fire yet); no partial state | High | 5 |
| SC-REF-007 | Offline refresh after deletion | Network disconnected after successful deletion | 1. Delete all TCs (API succeeds) 2. Disconnect network 3. Press F5 | App shows error state or service worker cached page; does NOT restore deleted TCs from old cache | Medium | 4 |

---

## 7 · Verifying No Ghost Records (`SC-GHO`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-GHO-001 | Deleted TCs do not reappear on page re-visit | Cleared all TCs | 1. Navigate away to Dashboard 2. Navigate back to Test Cases | Empty state persists; no ghost records reappear | Critical | 2 |
| SC-GHO-002 | Deleted TCs do not appear in CSV export | All TCs deleted | 1. If CSV export button is enabled, click it 2. Open downloaded file | File is empty (headers only) or export is disabled | High | 3 |
| SC-GHO-003 | Deleted TCs do not appear in JSON export | All TCs deleted | 1. If JSON export button is enabled, click it 2. Inspect downloaded JSON | JSON contains empty array `[]` or export is disabled | High | 3 |
| SC-GHO-004 | Deleted TCs do not appear in Excel export | All TCs deleted | 1. If Excel export is enabled, click it 2. Open downloaded xlsx | Sheet is empty (headers only) or export disabled | High | 3 |
| SC-GHO-005 | Deleted TCs do not appear in Defect Prediction as stale input | 5 TCs existed; all deleted | 1. Navigate to Defect Prediction page 2. Check if any stale TC data is referenced | Defect prediction does not display or reference deleted test case data | High | 3 |
| SC-GHO-006 | Search/filter for a deleted TC returns no results | Deleted test case had scenario "Verify login with valid email" | 1. Navigate to Test Cases page 2. Search for "Verify login with valid email" | Search returns 0 results; no ghost match | Medium | 2 |
| SC-GHO-007 | Re-generating TCs after deletion creates entirely new records | All TCs deleted; requirement text still in session | 1. Go to Upload Requirement → click Generate 2. New TCs appear 3. Check their IDs on Test Cases page | New TCs have new unique IDs; no reuse of deleted IDs; no duplication | Critical | 4 |
| SC-GHO-008 | Browser autocomplete does not restore deleted TC data in forms | Deleted all TCs | 1. Click in search field on Test Cases page 2. Check browser autocomplete suggestions | Autocomplete may suggest old search terms (browser behavior) but no ghost TC data is restored into the app state | Low | 2 |
| SC-GHO-009 | Select-all checkbox after deletion reflects 0 items | All TCs deleted | 1. Observe "select all" checkbox state | Checkbox is hidden or non-functional when list is empty; `selectedIds` is empty Set | Medium | 2 |

---

## 8 · Verifying No Stale Memory Restoration (`SC-STL`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SC-STL-001 | React state does not restore deleted data on re-mount | Deleted all TCs; navigate away and back | 1. Clear all TCs on Test Cases page 2. Navigate to Dashboard 3. Navigate back to Test Cases | `useEffect` calls `fetchTestCases()` which returns `[]`; React state is `[]`; no stale restoration | Critical | 3 |
| SC-STL-002 | sessionStorage result not restored after DB-side deletion | TCs deleted via API directly (not UI); sessionStorage still has old result | 1. Delete TCs via `curl -X DELETE /api/test-cases/clear/1` 2. Navigate to Upload Requirement page | Session-stored result may show old TCs in the inline table; but Test Cases page (which fetches from API) shows 0 — document this inconsistency | High | 4 |
| SC-STL-003 | Component closure variables do not hold stale references | User deletes TCs; component async callbacks still pending | 1. Click Generate on Upload Requirement 2. While spinner is active, quickly navigate to Test Cases and Clear All 3. If generation completes, check that new results don't include phantom old data | New generation result is independent of deletion; old closures do not inject stale data | High | 5 |
| SC-STL-004 | Browser memory (heap) does not hold deleted TC objects | Large dataset: 100+ TCs generated then cleared | 1. Generate 100+ TCs 2. Clear all 3. Open DevTools → Memory → Take heap snapshot 4. Search for test case objects | Deleted TC objects are garbage collected; no memory leak of old data | Medium | 5 |
| SC-STL-005 | Re-mounting Upload Design does not restore stale design results | Cleared design analysis results | 1. Generate design analysis on Upload Design page 2. Clear `upload_design_result` from sessionStorage 3. Navigate away and back to Upload Design | Page shows clean upload form; no stale analysis results restored | High | 3 |
| SC-STL-006 | `window.history.state` does not hold deleted TC references | Deleted all TCs after navigating through app | 1. Clear all TCs 2. Inspect `window.history.state` in DevTools Console | History state does not contain test case data (React Router doesn't store it there) | Medium | 3 |
| SC-STL-007 | Deleting TCs and immediately re-generating does not merge old + new | 10 old TCs deleted; new generation yields 8 TCs | 1. Clear all TCs 2. Immediately generate new TCs 3. Count results | Exactly 8 new TCs shown; no contamination from deleted 10; IDs are all new | Critical | 4 |
| SC-STL-008 | Switching between Enterprise and Standard mode after deletion starts fresh | Generated Enterprise TCs (30+); deleted all | 1. Clear all TCs 2. On Upload Requirement, switch to Standard mode 3. Generate new TCs | New standard-mode TCs appear; no Enterprise-mode stale data mixed in; coverage report from Enterprise mode is gone | High | 4 |

---

## Coverage Summary

| Category | Test Cases | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| Deleting All Test Cases | 10 | 5 | 3 | 1 | 0 |
| Verifying DB Deletion | 8 | 4 | 3 | 1 | 0 |
| Verifying Cache Invalidation | 7 | 2 | 4 | 1 | 0 |
| Verifying Session Clearing | 7 | 3 | 3 | 1 | 0 |
| Verifying No Auto-Regeneration | 6 | 3 | 1 | 2 | 0 |
| Verifying Refresh Loads Correct State | 7 | 2 | 3 | 1 | 1 |
| Verifying No Ghost Records | 9 | 2 | 4 | 2 | 1 |
| Verifying No Stale Memory Restoration | 8 | 3 | 4 | 1 | 0 |
| **Total** | **62** | **24** | **25** | **10** | **2** |

---

## Risk Matrix

| Risk Area | Likelihood | Impact | Covering Test Cases |
|---|---|---|---|
| UI shows empty but DB still has records | Medium | Critical | SC-DB-001, SC-DB-002, SC-DB-003 |
| sessionStorage restores deleted results | High | High | SC-SES-001, SC-SES-002, SC-STL-002 |
| Stale Dashboard counts after deletion | High | Medium | SC-CAC-001, SC-REF-005 |
| Auto-regeneration after clear | Low | Critical | SC-ARG-001, SC-ARG-002, SC-ARG-003 |
| Ghost records in exports | Medium | High | SC-GHO-002, SC-GHO-003, SC-GHO-004 |
| Race condition: delete + refresh | Medium | High | SC-REF-006, SC-DEL-008 |
| Memory leak from un-GC'd TC objects | Low | Medium | SC-STL-004 |
| Old + new data merge on re-generate | Medium | Critical | SC-STL-007, SC-GHO-007 |
