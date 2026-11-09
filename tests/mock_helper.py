import sys
from unittest.mock import MagicMock

def setup_mocks():
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

    pyro_types = sys.modules["pyrogram.types"]
    def make_dummy_type(name):
        class Dummy:
            text = ""
            callback_data = None
            url = None
            inline_keyboard = []

            def __init__(self, *args, **kwargs):
                self.text = ""
                self.callback_data = None
                self.url = None
                self.inline_keyboard = []
                for k, v in kwargs.items():
                    setattr(self, k, v)
                if args:
                    self._args = args
                    if not self.text and isinstance(args[0], str):
                        self.text = args[0]
                    if not self.inline_keyboard and isinstance(args[0], list):
                        self.inline_keyboard = args[0]
        Dummy.__name__ = name
        return Dummy

    type_names = ["User", "Chat", "Message", "CallbackQuery", "InlineKeyboardButton", "InlineKeyboardMarkup"]
    for t_name in type_names:
        if not hasattr(pyro_types, t_name) or isinstance(getattr(pyro_types, t_name), MagicMock):
            setattr(pyro_types, t_name, make_dummy_type(t_name))

setup_mocks()
