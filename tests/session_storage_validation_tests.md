# Session Storage Validation — Test Cases
> **Assumption:** Session storage remains active until a full page refresh.
> **Date Generated:** 2026-02-28
> **Project:** AI-TestCase-Defect-Prediction-System

---

## Module Legend

| ID Prefix | Module |
|---|---|
| `SS-NAV` | Data Retained During Navigation |
| `SS-WRK` | Data Retained After Partial Workflow |
| `SS-EXP` | Token / Session Expiration Behavior |
| `SS-REF` | Manual Refresh Behavior |
| `SS-BCR` | Browser Close / Reopen Cases |
| `SS-TAB` | Multi-Tab Behavior |
| `SS-HIJ` | Session Hijacking Risks |
| `SS-CON` | Concurrent Login Session Handling |

---

## 1 · Data Retained During Navigation (`SS-NAV`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-NAV-001 | Session data persists on SPA route change | User is logged in; session token stored in sessionStorage | 1. Navigate from Dashboard → Test Generator page via sidebar 2. Open DevTools → Application → Session Storage 3. Verify token and user profile keys | All sessionStorage keys/values remain intact after client-side route change | Critical | 2 |
| SS-NAV-002 | Form input preserved across forward navigation | User begins filling the test-case generation form | 1. Enter requirement text and select defect category 2. Navigate to Predictions page using nav link 3. Return to Generator page via back navigation | Previously entered form data is still present if bound to sessionStorage | High | 3 |
| SS-NAV-003 | Session data survives browser Back button | Session contains auth token + cached API response | 1. Visit Dashboard 2. Navigate to Results page 3. Press browser Back button 4. Inspect sessionStorage | Session data unchanged; no keys deleted or overwritten | Critical | 2 |
| SS-NAV-004 | Session data survives browser Forward button | User pressed Back in the previous step | 1. From Dashboard, press browser Forward button to Results page 2. Inspect sessionStorage | All session keys/values remain intact | High | 2 |
| SS-NAV-005 | Deep-link navigation retains session | User is authenticated with active session | 1. Copy URL of Results page 2. Paste into same tab's address bar and press Enter 3. Inspect sessionStorage | Session remains; user is not logged out | High | 3 |
| SS-NAV-006 | Hash-based navigation preserves session | Session is active; app uses hash-based routing | 1. Change URL hash manually (e.g., `#/settings`) 2. Inspect sessionStorage | No sessionStorage key loss due to hash change | Medium | 2 |
| SS-NAV-007 | Rapid sequential navigation does not corrupt session | Active session with multiple stored keys | 1. Rapidly click through 5+ navigation links within 3 seconds 2. Inspect sessionStorage after settling | All keys remain intact; no race-condition data loss or duplication | High | 4 |
| SS-NAV-008 | Session preserved when navigating to 404 / error page | Active session | 1. Navigate to a non-existent route (e.g., `/nonexistent`) 2. App renders 404/error component 3. Inspect sessionStorage | Session data untouched; error handling does not clear storage | Medium | 3 |

---

## 2 · Data Retained After Partial Workflow (`SS-WRK`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-WRK-001 | Partial form submission retains draft in session | User opens test-case generator form | 1. Fill in 3 of 6 required fields 2. Click another nav link (do NOT submit) 3. Return to generator page 4. Inspect sessionStorage | Draft data persists in sessionStorage; form can resume | High | 3 |
| SS-WRK-002 | Abandoned multi-step wizard retains completed steps | Multi-step workflow (e.g., configure → generate → review) | 1. Complete Step 1 (configure) 2. Begin Step 2 (generate) but do not complete 3. Navigate away 4. Return to wizard | Step 1 data retained; Step 2 shows last-entered state | High | 4 |
| SS-WRK-003 | File upload reference retained after navigation | User selects a file but does not submit | 1. Select a CSV dataset file in upload control 2. Navigate to another page 3. Return to upload page 4. Inspect sessionStorage | File metadata (name, size) in sessionStorage is preserved; file re-selection may be needed but reference is intact | Medium | 4 |
| SS-WRK-004 | In-progress API call – session state on interruption | Auto-save / partial result stored mid-workflow | 1. Trigger test-case generation 2. While loading spinner is active, navigate away 3. Return to page 4. Inspect sessionStorage | Partial results or "in-progress" flag persists; UI shows recovery option | High | 5 |
| SS-WRK-005 | Filter/sort selections retained on return | User applies filters on results list | 1. Apply category filter + sort-by-priority on Results page 2. Navigate to Dashboard 3. Return to Results page | If filters are stored in sessionStorage, they are re-applied automatically | Medium | 3 |
| SS-WRK-006 | Pagination state retained after navigation | User is on page 3 of a paginated result list | 1. Navigate to page 3 2. Click away to another section 3. Return to results | Page 3 is shown if pagination index is sessionStorage-backed | Medium | 3 |
| SS-WRK-007 | Session data retained after a client-side error | Active workflow with session data | 1. Trigger a handled JS error (e.g., invalid JSON parse) 2. Error boundary catches and renders fallback 3. Inspect sessionStorage | No sessionStorage keys are cleared by the error boundary | High | 4 |

