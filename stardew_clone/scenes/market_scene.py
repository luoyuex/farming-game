import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, CROP_TYPES, ANIMAL_TYPES, TOOL_TYPES
from entities.inventory import Inventory
from utils.font_manager import font_manager
from utils.audio_manager import audio_manager 

class MarketScene:
    """市场场景，玩家可以在这里购买种子、动物和工具，以及出售农产品"""
    
    def __init__(self, game):
        """初始化市场场景
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.db = game.db
        
        # 字体 - 使用系统默认字体以支持中文
        self.font = font_manager.get_font(20)
        self.font_medium = font_manager.get_font(28)
        self.font_large = font_manager.get_font(32)
        
        # 玩家
        self.player = None
        
        # 物品栏
        self.inventory = None
        
        # 市场UI状态
        self.current_tab = "种子"  # 当前选中的标签：种子、动物、工具、饲料、出售
        self.tabs = ["种子", "动物", "工具", "饲料", "出售"]
        
        # 商品列表
        self.items_for_sale = []
        self.selected_item_index = 0
        
        # 滚动位置
        self.scroll_offset = 0
        self.max_visible_items = 8
        
        # 状态提示
        self.status_message = ""
        self.status_time = 0
    
    def setup(self, **kwargs):
        """设置场景参数
        
        Args:
            **kwargs: 场景参数
        """
        # 加载玩家
        from entities.player import Player
        self.player = Player(self.db, self.game.player_id)
        
        # 初始化物品栏
        self.inventory = Inventory(self.db, self.game.player_id)
        
        # 加载商品列表
        self.load_items_for_sale()
        
        # 播放背景音乐
        audio_manager.play_music()
    
    def load_items_for_sale(self):
        """根据当前标签加载商品列表"""
        self.items_for_sale = []
        self.selected_item_index = 0
        self.scroll_offset = 0
        
        if self.current_tab == "种子":
            # 加载种子列表
            for crop_name, crop_info in CROP_TYPES.items():
                self.items_for_sale.append({
                    "name": f"{crop_name}种子",
                    "price": crop_info["seed_price"],
                    "description": f"种植{crop_name}的种子，生长期{crop_info['growth_time']}天",
                    "type": "种子",
                    "crop_type": crop_name
                })
        
        elif self.current_tab == "动物":
            # 加载动物列表
            for animal_name, animal_info in ANIMAL_TYPES.items():
                self.items_for_sale.append({
                    "name": animal_name,
                    "price": animal_info["purchase_price"],
                    "description": f"产出{animal_info['product']}，每{animal_info['days_to_produce']}天一次",
                    "type": "动物",
                    "animal_type": animal_name
                })
        
        elif self.current_tab == "工具":
            # 加载工具列表
            for tool_name, tool_info in TOOL_TYPES.items():
                # 检查玩家是否已拥有该工具
                has_tool = False
                for tool in self.inventory.tools:
                    if tool["tool_name"] == tool_name:
                        has_tool = True
                        break
                
                if not has_tool:
                    self.items_for_sale.append({
                        "name": tool_name,
                        "price": 500,  # 基础工具价格
                        "description": f"基础{tool_name}，用于农场工作",
                        "type": "工具",
                        "tool_type": tool_name
                    })
        
        elif self.current_tab == "饲料":
            # 加载饲料列表
            for animal_name, animal_info in ANIMAL_TYPES.items():
                self.items_for_sale.append({
                    "name": animal_info["feed_name"],
                    "price": animal_info["feed_price"],
                    "description": f"用于喂养{animal_name}的饲料",
                    "type": "饲料",
                    "animal_type": animal_name
                })
        
        elif self.current_tab == "出售":
            # 加载玩家物品栏中可出售的物品
            for item in self.inventory.items:
                price = 0
                
                # 根据物品类型确定售价
                if item["item_type"] == "作物":
                    crop_name = item["item_name"]
                    if crop_name in CROP_TYPES:
                        price = CROP_TYPES[crop_name]["sell_price"]
                
                elif item["item_type"] == "动物产品":
                    product_name = item["item_name"]
                    for animal_info in ANIMAL_TYPES.values():
                        if animal_info["product"] == product_name:
                            price = animal_info["product_price"]
                            break
                
                if price > 0:
                    # 根据玩家等级计算价格加成
                    level_bonus = 1 + (self.player.level - 1) * 0.05
                    final_price = int(price * level_bonus)
                    
                    # 准备描述文本
                    if self.player.level > 1:
                        description = f"出售价格：{final_price}金币/个 (等级{self.player.level}加成：+{int((level_bonus-1)*100)}%)"
                    else:
                        description = f"出售价格：{final_price}金币/个"
                    
                    self.items_for_sale.append({
                        "name": item["item_name"],
                        "price": price,  # 保存原始价格，实际售卖时会应用加成
                        "final_price": final_price,  # 添加最终价格字段
                        "description": description,
                        "type": "出售",
                        "item_id": item["id"],
                        "quantity": item["quantity"]
                    })
    
    def handle_event(self, event):
        """处理输入事件
        
        Args:
            event: pygame事件
        """
        if event.type == pygame.KEYDOWN:
            # 切换标签
            if event.key == pygame.K_LEFT:
                tab_index = self.tabs.index(self.current_tab)
                self.current_tab = self.tabs[(tab_index - 1) % len(self.tabs)]
                self.load_items_for_sale()
            
            elif event.key == pygame.K_RIGHT:
                tab_index = self.tabs.index(self.current_tab)
                self.current_tab = self.tabs[(tab_index + 1) % len(self.tabs)]
                self.load_items_for_sale()
            
            # 选择商品
            elif event.key == pygame.K_UP:
                if len(self.items_for_sale) > 0:
                    self.selected_item_index = (self.selected_item_index - 1) % len(self.items_for_sale)
                    # 调整滚动位置
                    if self.selected_item_index < self.scroll_offset:
                        self.scroll_offset = self.selected_item_index
            
            elif event.key == pygame.K_DOWN:
                if len(self.items_for_sale) > 0:
                    self.selected_item_index = (self.selected_item_index + 1) % len(self.items_for_sale)
                    # 调整滚动位置
                    if self.selected_item_index >= self.scroll_offset + self.max_visible_items:
                        self.scroll_offset = self.selected_item_index - self.max_visible_items + 1
            
            # 购买/出售
            elif event.key == pygame.K_RETURN:
                if len(self.items_for_sale) > 0:
                    if self.current_tab in ["种子", "动物", "工具", "饲料"]:
                        self.buy_item(self.selected_item_index)
                    elif self.current_tab == "出售":
                        self.sell_item(self.selected_item_index)
            
            # 返回农场
            elif event.key == pygame.K_ESCAPE:
                # 保存玩家状态
                self.player.save()
                # 播放成功音效
                audio_manager.play_sound("success")
                # 切换到农场场景
                self.game.change_scene("farm")
    
    def buy_item(self, index):
        """购买商品
        
        Args:
            index: 商品索引
        """
        if 0 <= index < len(self.items_for_sale):
            item = self.items_for_sale[index]
            
            # 检查玩家金钱是否足够
            if self.player.money >= item["price"]:
                # 扣除金钱
                self.player.money -= item["price"]
                
                # 根据商品类型处理
                if item["type"] == "种子":
                    # 添加种子到物品栏
                    self.inventory.add_item(item["name"], 1, "种子")
                    # 播放成功音效
                    audio_manager.play_sound("success")
                    self.show_status(f"购买了 {item['name']}！")
                
                elif item["type"] == "动物":
                    # 创建新动物
                    from entities.animal import Animal
                    animal_name = f"我的{item['animal_type']}"
                    Animal(self.db, player_id=self.game.player_id, animal_type=item["animal_type"], name=animal_name)
                    # 播放成功音效
                    audio_manager.play_sound("success")
                    self.show_status(f"购买了 {item['name']}！")
                
                elif item["type"] == "工具":
                    # 添加工具到玩家工具列表
                    self.db.add_tool(self.game.player_id, item["tool_type"], 1)
                    self.inventory.refresh()
                    # 播放成功音效
                    audio_manager.play_sound("success")
                    self.show_status(f"购买了 {item['name']}！")
                
                elif item["type"] == "饲料":
                    # 添加饲料到物品栏
                    self.inventory.add_item(item["name"], 1, "饲料")
                    # 播放成功音效
                    audio_manager.play_sound("success")
                    self.show_status(f"购买了 {item['name']}！")
                
                # 刷新商品列表
                self.load_items_for_sale()
            else:
                self.show_status("金钱不足！")
    
    def sell_item(self, index):
        """出售物品
        
        Args:
            index: 物品索引
        """
        if 0 <= index < len(self.items_for_sale):
            item = self.items_for_sale[index]
            
            # 获取出售数量（默认为1）
            quantity = 1
            
            # 从物品栏移除物品
            if self.inventory.remove_item(item["item_id"], quantity):
                # 使用已计算好的最终价格
                final_price = item.get("final_price", item["price"]) * quantity
                
                # 增加金钱
                self.player.money += final_price
                
                # 播放成功音效
                audio_manager.play_sound("success")
                
                # 显示价格加成信息
                if self.player.level > 1:
                    level_bonus = 1 + (self.player.level - 1) * 0.05
                    bonus_info = f"(等级{self.player.level}加成：+{int((level_bonus-1)*100)}%)"
                    self.show_status(f"出售了 {item['name']} x{quantity}，获得 {final_price} 金币！{bonus_info}")
                else:
                    self.show_status(f"出售了 {item['name']} x{quantity}，获得 {final_price} 金币！")
                
                # 刷新商品列表
                self.load_items_for_sale()
    
    def show_status(self, message, duration=3000):
        """显示状态消息
        
        Args:
            message: 消息内容
            duration: 显示时间（毫秒）
        """
        self.status_message = message
        self.status_time = pygame.time.get_ticks() + duration
    
    def update(self):
        """更新场景状态"""
        pass
    
    def render(self, screen):
        """渲染场景
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制背景
        screen.fill((50, 50, 80))  # 深蓝色背景
        
        # 绘制标题
        title_text = self.font_large.render("市场", True, (255, 255, 255))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        # 绘制标签
        tab_width = WINDOW_WIDTH // len(self.tabs)
        for i, tab in enumerate(self.tabs):
            tab_x = i * tab_width
            tab_color = (100, 100, 200) if tab == self.current_tab else (70, 70, 120)
            pygame.draw.rect(screen, tab_color, (tab_x, 80, tab_width, 40))
            
            tab_text = self.font_medium.render(tab, True, (255, 255, 255))
            screen.blit(tab_text, (tab_x + tab_width // 2 - tab_text.get_width() // 2, 90))
        
        # 绘制商品列表
        item_height = 60
        list_y = 140
        list_x = 50
        list_width = WINDOW_WIDTH - 100
        
        # 绘制可见的商品
        visible_items = self.items_for_sale[self.scroll_offset:self.scroll_offset + self.max_visible_items]
        for i, item in enumerate(visible_items):
            item_index = i + self.scroll_offset
            item_y = list_y + i * item_height
            
            # 绘制商品背景
            item_color = (100, 150, 100) if item_index == self.selected_item_index else (70, 100, 70)
            pygame.draw.rect(screen, item_color, (list_x, item_y, list_width, item_height))
            
            # 绘制商品名称
            name_text = self.font_medium.render(item["name"], True, (255, 255, 255))
            screen.blit(name_text, (list_x + 10, item_y + 10))
            
            # 绘制商品价格
            if self.current_tab == "出售":
                # 显示考虑等级加成后的最终价格
                final_price = item.get("final_price", item["price"])
                price_text = self.font.render(f"售价: {final_price} 金币 (数量: {item['quantity']})", True, (255, 255, 0))
            else:
                price_text = self.font.render(f"价格: {item['price']} 金币", True, (255, 255, 0))
            screen.blit(price_text, (list_x + 10, item_y + 35))
            
            # 绘制商品描述
            desc_text = self.font.render(item["description"], True, (200, 200, 200))
            screen.blit(desc_text, (list_x + 300, item_y + 20))
        
        # 绘制玩家信息
        money_text = self.font_medium.render(f"金钱: {self.player.money} 金币", True, (255, 255, 0))
        screen.blit(money_text, (50, WINDOW_HEIGHT - 100))
        
        # 绘制操作提示
        controls_text = self.font.render("方向键: 选择商品  回车: 购买/出售  ESC: 返回农场", True, (255, 255, 255))
        screen.blit(controls_text, (WINDOW_WIDTH // 2 - controls_text.get_width() // 2, WINDOW_HEIGHT - 50))
        
        # 绘制状态消息
        if self.status_message and pygame.time.get_ticks() < self.status_time:
            status_text = self.font_medium.render(self.status_message, True, (255, 255, 255))
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 150))
            
            # 绘制背景
            bg_rect = status_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            
            screen.blit(status_text, status_rect)