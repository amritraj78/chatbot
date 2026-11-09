# tests package
import sys
from unittest.mock import MagicMock

MOCK_MODULES = [
    "dotenv", "pymongo", "motor", "motor.motor_asyncio",
    "pyrogram", "pyrogram.enums", "pyrogram.types",
    "pyrogram.errors", "pyrogram.errors.exceptions",
    "pyrogram.errors.exceptions.bad_request_400",
    "uvloop", "Abg", "flask", "speedtest", "psutil",
    "requests", "requests.adapters",
    "urllib3", "urllib3.util", "urllib3.util.retry"
]

for mod_name in MOCK_MODULES:
    if mod_name not in sys.modules:
        m = MagicMock()
        m.on_message = MagicMock(return_value=lambda f: f)
        m.on_callback_query = MagicMock(return_value=lambda f: f)
        sys.modules[mod_name] = m

# Configure pyrogram enums mock defaults
pyro_enums = sys.modules["pyrogram.enums"]
if not hasattr(pyro_enums, "ChatType") or isinstance(pyro_enums.ChatType, MagicMock):
    class MockChatType:
        SUPERGROUP = "supergroup"
        GROUP = "group"
        PRIVATE = "private"
        CHANNEL = "channel"
    pyro_enums.ChatType = MockChatType

if not hasattr(pyro_enums, "ChatMemberStatus") or isinstance(pyro_enums.ChatMemberStatus, MagicMock):
    class MockChatMemberStatus:
        OWNER = "owner"
        ADMINISTRATOR = "administrator"
        MEMBER = "member"
    pyro_enums.ChatMemberStatus = MockChatMemberStatus

if not hasattr(pyro_enums, "ChatAction") or isinstance(pyro_enums.ChatAction, MagicMock):
    class MockChatAction:
        TYPING = "typing"
    pyro_enums.ChatAction = MockChatAction

if not hasattr(pyro_enums, "MessageEntityType") or isinstance(pyro_enums.MessageEntityType, MagicMock):
    class MockMessageEntityType:
        MENTION = "mention"
        TEXT_MENTION = "text_mention"
    pyro_enums.MessageEntityType = MockMessageEntityType