---

## 3 · Token / Session Expiration Behavior (`SS-EXP`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-EXP-001 | Expired JWT token triggers re-authentication prompt | JWT in sessionStorage with short TTL (e.g., 15 min) | 1. Log in and note token expiry time 2. Wait until token expires (or mock system clock) 3. Perform any API action | App detects 401 response; displays login/re-auth prompt; does NOT silently fail | Critical | 4 |
| SS-EXP-002 | Refresh token rotation updates sessionStorage | App uses access + refresh token pattern | 1. Wait for access token to expire 2. App auto-calls refresh endpoint 3. Inspect sessionStorage | Old access token replaced with new token; refresh token rotated (if applicable) | Critical | 5 |
| SS-EXP-003 | Expired session prevents API calls silently | Token expired; no refresh mechanism configured | 1. Let token expire 2. Click "Generate Test Cases" 3. Monitor network tab | API call is either blocked before sending (client guard) or returns 401; no data mutation occurs | Critical | 4 |
| SS-EXP-004 | Grace-period warning before expiration | Session nearing expiry (e.g., < 2 min remaining) | 1. Log in 2. Remain idle until grace-period threshold 3. Observe UI | Toast/modal warns user: "Session expiring soon — extend?" with an extend option | High | 4 |
| SS-EXP-005 | Extending session resets expiry timer | Grace-period warning shown | 1. Click "Extend Session" in warning dialog 2. Inspect sessionStorage 3. Verify new expiry timestamp | Token TTL is refreshed; warning disappears; API calls succeed | High | 4 |
| SS-EXP-006 | Idle timeout clears session automatically | App enforces 30-min idle timeout | 1. Log in 2. Leave browser idle for > 30 min (or mock) 3. Move mouse / click | SessionStorage is cleared; user redirected to login | High | 4 |
| SS-EXP-007 | Clock-skew tolerance for token validation | Server and client clocks differ by ~5 min | 1. Set client clock 5 min behind server 2. Log in; receive token 3. Perform API action near expiry boundary | Token validation accounts for skew; no premature 401 errors | Medium | 5 |
| SS-EXP-008 | Backend session invalidation reflected on frontend | Admin revokes user's session from server-side | 1. User is logged in with valid token 2. Admin invalidates session via backend 3. User performs next API call | Frontend receives 401/403; sessionStorage cleared; user redirected to login | Critical | 4 |

---

## 4 · Manual Refresh Behavior (`SS-REF`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-REF-001 | Full page refresh clears sessionStorage (by design) | Active session with data | 1. Press F5 or Ctrl+R 2. Inspect sessionStorage after page reloads | **If design = clear on refresh:** all session keys are gone; user must re-auth. **If design = persist:** keys survive; verify assumption | Critical | 2 |
| SS-REF-002 | Hard refresh (Ctrl+Shift+R) clears sessionStorage | Active session | 1. Press Ctrl+Shift+R 2. Inspect sessionStorage | Same behavior as SS-REF-001; cache-busting does not alter sessionStorage behavior differently than regular refresh | High | 2 |
| SS-REF-003 | Refresh during active API call | API request in flight (loading spinner visible) | 1. Click "Generate" to start long-running request 2. Immediately press F5 3. After reload, inspect sessionStorage and UI | Session data handled gracefully; no orphaned "loading" flags; UI is in clean state | High | 4 |
| SS-REF-004 | Refresh on error page | App displays an error/500 page | 1. Trigger a server error page 2. Press F5 | App reloads cleanly; session state is consistent with refresh policy | Medium | 3 |
| SS-REF-005 | Refresh with unsaved form data | User has filled form but not submitted | 1. Fill in test-case fields 2. Press F5 3. Observe form state | If sessionStorage-backed draft: data restored. If not: data lost (verify user is warned via `beforeunload`) | High | 3 |
| SS-REF-006 | Repeated rapid refreshes (stress) | Active session | 1. Press F5 rapidly 10 times within 5 seconds 2. After final load, inspect sessionStorage and app state | No corrupted keys, no duplicate entries, app is stable | Medium | 3 |
| SS-REF-007 | Refresh while offline (network disconnected) | Active session; network disabled | 1. Disconnect network 2. Press F5 3. Reconnect network 4. Inspect sessionStorage | If app has service worker/offline support: session keys may persist. Otherwise: app shows offline error; session data per refresh policy | Medium | 4 |

