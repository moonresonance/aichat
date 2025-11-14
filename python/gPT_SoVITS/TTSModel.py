import os
import random
import numpy as np
import soundfile as sf
from TTS_infer_pack.TTS import TTS, TTS_Config


class TTSModel:
    """通用 TTS 模型封装类，可选择不同角色模型"""

    def __init__(self,
                 version="v4",
                 gpt_path=None,
                 sovits_path=None):

        self.version = version
        self.gpt_path = gpt_path
        self.sovits_path = sovits_path
        self.bert_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"
        self.hubert_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/pretrained_models/chinese-hubert-base"

        # ===== 初始化 TTS 配置 =====
        self.tts_config = TTS_Config()
        self.tts_config.update_version("v2ProPlus")
        self.tts_config.t2s_weights_path = gpt_path
        self.tts_config.vits_weights_path = sovits_path
        self.tts_config.bert_base_path = self.bert_path
        self.tts_config.cnhuhbert_base_path = self.hubert_path
        print("模型配置为：")
        print(self.tts_config)
        print("正在初始化模型，请稍等...")
        self.pipeline = TTS(self.tts_config)
        print("模型加载完成！")


    # ----------- 推理内部函数 ----------
    def _infer_once(self, **kwargs):
        seed = kwargs.get("seed", -1)
        keep_random = kwargs.get("keep_random", True)

        # 处理种子
        seed = -1 if keep_random else seed
        actual_seed = seed if seed not in [-1, "", None] else random.randint(0, 2**32 - 1)

        inputs = {
            "text": kwargs.get("text"),
            "text_lang": "all_zh",
            "ref_audio_path": kwargs.get("ref_audio_path"),
            "prompt_text": kwargs.get("prompt_text") if not kwargs.get("ref_text_free", False) else "",
            "prompt_lang": "all_zh",
            "aux_ref_audio_paths": kwargs.get("aux_ref_audio_paths") or [],
            "top_k": kwargs.get("top_k", 5),
            "top_p": kwargs.get("top_p", 1.0),
            "temperature": kwargs.get("temperature", 1.0),
            "text_split_method": "cut1",
            "batch_size": int(kwargs.get("batch_size", 20)),
            "speed_factor": float(kwargs.get("speed_factor", 1.0)),
            "split_bucket": kwargs.get("split_bucket", True),
            "return_fragment": False,
            "fragment_interval": kwargs.get("fragment_interval", 0.3),
            "seed": actual_seed,
            "parallel_infer": kwargs.get("parallel_infer", True),
            "repetition_penalty": kwargs.get("repetition_penalty", 1.35),
            "sample_steps": int(kwargs.get("sample_steps", 32)),
            "super_sampling": kwargs.get("super_sampling", True),
        }

        for item in self.pipeline.run(inputs):
            yield item, actual_seed

    # ----------- 对外暴露的语音合成 API ----------
    def synthesize(self, save_path, **kwargs):
        print("开始语音生成...")

        final_audio = []
        final_sr = None
        used_seed = None

        try:
            for audio_chunk, seed in self._infer_once(**kwargs):
                used_seed = seed
                sr, audio_data = audio_chunk
                final_sr = sr
                final_audio.append(audio_data)

            if not final_audio:
                print("没有生成音频，生成空白音频")
                final_audio = [np.zeros(int(16000), dtype=np.int16)]
                final_sr = 16000

            # 合并音频
            final_audio = np.concatenate(final_audio, axis=0).astype(np.float32)

            # 归一化（防爆音）
            max_val = np.max(np.abs(final_audio))
            if max_val > 1.0:
                final_audio = final_audio / (max_val + 1e-8)
            final_audio = np.clip(final_audio, -1.0, 1.0)

            # 保存
            sf.write(save_path, (final_audio * 32767).astype(np.int16), final_sr)
            print(f"语音合成完成：{save_path}")
            print(f"使用的随机种子: {used_seed}")

        except Exception as e:
            print("语音合成出错:", e)

        return save_path, used_seed


class ModelManager:
    """管理多个模型，可快速切换"""

    def __init__(self):
        self.models = {}
        self.current = None  # 当前模型名

    # 注册模型
    def register(self, name, version, gpt_path, sovits_path, ):
        self.models[name] = TTSModel(
            version, gpt_path, sovits_path
        )
        print(f"【模型注册成功】→ {name}")

    # 选择模型
    def use(self, name):
        if name not in self.models:
            raise ValueError(f"模型 '{name}' 未注册")
        self.current = name
        print(f"【切换模型】→ {name}")

    # 执行推理
    def synthesize(self, save_path, **kwargs):
        if not self.current:
            raise RuntimeError("未选择模型，请先调用 use(name)")

        return self.models[self.current].synthesize(save_path, **kwargs)