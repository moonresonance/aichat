import os
import random
import numpy as np
import soundfile as sf
from TTS_infer_pack.TTS import TTS, TTS_Config

# ===== TTS 模型路径配置 =====
version = "v4"
hu_gpt_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/model/v4/胡桃_ZH/胡桃_ZH-e10.ckpt"
hu_sovits_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/model/v4/胡桃_ZH/胡桃_ZH_e10_s860_l32.pth"
fu_sovits_path = "F:\langchain_test_model\LangGraph\gPT_SoVITS\model\\v4\芙宁娜_ZH\芙宁娜_ZH_e10_s950_l32.pth"
fu_gpt_path = "F:\langchain_test_model\LangGraph\gPT_SoVITS\model\\v4\芙宁娜_ZH\芙宁娜_ZH-e10.ckpt"
bert_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large"
base_path = "F:/langchain_test_model/LangGraph/gPT_SoVITS/pretrained_models/chinese-hubert-base"
# ===== 初始化 TTS 配置 =====
tts_config = TTS_Config()
tts_config.update_version("v2ProPlus")
tts_config.t2s_weights_path = fu_gpt_path
tts_config.vits_weights_path = fu_sovits_path
tts_config.bert_base_path = bert_path
tts_config.cnhuhbert_base_path = base_path
tts_pipeline = TTS(tts_config)

# ===== 输出目录 =====
output_dir = "F:/langchain_test_model/LangGraph/gPT_SoVITS/output_audio"
os.makedirs(output_dir, exist_ok=True)
full_wav_path = os.path.join(output_dir, "full_output.wav")

# ===== inference 函数 =====
def inference(
    text, ref_audio_path, aux_ref_audio_paths, prompt_text,
    top_k=5, top_p=1.0, temperature=1.0, batch_size=20, speed_factor=1.0,
    ref_text_free=False, split_bucket=True, fragment_interval=0.3, seed=-1,
    keep_random=True, parallel_infer=True, repetition_penalty=1.35,
    sample_steps=64, super_sampling=True
):
    seed = -1 if keep_random else seed
    actual_seed = seed if seed not in [-1, "", None] else random.randint(0, 2**32 - 1)

    inputs = {
        "text": text,
        "text_lang": "all_zh",
        "ref_audio_path": ref_audio_path,
        "aux_ref_audio_paths": [item.name for item in aux_ref_audio_paths] if aux_ref_audio_paths else [],
        "prompt_text": prompt_text if not ref_text_free else "",
        "prompt_lang": "all_zh",
        "top_k": top_k,
        "top_p": top_p,
        "temperature": temperature,
        "text_split_method": "cut1",
        "batch_size": int(batch_size),
        "speed_factor": float(speed_factor),
        "split_bucket": split_bucket,
        "return_fragment": False,  # 保证完整音频
        "fragment_interval": fragment_interval,
        "seed": actual_seed,
        "parallel_infer": parallel_infer,
        "repetition_penalty": repetition_penalty,
        "sample_steps": int(sample_steps),
        "super_sampling": super_sampling,
    }

    for item in tts_pipeline.run(inputs):
        yield item, actual_seed

# ===== 配置 =====
INFERENCE_CONFIG = {
    "text": "哼哼，我可是伟大的水神，只是水元素充盈而已",
    "ref_audio_path": "F:\langchain_test_model\LangGraph\gPT_SoVITS\model\\v4\芙宁娜_ZH\\reference_audios\中文\emotions\【默认】根据故事走向，前往特定情景吗？听起来挺新颖。所以信封里写了什么？.wav",
    "aux_ref_audio_paths": [],
    "prompt_text": "根据故事走向，前往特定情景吗？听起来挺新颖。所以信封里写了什么？。",
    "top_k": 5,
    "top_p": 1.0,
    "temperature": 1.0,
    "batch_size": 20,
    "speed_factor": 1.0,
    "ref_text_free": False, #是否关闭参考文本
    "split_bucket": True,#并行
    "fragment_interval": 0.3,
    "seed": -1,
    "keep_random": True,
    "parallel_infer": True,
    "repetition_penalty": 1.35,
    "sample_steps": 32,
    "super_sampling": True,
}

# ===== 主程序 =====
if __name__ == "__main__":
    print("开始语音合成推理...")

    final_audio = []
    final_sr = None
    used_seed = None

    try:
        for audio_chunk, seed in inference(**INFERENCE_CONFIG):
            used_seed = seed
            sr, audio_data = audio_chunk
            final_sr = sr
            final_audio.append(audio_data)

        if not final_audio:
            print("没有生成音频，使用空白音频代替")
            final_audio = [np.zeros(int(16000 * 1), dtype=np.int16)]
            final_sr = 16000

        final_audio = np.concatenate(final_audio, axis=0).astype(np.float32)

        # 防爆音归一化
        max_val = np.max(np.abs(final_audio))
        if max_val > 1.0:
            final_audio = final_audio / (max_val + 1e-8)
        final_audio = np.clip(final_audio, -1.0, 1.0)

        # 保存为 WAV
        sf.write(full_wav_path, (final_audio * 32767).astype(np.int16), final_sr)
        print(f"语音合成完成，文件已保存: {full_wav_path}")
        print(f"使用的随机种子: {used_seed}")

    except Exception as e:
        print("语音合成过程中出现异常:", e)
