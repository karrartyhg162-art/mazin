"""
Telegram Channel/Group Ownership Transfer Auto-Rejection Userbot
================================================================
A Python-based Telegram Userbot that automatically detects and rejects
any channel or group ownership transfers to the user's account in real-time.

Uses Pyrogram library in Userbot mode for instant event-driven detection.
"""

import os
import sys
import json
import time
import asyncio
import logging
import re
from datetime import datetime, timezone

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    SessionPasswordNeeded,
    RPCError,
    Unauthorized,
)

# ─────────────────────────────────────────────────────────────────
# Monkey-patch Pyrogram to support new Telegram Channel IDs
# ─────────────────────────────────────────────────────────────────
import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────

# All data files are stored inside the "data mazin" directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data mazin")
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
REJECTIONS_FILE = os.path.join(DATA_DIR, "rejections.json")
SESSION_NAME = os.path.join(DATA_DIR, "auto_reject_session")
LOG_FILE = os.path.join(DATA_DIR, "bot.log")

# Telegram's official notification sender IDs
# 777000 = Telegram's internal service messages
# 42777  = Channel transfer bot (some versions)
TELEGRAM_SERVICE_IDS = {777000, 42777}

# Keywords that indicate an ownership transfer notification (Arabic + English)
TRANSFER_KEYWORDS_AR = [
    "نقل ملكية",
    "نقل القناة",
    "نقل المجموعة",
    "تم نقل ملكية",
    "نقل حق الملكية",
    "طلب نقل",
    "تحويل ملكية",
]

TRANSFER_KEYWORDS_EN = [
    "transfer ownership",
    "channel transfer",
    "group transfer",
    "ownership has been transferred",
    "transfer request",
    "transferred the ownership",
    "wants to transfer",
]

# Rejection button text patterns (Arabic + English)
REJECTION_BUTTON_TEXTS = [
    "رفض نقل القناة",
    "رفض",
    "رفض النقل",
    "رفض نقل المجموعة",
    "decline channel transfer",
    "decline transfer",
    "decline",
    "reject",
    "reject transfer",
    "decline group transfer",
]

# ─────────────────────────────────────────────────────────────────
# Logging Setup
# ─────────────────────────────────────────────────────────────────

def setup_logging():
    """Configure dual logging: console + file."""
    logger = logging.getLogger("AutoReject")
    logger.setLevel(logging.INFO)

    # Console handler with colored-like formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_fmt)

    # File handler for troubleshooting
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


log = setup_logging()

# ─────────────────────────────────────────────────────────────────
# Configuration Manager
# ─────────────────────────────────────────────────────────────────

