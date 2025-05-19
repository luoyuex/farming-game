import pygame
import os

class AudioManager:
    """音频管理器，负责加载和播放游戏中的音效和背景音乐"""
    
    def __init__(self):
        """初始化音频管理器"""
        # 确保pygame的mixer模块已初始化
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # 音效字典
        self.sounds = {}
        
        # 背景音乐
        self.background_music = None
        
        # 音量设置
        self.music_volume = 0.5  # 背景音乐音量 (0.0 到 1.0)
        self.sound_volume = 0.7  # 音效音量 (0.0 到 1.0)
        
        # 静音状态
        self.muted = False
        
        # 加载所有音效
        self.load_sounds()
    
    def load_sounds(self):
        """加载所有音效文件"""
        sounds_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sounds')
        
        # 加载音效文件
        sound_files = {
            'hoe': 'hoe.wav',
            'water': 'water.mp3',
            'axe': 'axe.mp3',
            'plant': 'plant.wav',
            'success': 'success.wav'
        }
        
        for sound_name, file_name in sound_files.items():
            sound_path = os.path.join(sounds_dir, file_name)
            if os.path.exists(sound_path):
                try:
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name].set_volume(self.sound_volume)
                except Exception as e:
                    print(f"无法加载音效 {sound_name}: {e}")
        
        # 加载背景音乐
        music_path = os.path.join(sounds_dir, 'music.mp3')
        if os.path.exists(music_path):
            self.background_music = music_path
    
    def play_sound(self, sound_name):
        """播放指定的音效
        
        Args:
            sound_name: 音效名称
        """
        if self.muted or sound_name not in self.sounds:
            return
        
        try:
            self.sounds[sound_name].play()
        except Exception as e:
            print(f"播放音效 {sound_name} 时出错: {e}")
    
    def play_music(self):
        """播放背景音乐"""
        if self.muted or not self.background_music:
            return
        
        try:
            pygame.mixer.music.load(self.background_music)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1表示循环播放
        except Exception as e:
            print(f"播放背景音乐时出错: {e}")
    
    def stop_music(self):
        """停止背景音乐"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """设置背景音乐音量
        
        Args:
            volume: 音量值 (0.0 到 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume):
        """设置音效音量
        
        Args:
            volume: 音量值 (0.0 到 1.0)
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def toggle_mute(self):
        """切换静音状态"""
        self.muted = not self.muted
        
        if self.muted:
            pygame.mixer.music.set_volume(0.0)
            for sound in self.sounds.values():
                sound.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            for sound in self.sounds.values():
                sound.set_volume(self.sound_volume)
        
        return self.muted

# 创建全局音频管理器实例
audio_manager = AudioManager()