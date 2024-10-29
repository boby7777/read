import asyncio
import edge_tts
import pygame
import os
import time
import re
from typing import List

class OfflineTextToSpeech:
    def __init__(self):
        self.available_voices = []
        # 初始化可用的語音列表
        asyncio.run(self.init_voices())
        
        # 默認設置
        self.voice = "zh-TW-HsiaoChenNeural"  # 默認使用台灣中文女聲
        self.rate = "+0%"                      # 正常語速
        self.volume = "+0%"                    # 正常音量

    async def init_voices(self):
        """初始化並獲取所有可用的語音"""
        self.available_voices = await edge_tts.list_voices()
        
    def list_voices(self):
        """列出所有可用的語音"""
        print("\n中文可用的語音：")
        for i, voice in enumerate(self.available_voices):
            name = voice.get('Name', 'Unknown')
            gender = voice.get('Gender', 'Unknown')
            language = voice.get('Locale', 'Unknown')
            if 'zh-' in language:
                print(f"{i}: {voice['ShortName']} - {name}")
                print(f"   語言: {language}, 性別: {gender}")

    def set_voice(self, voice_index: int):
        """設置語音"""
        if 0 <= voice_index < len(self.available_voices):
            self.voice = self.available_voices[voice_index]["ShortName"]
            name = self.available_voices[voice_index].get('Name', 'Unknown')
            print(f"已設置語音為: {name}")
        else:
            print("無效的語音索引")

    def set_rate(self, rate: int):
        """設置語速（-50 到 50）"""
        # 確保 rate 在有效範圍內
        rate = max(-50, min(50, rate))
        self.rate = f"{rate:+d}%"
        print(f"語速設置為: {self.rate}")

    def set_volume(self, volume: int):
        """設置音量（-50 到 50）"""
        # 確保 volume 在有效範圍內
        volume = max(-50, min(50, volume))
        self.volume = f"{volume:+d}%"
        print(f"音量設置為: {self.volume}")

    def split_text(self, text: str, max_chars: int = 1000) -> List[str]:
        """將文字分段，並移除 ## 和 ** 標記"""
        # 移除 #, ##, * 和 ** 標記
        cleaned_text = re.sub(r'# |\* |##|\*\*', '', text)

        segments = []
        current_segment = ""
        sentence_endings = '.!?。！？'
        i = 0
        
        while i < len(cleaned_text):
            char = cleaned_text[i]
            current_segment += char

            # 檢查 \n\n 是否出現並分段
            if current_segment.endswith("\n\n"):
                segments.append(current_segment.strip())
                current_segment = ""

            # 檢查字數限制和句尾標點符號
            elif len(current_segment) >= max_chars and char in sentence_endings:
                segments.append(current_segment.strip())
                current_segment = ""

            i += 1
        
        # 添加最後一段
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments



    async def _speak_segment(self, text: str, output_file: str):
        """轉換單個文字段落為語音"""
        communicate = edge_tts.Communicate(
            text=text,
            voice=self.voice,
            rate=self.rate,
            volume=self.volume
        )
        await communicate.save(output_file)

    def play_audio(self, file_path: str):
        """播放音頻文件"""
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()

    def read_file(self, filename: str):
        """讀取並朗讀文件內容"""
        try:
            # 創建臨時目錄
            temp_dir = "temp_audio"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # 讀取文件
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # 分段處理
            segments = self.split_text(text)
            
            # 處理每個段落
            for i, segment in enumerate(segments, 1):
                print(f"\n處理第 {i}/{len(segments)} 段...")
                print(f"內容預覽: {segment[:50]}...")
                
                # 臨時音頻文件路徑
                temp_file = os.path.join(temp_dir, f"segment_{i}.mp3")
                
                # 轉換文字為語音
                asyncio.run(self._speak_segment(segment, temp_file))
                
                # 播放語音
                print(f"播放第 {i} 段...")
                self.play_audio(temp_file)
            
            # 清理臨時文件
            print("\n清理臨時文件...")
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)
            
            print("播放完畢！")
            
        except FileNotFoundError:
            print(f"找不到文件: {filename}")
        except Exception as e:
            print(f"發生錯誤: {str(e)}")
            # 確保清理臨時文件
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    os.remove(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)

    def print_voice_info(self):
        """打印當前語音設置信息"""
        print("\n當前語音設置：")
        print(f"語音: {self.voice}")
        print(f"語速: {self.rate}")
        print(f"音量: {self.volume}")

if __name__ == "__main__":
    # 創建 TTS 物件
    tts = OfflineTextToSpeech()
    
    # 列出所有可用語音
    tts.list_voices()
    
    # 設置參數
    voice = input("請輸入語音項目：") or "55"
    tts.set_voice(int(voice))
    rate = input("請輸入語速 (0 正常 100 快速 -100 慢速)：") or "0"
    tts.set_rate(int(rate))
    volume = input("請輸入音量 (0 正常 100 最大 -100 最小)：") or "0"
    tts.set_volume(int(volume))
    
    # 顯示當前設置
    tts.print_voice_info()
    
    # 讀取文件
    tts.read_file("test.txt")