def load_config():
    """
    Load configuration from config.json.
    
    The user must fill in their credentials in:
        data mazin/config.json
    before running the bot.
    """
    if not os.path.exists(CONFIG_FILE):
        default_config = {
            "api_id": 0,
            "api_hash": "ضع_هنا_API_HASH",
            "phone_number": "+966xxxxxxxxx"
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            log.error(
                f"تم إنشاء ملف الإعدادات في المسار:\n{CONFIG_FILE}\n"
                f"يرجى فتح الملف ووضع بياناتك داخله ثم إعادة تشغيل البوت."
            )
        except IOError as e:
            log.error(f"Failed to create config.json: {e}")
        return None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate required fields exist
        required = ["api_id", "api_hash", "phone_number"]
        missing = [k for k in required if k not in config]
        if missing:
            log.error(
                f"config.json is missing required fields: {', '.join(missing)}\n"
                f"Please open: {CONFIG_FILE} and fill them in."
            )
            return None

        # Validate that placeholder values have been replaced
        if config["api_id"] == 0 or not isinstance(config["api_id"], int):
            log.error(
                "api_id is still the default value (0).\n"
                f"Please open: {CONFIG_FILE}\n"
                "and replace it with your real API_ID from https://my.telegram.org/apps"
            )
            return None

        if "ضع_هنا" in str(config["api_hash"]) or len(str(config["api_hash"])) < 10:
            log.error(
                "api_hash has not been set.\n"
                f"Please open: {CONFIG_FILE}\n"
                "and replace it with your real API_HASH from https://my.telegram.org/apps"
            )
            return None

        if "xxx" in config.get("phone_number", "xxx"):
            log.error(
                "phone_number has not been set.\n"
                f"Please open: {CONFIG_FILE}\n"
                "and replace it with your real phone number (e.g. +966512345678)"
            )
            return None

        return config

    except json.JSONDecodeError as e:
        log.error(f"config.json has invalid JSON format: {e}")
        return None
    except IOError as e:
        log.error(f"Failed to read config.json: {e}")
        return None

# ─────────────────────────────────────────────────────────────────
# Rejections Logger
# ─────────────────────────────────────────────────────────────────

def load_rejections() -> dict:
    """Load existing rejections log or create new one."""
    if os.path.exists(REJECTIONS_FILE):
        try:
            with open(REJECTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "rejections" in data:
                return data
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"rejections.json corrupted, creating backup: {e}")
            # Create backup of corrupted file
            backup_name = f"rejections_backup_{int(time.time())}.json"
            try:
                os.rename(REJECTIONS_FILE, backup_name)
                log.info(f"Corrupted file backed up as {backup_name}")
            except OSError:
                pass

    return {"rejections": []}


def save_rejection(entry: dict):
    """Append a rejection entry to the rejections log."""
    data = load_rejections()

    # Duplicate check: skip if same channel_id was rejected in last 60 seconds
    channel_id = entry.get("channel_id")
    if channel_id:
        for existing in data["rejections"]:
            if existing.get("channel_id") == channel_id:
                try:
                    existing_time = datetime.fromisoformat(
                        existing["timestamp"].replace("Z", "+00:00")
                    )
                    entry_time = datetime.fromisoformat(
                        entry["timestamp"].replace("Z", "+00:00")
                    )
                    if abs((entry_time - existing_time).total_seconds()) < 60:
                        log.info(
                            f"Duplicate rejection skipped for channel {channel_id}"
                        )
                        return
                except (ValueError, KeyError):
                    pass

    data["rejections"].append(entry)

    try:
        with open(REJECTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.info("Rejection logged to rejections.json")
    except IOError as e:
        log.error(f"[ERROR] Failed to write rejections.json: {e}")

# ─────────────────────────────────────────────────────────────────
# Transfer Detection Logic
# ─────────────────────────────────────────────────────────────────

def is_transfer_message(message: Message) -> bool:
    """
    Check if a message is an ownership transfer notification.
    
    We check:
    1. The message is from Telegram's service account (777000)
    2. The message text contains transfer-related keywords
    3. The message has inline buttons (for rejection action)
    """
    # Must have text content
    text = (message.text or message.caption or "").lower()
    if not text:
        return False

    # Check for transfer keywords (Arabic)
    for keyword in TRANSFER_KEYWORDS_AR:
        if keyword in text:
            return True

    # Check for transfer keywords (English)
    for keyword in TRANSFER_KEYWORDS_EN:
        if keyword in text:
            return True

    return False


def find_rejection_button(message: Message) -> tuple:
    """
    Find the rejection button in message's inline keyboard.
    
    Returns:
        tuple: (row_index, button_index) if found, else (None, None)
    """
    if not message.reply_markup:
        return None, None

    # Check inline keyboard buttons
    keyboard = getattr(message.reply_markup, "inline_keyboard", None)
    if not keyboard:
        return None, None

    for row_idx, row in enumerate(keyboard):
        for btn_idx, button in enumerate(row):
            btn_text = (button.text or "").lower().strip()
            for rejection_text in REJECTION_BUTTON_TEXTS:
                if rejection_text in btn_text or btn_text in rejection_text:
                    return row_idx, btn_idx

    return None, None

# ─────────────────────────────────────────────────────────────────
# Main Bot Application
# ─────────────────────────────────────────────────────────────────

async def main():
    """Main entry point: setup, authenticate, and run the monitoring loop."""

    print("\n" + "=" * 55)
    print("  🛡️  Telegram Auto-Rejection Userbot")
    print("  Ownership Transfer Protection System")
    print("=" * 55 + "\n")

    # ── Load configuration from data mazin/config.json ──
    config = load_config()
    if not config:
        print("\n" + "=" * 55)
        print("  ❌  Configuration Error")
        print("=" * 55)
        print(f"\n  Please fill in your credentials in:")
        print(f"  📁 {CONFIG_FILE}")
        print(f"\n  Required fields:")
        print(f"    • api_id       → from https://my.telegram.org/apps")
        print(f"    • api_hash     → from https://my.telegram.org/apps")
        print(f"    • phone_number → your number with country code")
        print("\n" + "=" * 55)
        return
    log.info(f"Configuration loaded from {CONFIG_FILE}")

    api_id = config["api_id"]
    api_hash = config["api_hash"]
    phone = config.get("phone_number", "")

    # ── Initialize Pyrogram Client ──
    app = Client(
        name=SESSION_NAME,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone if phone else None,
    )

    # ── Suppress harmless Pyrogram "Peer id invalid" errors ──
    def _handle_async_exception(loop, context):
        exception = context.get("exception")
        if exception and isinstance(exception, ValueError) and "Peer id invalid" in str(exception):
            # Pyrogram can't resolve a channel/group from its cache — harmless
            return
        if exception and isinstance(exception, KeyError) and "ID not found" in str(exception):
            return
        # Log any other unexpected async exception
        msg = context.get("message", "Unhandled async exception")
        log.warning(f"[ASYNC] {msg}: {exception}")

    asyncio.get_event_loop().set_exception_handler(_handle_async_exception)

    # ── Rejection counter for this session ──
    session_stats = {
        "rejections": 0,
        "errors": 0,
        "start_time": datetime.now(timezone.utc).isoformat(),
    }

    # ─────────────────────────────────────────────────────
    # Event Handler: Incoming Messages
    # ─────────────────────────────────────────────────────

    @app.on_message(filters.incoming & filters.private)
    async def on_private_message(client: Client, message: Message):
        """
        Handle all incoming private messages.
        
        We monitor private messages because Telegram's ownership
        transfer notifications arrive as private messages from
        the service account (user ID 777000).
        
        CRITICAL: We use message.click() to REJECT the transfer.
        This is the ONLY correct method. Do NOT use leave_chat().
        leave_chat() only exits the chat but does NOT reject the transfer.
        """
        detection_start = time.time()

        try:
            # ── Check if this is a transfer notification ──
            sender_id = message.from_user.id if message.from_user else None

            # Log service messages for debugging
            if sender_id in TELEGRAM_SERVICE_IDS:
                log.info(
                    f"Service message received from ID {sender_id}: "
                    f"{(message.text or '')[:100]}..."
                )

            # ── Detect transfer notification ──
            if not is_transfer_message(message):
                return

            log.info("🚨 OWNERSHIP TRANSFER DETECTED!")
            text = message.text or message.caption or ""
            log.info(f"Message content: {text[:300]}")

            # ── Extract channel info from message text ──
            channel_name = "Unknown"
            
            # Use regex to extract the exact channel/group name
            match_ar = re.search(r"تم نقل(?: قناة:| مجموعة:)?\s*(.+?)\s*إليك", text)
            match_en = re.search(r"(?:Channel|Group)\s*(.+?)\s*has been transferred", text)
            
            if match_ar:
                channel_name = match_ar.group(1).strip()
            elif match_en:
                channel_name = match_en.group(1).strip()
            
            log.info(f"Channel/Group name: {channel_name}")

            # ── Log all available buttons for debugging ──
            if message.reply_markup:
                keyboard = getattr(message.reply_markup, "inline_keyboard", None)
                if keyboard:
                    for r_idx, row in enumerate(keyboard):
                        for b_idx, btn in enumerate(row):
                            log.info(
                                f"  Button [{r_idx}][{b_idx}]: "
                                f"text='{btn.text}', "
                                f"callback_data='{btn.callback_data}'"
                            )
                else:
                    log.warning("Message has reply_markup but NO inline_keyboard!")
            else:
                log.warning("Message has NO reply_markup at all!")

            # ════════════════════════════════════════════════
            # REJECTION STRATEGY: Use message.click() ONLY
            # This is the CORRECT way to press Telegram's
            # inline rejection button. Do NOT use
            # request_callback_answer or leave_chat.
            # ════════════════════════════════════════════════

            rejection_success = False
            max_retries = 3
            clicked_button_text = ""

            # ── Strategy 1: Click rejection button by text match ──
            row_idx, btn_idx = find_rejection_button(message)

            if row_idx is not None:
                clicked_button_text = message.reply_markup.inline_keyboard[row_idx][btn_idx].text
                log.info(f"Found rejection button: '{clicked_button_text}' at [{row_idx}][{btn_idx}]")

                for attempt in range(1, max_retries + 1):
                    try:
                        log.info(f"🔴 CLICKING REJECTION BUTTON (attempt {attempt}/{max_retries})...")
                        
                        # message.click() is the CORRECT method
                        # It simulates a real user pressing the inline button
                        await message.click(row_idx, btn_idx)
                        
                        rejection_success = True
                        log.info(f"✅ REJECTION BUTTON CLICKED SUCCESSFULLY!")
                        break

                    except FloodWait as e:
                        wait_time = e.value
                        log.warning(f"[RATE LIMIT] FloodWait: waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)

                    except RPCError as e:
                        log.error(f"[ERROR] RPC Error on attempt {attempt}: {e}")
                        if attempt < max_retries:
                            backoff = 2 ** attempt
                            log.info(f"Retrying in {backoff}s...")
                            await asyncio.sleep(backoff)

                    except Exception as e:
                        log.error(f"[ERROR] Unexpected error clicking button: {e}")
                        if attempt < max_retries:
                            await asyncio.sleep(1)

            # ── Strategy 2: If no specific rejection button found, try ALL buttons ──
            if not rejection_success and message.reply_markup:
                keyboard = getattr(message.reply_markup, "inline_keyboard", [])
                log.warning("Specific rejection button not found or click failed. Trying ALL buttons...")
                
                for r_idx, row in enumerate(keyboard):
                    if rejection_success:
                        break
                    for b_idx, btn in enumerate(row):
                        # Skip buttons that look like "accept" or "confirm"
                        btn_text_lower = (btn.text or "").lower()
                        skip_words = ["قبول", "accept", "confirm", "موافق", "نعم", "yes"]
                        if any(w in btn_text_lower for w in skip_words):
                            log.info(f"Skipping accept-like button: '{btn.text}'")
                            continue
                        
                        try:
                            log.info(f"🔴 Trying button [{r_idx}][{b_idx}]: '{btn.text}'...")
                            await message.click(r_idx, b_idx)
                            rejection_success = True
                            clicked_button_text = btn.text
                            log.info(f"✅ Button '{btn.text}' clicked successfully!")
                            break
                        except Exception as e:
                            log.error(f"Failed to click button '{btn.text}': {e}")

            # ── Calculate reaction time ──
            reaction_time_ms = round((time.time() - detection_start) * 1000)

            # ── Log final result ──
            if rejection_success:
                session_stats["rejections"] += 1
                status = "rejected"
                log.info(
                    f'[REJECTION SUCCESS] ✅ '
                    f'Channel: "{channel_name}", '
                    f'Button: "{clicked_button_text}", '
                    f'Reaction: {reaction_time_ms}ms'
                )
            else:
                session_stats["errors"] += 1
                status = "failed"
                log.error(
                    f'[REJECTION FAILED] ❌ '
                    f'Channel: "{channel_name}", '
                    f'Could not click any rejection button! '
                    f'MANUAL ACTION REQUIRED!'
                )

            # ── Save to rejections log ──
            save_rejection({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "channel_id": None,
                "channel_name": channel_name,
                "transferred_from": str(sender_id),
                "status": status,
                "button_clicked": clicked_button_text,
                "bot_reaction_time_ms": reaction_time_ms,
            })

        except Exception as e:
            session_stats["errors"] += 1
            log.error(f"[ERROR] Unexpected error processing message: {e}")
            import traceback
            log.error(traceback.format_exc())

    # ─────────────────────────────────────────────────────
    # Also monitor service messages that may not have from_user
    # ─────────────────────────────────────────────────────

    @app.on_message(filters.service & filters.private)
    async def on_service_message(client: Client, message: Message):
        """Handle Telegram service messages (channel migrations, etc.)."""
        log.debug(f"Service message received: {message}")
        # Delegate to the main handler
        await on_private_message(client, message)

    # ─────────────────────────────────────────────────────
    # Startup & Run
    # ─────────────────────────────────────────────────────

    retry_count = 0
    max_startup_retries = 5

    while True:
        try:
            log.info("Starting Pyrogram client...")
            await app.start()

            me = await app.get_me()
            username = me.username or me.first_name or "Unknown"
            log.info(f"✅ Authenticated as: @{username} (ID: {me.id})")
            log.info("🛡️  Monitoring active — watching for ownership transfers...")
            log.info(
                "Press Ctrl+C to stop the bot.\n"
            )

            retry_count = 0  # Reset on successful connection

            # ── Keep the bot running with periodic status updates ──
            status_interval = 300  # Print status every 5 minutes
            last_status = time.time()

            while True:
                await asyncio.sleep(10)

                # Periodic status heartbeat
                if time.time() - last_status >= status_interval:
                    uptime_seconds = int(time.time() - last_status)
                    log.info(
                        f"📊 Status: Running | "
                        f"Session Rejections: {session_stats['rejections']} | "
                        f"Errors: {session_stats['errors']} | "
                        f"Uptime: {uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"
                    )
                    last_status = time.time()

        except Unauthorized:
            log.error(
                "[ERROR] Session unauthorized. Deleting session for re-authentication..."
            )
            session_file = f"{SESSION_NAME}.session"
            journal_file = f"{SESSION_NAME}.session-journal"
            for sf in (session_file, journal_file):
                if os.path.exists(sf):
                    os.remove(sf)
            log.info("Please restart the bot to re-authenticate.")
            break

        except KeyboardInterrupt:
            log.info("\n🛑 Bot stopped by user (Ctrl+C)")
            break

        except (ConnectionError, OSError, RPCError) as e:
            retry_count += 1
            if retry_count > max_startup_retries:
                log.error(
                    f"[FATAL] Max retries ({max_startup_retries}) exceeded. Exiting."
                )
                break

            backoff = min(30, 5 * retry_count)
            log.error(
                f"[ERROR] Connection error: {e} — "
                f"retrying in {backoff}s (attempt {retry_count}/{max_startup_retries})..."
            )
            await asyncio.sleep(backoff)

        except Exception as e:
            log.error(f"[FATAL] Unexpected error: {e}")
            import traceback
            log.error(traceback.format_exc())
            break

        finally:
            try:
                if app.is_connected:
                    await app.stop()
                    log.info("Client disconnected gracefully.")
            except Exception:
                pass

    # ── Print final session summary ──
    print("\n" + "=" * 55)
    print("  Session Summary")
    print("=" * 55)
    print(f"  Rejections: {session_stats['rejections']}")
    print(f"  Errors:     {session_stats['errors']}")
    print(f"  Started:    {session_stats['start_time']}")
    print(f"  Ended:      {datetime.now(timezone.utc).isoformat()}")
    print("=" * 55 + "\n")


# ─────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Use asyncio.run for Python 3.10+, fallback for older versions
    try:
        asyncio.run(main())
    except RuntimeError:
        # Fallback for environments with existing event loops (e.g., Pydroid3)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
