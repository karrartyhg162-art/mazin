# Product Requirements Document (PRD)
## Telegram Channel/Group Ownership Transfer Auto-Rejection Userbot

---

## 1. Executive Summary

A Python-based Telegram Userbot that automatically detects and rejects any channel or group ownership transfers to the user's account in real-time. The bot monitors incoming notifications from Telegram's official channel transfer system and instantly clicks the rejection button before malicious actors can modify the transferred channel/group content.

**Project Type:** Personal Security Automation Tool
**Platform:** Python 3 (Pydroid3 on Android)
**Scope:** Personal use only (single account)
**Priority:** Critical (Account Protection)

---

## 2. Problem Statement

The user's Telegram account is under threat from a malicious actor who employs the following attack vector:

1. Transfer channel or group ownership to the user's account
2. Immediately populate the channel/group with policy-violating content
3. Result: User's account gets flagged/banned by Telegram for TOS violations

The user has no time to manually click the rejection button because the attacker automates the content upload. The system needs to react **faster than the attacker can move**.

Current Workflow (Manual - Insufficient):
- Telegram sends rejection notification
- User sees notification
- User manually clicks rejection button
- By this time, content may already be uploaded

Required Workflow (Automated - Secure):
- Telegram sends rejection notification
- Userbot detects the notification message
- Userbot immediately clicks rejection button
- Attacker cannot escalate the attack

---

## 3. Solution Overview

Deploy a 24/7 Python Userbot (using Pyrogram library) that:
- Runs continuously on the user's device (laptop → Pydroid3 on mobile)
- Monitors incoming messages from Telegram's official notification system
- Detects ownership transfer notifications in real-time
- Automatically presses the rejection button within milliseconds
- Logs all rejected channels/groups for user visibility
- Handles network interruptions and maintains continuous operation

The bot operates on the user's personal Telegram account (not a separate bot account) to access the rejection functionality.

---

## 4. Core Features

### 4.1 Real-Time Ownership Transfer Detection
- Monitor incoming messages with pattern matching for ownership transfer notifications
- Detect both channel and supergroup/group transfers
- Identify the rejection button (inline button with text "رفض نقل القناة" or "Decline Channel Transfer")
- React within milliseconds of detection

### 4.2 Automatic Rejection Action
- Click the rejection button programmatically via Pyrogram API
- Confirm successful rejection
- Log the action with timestamp

### 4.3 Rejection History & Logging
- Maintain a local JSON file tracking all rejected channels/groups
- Log fields: timestamp, channel_name, channel_id, transferred_from, action_status
- Display rejection history to user on demand
- Persist data across bot restarts

### 4.4 Continuous Operation
- Run 24/7 without interruption
- Auto-reconnect on network failure
- Graceful error handling for API rate limits
- Recovery mechanism for session crashes
- No manual intervention required after initial setup

### 4.5 Startup Configuration
- On first run, prompt user for:
  - Telegram API_ID (from my.telegram.org)
  - Telegram API_HASH (from my.telegram.org)
  - Phone number for account login
  - One-time verification code
- Store credentials securely in local config.json
- Reuse stored credentials on subsequent runs (no repeated login)

### 4.6 Monitoring & Visibility
- Console output showing:
  - Bot startup status
  - Active monitoring status
  - Each rejection event (timestamp + channel info)
  - Network status
  - Error messages
- Optional file-based logging for troubleshooting

---

## 5. Technical Architecture

### 5.1 Technology Stack
- **Language:** Python 3.8+
- **Telegram Library:** Pyrogram (Userbot mode)
- **Data Storage:** JSON (local file-based)
- **Deployment:** Pydroid3 on Android
- **Development:** Any Python IDE (VS Code, PyCharm)

### 5.2 System Components

#### Component 1: Session Manager
- Initialize Telegram session using API_ID + API_HASH
- Load stored credentials from config.json
- Handle user authentication (phone + OTP code)
- Store session tokens for quick restart

#### Component 2: Message Listener
- Listen for incoming messages in real-time (polling or event-based)
- Filter messages from Telegram's official notification service
- Pattern match for ownership transfer notification text

#### Component 3: Transfer Detector
- Parse notification message content
- Extract channel/group name and ID
- Locate rejection button in message
- Validate button before action

#### Component 4: Rejection Handler
- Invoke Pyrogram's button click API
- Confirm action completion
- Handle rejection failures gracefully
- Retry logic for transient failures

#### Component 5: Logging System
- Record rejected channel metadata
- Store in JSON file with timestamp
- Provide lookup/query capability
- Generate summary reports