---

## 5 · Browser Close / Reopen Cases (`SS-BCR`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-BCR-001 | Closing browser tab clears sessionStorage | Active session on single tab | 1. Close the tab (not the browser) by clicking × 2. Open a new tab and navigate to the app URL 3. Inspect sessionStorage | sessionStorage is empty (spec: scoped to tab lifetime); user must re-authenticate | Critical | 2 |
| SS-BCR-002 | Closing entire browser clears sessionStorage | Active session; single window | 1. Close all browser windows 2. Reopen browser (not via session restore) 3. Navigate to app URL 4. Inspect sessionStorage | sessionStorage is empty; user is on login page | Critical | 2 |
| SS-BCR-003 | Browser session restore ("Continue where you left off") | Browser is configured to restore tabs on startup | 1. Close browser with app tab open 2. Reopen browser (session restore active) 3. Inspect sessionStorage | **Browser-dependent**: some browsers restore sessionStorage with session restore; verify user state is consistent (either fully restored or clean login) | Critical | 4 |
| SS-BCR-004 | Closing tab with unsaved work – beforeunload prompt | User has in-progress unsaved form data | 1. Fill in form fields 2. Click tab close (×) 3. Observe browser prompt | Browser shows "Leave site? Changes may not be saved" confirmation if `beforeunload` handler is implemented | High | 3 |
| SS-BCR-005 | Duplicate tab retains independent session copy | Active session in Tab A | 1. Right-click tab → "Duplicate" 2. Inspect sessionStorage in both tabs | Both tabs have independent copies of sessionStorage (browser spec); modifying one does NOT affect the other | High | 3 |
| SS-BCR-006 | Crash recovery does not leak session data | Active session before simulated crash | 1. Kill browser process via Task Manager 2. Reopen browser 3. If crash-recovery dialog appears, restore tab 4. Inspect sessionStorage | Session data should be cleared (no guarantee of persistence post-crash); app must not expose stale tokens | High | 4 |
| SS-BCR-007 | Incognito/Private window — session isolation | Active session in normal window | 1. Open app in incognito/private window 2. Log in 3. Compare sessionStorage in normal vs. incognito | sessionStorage is completely isolated between normal and incognito windows | High | 3 |

---

## 6 · Multi-Tab Behavior (`SS-TAB`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-TAB-001 | Each tab has independent sessionStorage | User opens app in Tab A and Tab B (via `window.open` or new tab) | 1. Open app in Tab A → log in 2. Open app in new Tab B → log in 3. Modify sessionStorage value in Tab A 4. Inspect Tab B's sessionStorage | Tab B is NOT affected by Tab A's sessionStorage changes (per spec: independent per tab) | Critical | 3 |
| SS-TAB-002 | Logout in one tab does NOT auto-logout other tab (sessionStorage) | User logged in on Tab A and Tab B | 1. Click "Logout" on Tab A (sessionStorage cleared) 2. Switch to Tab B 3. Perform an action | Tab B session remains active (sessionStorage is tab-scoped); Tab B continues to function until its own token expires or user logs out | High | 3 |
| SS-TAB-003 | Cross-tab sync via BroadcastChannel/localStorage events | App implements cross-tab communication | 1. Log out on Tab A 2. Observe Tab B | If cross-tab sync is implemented: Tab B detects logout event and clears its own session. If not: Tab B remains active (document this as a risk) | High | 4 |
| SS-TAB-004 | Opening app in 10+ tabs simultaneously | Fresh browser session | 1. Open 10 tabs, each navigating to the app 2. Log in on each tab 3. Inspect sessionStorage of each | Each tab has its own session; no memory errors; app remains responsive | Medium | 3 |
| SS-TAB-005 | Token refresh in one tab does not update others | Tabs A and B both have tokens nearing expiry | 1. Tab A's token auto-refreshes 2. Tab B's token has NOT refreshed 3. Tab B makes an API call | Tab B either independently refreshes or gets 401; no assumption that Tab A's refresh applies to Tab B | High | 4 |
| SS-TAB-006 | Different users in different tabs | User A logged in on Tab 1; User B logged in on Tab 2 | 1. Log in as User A in Tab 1 2. Log in as User B in Tab 2 3. Perform actions in each | Each tab operates independently with its own user context; no data cross-contamination | Critical | 4 |
| SS-TAB-007 | Duplicate tab via Ctrl+K / middle-click link | Active session in original tab | 1. Middle-click a navigation link → opens in new tab 2. Inspect sessionStorage in new tab | New tab receives a copy of the original sessionStorage snapshot at time of duplication; subsequent changes are independent | Medium | 3 |

