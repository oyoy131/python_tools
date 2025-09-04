#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoviePy 2.0+ 精简教学程序
适用于MoviePy 2.0及以上版本
"""

import os
from moviepy import VideoFileClip, AudioFileClip, ImageClip, TextClip, ColorClip
from moviepy import CompositeVideoClip, concatenate_videoclips
import numpy as np


class MoviePy2Tutorial:
    def __init__(self):
        """初始化教学程序"""
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def basic_operations(self, video_path):
        """
        基础操作演示
        MoviePy 2.0+ 主要变化：
        - 分离导入各个组件
        - 改进的编码器支持
        - 更好的错误处理
        """
        print("=== 基础操作 ===")

        # 1. 加载和基本信息
        video = VideoFileClip(video_path)
        print(f"时长: {video.duration:.2f}s, 尺寸: {video.size}, 帧率: {video.fps}")

        # 2. 时间和尺寸处理
        processed = (video
                     .subclipped(0, 10)  # 截取前10秒
                     .resized(height=480)  # 调整高度为480p
                     .with_fps(30))  # 设置30fps

        # 3. 保存 - MoviePy 2.0+ 改进的写入方法
        output = os.path.join(self.output_dir, "basic.mp4")
        processed.write_videofile(output, logger=None)  # logger=None 减少输出

        video.close()
        processed.close()
        print(f"保存至: {output}")

    def audio_and_text(self, video_path):
        """
        音频和文字处理
        """
        print("\n=== 音频文字处理 ===")

        video = VideoFileClip(video_path).subclipped(0, 8)

        # 1. 音频处理 - MoviePy 2.0+ 语法
        if video.audio:
            # 音量调节和淡化
            audio = video.audio.with_volume_scaled(0.7).with_fadein(1).with_fadeout(1)
            video = video.with_audio(audio)

        # 2. 添加文字 - 改进的TextClip
        title = (TextClip("MoviePy 2.0 演示", font_size=50, color='white')
                 .with_duration(3)
                 .with_position('center')
                 .with_fadein(0.5))

        # 3. 视频合成
        final = CompositeVideoClip([video, title])

        # 4. 保存
        output = os.path.join(self.output_dir, "audio_text.mp4")
        final.write_videofile(output, logger=None)

        video.close()
        final.close()
        print(f"保存至: {output}")

    def effects_and_transitions(self):
        """
        特效和过渡演示
        """
        print("\n=== 特效过渡 ===")

        # 1. 创建彩色背景片段
        colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        clips = []

        for i, color in enumerate(colors):
            # ColorClip创建纯色背景
            bg = ColorClip(size=(640, 360), color=color, duration=3)

            # 添加标签文字
            text = (TextClip(f"片段 {i + 1}", font_size=40, color='white')
                    .with_duration(3)
                    .with_position('center'))

            # 合成并添加过渡效果
            clip = CompositeVideoClip([bg, text]).with_fadein(0.5).with_fadeout(0.5)
            clips.append(clip)

        # 2. 拼接视频
        final = concatenate_videoclips(clips)

        # 3. 保存
        output = os.path.join(self.output_dir, "transitions.mp4")
        final.write_videofile(output, logger=None)

        final.close()
        print(f"保存至: {output}")

    def create_gif_animation(self):
        """
        创建GIF动画
        """
        print("\n=== GIF动画 ===")

        # 1. 创建动画函数
        def make_frame(t):
            """生成动画帧"""
            # 创建渐变背景
            img = np.zeros((200, 300, 3), dtype=np.uint8)

            # 移动的圆形
            center_x = int(150 + 100 * np.sin(t * 2))
            center_y = int(100 + 50 * np.cos(t * 3))

            # 绘制圆形区域
            Y, X = np.ogrid[:200, :300]
            mask = (X - center_x) ** 2 + (Y - center_y) ** 2 <= 25 ** 2
            img[mask] = [255, 200, 0]  # 黄色圆形

            return img

        # 2. 创建动画剪辑
        from moviepy import VideoClip
        animation = VideoClip(make_frame, duration=4)

        # 3. 保存为GIF
        gif_output = os.path.join(self.output_dir, "animation.gif")
        animation.write_gif(gif_output, fps=15)

        animation.close()
        print(f"GIF保存至: {gif_output}")

    def run_tutorial(self, input_video=None):
        """
        运行教学程序
        """
        print("MoviePy 2.0+ 精简教学开始")
        print("=" * 40)

        # 如果没有输入视频，创建演示视频
        if not input_video or not os.path.exists(input_video):
            demo_path = self.create_demo_video()
            input_video = demo_path

        # 运行各个演示
        self.basic_operations(input_video)
        self.audio_and_text(input_video)
        self.effects_and_transitions()
        self.create_gif_animation()

        print("\n" + "=" * 40)
        print("教学完成！主要学习点：")
        print("• VideoFileClip: 视频加载")
        print("• subclipped/resized/with_fps: 基础处理")
        print("• TextClip: 文字添加")
        print("• CompositeVideoClip: 合成")
        print("• concatenate_videoclips: 拼接")
        print("• write_videofile/write_gif: 输出")

    def create_demo_video(self):
        """创建简单的演示视频"""
        # 创建渐变背景
        bg = ColorClip(size=(640, 360), color=(50, 50, 100), duration=10)

        # 添加标题
        title = (TextClip("MoviePy 2.0 Demo", font_size=48, color='white')
                 .with_duration(10)
                 .with_position('center'))

        # 合成和保存
        demo = CompositeVideoClip([bg, title])
        demo_path = os.path.join(self.output_dir, "demo.mp4")
        demo.write_videofile(demo_path, logger=None)

        demo.close()
        return demo_path


# 快速使用示例
def quick_examples():
    """MoviePy 2.0+ 快速使用示例"""
    print("\n=== 快速示例 ===")

    # 基础处理链式操作
    example_code = '''
# 链式操作示例
video = (VideoFileClip("input.mp4")
         .subclipped(0, 30)
         .resized(height=720)
         .with_fps(30)
         .with_fadein(1)
         .with_fadeout(1))

# 文字合成
title = TextClip("标题", font_size=50).with_duration(5).with_position('center')
final = CompositeVideoClip([video, title])
final.write_videofile("output.mp4")
    '''
    print("链式操作使代码更简洁清晰")


if __name__ == "__main__":
    # 运行教学
    tutorial = MoviePy2Tutorial()
    tutorial.run_tutorial()

    # 显示语法变化
    quick_examples()