import os
import pygame
from utils.font_manager import font_manager 

def get_font_path(font_name):
    """
    获取字体文件的路径
    
    Args:
        font_name: 字体文件名（不含路径）
        
    Returns:
        字体文件的完整路径
    """
    # 字体文件夹路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    font_dir = os.path.join(base_dir, 'assets', 'fonts')
    
    # 返回字体文件的完整路径
    return os.path.join(font_dir, font_name)

def load_system_font(font_names, size, bold=False):
    """
    尝试加载系统字体
    
    Args:
        font_names: 字体名称列表
        size: 字体大小
        bold: 是否粗体
        
    Returns:
        pygame.font.Font对象，如果加载失败则返回None
    """
    try:
        font = pygame.font.SysFont(font_names, size, bold=bold)
        # 测试字体是否能正确渲染中文
        test_text = font.render("测试", True, (0, 0, 0))
        return font
    except:
        return None