import os
import pygame

class FontManager:
    """字体管理器，用于统一管理游戏中的字体"""

    def __init__(self, font_path="assets/fonts/YShiMinchoCL-Regular.ttf"):
        """初始化字体管理器"""
        self.fonts = {}
        self.font_path = font_path if os.path.exists(font_path) else None

    def get_font(self, size, bold=False):
        """获取指定大小的字体"""
        key = f"{size}_{bold}"

        if key not in self.fonts:
            try:
                if self.font_path:
                    font = pygame.font.Font(self.font_path, size)
                    font.set_bold(bold)
                else:
                    font = pygame.font.SysFont("Arial", size, bold=bold)
                # 中文渲染测试
                font.render("测试", True, (0, 0, 0))
                self.fonts[key] = font
            except Exception as e:
                print(f"字体加载失败: {e}")
                self.fonts[key] = pygame.font.Font(None, size)

        return self.fonts[key]


# 创建全局字体管理器实例
font_manager = FontManager()