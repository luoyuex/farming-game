import pygame
import datetime
from config import ANIMAL_TYPES

class Animal:
    """动物类，管理动物的状态和产出"""
    
    def __init__(self, db_manager, animal_id=None, player_id=None, animal_type=None, name=None, load_from_db=True, game=None):
        """初始化动物
        
        Args:
            db_manager: 数据库管理器实例
            animal_id: 动物ID，如果提供则从数据库加载
            player_id: 玩家ID，创建新动物时使用
            animal_type: 动物类型，创建新动物时使用
            name: 动物名称，创建新动物时使用
            load_from_db: 是否从数据库加载数据
            game: 游戏实例，用于获取图像管理器
        """
        self.db = db_manager
        self.game = game
        
        # 动物属性
        self.id = None
        self.player_id = None
        self.animal_type = None
        self.name = None
        self.age = 0
        self.is_fed = False
        self.produce_time = None
        
        # 位置属性
        self.x = 0
        self.y = 0
        
        # 动物配置信息
        self.config = None
        
        if animal_id and load_from_db:
            # 从数据库加载动物
            self.load_animal(animal_id)
        elif player_id and animal_type and name:
            # 创建新动物
            self.create_new_animal(player_id, animal_type, name)
    
    def create_new_animal(self, player_id, animal_type, name):
        """创建新动物
        
        Args:
            player_id: 玩家ID
            animal_type: 动物类型
            name: 动物名称
        """
        if animal_type not in ANIMAL_TYPES:
            raise ValueError(f"未知的动物类型: {animal_type}")
        
        self.player_id = player_id
        self.animal_type = animal_type
        self.name = name
        self.age = 0
        self.is_fed = False
        self.produce_time = datetime.datetime.now()
        
        # 保存到数据库
        self.id = self.db.add_animal(player_id, animal_type, name)
        
        # 加载动物配置
        self.config = ANIMAL_TYPES[animal_type]
    
    def load_animal(self, animal_id):
        """从数据库加载动物数据
        
        Args:
            animal_id: 动物ID
        """
        # 查询数据库获取动物信息
        self.db.cursor.execute("SELECT * FROM animals WHERE id = ?", (animal_id,))
        animal_data = self.db.cursor.fetchone()
        
        if animal_data:
            self.id = animal_data["id"]
            self.player_id = animal_data["player_id"]
            self.animal_type = animal_data["animal_type"]
            self.name = animal_data["name"]
            self.age = animal_data["age"]
            self.is_fed = bool(animal_data["is_fed"])
            # 使用字典索引访问，如果字段不存在则使用默认值0
            self.x = animal_data["x"] if "x" in animal_data.keys() else 0
            self.y = animal_data["y"] if "y" in animal_data.keys() else 0
            
            # 解析产出时间
            if animal_data["produce_time"]:
                self.produce_time = datetime.datetime.fromisoformat(animal_data["produce_time"])
            
            # 加载动物配置
            if self.animal_type in ANIMAL_TYPES:
                self.config = ANIMAL_TYPES[self.animal_type]
    
    def save(self):
        """保存动物数据到数据库"""
        if self.id:
            self.db.update_animal(
                self.id,
                age=self.age,
                is_fed=int(self.is_fed),
                produce_time=self.produce_time.isoformat() if self.produce_time else None,
                x=self.x,
                y=self.y
            )
    
    def feed(self, feed_type=None):
        """喂食动物
        
        Args:
            feed_type: 饲料类型，如果提供则检查是否匹配
            
        Returns:
            是否成功喂食
        """
        if not self.is_fed:
            # 检查饲料类型是否匹配
            if feed_type and feed_type != self.config["feed_name"]:
                return False
                
            self.is_fed = True
            # 设置产出时间为当前时间
            if not self.produce_time:
                self.produce_time = datetime.datetime.now()
            self.save()
            return True
        return False
    
    def age_up(self):
        """动物年龄增长，每天调用一次
        
        Returns:
            是否成功增长
        """
        if self.is_fed:
            # 增加年龄
            self.age += 1
            # 重置喂食状态
            self.is_fed = False
            # 更新产出时间，确保第二天可以产出
            if self.produce_time:
                # 将产出时间设置为更早的时间，确保满足产出条件
                days_to_produce = self.config["days_to_produce"]
                self.produce_time = datetime.datetime.now() - datetime.timedelta(days=days_to_produce)
            self.save()
            return True
        return False
    
    def can_produce(self):
        """检查动物是否可以产出产品
        
        Returns:
            是否可以产出
        """
        if not self.config or not self.produce_time:
            return False
        
        # 计算距离上次产出的天数
        now = datetime.datetime.now()
        days_since_produce = (now - self.produce_time).days
        
        return days_since_produce >= self.config["days_to_produce"]
    
    def collect_product(self):
        """收集动物产品
        
        Returns:
            (产品名称, 收获数量, 经验值) 元组，如果无法收集则返回None
        """
        if self.can_produce():
            product_name = self.config["product"]
            exp_reward = self.config["exp_reward"]
            
            # 更新产出时间
            self.produce_time = datetime.datetime.now()
            self.save()
            
            # 返回产品信息
            return (product_name, 1, exp_reward)
        
        return None
    
    def render(self, screen, x, y, size, camera_offset=(0, 0)):
        """渲染动物
        
        Args:
            screen: pygame屏幕对象
            x: X坐标
            y: Y坐标
            size: 大小
            camera_offset: 相机偏移量
        """
        # 计算屏幕位置
        screen_x = x - camera_offset[0]
        screen_y = y - camera_offset[1]
        
        # 加载动物图像
        if self.game and hasattr(self.game, 'image_manager'):
            animal_image = self.game.image_manager.load_image('animals', self.animal_type)
            # 调整图像大小
            scaled_image = pygame.transform.scale(animal_image, (size, size))
            # 绘制动物图像
            screen.blit(scaled_image, (screen_x, screen_y))
        else:
            # 如果没有图像管理器，使用占位符颜色
            # 根据动物类型选择颜色
            if self.animal_type == "牛":
                color = (200, 200, 200)  # 灰白色
            elif self.animal_type == "羊":
                color = (255, 255, 255)  # 白色
            elif self.animal_type == "鸡":
                color = (255, 255, 0)    # 黄色
            else:
                color = (150, 75, 0)     # 棕色
            
            # 绘制动物
            animal_rect = pygame.Rect(screen_x, screen_y, size, size)
            pygame.draw.rect(screen, color, animal_rect)
        
        # 如果已喂食，绘制绿色边框
        animal_rect = pygame.Rect(screen_x, screen_y, size, size)
        if self.is_fed:
            pygame.draw.rect(screen, (0, 255, 0), animal_rect, 2)  # 2像素宽的绿色边框
        
        # 如果可以产出，绘制闪烁效果
        if self.can_produce():
            # 使用当前时间创建闪烁效果
            if pygame.time.get_ticks() % 1000 < 500:  # 每秒闪烁一次
                pygame.draw.rect(screen, (255, 215, 0), animal_rect, 3)  # 3像素宽的金色边框
                
    def move(self, dx, dy, farm_grid, areas=None):
        """移动动物
        
        Args:
            dx: X方向移动量
            dy: Y方向移动量
            farm_grid: 农场网格，用于碰撞检测
            areas: 区域列表，用于检查区域限制
            
        Returns:
            是否成功移动
        """
        # 计算新位置
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 检查是否超出边界或碰到障碍物
        tile_x = int(new_x / TILE_SIZE)
        tile_y = int(new_y / TILE_SIZE)
        
        if 0 <= tile_x < FARM_WIDTH and 0 <= tile_y < FARM_HEIGHT:
            # 检查目标位置是否有障碍物
            if farm_grid[tile_y][tile_x] is None or farm_grid[tile_y][tile_x].get("type") != "crop":
                # 检查是否在饲养区内
                if areas:
                    in_breeding_area = False
                    for area in areas:
                        if hasattr(area, 'area_type') and area.area_type == 'breeding' and area.contains_point(tile_x, tile_y):
                            in_breeding_area = True
                            break
                    
                    if not in_breeding_area:
                        return False  # 不在饲养区内，不允许移动
                
                self.x = new_x
                self.y = new_y
                return True
        
        return False