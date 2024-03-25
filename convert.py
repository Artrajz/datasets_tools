import glob
import os
from concurrent.futures import ProcessPoolExecutor

import ffmpeg
from tqdm import tqdm

AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.m4a', '.ogg', '.mp4']
TARGET_FORMAT = '.wav'


def is_audio_file(filepath):
    # 检查文件是否为音频文件
    return os.path.splitext(filepath)[1].lower() in AUDIO_EXTENSIONS

def process_audio(input_path, output_dir, input_base_path, output_sample_rate=44100, output_channel=1):
    # 保留目录结构
    rel_path = os.path.relpath(input_path, start=input_base_path)
    output_path = os.path.join(output_dir, rel_path)

    output_file_path = os.path.splitext(output_path)[0] + TARGET_FORMAT

    ffmpeg.input(input_path).output(output_file_path, ar=output_sample_rate, ac=output_channel).global_args(
        '-loglevel', 'error').global_args(
        '-y').run()


def convert(input_path, output_path=None, target_sample_rate=44100, output_channel=1, max_processes=os.cpu_count()):
    # 如果没有指定输出路径，则使用默认名称
    if output_path is None:
        output_path = f"{input_path}_processed"

    input_path = os.path.normpath(input_path)
    output_path = os.path.normpath(output_path)
    if input_path == output_path:
        print("warning: input_path same as outputpath!")

    os.makedirs(output_path, exist_ok=True)

    # 在子目录中搜索所有音频文件
    audio_files = glob.glob(os.path.join(input_path, "**", "*.*"), recursive=True)
    audio_files = [f for f in audio_files if is_audio_file(f)]

    len_audio_files = len(audio_files)

    # 多进程
    with ProcessPoolExecutor(max_processes) as executor:
        list(tqdm(
            executor.map(process_audio, audio_files, [output_path] * len_audio_files, [input_path] * len_audio_files,
                         [target_sample_rate] * len_audio_files, [output_channel] * len_audio_files),
            total=len_audio_files))

    return output_path


if __name__ == '__main__':
    output_path = convert(r"J:\datasets\genshin\paimon", output_path=r"J:\datasets\genshin\paimon_mew",
                          target_sample_rate=44100, output_channel=1)
    print(output_path)
