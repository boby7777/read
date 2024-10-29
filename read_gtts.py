import pyttsx3
import pygame
import time
import os
from gtts import gTTS

class TextToSpeech:
    def __init__(self):
        # 初始化 pyttsx3 引擎
        self.engine = pyttsx3.init()
        
        # 獲取可用的聲音
        self.voices = self.engine.getProperty('voices')
        
        # 預設設定
        self.rate = 150    # 語速 (默認 150)
        self.volume = 1.0  # 音量 (0.0 到 1.0)
        self.voice_id = 0  # 聲音ID
        
        # 設定默認值
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)
        if self.voices:  # 如果有可用的聲音
            self.engine.setProperty('voice', self.voices[self.voice_id].id)

    def list_available_voices(self):
        """列出所有可用的聲音"""
        print("\n可用的聲音：")
        for i, voice in enumerate(self.voices):
            print(f"{i}: {voice.name} ({voice.id}) - {voice.languages}")

    def set_voice(self, voice_id):
        """設定聲音"""
        if 0 <= voice_id < len(self.voices):
            self.voice_id = voice_id
            self.engine.setProperty('voice', self.voices[voice_id].id)
            print(f"已設定聲音為: {self.voices[voice_id].name}")
        else:
            print("無效的聲音ID")

    def set_rate(self, rate):
        """設定語速 (通常在 50-300 之間)"""
        self.rate = rate
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        """設定音量 (0.0-1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self.engine.setProperty('volume', self.volume)

    def split_text(self, text, max_chars=1000):
        """將文字分段"""
        segments = []
        current_segment = ""
        sentence_endings = '.!?。！？'
        
        for char in text:
            current_segment += char
            if len(current_segment) >= max_chars and char in sentence_endings:
                segments.append(current_segment.strip())
                current_segment = ""
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments

    def read_text_pyttsx3(self, text):
        """使用 pyttsx3 讀取文字"""
        self.engine.say(text)
        self.engine.runAndWait()

    def read_text_gtts(self, text, lang='zh-tw'):
        """使用 gTTS 讀取文字"""
        temp_file = 'temp.mp3'
        tts = gTTS(text=text, lang=lang)
        tts.save(temp_file)
        
        # 使用 pygame 播放
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            
        pygame.mixer.quit()
        os.remove(temp_file)

    def read_file(self, filename, use_gtts=False, lang='zh-tw'):
        """讀取檔案並轉換為語音"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read()

            segments = self.split_text(text)
            
            for i, segment in enumerate(segments, 1):
                print(f"\n處理第 {i}/{len(segments)} 段...")
                print(f"內容預覽: {segment[:50]}...")
                
                if use_gtts:
                    self.read_text_gtts(segment, lang)
                else:
                    self.read_text_pyttsx3(segment)
                    
            print("\n全部播放完成！")
            
        except FileNotFoundError:
            print(f"找不到檔案: {filename}")
        except Exception as e:
            print(f"發生錯誤: {str(e)}")

if __name__ == "__main__":
    # 建立 TTS 物件
    tts = TextToSpeech()
    
    # 顯示可用的聲音
    tts.list_available_voices()
    
    # 設定參數範例
    tts.set_rate(150)      # 設定語速
    tts.set_volume(0.8)    # 設定音量
    tts.set_voice(0)       # 設定聲音
    
    # 讀取檔案
    # 使用 pyttsx3 引擎
    # tts.read_file('test.txt', use_gtts=False)
    
    # 或使用 Google TTS
    tts.read_file('test.txt', use_gtts=True, lang='zh-tw')