---

## 7 · Session Hijacking Risks (`SS-HIJ`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-HIJ-001 | Session token not exposed in URL parameters | User is authenticated | 1. Navigate through all pages 2. Inspect URL bar and network requests | Token is NEVER passed as a URL query parameter (prevents Referer leakage & browser history exposure) | Critical | 2 |
| SS-HIJ-002 | Session token not logged to console | Active session | 1. Open DevTools Console 2. Navigate through app 3. Search console output for token value | Token or sensitive session data is NOT printed to console in production build | Critical | 2 |
| SS-HIJ-003 | XSS cannot read sessionStorage | Simulated XSS injection point | 1. Inject `<img src=x onerror="alert(sessionStorage.getItem('token'))">` in any user-input field 2. Observe result | XSS payload is sanitized; no alert fires; sessionStorage data not extractable via script injection | Critical | 5 |
| SS-HIJ-004 | CSRF protection on session-authenticated requests | Active session | 1. Craft a cross-origin POST request to a sensitive endpoint 2. Include session-based auth headers 3. Send from external origin | Request is rejected (CSRF token missing or Origin mismatch); session cannot be exploited cross-origin | Critical | 5 |
| SS-HIJ-005 | Man-in-the-middle: token interception over HTTP | App accessible over HTTP (non-HTTPS) | 1. Access app over plain HTTP 2. Use packet sniffer (Wireshark) to capture traffic 3. Search for session token in captured packets | **Expected risk:** Token is visible in plaintext. **Mitigation:** App MUST enforce HTTPS; redirect HTTP → HTTPS | Critical | 4 |
| SS-HIJ-006 | Token replay attack | Attacker obtains a valid token | 1. Copy a valid session token 2. Token owner logs out (sessionStorage cleared) 3. Attacker sends API request with copied token | Server rejects the replayed token (token is invalidated server-side upon logout) | Critical | 5 |
| SS-HIJ-007 | Session fixation attack | Attacker sets a known session ID before victim logs in | 1. Attacker sets `sessionStorage.setItem('token', 'known-value')` via DevTools 2. Victim logs in 3. Check if server-issued token overwrites the attacker's token | Login MUST generate a new token server-side; pre-existing token is overwritten, preventing fixation | Critical | 5 |
| SS-HIJ-008 | Third-party script access to sessionStorage | App loads external scripts (analytics, CDN libraries) | 1. Audit all third-party scripts loaded by the app 2. Check if any script reads/writes sessionStorage 3. Use CSP (Content Security Policy) headers | Third-party scripts should NOT have access to session tokens; CSP restricts inline script execution | High | 4 |
| SS-HIJ-009 | Browser extension access to sessionStorage | User has browser extensions installed | 1. Install a test browser extension with storage permissions 2. Check if extension can read sessionStorage of the app origin | **Known risk:** Extensions with sufficient permissions CAN read sessionStorage. Mitigation: encrypt token values or use HttpOnly cookies as alternative | Medium | 4 |
| SS-HIJ-010 | Shared/public computer — session remnants | Previous user did not log out | 1. User A logs in and uses the app 2. User A closes tab (but not browser) 3. User B opens a new tab to same URL | sessionStorage should be empty for User B's new tab; if tab was merely reloaded (not closed), warn about shared-computer risks | High | 3 |

---

## 8 · Concurrent Login Session Handling (`SS-CON`)

