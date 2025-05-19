import pygame
from config import TOOL_TYPES
from utils.font_manager import font_manager

class Tool:
    """工具类，管理玩家的工具属性和使用"""
    
    def __init__(self, db_manager, tool_id=None, player_id=None, tool_name=None, load_from_db=True, game=None):
        """初始化工具
        
        Args:
            db_manager: 数据库管理器实例
            tool_id: 工具ID，如果提供则从数据库加载
            player_id: 玩家ID，创建新工具时使用
            tool_name: 工具名称，创建新工具时使用
            load_from_db: 是否从数据库加载数据
            game: 游戏实例，用于获取图像管理器
        """
        self.db = db_manager
        self.game = game
        
        # 工具属性
        self.id = None
        self.player_id = None
        self.tool_name = None
        self.durability = 100
        self.level = 1
        
        # 工具配置信息
        self.config = None
        
        if tool_id and load_from_db:
            # 从数据库加载工具
            self.load_tool(tool_id)
        elif player_id and tool_name:
            # 创建新工具
            self.create_new_tool(player_id, tool_name)
    
    def create_new_tool(self, player_id, tool_name):
        """创建新工具
        
        Args:
            player_id: 玩家ID
            tool_name: 工具名称
        """
        if tool_name not in TOOL_TYPES:
            raise ValueError(f"未知的工具类型: {tool_name}")
        
        self.player_id = player_id
        self.tool_name = tool_name
        self.durability = TOOL_TYPES[tool_name]["durability"]
        self.level = 1
        
        # 保存到数据库
        self.db.cursor.execute(
            "INSERT INTO tools (player_id, tool_name, durability, level) VALUES (?, ?, ?, ?)",
            (player_id, tool_name, self.durability, self.level)
        )
        self.db.conn.commit()
        self.id = self.db.cursor.lastrowid
        
        # 加载工具配置
        self.config = TOOL_TYPES[tool_name]
    
    def load_tool(self, tool_id):
        """从数据库加载工具数据
        
        Args:
            tool_id: 工具ID
        """
        # 查询数据库获取工具信息
        self.db.cursor.execute("SELECT * FROM tools WHERE id = ?", (tool_id,))
        tool_data = self.db.cursor.fetchone()
        
        if tool_data:
            self.id = tool_data["id"]
            self.player_id = tool_data["player_id"]
            self.tool_name = tool_data["tool_name"]
            self.durability = tool_data["durability"]
            self.level = tool_data["level"]
            
            # 加载工具配置
            if self.tool_name in TOOL_TYPES:
                self.config = TOOL_TYPES[self.tool_name]
    
    def save(self):
        """保存工具数据到数据库"""
        if self.id:
            self.db.update_tool(
                self.id,
                durability=self.durability,
                level=self.level
            )
    
    def use(self):
        """使用工具，减少耐久度
        
        Returns:
            是否成功使用（耐久度是否足够）
        """
        if self.durability > 0:
            # 根据工具等级减少不同的耐久度
            durability_cost = max(1, 3 - self.level * 0.5)  # 高级工具耐久度消耗更少
            self.durability -= durability_cost
            if self.durability < 0:
                self.durability = 0
            self.save()
            return True
        return False
    
    def repair(self, amount=None):
        """修复工具耐久度
        
        Args:
            amount: 修复量，如果不提供则完全修复
            
        Returns:
            实际修复的耐久度
        """
        if amount is None:
            # 完全修复
            old_durability = self.durability
            self.durability = self.config["durability"]
            self.save()
            return self.durability - old_durability
        else:
            # 部分修复
            old_durability = self.durability
            self.durability = min(self.durability + amount, self.config["durability"])
            self.save()
            return self.durability - old_durability
    
    def upgrade(self):
        """升级工具
        
        Returns:
            是否成功升级
        """
        if self.level < len(self.config["efficiency"]) - 1:
            self.level += 1
            # 升级后完全修复耐久度
            self.durability = self.config["durability"]
            self.save()
            return True
        return False
    
    def get_efficiency(self):
        """获取工具效率
        
        Returns:
            工具效率值
        """
        if not self.config:
            return 1.0
        return self.config["efficiency"][self.level - 1]
    
    def get_upgrade_cost(self):
        """获取升级所需金钱
        
        Returns:
            升级费用，如果已达最高级则返回None
        """
        if not self.config or self.level >= len(self.config["upgrade_cost"]):
            return None
        return self.config["upgrade_cost"][self.level - 1]
    
    def render(self, screen, x, y, size):
        """渲染工具
        
        Args:
            screen: pygame屏幕对象
            x: X坐标
            y: Y坐标
            size: 大小
        """
        # 加载工具图像
        if self.game and hasattr(self.game, 'image_manager'):
            tool_image = self.game.image_manager.load_image('tools', self.tool_name)
        else:
            # 创建一个占位符图像（彩色矩形）
            tool_image = pygame.Surface((32, 32), pygame.SRCALPHA)
            if self.tool_name == '锄头':
                color = (139, 69, 19)  # 棕色
            elif self.tool_name == '水壶':
                color = (0, 0, 255)    # 蓝色
            elif self.tool_name == '镰刀':
                color = (255, 215, 0)  # 金色
            else:
                color = (150, 150, 150)  # 灰色
            tool_image.fill(color)
        
        # 调整图像大小以适应指定尺寸
        scaled_image = pygame.transform.scale(tool_image, (size, size))
        
        # 绘制工具图像
        screen.blit(scaled_image, (x, y))
        
        # 绘制工具等级
        font = font_manager.get_font(20)
        level_text = font.render(f"Lv.{self.level}", True, (255, 255, 255))
        screen.blit(level_text, (x + 5, y + 5))
        
        # 绘制耐久度条
        durability_percent = self.durability / self.config["durability"]
        bar_width = int(size * 0.8)
        bar_height = 5
        bar_x = x + (size - bar_width) // 2
        bar_y = y + size - 10
        
        # 背景条
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # 耐久度条
        if durability_percent > 0:
            # 根据耐久度百分比选择颜色
            if durability_percent > 0.6:
                bar_color = (0, 255, 0)  # 绿色
            elif durability_percent > 0.3:
                bar_color = (255, 255, 0)  # 黄色
            else:
                bar_color = (255, 0, 0)  # 红色
            
            pygame.draw.rect(
                screen, 
                bar_color, 
                (bar_x, bar_y, int(bar_width * durability_percent), bar_height)
            )