import pygame
import os
from config import TILE_SIZE

class Area:
    """区域类，用于管理农场中的不同功能区域"""
    
    # 区域类型常量
    PLANTING = "planting"  # 种植区
    BREEDING = "breeding"  # 饲养区
    HOUSING = "housing"    # 住宅区
    GENERAL = "general"    # 通用区域
    
    def __init__(self, x, y, width, height, area_type, db_manager=None, area_id=None, player_id=None, game=None):
        """初始化区域
        
        Args:
            x: 区域左上角X坐标（瓦片坐标）
            y: 区域左上角Y坐标（瓦片坐标）
            width: 区域宽度（瓦片数）
            height: 区域高度（瓦片数）
            area_type: 区域类型，使用Area类中定义的常量
            db_manager: 数据库管理器实例
            area_id: 区域ID，如果提供则从数据库加载
            player_id: 玩家ID，创建新区域时使用
            game: 游戏实例
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.area_type = area_type
        self.db = db_manager
        self.game = game
        self.id = None
        self.player_id = player_id
        
        # 区域边界颜色
        self.border_colors = {
            self.PLANTING: (0, 200, 0),      # 绿色
            self.BREEDING: (200, 150, 0),    # 棕色
            self.HOUSING: (0, 100, 200),     # 蓝色
            self.GENERAL: (150, 150, 150)    # 灰色
        }
        
        # 加载边框图片
        self.border_images = {}
        self._load_border_images()
        
        # 加载区域特定图像
        self.area_images = {}
        self._load_area_images()
        
        if area_id:
            # 从数据库加载区域
            self.load_area(area_id)
        elif player_id:
            # 创建新区域
            self.create_new_area()
    
    def create_new_area(self):
        """创建新区域并保存到数据库"""
        if self.db and self.player_id:
            # 保存到数据库
            self.db.cursor.execute(
                "INSERT INTO areas (player_id, x, y, width, height, area_type) VALUES (?, ?, ?, ?, ?, ?)",
                (self.player_id, self.x, self.y, self.width, self.height, self.area_type)
            )
            self.db.conn.commit()
            self.id = self.db.cursor.lastrowid
    
    def load_area(self, area_id):
        """从数据库加载区域数据
        
        Args:
            area_id: 区域ID
        """
        if self.db:
            # 查询数据库获取区域信息
            self.db.cursor.execute("SELECT * FROM areas WHERE id = ?", (area_id,))
            area_data = self.db.cursor.fetchone()
            
            if area_data:
                self.id = area_data["id"]
                self.player_id = area_data["player_id"]
                self.x = area_data["x"]
                self.y = area_data["y"]
                self.width = area_data["width"]
                self.height = area_data["height"]
                self.area_type = area_data["area_type"]
    
    def save(self):
        """保存区域数据到数据库"""
        if self.db and self.id:
            self.db.cursor.execute(
                "UPDATE areas SET x = ?, y = ?, width = ?, height = ?, area_type = ? WHERE id = ?",
                (self.x, self.y, self.width, self.height, self.area_type, self.id)
            )
            self.db.conn.commit()
    
    def contains_point(self, x, y):
        """检查指定点是否在区域内
        
        Args:
            x: X坐标（瓦片坐标）
            y: Y坐标（瓦片坐标）
            
        Returns:
            是否在区域内
        """
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def _load_border_images(self):
        """加载区域边框图片"""
        border_types = {
            self.PLANTING: "planting_border.svg",
            self.BREEDING: "breeding_border.svg",
            self.HOUSING: "housing_border.svg",
            self.GENERAL: "general_border.svg"
        }
        
        # 尝试加载对应类型的边框图片
        border_file = border_types.get(self.area_type)
        if border_file:
            border_path = os.path.join("assets", "images", "borders", border_file)
            try:
                if os.path.exists(border_path):
                    self.border_images[self.area_type] = pygame.image.load(border_path).convert_alpha()
            except Exception as e:
                print(f"无法加载边框图片 {border_path}: {e}")
    
    def _load_area_images(self):
        """加载区域特定图像，如住宅区的房屋图像"""
        # 区域特定图像映射
        area_image_types = {
            self.HOUSING: "pixel_house.svg",  # 默认房屋样式
            # 其他区域类型的特定图像可以在这里添加
        }
        
        # 尝试加载对应类型的区域图片
        area_file = area_image_types.get(self.area_type)
        if area_file:
            area_path = os.path.join("assets", "images", "houses", area_file)
            try:
                if os.path.exists(area_path):
                    self.area_images[self.area_type] = pygame.image.load(area_path).convert_alpha()
            except Exception as e:
                print(f"无法加载区域图片 {area_path}: {e}")

    
    def render(self, screen, camera_offset=(0, 0)):
        """渲染区域边界
        
        Args:
            screen: pygame屏幕对象
            camera_offset: 相机偏移量
        """
        # 获取区域边界颜色
        border_color = self.border_colors.get(self.area_type, (150, 150, 150))
        
        # 计算屏幕坐标
        screen_x = self.x * TILE_SIZE - camera_offset[0]
        screen_y = self.y * TILE_SIZE - camera_offset[1]
        width_px = self.width * TILE_SIZE
        height_px = self.height * TILE_SIZE
        
        # 住宅区不绘制半透明填充和边框
        if self.area_type != self.HOUSING:
            # 绘制半透明填充
            s = pygame.Surface((width_px, height_px), pygame.SRCALPHA)
            s.fill((border_color[0], border_color[1], border_color[2], 50))  # 增加透明度填充
            screen.blit(s, (screen_x, screen_y))
        
        # 检查是否有边框图片
        if self.area_type != self.HOUSING and self.area_type in self.border_images and self.border_images[self.area_type]:
            # 使用边框图片
            border_img = self.border_images[self.area_type]
            
            # 绘制四个角落
            corner_size = 32  # 角落大小
            
            # 缩放图片以适应角落大小
            scaled_img = pygame.transform.scale(border_img, (corner_size, corner_size))
            
            # 左上角
            screen.blit(scaled_img, (screen_x, screen_y))
            
            # 右上角 (水平翻转)
            flipped_h = pygame.transform.flip(scaled_img, True, False)
            screen.blit(flipped_h, (screen_x + width_px - corner_size, screen_y))
            
            # 左下角 (垂直翻转)
            flipped_v = pygame.transform.flip(scaled_img, False, True)
            screen.blit(flipped_v, (screen_x, screen_y + height_px - corner_size))
            
            # 右下角 (水平和垂直翻转)
            flipped_hv = pygame.transform.flip(scaled_img, True, True)
            screen.blit(flipped_hv, (screen_x + width_px - corner_size, screen_y + height_px - corner_size))
            
            # 绘制边框线
            # 上边框
            for x in range(corner_size, width_px - corner_size, corner_size):
                screen.blit(pygame.transform.scale(border_img, (corner_size, 8)), 
                           (screen_x + x, screen_y))
            
            # 下边框
            for x in range(corner_size, width_px - corner_size, corner_size):
                screen.blit(pygame.transform.scale(pygame.transform.flip(border_img, False, True), 
                                                 (corner_size, 8)), 
                           (screen_x + x, screen_y + height_px - 8))
            
            # 左边框
            for y in range(corner_size, height_px - corner_size, corner_size):
                screen.blit(pygame.transform.scale(border_img, (8, corner_size)), 
                           (screen_x, screen_y + y))
            
            # 右边框
            for y in range(corner_size, height_px - corner_size, corner_size):
                screen.blit(pygame.transform.scale(pygame.transform.flip(border_img, True, False), 
                                                 (8, corner_size)), 
                           (screen_x + width_px - 8, screen_y + y))
        elif self.area_type != self.HOUSING:
            # 使用默认矩形边框（非住宅区）
            # 绘制边界
            pygame.draw.rect(
                screen, 
                border_color, 
                (screen_x, screen_y, width_px, height_px), 
                4  # 边框宽度
            )
            
            # 绘制内边框，增强视觉效果
            pygame.draw.rect(
                screen, 
                (255, 255, 255), 
                (screen_x + 2, screen_y + 2, width_px - 4, height_px - 4), 
                1  # 内边框宽度
            )
        
        # 绘制区域特定图像（如住宅区的房屋）
        if self.area_type in self.area_images and self.area_images[self.area_type]:
            area_img = self.area_images[self.area_type]
            
            # 计算图像位置（居中显示）
            img_width, img_height = area_img.get_rect().size
            img_x = screen_x + (width_px - img_width) // 2
            img_y = screen_y + (height_px - img_height) // 2
            
            # 绘制区域图像
            screen.blit(area_img, (img_x, img_y))
        
        # 绘制区域类型标识
        area_labels = {
            self.PLANTING: "种植区",
            self.BREEDING: "饲养区",
            self.HOUSING: "住宅区",
            self.GENERAL: "通用区"
        }
        
        # 使用全局字体管理器获取字体，参考main_menu.py的方式
        from utils.font_manager import font_manager
        font = font_manager.get_font(24)  # 增大字体
        
        label = area_labels.get(self.area_type, "未知区域")
        
        # 只为非住宅区绘制标签
        if self.area_type != self.HOUSING:
            # 创建文本背景
            text = font.render(label, True, (255, 255, 255))  # 白色文字
            text_width, text_height = text.get_size()
            text_bg = pygame.Surface((text_width + 10, text_height + 6), pygame.SRCALPHA)
            text_bg.fill((border_color[0], border_color[1], border_color[2], 200))  # 高透明度背景
            
            # 绘制文本背景和文本
            screen.blit(text_bg, (screen_x + 5, screen_y + 5))
            screen.blit(text, (screen_x + 10, screen_y + 8))