| TC ID | Title | Precondition | Steps | Expected Result | Priority | Complexity |
|---|---|---|---|---|---|---|
| SS-CON-001 | Same user logs in on two different browsers | User account exists | 1. Log in as User A on Chrome 2. Log in as User A on Firefox 3. Perform actions in both | Both sessions are active (if server allows multiple sessions) OR older session is invalidated (if single-session policy) — verify per business rule | Critical | 3 |
| SS-CON-002 | Same user logs in on two devices | User A on laptop and mobile browser | 1. Log in as User A on laptop 2. Log in as User A on phone browser 3. Perform actions on both | Behavior matches server-side session policy; if max-session = 1, first device is kicked and notified | Critical | 4 |
| SS-CON-003 | Login on new device invalidates old session | Single-session enforcement policy active | 1. Log in on Device A 2. Log in on Device B 3. On Device A, try to perform any action | Device A receives 401; UI displays "Session invalidated — you logged in from another device" | Critical | 4 |
| SS-CON-004 | Concurrent logins with different roles (same user) | User has role changes pending (e.g., promoted to admin) | 1. Log in on Browser A (role: Analyst) 2. Admin changes user's role to Admin 3. Log in on Browser B (role: Admin) 4. On Browser A, check permissions | Browser A's session uses old role until re-auth/refresh; Browser B has new role. Verify no privilege escalation on Browser A | Critical | 5 |
| SS-CON-005 | Password change invalidates all active sessions | User logged in on multiple browsers/tabs | 1. User A logged in on Chrome and Firefox 2. User A changes password on Chrome 3. On Firefox, perform next action | Firefox session is invalidated (401); user must re-authenticate with new password | Critical | 4 |
| SS-CON-006 | Account lockout propagation to active sessions | User A is logged in; admin locks the account | 1. User A is working normally 2. Admin locks User A's account 3. User A performs next API call | API returns 403 (account locked); sessionStorage is cleared; user sees "Account locked" message | Critical | 4 |
| SS-CON-007 | Race condition: simultaneous login requests | Same credentials submitted from two clients at the exact same moment | 1. Script sends two login requests concurrently with same credentials 2. Check both responses 3. Verify server-side session count | Server handles gracefully — either both get separate valid sessions or one is queued; no server crash or token collision | High | 5 |
| SS-CON-008 | Session count limit enforcement | Server enforces max 3 concurrent sessions per user | 1. Log in on Device 1, 2, 3 (all succeed) 2. Attempt login on Device 4 | Device 4 login is denied ("Maximum sessions reached") OR oldest session is evicted; user is notified | High | 4 |
| SS-CON-009 | "Log out all devices" feature | User is logged in on 3 devices | 1. On Device 1, click "Log out all sessions" 2. On Device 2 and 3, attempt next action | All sessions except current (or all) are invalidated server-side; Devices 2 & 3 get 401; sessionStorage on those clients is cleared upon next API call | High | 4 |
| SS-CON-010 | OAuth / SSO session revocation | User authenticated via third-party SSO (e.g., Google) | 1. User logs in via SSO 2. User revokes app access from SSO provider's settings 3. User performs next action in app | App detects SSO token revocation; session is invalidated; user redirected to SSO login | High | 5 |

---

## Coverage Summary

| Category | Test Cases | Critical | High | Medium |
|---|---|---|---|---|
| Navigation Retention | 8 | 2 | 4 | 2 |
| Partial Workflow | 7 | 0 | 5 | 2 |
| Token/Session Expiration | 8 | 4 | 2 | 2 |
| Manual Refresh | 7 | 1 | 3 | 3 |
| Browser Close/Reopen | 7 | 3 | 3 | 0 (1 Medium redirect) |
| Multi-Tab Behavior | 7 | 2 | 3 | 2 |
| Session Hijacking Risks | 10 | 6 | 2 | 2 |
| Concurrent Login Handling | 10 | 6 | 4 | 0 |
| **Total** | **64** | **24** | **26** | **14** |

---

## Risk Matrix

| Risk Area | Likelihood | Impact | Test Coverage |
|---|---|---|---|
| Token leakage via URL/console | Medium | Critical | SS-HIJ-001, SS-HIJ-002 |
| XSS extraction of sessionStorage | High | Critical | SS-HIJ-003 |
| Session fixation | Medium | Critical | SS-HIJ-007 |
| Stale sessions after password change | High | High | SS-CON-005 |
| Cross-tab session inconsistency | High | Medium | SS-TAB-002, SS-TAB-003 |
| Data loss on unexpected refresh | Medium | Medium | SS-REF-003, SS-REF-005 |
| Session restore after crash | Low | High | SS-BCR-006 |
| Concurrent token collision | Low | Critical | SS-CON-007 |
