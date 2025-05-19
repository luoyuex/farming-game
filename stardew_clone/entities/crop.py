import pygame
import datetime
from config import CROP_TYPES

class Crop:
    """作物类，管理作物的生长和状态"""
    
    def __init__(self, db_manager, crop_id=None, player_id=None, crop_type=None, x=None, y=None, load_from_db=True, game=None):
        """初始化作物
        
        Args:
            db_manager: 数据库管理器实例
            crop_id: 作物ID，如果提供则从数据库加载
            player_id: 玩家ID，创建新作物时使用
            crop_type: 作物类型，创建新作物时使用
            x: 种植位置X坐标
            y: 种植位置Y坐标
            load_from_db: 是否从数据库加载数据
            game: 游戏实例，用于获取图像管理器
        """
        self.db = db_manager
        self.game = game
        
        # 作物属性
        self.id = None
        self.player_id = None
        self.crop_type = None
        self.x = 0
        self.y = 0
        self.growth_stage = 0
        self.planted_at = None
        self.is_watered = False
        
        # 作物配置信息
        self.config = None
        
        if crop_id and load_from_db:
            # 从数据库加载作物
            self.load_crop(crop_id)
        elif player_id and crop_type and x is not None and y is not None:
            # 创建新作物
            self.create_new_crop(player_id, crop_type, x, y)
    
    def create_new_crop(self, player_id, crop_type, x, y):
        """创建新作物
        
        Args:
            player_id: 玩家ID
            crop_type: 作物类型
            x: X坐标
            y: Y坐标
        """
        if crop_type not in CROP_TYPES:
            raise ValueError(f"未知的作物类型: {crop_type}")
        
        self.player_id = player_id
        self.crop_type = crop_type
        self.x = x
        self.y = y
        self.growth_stage = 0
        self.planted_at = datetime.datetime.now()
        self.is_watered = False
        
        # 保存到数据库
        self.id = self.db.add_crop(player_id, crop_type, x, y)
        
        # 加载作物配置
        self.config = CROP_TYPES[crop_type]
    
    def load_crop(self, crop_id):
        """从数据库加载作物数据
        
        Args:
            crop_id: 作物ID
        """
        # 查询数据库获取作物信息
        self.db.cursor.execute("SELECT * FROM crops WHERE id = ?", (crop_id,))
        crop_data = self.db.cursor.fetchone()
        
        if crop_data:
            self.id = crop_data["id"]
            self.player_id = crop_data["player_id"]
            self.crop_type = crop_data["crop_type"]
            self.x = crop_data["x"]
            self.y = crop_data["y"]
            self.growth_stage = crop_data["growth_stage"]
            self.is_watered = bool(crop_data["is_watered"])
            
            # 解析种植时间
            if crop_data["planted_at"]:
                self.planted_at = datetime.datetime.fromisoformat(crop_data["planted_at"])
            
            # 加载作物配置
            if self.crop_type in CROP_TYPES:
                self.config = CROP_TYPES[self.crop_type]
    
    def save(self):
        """保存作物数据到数据库"""
        if self.id:
            self.db.update_crop(
                self.id,
                growth_stage=self.growth_stage,
                is_watered=int(self.is_watered)
            )
    
    def water(self):
        """给作物浇水
        
        Returns:
            是否成功浇水
        """
        if not self.is_watered and not self.is_fully_grown():
            self.is_watered = True
            self.save()
            return True
        return False
    
    def grow(self):
        """作物生长，每天调用一次
        
        Returns:
            是否成功生长
        """
        if self.is_watered and not self.is_fully_grown():
            # 增加生长阶段
            self.growth_stage += 1
            # 重置浇水状态
            self.is_watered = False
            self.save()
            return True
        return False
    
    def is_fully_grown(self):
        """检查作物是否完全成熟
        
        Returns:
            是否完全成熟
        """
        if not self.config:
            return False
        return self.growth_stage >= self.config["growth_time"]
    
    def get_days_to_grow(self):
        """获取距离成熟还需要的天数
        
        Returns:
            剩余天数
        """
        if not self.config:
            return 0
        return max(0, self.config["growth_time"] - self.growth_stage)
    
    def harvest(self):
        """收获作物
        
        Returns:
            (作物名称, 收获数量, 经验值) 元组，如果无法收获则返回None
        """
        if self.is_fully_grown():
            crop_name = self.crop_type
            exp_reward = self.config["exp_reward"]
            
            # 从数据库中删除作物
            self.db.delete_crop(self.id)
            
            # 返回收获信息
            return (crop_name, 1, exp_reward)
        
        return None
    
    def render(self, screen, tile_size, camera_offset=(0, 0)):
        """渲染作物
        
        Args:
            screen: pygame屏幕对象
            tile_size: 瓦片大小
            camera_offset: 相机偏移量
        """
        # 计算屏幕位置
        screen_x = self.x * tile_size - camera_offset[0]
        screen_y = self.y * tile_size - camera_offset[1]
        
        # 加载作物图像
        # 根据生长阶段加载不同的图像
        growth_percent = self.growth_stage / self.config["growth_time"]
        
        # 将生长百分比映射到4个生长阶段（0-3）
        stage = min(int(growth_percent * 4), 3)
        
        # 加载作物图像
        if self.game and hasattr(self.game, 'image_manager'):
            crop_images = self.game.image_manager.load_crop_stages(self.crop_type, 4)
        else:
            # 创建占位符图像
            crop_images = []
            for i in range(4):
                placeholder = pygame.Surface((32, 32), pygame.SRCALPHA)
                green_value = max(50, 255 - (i * 50))  # 随着阶段增加，绿色变深
                placeholder.fill((139, 69, 19))  # 棕色底色
                crop_images.append(placeholder)
        
        # 确保生长阶段在有效范围内
        stage = min(stage, len(crop_images) - 1)
        
        # 调整图像大小
        scaled_image = pygame.transform.scale(crop_images[stage], (tile_size, tile_size))
        
        # 绘制作物图像
        screen.blit(scaled_image, (screen_x, screen_y))
        
        # 如果已浇水，绘制水滴标记
        if self.is_watered:
            # 加载水滴图像或绘制一个蓝色小圆圈表示已浇水
            water_indicator = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(water_indicator, (0, 0, 255, 180), (5, 5), 5)
            screen.blit(water_indicator, (screen_x + tile_size - 10, screen_y))