import torchaudio
import os
import tempfile
import uuid
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
import re
import io

video_extensions = ['webm', 'mp4', 'mkv', 'gif', 'mov']


class DamoASRNode:
    def __init__(self):
        self.loadmodel = None
        self.wave_file_name = None
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sample_audio": ("AUDIO",),
                "model_name": ("STRING", {"default": "iic/SenseVoiceSmall", "display_name": "模型名称"}),
                "vad_model": ("STRING", {"default": "fsmn-vad", "display_name": "VAD模型"}),
                "vad_max_time": ("INT", {"default": 30000, "display_name": "最大分段时长(ms)"}),
                "language": (["auto", "zh", "en", "yue", "ja", "ko"], {"default": "auto", "display_name": "语言"}),
                "use_itn": (["enable", "disable"], {"default": "enable", "display_name": "ITN处理"}),
                "batch_size_s": ("INT", {"default": 60, "display_name": "批处理时长(s)"}),
                "merge_vad": (["enable", "disable"], {"default": "enable", "display_name": "合并VAD"}),
                "merge_length_s": ("INT", {"default": 15, "display_name": "合并时长(s)"})
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "execute"
    CATEGORY = "audio"

    def load_voice_from_input(self, sample_audio):
        wave_file = tempfile.NamedTemporaryFile(
            suffix=".wav", delete=False
        )
        self.wave_file_name = wave_file.name
        wave_file.close()

        hasAudio = False
        for (batch_number, waveform) in enumerate(
                sample_audio["waveform"].cpu()
        ):
            buff = io.BytesIO()
            torchaudio.save(
                buff, waveform, sample_audio["sample_rate"], format="WAV"
            )
            with open(self.wave_file_name, 'wb') as f:
                f.write(buff.getbuffer())
            hasAudio = True
            break
        if not hasAudio:
            raise FileNotFoundError("No audio input")
        return self.wave_file_name

    def remove_wave_file(self):
        if self.wave_file_name is not None:
            try:
                os.unlink(self.wave_file_name)
                self.wave_file_name = None
            except Exception as e:
                print("Cannot remove? " + self.wave_file_name)
                print(e)

    def execute(self, sample_audio, model_name, vad_model, vad_max_time, language, use_itn, batch_size_s, merge_vad,
                merge_length_s):
        model_path = os.path.dirname(__file__)
        os.makedirs(model_path, exist_ok=True)
        audio_path = self.load_voice_from_input(sample_audio)
        os.environ["MODELSCOPE_CACHE"] = model_path

        if self.loadmodel is None or self.current_model_name != model_name:
            self.loadmodel = None
            self.current_model_name = model_name
            self.loadmodel = AutoModel(
                model=model_name,
                vad_model=vad_model,
                vad_kwargs={"max_single_segment_time": vad_max_time},
                trust_remote_code=True,
                remote_code=os.path.join(os.path.dirname(__file__), "model.py")
            )

        res = self.loadmodel.generate(
            input=audio_path,
            cache={},
            language=language,
            use_itn=(use_itn == "enable"),
            batch_size_s=batch_size_s,
            merge_vad=(merge_vad == "enable"),
            merge_length_s=merge_length_s,
        )

        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception as e:
                print(f"删除临时文件失败：{str(e)}")

        # 执行语音识别
        # text = rich_transcription_postprocess(res[0]["text"])
        text = re.sub(r'<\|.*?\|>', '', res[0]["text"])
        return (text,)


NODE_CLASS_MAPPINGS = {"DamoASRNode": DamoASRNode}
NODE_DISPLAY_NAME_MAPPINGS = {"DamoASRNode": "达摩语音转文字"}
