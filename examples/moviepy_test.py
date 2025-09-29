import numpy
import threading
from moviepy import (
    VideoClip,
    VideoFileClip,
    ImageSequenceClip,
    ImageClip,
    TextClip,
    ColorClip,
    AudioFileClip,
    AudioClip, CompositeVideoClip,
)
import numpy as np
from typing import List
from pathlib import Path
from moviepy import vfx, afx
import math

from numpy import float128

VIDEO_FILE_DIR = Path("../resource/videos").resolve()
AUDIO_FILE_DIR = Path("../resource/audios").resolve()
IMG_FILE_DIR = Path("../resource/img").resolve()
FONT_FILE_DIR = Path(__file__).parents[1] / 'resource' / 'fonts'
SONG_FILE_DIR = Path(__file__).parents[1] / 'resource' / 'songs'

video_path = VIDEO_FILE_DIR / 'final-1.mp4'
audio_path = AUDIO_FILE_DIR / '0315-1.mp3'
img_path = IMG_FILE_DIR / 'file_1.jpg'
font_path = FONT_FILE_DIR / 'Roboto-Light.ttf'
output = VIDEO_FILE_DIR / "output.mp4"
output_gif = VIDEO_FILE_DIR / "output.gif"

def clip_preview(video_clip: VideoFileClip = None, audio_clip: AudioFileClip = None):
    """使用多线程同时预览不同的clip"""
    def play_video():
        if video_clip:
            video_clip.preview()

    def play_audio():
        if audio_clip:
            audio_clip.audiopreview()

    # 创建线程来异步执行视频和音频播放
    if video_clip and audio_clip:
        video_thread = threading.Thread(target=play_video)
        audio_thread = threading.Thread(target=play_audio)
        video_thread.start()
        audio_thread.start()
        video_thread.join()  # 等待视频播放完成
        audio_thread.join()  # 等待音频播放完成
    elif video_clip:
        play_video()
    elif audio_clip:
        play_audio()
    else:
        print("error")

def timing_t(clip:VideoFileClip):
    """
    Modify only the timing of a Clip
    - 必需提供 keep_duration 否则会报错，虽然官网上面说不需要设置
    - 对视频进行速度控制，加速后的 keep_duration 应该小于等于（原视频 / 倍数），
    - 减速则可以提高 keep_duration
    - 否则会出现警告，并且超过这个时长的视频会卡到最后一帧
    """
    # 视频提速
    modified_clip1 = clip.time_transform(lambda t: t * 3, keep_duration=5)
    # 视频曲线变速
    modified_clip2 = clip.time_transform(lambda t: 1 + math.sin(t),keep_duration=20)

    return modified_clip1

def video_clip_info(clip:VideoFileClip):
    """显示视频 clip 的基本信息"""
    print("="*10+"VideoInformation"+"="*10)
    print(f"filename:{clip.filename}\n"
          f"duration:{clip.duration}\n"
          f"fps:{clip.fps}\n"
          f"size:{clip.size}\n"
          f"strat:{clip.start}\n"
          f"end:{clip.end}\n"
          f"audio:{clip.audio}\n"
          f"audio_fps:{clip.audio.fps}") # use chain to get audio parameters

def audio_clip_info(clip:AudioFileClip):
    """显示音频 clip 的基本信息"""
    print("="*10+"AudioInformation"+"="*10)
    print(f"audio:{clip}\n"
          f"audio_duration:{clip.duration}\n"
          f"audio_fps:{clip.fps}\n"
          f"audio_buffersize:{clip.buffersize}")

def img_clip_info(clip:ImageClip):
    """显示图片 clip 的基本信息"""
    print("="*10+"ImageInformation"+"="*10)
    print(f"size:{clip.size}\n"
          f"img_array:{clip.img}")

def video_clip(clip:VideoFileClip) -> VideoFileClip:
    """对视频进行处理"""
    clip = (clip
            .subclipped(0,5)
            .resized(height=720)
            .with_fps(30))
    return clip

def audio_clip(clip:AudioFileClip) -> AudioFileClip:
    """对音频进行处理"""
    pass

def text_clip(clip:TextClip) -> TextClip:
    """对文本进行处理"""
    clip.with_position(("center","center"))
    return clip

# load clips
my_video_clip = VideoFileClip(video_path)
my_audio_clip = AudioFileClip(audio_path)
my_img_clip = ImageClip(img_path)
my_txt_clip = TextClip(
    font_path,
    text="The Text of Clip",
    font_size=50,
    color="#fff",
    text_align="center",
    duration=3,
)

# 打印 clip 的基本信息
# video_clip_info(my_video_clip)
# audio_clip_info(my_audio_clip)
# img_clip_info(my_img_clip)

# 合成最终 clip
final_clip = CompositeVideoClip([video_clip(my_video_clip),
                                 text_clip(my_txt_clip)],
                                )

# 预览和保存 clip
clip_preview(final_clip)
# final_clip.write_videofile(output)
# final_clip.write_gif(output_gif, fps=10)
# final_clip.write_images_sequence("./%04d.jpg", fps=1)


# 一些练习时发现的错误
def error_1():
    """
    error:
        使用了 Path 类后就不支持使用“%”了
        TypeError: unsupported operand type(s) for %: 'WindowsPath' and 'int'
    solution:
        只能使用 os.path 或者是字符串路径
    """
    my_video_clip.write_images_sequence(IMG_FILE_DIR / "%04d.jpg", fps=1)
def error_2():
    """
    error:
        使用了 CompositeVideoClip() 得到的 clip 无法直接转为 JPEG 格式
        OSError: cannot write mode RGBA as JPEG
    solution:
        RGBA 模式是指图像有 红色(R)、绿色(G)、蓝色(B) 和 透明度(A) 通道。每个像素都包含这四个通道的信息。
        JPEG 格式只支持 RGB 模式，即没有透明度通道。如果你尝试将 RGBA 模式的图像保存为 JPEG 格式，就会触发这个错误。
    """
    final_clip = CompositeVideoClip([video_clip(my_video_clip),
                                     text_clip(my_txt_clip)],
                                    )
    final_clip.write_images_sequence("./%04d.jpg", fps=1)














