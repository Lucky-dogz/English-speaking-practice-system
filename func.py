import os, torch
from ffmpy3 import FFmpeg
from speechbrain.pretrained import EncoderDecoderASR
from gramformer import Gramformer
from gtts import gTTS


from speechbrain.pretrained import EncoderDecoderASR
from gramformer import Gramformer
class speechbrain_model:
    print("speechbrain_model loading...")
    asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech", savedir="pretrained_models/asr-crdnn-rnnlm-librispeech")
class gramformer_model:
    print("gramformer_model loading...")
    seed = 1212
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    gf_model = Gramformer(models=1, use_gpu=False)  # 1=corrector, 2=detector

def grammar_recognition(gf, text):
    for influent_sentence in {text}:
        corrected_sentences = gf.correct(
            str(influent_sentence).capitalize(), max_candidates=1
        )
        for corrected_sentence in corrected_sentences:
            return corrected_sentence

def aac2wav(name):
    name = name
    cmd = f"ffmpeg -i {name}.aac -b:v 64k -bufsize 64k {name}.wav"
    os.system(cmd)


def text2audio(text):
    language = "en"
    file = gTTS(text=text, lang=language, slow=False)
    file.save("./static/test.aac")