import pygame
import os
import io
import cairosvg

class ImageManager:
    """图像管理器，负责加载和缓存游戏中使用的图像资源"""
    
    def __init__(self):
        """初始化图像管理器"""
        self.images = {}
        self.sprites = {}
        self.base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')
    
    def load_image(self, category, name):
        """加载单个图像
        
        Args:
            category: 图像类别（如 'tools', 'crops', 'player'）
            name: 图像名称
            
        Returns:
            加载的图像对象
        """
        key = f"{category}/{name}"
        if key not in self.images:
            try:
                image_path = os.path.join(self.base_path, category, f"{name}.png")
                self.images[key] = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                print(f"无法加载图像 {image_path}: {e}")
                # 创建一个占位符图像（彩色矩形）
                placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
                if category == 'tools':
                    if name == '锄头':
                        color = (139, 69, 19)  # 棕色
                    elif name == '水壶':
                        color = (0, 0, 255)    # 蓝色
                    elif name == '镰刀':
                        color = (255, 215, 0)  # 金色
                    else:
                        color = (150, 150, 150)  # 灰色
                elif category == 'crops':
                    color = (0, 255, 0)  # 绿色
                else:
                    color = (200, 200, 200)  # 浅灰色
                
                placeholder.fill(color)
                self.images[key] = placeholder
        
        return self.images[key]
    
    def load_player_sprite(self, direction):
        """加载玩家精灵图
        
        Args:
            direction: 方向（'down', 'up', 'left', 'right'）
            
        Returns:
            玩家精灵图
        """
        key = f"player/{direction}"
        if key not in self.sprites:
            try:
                image_path = os.path.join(self.base_path, 'player', f"{direction}.png")
                self.sprites[key] = pygame.image.load(image_path).convert_alpha()
            except pygame.error as e:
                print(f"无法加载玩家精灵图 {image_path}: {e}")
                # 创建一个占位符图像（红色矩形）
                placeholder = pygame.Surface((32, 48), pygame.SRCALPHA)
                placeholder.fill((255, 0, 0))
                self.sprites[key] = placeholder
        
        return self.sprites[key]
    
    def load_crop_stages(self, crop_name, stages=4):
        """加载作物的不同生长阶段图像
        
        Args:
            crop_name: 作物名称
            stages: 生长阶段数量
            
        Returns:
            包含所有生长阶段图像的列表
        """
        stage_images = []
        for i in range(1, stages + 1):
            key = f"crops/{crop_name}_stage{i}"
            if key not in self.images:
                try:
                    image_path = os.path.join(self.base_path, 'crops', f"{crop_name}_stage{i}.png")
                    self.images[key] = pygame.image.load(image_path).convert_alpha()
                except pygame.error as e:
                    print(f"无法加载作物图像 {image_path}: {e}")
                    # 创建一个占位符图像（绿色矩形，随着阶段增加颜色加深）
                    placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
                    green_value = max(50, 255 - (i * 50))  # 随着阶段增加，绿色变深
                    placeholder.fill((0, green_value, 0))
                    self.images[key] = placeholder
            
            stage_images.append(self.images[key])

        return stage_images
            
    def load_svg(self, path, size=None):
        """加载SVG图像并转换为pygame表面
        
        Args:
            path: SVG文件路径（相对于images目录）
            size: 可选的输出尺寸元组 (width, height)
            
        Returns:
            转换后的pygame表面
        """
        key = f"svg/{path}_{size}"
        if key not in self.images:
            try:
                # 构建完整的SVG文件路径
                svg_path = os.path.join(self.base_path, path)
                
                # 尝试使用cairosvg将SVG转换为PNG
                try:
                    # 如果指定了尺寸，使用指定尺寸
                    if size:
                        width, height = size
                        png_data = cairosvg.svg2png(url=svg_path, output_width=width, output_height=height)
                    else:
                        png_data = cairosvg.svg2png(url=svg_path)
                    
                    # 从内存加载PNG数据
                    png_file = io.BytesIO(png_data)
                    self.images[key] = pygame.image.load(png_file).convert_alpha()
                    
                except ImportError:
                    # 如果没有cairosvg，创建一个简单的占位符
                    print(f"警告：无法加载SVG图像 {svg_path}，cairosvg库未安装")
                    if size:
                        width, height = size
                    else:
                        width, height = 64, 64
                    placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
                    placeholder.fill((34, 139, 34, 200))  # 半透明绿色
                    # 绘制一个简单的树形状
                    pygame.draw.rect(placeholder, (139, 69, 19), (width//2-width//8, height//2, width//4, height//2))
                    pygame.draw.circle(placeholder, (0, 100, 0), (width//2, height//3), width//3)
                    self.images[key] = placeholder
                    
            except Exception as e:
                print(f"无法加载SVG图像 {path}: {e}")
                # 创建一个占位符
                if size:
                    width, height = size
                else:
                    width, height = 64, 64
                placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
                placeholder.fill((34, 139, 34, 200))  # 半透明绿色
                self.images[key] = placeholder
        
        return self.images[key]
        
        return stage_images

# 创建全局图像管理器实例
# 不再在这里创建单例实例，而是在game.py中创建
# 这样可以确保pygame已经初始化
image_manager = None

# 设置全局图像管理器实例的函数
def set_image_manager(manager):
    """设置全局图像管理器实例
    
    Args:
        manager: ImageManager实例
    """
    global image_manager
    image_manager = manager