#### Component 6: Error Recovery
- Detect connection loss
- Auto-reconnect to Telegram servers
- Resume monitoring without data loss
- Log all error events

---

## 6. Data Model

### 6.1 Configuration File (config.json)
```json
{
  "api_id": 12345678,
  "api_hash": "abc123def456",
  "phone_number": "+1234567890",
  "session_name": "telegram_session",
  "polling_interval": 1,
  "log_file": "rejections.json"
}
```

### 6.2 Rejections Log (rejections.json)
```json
{
  "rejections": [
    {
      "timestamp": "2025-05-05T10:30:45Z",
      "channel_id": 1001234567890,
      "channel_name": "Channel Name",
      "transferred_from": "username_or_id",
      "status": "rejected",
      "bot_reaction_time_ms": 150
    }
  ]
}
```

---

## 7. Functional Requirements

### 7.1 FR1: Session Initialization
- User enters API_ID and API_HASH on first run
- User enters phone number
- Bot sends OTP code to Telegram
- User enters OTP code
- Credentials stored in config.json for future runs
- Success confirmation displayed

### 7.2 FR2: Message Monitoring
- Bot polls Telegram API for new messages every N seconds (configurable, default 1-2 seconds)
- Filters only messages from Telegram's official system account
- Checks message content for ownership transfer keywords (Arabic and English support)

### 7.3 FR3: Rejection Detection
- Identify inline button with rejection action
- Verify button targets rejection API endpoint
- Extract channel/group information from message

### 7.4 FR4: Automatic Rejection
- Trigger button click via Pyrogram API call
- Confirm Telegram API response (success = 200/OK)
- Record rejection in local log with timestamp

### 7.5 FR5: Rejection Logging
- Log each rejection with: timestamp, channel_id, channel_name, transferred_from_user, action_status
- Append to rejections.json file
- Provide count and summary of daily rejections

### 7.6 FR6: Graceful Error Handling
- Connection timeout → auto-retry (exponential backoff)
- API rate limit → queue requests, wait, retry
- Session expired → re-authenticate silently
- Message parse error → log error, skip message, continue
- File I/O error → alert user, don't crash

### 7.7 FR7: Continuous Operation
- No manual restarts required
- Run indefinitely (until user manually stops)
- Survive network outages
- Survive API temporary failures
- Maintain state across restarts

---

## 8. Non-Functional Requirements

### 8.1 Performance
- **Detection Latency:** Detect transfer notification within 2 seconds of Telegram's notification
- **Rejection Speed:** Click rejection button within 200-500ms of detection
- **Polling Interval:** Check for new messages every 1-2 seconds
- **CPU Usage:** Minimal (< 5% idle, < 15% active)
- **Memory Usage:** < 100MB

### 8.2 Reliability
- **Uptime:** 99.5% (acceptable for personal use; brief network outages expected)
- **Error Recovery:** Auto-recovery for 100% of transient network errors
- **Data Integrity:** No log data loss on unexpected shutdown
- **Failure Modes:** Graceful degradation (never crash/hang)

### 8.3 Security
- API credentials stored locally (config.json) - encrypted or access-restricted
- No sensitive data logged to console
- Session tokens managed securely
- Phone number not stored after initial setup (only in session)
- No telemetry or external data transmission

### 8.4 Scalability
- Single account support only (not multi-account)
- Designed for personal use
- No external database dependency
- JSON file-based logging sufficient

### 8.5 Maintainability
- Clean, readable Python code
- Comprehensive comments for logic
- Structured error messages
- Configuration externalized to config.json
- Logging for troubleshooting

---

## 9. User Stories

### US1: Initial Setup
**As a** user with no prior setup
**I want to** run the bot for the first time without manual complexity
**So that** I can protect my account immediately

**Acceptance Criteria:**
- Bot prompts for API_ID and API_HASH
- Bot guides phone verification with OTP
- Bot confirms successful authentication
- Credentials saved to config.json
- Bot starts monitoring automatically after setup

### US2: Active Monitoring
**As a** user running the bot continuously
**I want to** see that the bot is actively monitoring my account
**So that** I have confidence it's protecting me

**Acceptance Criteria:**
- Console displays "Monitoring active..." message
- Bot logs each polling cycle (or at least periodic status updates)
- On rejection event, displays: "[REJECTION] Channel: X, Time: Y, Status: Success"
- User can see rejection history file (rejections.json) at any time

### US3: Rejection Event Handling
**As a** user under attack
**I want to** automatically reject ownership transfers in real-time
**So that** the attacker cannot modify my account's channels

