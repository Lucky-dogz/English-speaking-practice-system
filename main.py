from email.mime import audio
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, 
    PostbackEvent,
    TextMessage, 
    AudioMessage,
    TextSendMessage,
    AudioSendMessage,
    TemplateSendMessage,
    MessageAction,
    ConfirmTemplate,
    PostbackAction,
)

from func import aac2wav, text2audio,speechbrain_model,gramformer_model,grammar_recognition
import os
app = Flask(__name__)

line_bot_api = LineBotApi('bnqb6WhZRf8gDmBuDbsyZGpviCyukR/gmXe2x0J2mjjYcu3dwSebqgfrlpMclUskZF89CONQYLRRsRruMj/uFJ4X6L9WHAaa2CteiFsxu3L7lw/A3MtRM4mPqUN24Kl+uD5h8TQO72/5ll+YjMpONgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3f808f7c1457987cc5e99aa8c501b32a')
domain='' #your url

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=AudioMessage)
def handle_message(event):
    if event.message.type == "audio":
        UserSendAudio = line_bot_api.get_message_content(event.message.id)
        with open("a.aac", "wb") as fd:
            for chunk in UserSendAudio.iter_content():
                fd.write(chunk)
        aac2wav('a')
        audio_text = str((speechbrain_model.asr_model.transcribe_file("a.wav")).lower()).capitalize() #max=
        os.remove("a.aac")
        os.remove("a.wav")
        result=[]
        result.append(TextSendMessage(audio_text))
        result.append(TemplateSendMessage(
                            alt_text="Confirm template",
                            template=ConfirmTemplate(
                                text='Speech recognition result',
                                actions=[
                                    PostbackAction(
                                        label="correct", text="correct",data=audio_text,
                                    ),
                                    MessageAction(
                                        label="incorrect", text="incorrect"
                                    ),
                                ],
                            ),
                        ),
                    )
        if (len(audio_text)<=240):
            line_bot_api.reply_message(event.reply_token,result)
        else:
            line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(text='The Line official regulation max-size is 240 characters'),
            )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "Start":
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(
                text="Welcome to chat with you, please use the microphone to say something, Line officially stipulates a maximum of 240 characters, the program running time is 30 seconds, if the waiting time is too long after speaking,please try again"
            ),
        )
    elif event.message.text == "incorrect":
        line_bot_api.reply_message(  # 回復傳入的訊息文字
            event.reply_token,
            TextSendMessage(text="Please listen to the demonstration after written the correct content."),
        )
    else:
        if (isinstance(event, MessageEvent) and (event.message.text !='correct')) :
            text = event.message.text
            text_duratio=len(text)*76
            text2audio(text)
            stream_url = domain+"/static/test.aac"
            line_bot_api.reply_message(event.reply_token,AudioSendMessage(original_content_url=stream_url,duration=text_duratio))

@handler.add(PostbackEvent)
def handle_message(event):
    result=[]
    result.append(TextSendMessage('Grammar recognition result:'))
    result.append(TextSendMessage(grammar_recognition(gramformer_model.gf_model,str(event.postback.data))))
    line_bot_api.reply_message(event.reply_token,result)

if __name__ == "__main__":
    app.run()