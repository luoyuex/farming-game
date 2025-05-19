import pygame
import datetime
from config import INITIAL_PLAYER, LEVEL_EXP_REQUIREMENTS
# from utils.font_manager import font_manager

class Player:
    """玩家类，管理玩家属性和状态"""
    
    def __init__(self, db_manager, player_id=None, name=None, game=None):
        """初始化玩家
        
        Args:
            db_manager: 数据库管理器实例
            player_id: 玩家ID，如果提供则加载现有玩家
            name: 新玩家名称，仅在创建新玩家时使用
            game: 游戏实例，用于获取图像管理器
        """
        self.db = db_manager
        self.game = game
        
        # 玩家属性
        self.id = None
        self.name = ""
        self.level = 1
        self.exp = 0
        self.money = 0
        self.last_login = None
        self.energy = INITIAL_PLAYER["energy"]
        self.max_energy = INITIAL_PLAYER["energy"]
        
        # 玩家位置和方向
        self.x = 0
        self.y = 0
        self.direction = "down"  # down, up, left, right
        
        # 玩家是否在房子内
        self.in_house = False
        
        # 当前选中的工具/物品
        self.selected_item = None
        
        if player_id:
            # 加载现有玩家
            self.load_player(player_id)
        elif name:
            # 创建新玩家
            self.create_new_player(name)
    
    def create_new_player(self, name):
        """创建新玩家
        
        Args:
            name: 玩家名称
        """
        self.id = self.db.create_new_player(name)
        self.name = name
        self.level = INITIAL_PLAYER["level"]
        self.exp = INITIAL_PLAYER["exp"]
        self.money = INITIAL_PLAYER["money"]
        self.last_login = datetime.datetime.now()
    
    def load_player(self, player_id):
        """从数据库加载玩家数据
        
        Args:
            player_id: 玩家ID
        """
        player_data = self.db.get_player(player_id)
        if player_data:
            self.id = player_data["id"]
            self.name = player_data["name"]
            self.level = player_data["level"]
            self.exp = player_data["exp"]
            self.money = player_data["money"]
            self.day = player_data.get("day", 1)
            # 解析上次登录时间
            if player_data["last_login"]:
                self.last_login = datetime.datetime.fromisoformat(player_data["last_login"])
    
    def save(self):
        """保存玩家数据到数据库"""
        if self.id:
            self.db.update_player(
                self.id,
                name=self.name,
                level=self.level,
                exp=self.exp,
                money=self.money,
                last_login=datetime.datetime.now().isoformat(),
                day=getattr(self, "day", 1)
            )
    
    def add_exp(self, amount):
        """增加经验值并检查是否升级
        
        Args:
            amount: 经验值数量
            
        Returns:
            是否升级
        """
        self.exp += amount
        
        # 检查是否可以升级
        if self.level < len(LEVEL_EXP_REQUIREMENTS) and self.exp >= LEVEL_EXP_REQUIREMENTS[self.level]:
            self.level += 1
            # 升级时恢复能量
            self.energy = self.max_energy
            return True
        
        return False
    
    def add_money(self, amount):
        """增加金钱
        
        Args:
            amount: 金钱数量
        """
        self.money += amount
    
    def spend_money(self, amount):
        """花费金钱
        
        Args:
            amount: 金钱数量
            
        Returns:
            是否成功花费（余额是否足够）
        """
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def use_energy(self, amount):
        """消耗能量
        
        Args:
            amount: 能量数量
            
        Returns:
            是否成功消耗（能量是否足够）
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def restore_energy(self, amount):
        """恢复能量
        
        Args:
            amount: 能量数量
        """
        self.energy = min(self.energy + amount, self.max_energy)
    
    def get_inventory(self):
        """获取玩家背包
        
        Returns:
            背包物品列表
        """
        return self.db.get_inventory(self.id)
    
    def get_tools(self):
        """获取玩家工具
        
        Returns:
            工具列表
        """
        return self.db.get_tools(self.id)
    
    def add_item(self, item_name, quantity, item_type):
        """添加物品到背包
        
        Args:
            item_name: 物品名称
            quantity: 数量
            item_type: 物品类型
        """
        self.db.add_inventory_item(self.id, item_name, quantity, item_type)
    
    def remove_item(self, item_id, quantity):
        """从背包移除物品
        
        Args:
            item_id: 物品ID
            quantity: 要移除的数量
            
        Returns:
            是否成功移除（数量是否足够）
        """
        # 获取当前物品信息
        inventory = self.get_inventory()
        for item in inventory:
            if item["id"] == item_id:
                if item["quantity"] >= quantity:
                    # 更新物品数量
                    new_quantity = item["quantity"] - quantity
                    self.db.update_inventory_item(item_id, new_quantity)
                    return True
                break
        return False
    
    def update(self, keys):
        """根据按键更新玩家状态
        
        Args:
            keys: pygame按键状态
        """
        # 这里可以实现玩家移动等逻辑
        pass
    
    def render(self, screen, camera_offset=(0, 0)):
        """渲染玩家
        
        Args:
            screen: pygame屏幕对象
            camera_offset: 相机偏移量
        """
        # 加载玩家精灵图
        if self.game and hasattr(self.game, 'image_manager'):
            player_sprite = self.game.image_manager.load_player_sprite(self.direction)
        else:
            # 创建一个占位符图像（红色矩形）
            player_sprite = pygame.Surface((32, 48), pygame.SRCALPHA)
            player_sprite.fill((255, 0, 0))
        
        # 放大玩家精灵图到1.5倍大小
        original_width = player_sprite.get_width()
        original_height = player_sprite.get_height()
        scaled_width = int(original_width * 1.5)
        scaled_height = int(original_height * 1.5)
        scaled_player_sprite = pygame.transform.scale(player_sprite, (scaled_width, scaled_height))
        
        # 绘制放大后的玩家精灵图
        screen.blit(
            scaled_player_sprite, 
            (self.x - camera_offset[0], self.y - camera_offset[1])
        )  # 放大后的玩家图像