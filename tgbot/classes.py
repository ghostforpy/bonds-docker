
class UserFrom:
    def __init__(self,
                 id: int,
                 is_bot: bool,
                 first_name: str,
                 language_code: str = None,
                 * args, **kwargs):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.language_code = language_code


class Chat:
    def __init__(self,
                 id: int,
                 first_name: str,
                 type_chat: str,
                 *args, **kwargs):
        self.id = id
        self.first_name = first_name
        self.type = type_chat


class Document:
    def __init__(self,
                 file_name: str,
                 mime_type: str,
                 file_id: str,
                 file_unique_id: str,
                 file_size: int,
                 *args, **kwargs):
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_size = file_size


class Audio:
    def __init__(self,
                 duration: int,
                 file_name: str,
                 mime_type: str,
                 file_id: str,
                 file_unique_id: str,
                 file_size: int,

                 *args, **kwargs):
        self.duration = duration
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_size = file_size


class Message:
    def __init__(self,
                 message_id: int = None,
                 text: str = None,
                 user_from: UserFrom = None,
                 chat: Chat = None,
                 document: Document = None,
                 audio: Audio = None,
                 caption: str = None,
                 *args, **kwargs):
        self.message_id = message_id
        self.caption = caption
        self.user_from = UserFrom(**kwargs['from'])
        if chat:
            chat['type_chat'] = chat.pop('type')
            self.chat = Chat(**chat)
        else:
            self.chat = chat
        if document:
            self.document = Document(**document)
        else:
            self.document = document
        self.text = text
        if audio:
            self.audio = Audio(**audio)
        else:
            self.audio = audio

    def __str__(self):
        if self.document:
            content = 'document'
        elif self.text:
            content = 'text'
        elif self.audio:
            content = 'audio'
        else:
            content = 'unknown content'
        return 'Message with {}'.format(content)


class CallbackQuery:
    def __init__(self,
                 id: int,
                 user_from: UserFrom = None,
                 message: Message = None,
                 inline_message_id: str = None,
                 chat_instance: str = None,
                 data: str = None,
                 *args, **kwargs):
        self.id = id
        self.user_from = UserFrom(**kwargs['from'])
        if message:
            self.message = Message(**message)
        else:
            self.message = None
        self.inline_message_id = inline_message_id
        self.chat_instance = chat_instance
        self.data = data


class InlineQuery:
    def __init__(self,
                 id: int,
                 user_from: UserFrom = None,
                 query: str = None,
                 offset: str = None,
                 chat_type: str = None,
                 *args, **kwargs):
        self.id = id
        self.user_from = UserFrom(**kwargs['from'])
        self.query = query
        self.offset = offset
        self.chat_type = chat_type
