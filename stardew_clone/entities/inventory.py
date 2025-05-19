import pygame
from utils.font_manager import font_manager
class Inventory:
    """物品栏类，管理玩家的物品和工具"""
    
    def __init__(self, db_manager, player_id, game=None):
        """初始化物品栏
        
        Args:
            db_manager: 数据库管理器实例
            player_id: 玩家ID
            game: 游戏实例，用于获取图像管理器
        """
        self.db = db_manager
        self.player_id = player_id
        self.game = game
        self.selected_slot = 0  # 当前选中的物品槽
        self.slots_per_row = 8  # 每行显示的物品槽数量
        self.slot_size = 64     # 物品槽大小
        self.margin = 10        # 物品槽之间的间距
        
        # 加载物品和工具
        self.refresh()
    
    def refresh(self):
        """从数据库刷新物品和工具"""
        self.items = self.db.get_inventory(self.player_id)
        self.tools = self.db.get_tools(self.player_id)
    
    def get_selected_item(self):
        """获取当前选中的物品或工具
        
        Returns:
            选中的物品或工具，如果没有则返回None
        """
        all_items = self.items + self.tools
        if 0 <= self.selected_slot < len(all_items):
            return all_items[self.selected_slot]
        return None
    
    def add_item(self, item_name, quantity, item_type):
        """添加物品到物品栏
        
        Args:
            item_name: 物品名称
            quantity: 数量
            item_type: 物品类型
        """
        self.db.add_inventory_item(self.player_id, item_name, quantity, item_type)
        self.refresh()
    
    def remove_item(self, item_id, quantity):
        """从物品栏移除物品
        
        Args:
            item_id: 物品ID
            quantity: 要移除的数量
            
        Returns:
            是否成功移除
        """
        for item in self.items:
            if item["id"] == item_id:
                if item["quantity"] >= quantity:
                    # 更新物品数量
                    new_quantity = item["quantity"] - quantity
                    self.db.update_inventory_item(item_id, new_quantity)
                    self.refresh()
                    return True
                break
        return False
    
    def has_item(self, item_name, item_type, quantity=1):
        """检查物品栏是否有指定物品
        
        Args:
            item_name: 物品名称
            item_type: 物品类型
            quantity: 需要的数量
            
        Returns:
            是否有足够的物品
        """
        for item in self.items:
            if item["item_name"] == item_name and item["item_type"] == item_type:
                if item["quantity"] >= quantity:
                    return True
        return False
    
    def get_item_id(self, item_name, item_type):
        """获取指定物品的ID
        
        Args:
            item_name: 物品名称
            item_type: 物品类型
            
        Returns:
            物品ID，如果没有找到则返回None
        """
        for item in self.items:
            if item["item_name"] == item_name and item["item_type"] == item_type:
                return item["id"]
        return None
    
    def handle_event(self, event):
        """处理物品栏相关的事件
        
        Args:
            event: pygame事件
            
        Returns:
            是否处理了事件
        """
        if event.type == pygame.KEYDOWN:
            # 数字键1-9选择物品槽
            if pygame.K_1 <= event.key <= pygame.K_9:
                slot = event.key - pygame.K_1
                all_items = self.items + self.tools
                if slot < len(all_items):
                    self.selected_slot = slot
                    return True
            # 鼠标滚轮切换物品槽 (应该用原始列表长度)
            elif event.key == pygame.K_TAB:
                all_items_origin = self.items + self.tools # 使用原始列表
                if all_items_origin:
                    self.selected_slot = (self.selected_slot + 1) % len(all_items_origin)
                    return True
        
        return False
    
    def render(self, screen, x, y):
        """渲染物品栏
        
        Args:
            screen: pygame屏幕对象
            x: 物品栏左上角X坐标
            y: 物品栏左上角Y坐标
        """
        # 过滤掉所有 item_type 为“产品”的物品，只显示“种子”、工具和其他可用物品
        filtered_items = []
        filtered_indices = []
        for idx, item in enumerate(self.items):
            if item["item_type"] != "产品":
                filtered_items.append(item)
                filtered_indices.append(idx)
        all_items = filtered_items + self.tools
    
        # 计算当前选中槽在过滤后 all_items 中的索引
        selected_index = None
        all_items_origin = self.items + self.tools # 原始完整列表
    
        if 0 <= self.selected_slot < len(all_items_origin):
            # Case 1: Selected item is a tool
            if self.selected_slot >= len(self.items):
                tool_index_in_origin = self.selected_slot - len(self.items)
                selected_index = len(filtered_items) + tool_index_in_origin
            else:
                original_item_index = self.selected_slot
                original_selected_item = self.items[original_item_index]
                if original_selected_item.get("item_type") != "产品":
                    num_preceding_filtered = 0
                    for i in range(original_item_index):
                        if self.items[i].get("item_type") != "产品":
                            num_preceding_filtered += 1
                    selected_index = num_preceding_filtered
    
        for i, item in enumerate(all_items):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            slot_x = x + col * (self.slot_size + self.margin)
            slot_y = y + row * (self.slot_size + self.margin)
    
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            pygame.draw.rect(screen, (100, 100, 100), slot_rect)
            if self.game and hasattr(self.game, 'image_manager') and "item_type" in item:
                if item["item_type"] == "种子":
                    pygame.draw.rect(screen, (210, 180, 140), slot_rect)
                elif item["item_type"] == "作物":
                    pygame.draw.rect(screen, (144, 238, 144), slot_rect)
                elif item["item_type"] == "产品":
                    pygame.draw.rect(screen, (173, 216, 230), slot_rect)
                elif item["item_type"] == "饲料":
                    pygame.draw.rect(screen, (255, 218, 185), slot_rect)
    
            if i == selected_index:
                pygame.draw.rect(screen, (200, 200, 100), slot_rect)
    
            font = font_manager.get_font(14)
            number_text = font.render(str(i+1), True, (255,255,255))
            number_width = number_text.get_width()
            screen.blit(number_text, (slot_x + self.slot_size - number_width - 4, slot_y + 2))
    
            icon_rect = pygame.Rect(
                slot_x + 10, slot_y + 10,
                self.slot_size - 20, self.slot_size - 20
            )
    
            if self.game and hasattr(self.game, 'image_manager'):
                if "item_type" in item:
                    category = "items"
                    name = item["item_name"]
                    if item["item_type"] == "种子": category = "seeds"
                    elif item["item_type"] == "作物": category = "crops"
                    elif item["item_type"] == "产品": category = "products"
                    elif item["item_type"] == "饲料": category = "feeds"
    
                    if category != "products":
                        item_image = self.game.image_manager.load_image(category, name)
                        item_image = pygame.transform.scale(item_image, (icon_rect.width, icon_rect.height))
                        screen.blit(item_image, icon_rect)
                else:
                    tool_name = item["tool_name"]
                    tool_image = self.game.image_manager.load_image("tools", tool_name)
                    tool_image = pygame.transform.scale(tool_image, (icon_rect.width, icon_rect.height))
                    screen.blit(tool_image, icon_rect)
            else:
                if "item_type" in item:
                    if item["item_type"] == "种子": color = (139, 69, 19)
                    elif item["item_type"] == "作物": color = (0, 255, 0)
                    elif item["item_type"] == "产品": color = (255, 223, 0)
                    elif item["item_type"] == "饲料": color = (255, 218, 185)
                    else: color = (200, 200, 200)
                else:
                    if item["tool_name"] == "锄头": color = (139, 69, 19)
                    elif item["tool_name"] == "水壶": color = (0, 0, 255)
                    elif item["tool_name"] == "镰刀": color = (255, 215, 0)
                    else: color = (150, 150, 150)
                pygame.draw.rect(screen, color, icon_rect)
    
            if "quantity" in item:
                font = font_manager.get_font(14)
                text = font.render(str(item["quantity"]), True, (255, 255, 255))
                screen.blit(text, (slot_x + self.slot_size - 20, slot_y + self.slot_size - 20))
    
            if i == selected_index:
                pygame.draw.rect(screen, (255, 255, 0), slot_rect, 3)
            else:
                pygame.draw.rect(screen, (50, 50, 50), slot_rect, 2)
    
            name = item.get("item_name", item.get("tool_name", ""))
            if len(name) > 8:
                name = name[:7] + "..."
            name_text = font.render(name, True, (255, 255, 255))
            screen.blit(name_text, (slot_x + 5, slot_y + 5))