**Acceptance Criteria:**
- Ownership transfer notification detected within 2 seconds
- Rejection button clicked automatically within 500ms
- Rejection confirmed by Telegram API
- Event logged with timestamp and channel info
- User notified via console output

### US4: Network Interruption Recovery
**As a** user with unreliable internet
**I want to** the bot automatically reconnect after network loss
**So that** my account is protected even during internet outages

**Acceptance Criteria:**
- Bot detects connection loss (no response from API)
- Bot waits 10-30 seconds, then retries
- Bot reconnects without user intervention
- Monitoring resumes automatically
- No data loss in rejections.json

### US5: Viewing Rejection History
**As a** user wanting to understand my attack patterns
**I want to** view all rejected channels/groups with timestamps
**So that** I can track the attacker's activity

**Acceptance Criteria:**
- rejections.json file is human-readable JSON
- File includes: timestamp, channel_id, channel_name, status
- File persists across bot restarts
- User can view file directly or bot can display summary

---

## 10. Edge Cases & Error Handling

### 10.1 Message Parse Errors
**Scenario:** Bot receives an ownership transfer message with unexpected format
**Handling:** Log error with message content, skip message, continue monitoring

### 10.2 Button Not Found
**Scenario:** Rejection button is not found in the expected message location
**Handling:** Log warning, flag message for manual review, continue monitoring (don't crash)

### 10.3 Rejection API Failure
**Scenario:** Telegram API returns error when clicking rejection button
**Handling:** Retry up to 3 times with exponential backoff, log failure, alert user

### 10.4 Session Expired
**Scenario:** Telegram session token becomes invalid
**Handling:** Detect 401/Unauthorized response, prompt for re-authentication, resume monitoring

### 10.5 Rate Limit Hit
**Scenario:** Too many API requests trigger Telegram's rate limit
**Handling:** Queue requests, wait X seconds, resume in order, log event

### 10.6 Network Timeout
**Scenario:** API request times out (no response from Telegram)
**Handling:** Catch timeout exception, wait 30 seconds, retry, log event

### 10.7 File Corruption
**Scenario:** rejections.json is corrupted or unreadable
**Handling:** Create backup, reinitialize file, log warning, continue operation

### 10.8 Duplicate Rejections
**Scenario:** Same channel transfer notification received twice
**Handling:** Check channel_id in log before rejecting, avoid duplicate actions

---

## 11. Logging & Monitoring

### 11.1 Console Output
```
[2025-05-05 10:15:30] Bot Started
[2025-05-05 10:15:35] Authenticated as: username
[2025-05-05 10:15:40] Monitoring active... (polling every 1s)
[2025-05-05 10:30:45] [REJECTION] Channel: "Evil Channel", ID: 1001234567890, Status: SUCCESS
[2025-05-05 10:30:46] Rejection logged to rejections.json
[2025-05-05 10:45:12] [ERROR] Connection timeout - retrying in 30s...
[2025-05-05 10:45:42] Reconnected successfully
```

### 11.2 Rejections Log (rejections.json)
File continuously updated with:
- Timestamp (ISO 8601 format)
- Channel ID and name
- Transferred from (username or user ID)
- Action status (success/failed/retry)
- Reaction time in milliseconds

### 11.3 Error Logging
- All errors logged to console with timestamp
- Error type categorized (Network, API, Parse, etc.)
- Error message includes context for debugging

---

## 12. Deployment Instructions

### 12.1 Prerequisites
- Telegram account (personal account)
- API_ID and API_HASH from https://my.telegram.org/apps
- Python 3.8+ environment
- Pydroid3 app installed on Android device

### 12.2 Installation Steps (Laptop)

1. Clone or download the code from GitHub repository
2. Create virtual environment: `python -m venv env`
3. Activate environment: `source env/bin/activate` (Mac/Linux) or `env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run bot: `python main.py`
6. Follow prompts for API_ID, API_HASH, and phone verification

### 12.3 Deployment to Pydroid3 (Mobile)

1. Open Pydroid3
2. Create new project or import from GitHub
3. Ensure requirements are installed: `pip install pyrogram tgcrypto`
4. Transfer main.py and requirements.txt to Pydroid3
5. Run: `python main.py`
6. Bot will use stored credentials from config.json (if transferred from laptop)

### 12.4 Keeping Bot Running 24/7 on Pydroid3

Challenge: Android kills background processes to save battery
Solutions:
- Use Pydroid3's "Run in Background" feature
- Consider adding Android service wrapper (future enhancement)
- Use "WakeLock" library if needed (keep device awake during critical operations)
- Set phone to "Performance Mode" or disable sleep when running bot

### 12.5 Configuration & First Run

First Run:
```
Bot initialized. Configuration not found.
Enter API_ID: [user enters]
Enter API_HASH: [user enters]
Enter your phone number (with country code): [user enters]
Telegram is sending you an OTP code. Check your app.
Enter OTP code: [user enters]
✓ Authentication successful!
Configuration saved to config.json
✓ Monitoring started...
```

Subsequent Runs:
```
Configuration loaded from config.json
✓ Session established
✓ Monitoring started...
```

---

## 13. Success Metrics

### 13.1 Functional Success
- Bot successfully rejects 100% of test ownership transfer notifications
- Rejection occurs within 500ms of detection
- Log file accurately records all rejections
- Bot recovers from network interruptions without data loss

### 13.2 Reliability Metrics
- Uptime: 99.5% or higher (acceptable for personal use)
- Error recovery rate: 100% (all transient errors recovered)
- Mean time to detect: < 2 seconds
- Mean time to reject: < 500ms

### 13.3 User Experience
- Setup completes in < 5 minutes
- No crashes or hangs during operation
- Clear console output showing bot status
- Rejection history is accessible and human-readable

---

## 14. Development Priorities

### Phase 1: MVP (Minimum Viable Product)
- Core message listening
- Ownership transfer detection
- Automatic rejection
- Basic error handling
- JSON-based logging

### Phase 2: Enhancement (Future, Optional)
- Prettier console UI with colored output
- Statistics dashboard (rejections per day, etc.)
- Manual override options
- Whitelist/blacklist features
- Telegram notification alerts to user

---

## 15. Known Limitations & Constraints

1. **Personal Use Only:** Designed for single Telegram account, not multi-account
2. **Android Battery:** Pydroid3 may be killed by OS if battery-saver mode is enabled
3. **TOS Compliance:** Userbot usage must comply with Telegram's Terms of Service (personal automation is generally allowed)
4. **Network Dependency:** Bot cannot operate without internet connection
5. **Manual Restart Required:** If process is killed by OS, user must manually restart

---

## 16. Risks & Mitigation

### Risk 1: Telegram API Changes
**Impact:** API endpoints or button structure may change, breaking bot
**Mitigation:** Regular testing, subscribe to Telegram API updates, version-tag releases

### Risk 2: Session Invalidation
**Impact:** Stored session token becomes invalid after long inactivity
**Mitigation:** Periodic session refresh, automatic re-authentication on 401 error

### Risk 3: Rate Limiting
**Impact:** Too many API calls trigger Telegram's anti-spam measures
**Mitigation:** Implement request queuing, exponential backoff, logging of rate limits

### Risk 4: Attacker Adaptation
**Impact:** Attacker finds workaround to bot's rejection mechanism
**Mitigation:** Monitor for new attack patterns, log all attempts, prepare counter-measures

---

## 17. Code Structure

### Project Layout
```
telegram-auto-rejection-userbot/
├── main.py                 # Main entry point
├── config.json            # Credentials (auto-generated)
├── rejections.json        # Rejection history (auto-generated)
├── requirements.txt       # Dependencies
├── README.md              # User guide
└── .gitignore             # Exclude sensitive files
```

### Dependencies (requirements.txt)
```
pyrogram>=2.0.0
tgcrypto>=1.2.2
```

---

## 18. Support & Troubleshooting

### Common Issues

**Issue: "API ID not valid" error**
- Solution: Verify API_ID and API_HASH from https://my.telegram.org/apps
- Ensure no extra spaces or special characters

**Issue: Bot stops after a few hours**
- Solution (Pydroid3): Enable "Run in Background", disable sleep mode
- Solution (VPS): Use system service wrapper or screen/tmux

**Issue: Rejection button not detected**
- Solution: Ensure latest Pyrogram version, check if Telegram UI changed
- Manually test rejection by clicking button to confirm it exists

**Issue: rejections.json file not updating**
- Solution: Check file permissions, verify JSON syntax
- Check console for file I/O errors

---

## 19. Timeline

- **Week 1:** Code development and testing (MVP)
- **Week 2:** Deploy to Pydroid3, test on mobile
- **Week 3:** Stress testing, error handling improvements
- **Week 4:** Documentation and release

---

## 20. Conclusion

This PRD defines a critical security tool that protects the user's Telegram account from ownership transfer attacks. The bot operates silently and continuously, rejecting malicious transfers in real-time before damage can occur. With proper error handling and logging, it provides both security and visibility into attack patterns.

The solution prioritizes reliability, simplicity, and user peace of mind.
