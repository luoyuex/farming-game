import pygame
import datetime
import random
import math
from config import FARM_WIDTH, FARM_HEIGHT, TILE_SIZE, ENERGY_COSTS
from entities.inventory import Inventory
from entities.crop import Crop
from entities.animal import Animal
from entities.area import Area
from utils.font_manager import font_manager
from utils.audio_manager import audio_manager
from utils.image_manager import image_manager

class FarmScene:
    """农场场景，游戏的主要场景"""
    
    def __init__(self, game):
        """初始化农场场景
        
        Args:
            game: 游戏实例
        """
        self.game = game
        self.db = game.db
        
        # 字体 - 使用系统默认字体以支持中文
        self.font = font_manager.get_font(20)
        self.font_medium = font_manager.get_font(28)
        
        # 农场网格
        self.grid = [[None for _ in range(FARM_WIDTH)] for _ in range(FARM_HEIGHT)]
        
        # 玩家
        self.player = None
        
        # 物品栏
        self.inventory = None
        
        # 作物列表
        self.crops = []
        
        # 动物列表
        self.animals = []
        
        # 区域列表
        self.areas = []
        
        # 装饰树木列表
        self.trees = []
        
        # 农场外的花草装饰列表
        self.decorations = []
        
        # 相机偏移
        self.camera_x = 0
        self.camera_y = 0
        
        # 游戏时间
        self.game_time = 0  # 游戏内分钟数
        self.day = 1
        
        # 天气系统
        self.weather = "晴天"  # 默认为晴天，可选值："晴天"、"雨天"
        self.rain_drops = []  # 雨滴效果
        self.rain_intensity = 100  # 雨滴数量
        self.rain_speed = 5  # 雨滴下落速度
        
        # 状态提示
        self.status_message = ""
        self.status_time = 0
        
        # UI状态
        self.show_menu = False
        self.menu_options = ["前往市场", "睡觉 (结束当天)", "保存并退出"]
        self.selected_menu_option = 0
    
    def save_tilled_land(self):
        """保存所有耕地状态到数据库或存档文件"""
        # 示例：保存为玩家自定义表或json字段，具体实现需结合你的db_manager
        tilled_list = []
        for y in range(FARM_HEIGHT):
            for x in range(FARM_WIDTH):
                tile = self.grid[y][x]
                if tile and tile["type"] == "tilled":
                    tilled_list.append({"x": x, "y": y, "watered": tile.get("watered", False)})
        self.db.save_tilled_land(self.game.player_id, tilled_list)
    
    def load_areas(self):
        """从数据库加载区域"""
        self.areas = []
        # 假设db_manager有get_areas方法
        areas_data = self.db.get_areas(self.game.player_id) if hasattr(self.db, 'get_areas') else []
        
        for area_data in areas_data:
            area = Area(
                area_data["x"], 
                area_data["y"], 
                area_data["width"], 
                area_data["height"], 
                area_data["area_type"],
                db_manager=self.db, 
                area_id=area_data["id"],
                game=self.game
            )
            self.areas.append(area)
    
    def create_default_areas(self):
        """创建默认区域划分"""
        # 创建种植区（左侧区域，避开左上角）
        planting_area = Area(
            x=9, 
            y=1, 
            width=6, 
            height=5, 
            area_type=Area.PLANTING,
            db_manager=self.db,
            player_id=self.game.player_id,
            game=self.game
        )
        self.areas.append(planting_area)
        
        # 创建饲养区（右侧区域，位置更靠上）
        breeding_area = Area(
            x=9, 
            y=7, 
            width=6, 
            height=4, 
            area_type=Area.BREEDING,
            db_manager=self.db,
            player_id=self.game.player_id,
            game=self.game
        )
        self.areas.append(breeding_area)
        
        # 创建住宅区（底部中央区域）
        housing_area = Area(
            x=0, 
            y=7, 
            width=4, 
            height=4, 
            area_type=Area.HOUSING,
            db_manager=self.db,
            player_id=self.game.player_id,
            game=self.game
        )
        self.areas.append(housing_area)
    
    def load_tilled_land(self):
        """从数据库或存档文件加载耕地状态"""
        tilled_list = self.db.get_tilled_land(self.game.player_id)
        if tilled_list:
            for info in tilled_list:
                x, y = info["x"], info["y"]
                if 0 <= x < FARM_WIDTH and 0 <= y < FARM_HEIGHT:
                    self.grid[y][x] = {"type": "tilled", "watered": info.get("watered", False)}
    
    def setup(self, **kwargs):
        """设置场景参数
        
        Args:
            **kwargs: 场景参数
        """
        # 加载玩家
        from entities.player import Player
        self.player = Player(self.db, self.game.player_id, game=self.game)
        # 恢复天数
        player_data = self.db.get_player(self.game.player_id)
        if player_data and "day" in player_data:
            self.day = player_data["day"]
        else:
            self.day = 1
        
        # 初始化物品栏
        self.inventory = Inventory(self.db, self.game.player_id, game=self.game)
        
        # 加载作物
        self.load_crops()
        
        # 加载动物
        self.load_animals()
        # 加载耕地
        self.load_tilled_land()
        # 加载区域
        self.load_areas()
        
        # 如果没有区域，创建默认区域
        if not self.areas:
            self.create_default_areas()
            
        # 生成装饰树木
        self.generate_trees()
        
        # 生成农场外的花草装饰
        self.generate_decorations()
            
        # 播放背景音乐
        audio_manager.play_music()
    
    def load_crops(self):
        """从数据库加载作物"""
        self.crops = []
        crops_data = self.db.get_crops(self.game.player_id)
        
        for crop_data in crops_data:
            crop = Crop(self.db, crop_data["id"], load_from_db=True, game=self.game)
            self.crops.append(crop)
            
            # 更新农场网格
            if 0 <= crop.x < FARM_WIDTH and 0 <= crop.y < FARM_HEIGHT:
                self.grid[crop.y][crop.x] = {"type": "crop", "id": crop.id}
    
    def load_animals(self):
        """从数据库加载动物"""
        self.animals = []
        animals_data = self.db.get_animals(self.game.player_id)
        
        for animal_data in animals_data:
            animal = Animal(self.db, animal_data["id"], load_from_db=True, game=self.game)
            self.animals.append(animal)
            
    def generate_trees(self):
        """生成装饰性树木
        
        在非功能区域（种植区、饲养区和住宅区之外）随机生成树木
        """
        # 导入image_manager以确保它已被初始化
        from utils.image_manager import image_manager
        
        # 清空现有树木
        self.trees = []
        
        # 加载树木图像
        tree_image = image_manager.load_svg("decorations/tree.svg", (TILE_SIZE * 2, TILE_SIZE * 2.5))
        
        # 创建一个二维数组，标记哪些区域是功能区
        occupied = [[False for _ in range(FARM_WIDTH)] for _ in range(FARM_HEIGHT)]
        
        # 标记所有功能区域
        for area in self.areas:
            for y in range(area.y, area.y + area.height):
                for x in range(area.x, area.x + area.width):
                    if 0 <= x < FARM_WIDTH and 0 <= y < FARM_HEIGHT:
                        occupied[y][x] = True
        
        # 在非功能区域随机生成树木
        num_trees = random.randint(10, 20)  # 随机生成10-20棵树
        attempts = 0
        trees_added = 0
        
        while trees_added < num_trees and attempts < 100:
            attempts += 1
            
            # 随机选择位置
            x = random.randint(1, FARM_WIDTH - 2)  # 避开边界
            y = random.randint(1, FARM_HEIGHT - 2)  # 避开边界
            
            # 检查是否在功能区域内
            if not occupied[y][x]:
                # 检查周围是否有其他树木（避免树木过于密集）
                too_close = False
                for tree in self.trees:
                    tree_x, tree_y = tree["position"]
                    if abs(tree_x - x) < 3 and abs(tree_y - y) < 3:
                        too_close = True
                        break
                
                if not too_close:
                    # 添加树木
                    self.trees.append({
                        "position": (x, y),
                        "image": tree_image,
                        "size": random.uniform(0.8, 1.2)  # 随机大小变化
                    })
                    trees_added += 1
                    
                    # 标记树木位置及周围为已占用
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < FARM_WIDTH and 0 <= ny < FARM_HEIGHT:
                                occupied[ny][nx] = True
    
    def generate_decorations(self):
        """生成农场外的花草装饰
        
        在农场边界外随机生成花草装饰元素，增加场景美观度
        """
        # 导入image_manager以确保它已被初始化
        from utils.image_manager import image_manager
        
        # 清空现有装饰
        self.decorations = []
        
        # 加载花草图像
        flower_types = ["flower_red", "flower_blue", "flower_yellow", "grass_tall", "grass_short"]
        flower_images = {}
        for flower_type in flower_types:
            try:
                # 尝试加载SVG图像，如果不存在则创建占位符
                flower_images[flower_type] = image_manager.load_svg(f"decorations/{flower_type}.svg", (TILE_SIZE, TILE_SIZE))
            except Exception as e:
                # 创建占位符图像
                placeholder = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                if "flower" in flower_type:
                    if "red" in flower_type:
                        color = (255, 100, 100)  # 红花
                    elif "blue" in flower_type:
                        color = (100, 100, 255)  # 蓝花
                    elif "yellow" in flower_type:
                        color = (255, 255, 100)  # 黄花
                    else:
                        color = (255, 200, 200)  # 默认粉色
                else:  # 草
                    if "tall" in flower_type:
                        color = (100, 200, 100)  # 深绿色高草
                    else:
                        color = (150, 230, 150)  # 浅绿色矮草
                
                # 绘制简单的花或草形状
                if "flower" in flower_type:
                    # 绘制花朵中心
                    center_x, center_y = TILE_SIZE // 2, TILE_SIZE // 2
                    radius = TILE_SIZE // 4
                    pygame.draw.circle(placeholder, color, (center_x, center_y), radius)
                    # 绘制花瓣
                    for i in range(6):
                        angle = i * (2 * math.pi / 6)
                        petal_x = center_x + int(radius * 1.5 * math.cos(angle))
                        petal_y = center_y + int(radius * 1.5 * math.sin(angle))
                        pygame.draw.circle(placeholder, color, (petal_x, petal_y), radius // 2)
                    # 绘制茎
                    stem_color = (100, 180, 100)
                    pygame.draw.rect(placeholder, stem_color, (center_x - 2, center_y + radius, 4, TILE_SIZE // 2))
                else:  # 草
                    # 绘制草叶
                    height = TILE_SIZE // 2 if "short" in flower_type else TILE_SIZE * 3 // 4
                    for i in range(5):
                        start_x = TILE_SIZE // 2 + random.randint(-TILE_SIZE // 4, TILE_SIZE // 4)
                        end_x = start_x + random.randint(-TILE_SIZE // 4, TILE_SIZE // 4)
                        pygame.draw.line(placeholder, color, (start_x, TILE_SIZE), (end_x, TILE_SIZE - height), 2)
                
                flower_images[flower_type] = placeholder
        
        # 定义农场外的区域范围（扩展农场边界外10个瓦片）
        outer_range = 10
        
        # 生成农场外的花草装饰
        num_decorations = random.randint(80, 150)  # 生成大量花草
        
        for _ in range(num_decorations):
            # 随机选择位置（农场外的区域）
            position_type = random.randint(1, 4)  # 1=上方, 2=右侧, 3=下方, 4=左侧
            
            if position_type == 1:  # 上方
                x = random.randint(-outer_range, FARM_WIDTH + outer_range)
                y = random.randint(-outer_range, -1)
            elif position_type == 2:  # 右侧
                x = random.randint(FARM_WIDTH, FARM_WIDTH + outer_range)
                y = random.randint(-outer_range, FARM_HEIGHT + outer_range)
            elif position_type == 3:  # 下方
                x = random.randint(-outer_range, FARM_WIDTH + outer_range)
                y = random.randint(FARM_HEIGHT, FARM_HEIGHT + outer_range)
            else:  # 左侧
                x = random.randint(-outer_range, -1)
                y = random.randint(-outer_range, FARM_HEIGHT + outer_range)
            
            # 随机选择花草类型
            flower_type = random.choice(flower_types)
            
            # 添加花草装饰
            self.decorations.append({
                "position": (x, y),
                "image": flower_images[flower_type],
                "type": flower_type,
                "size": random.uniform(0.7, 1.3),  # 随机大小变化
                "rotation": random.uniform(0, 360),  # 随机旋转角度
                "z_index": random.randint(0, 2)  # 随机深度，用于层次感
            })
    
    def render_trees(self, screen):
        """渲染装饰性树木
        
        Args:
            screen: pygame屏幕对象
        """
        for tree in self.trees:
            x, y = tree["position"]
            image = tree["image"]
            size = tree["size"]
            
            # 计算屏幕位置
            screen_x = x * TILE_SIZE - self.camera_x
            screen_y = y * TILE_SIZE - self.camera_y
            
            # 扩大渲染范围，确保即使玩家移动到农场边界外，树木仍然可见
            if (-TILE_SIZE * 5 < screen_x < screen.get_width() + TILE_SIZE * 5 and
                -TILE_SIZE * 5 < screen_y < screen.get_height() + TILE_SIZE * 5):
                
                # 计算缩放后的尺寸
                width = int(image.get_width() * size)
                height = int(image.get_height() * size)
                
                # 缩放图像
                scaled_image = pygame.transform.scale(image, (width, height))
                
                # 绘制树木
                screen.blit(scaled_image, (screen_x - width // 4, screen_y - height // 2))
    
    def render_decorations(self, screen):
        """渲染农场外的花草装饰
        
        Args:
            screen: pygame屏幕对象
        """
        # 按z_index排序装饰元素，确保正确的层次感
        sorted_decorations = sorted(self.decorations, key=lambda x: x["z_index"])
        
        for decoration in sorted_decorations:
            x, y = decoration["position"]
            image = decoration["image"]
            size = decoration["size"]
            rotation = decoration["rotation"]
            
            # 计算屏幕位置
            screen_x = x * TILE_SIZE - self.camera_x
            screen_y = y * TILE_SIZE - self.camera_y
            
            # 扩大渲染范围，确保即使玩家移动到农场边界外，装饰元素仍然可见
            if (-TILE_SIZE * 15 < screen_x < screen.get_width() + TILE_SIZE * 15 and
                -TILE_SIZE * 15 < screen_y < screen.get_height() + TILE_SIZE * 15):
                
                # 计算缩放后的尺寸
                width = int(image.get_width() * size)
                height = int(image.get_height() * size)
                
                # 缩放图像
                scaled_image = pygame.transform.scale(image, (width, height))
                
                # 旋转图像
                rotated_image = pygame.transform.rotate(scaled_image, rotation)
                
                # 获取旋转后的矩形，以便正确定位
                rot_rect = rotated_image.get_rect(center=(width//2, height//2))
                
                # 绘制装饰元素
                screen.blit(rotated_image, (screen_x - rot_rect.width//2, screen_y - rot_rect.height//2))
                
                # 如果是雨天，为花朵添加雨滴效果
                if self.weather == "雨天" and "flower" in decoration["type"]:
                    # 随机添加雨滴效果（闪光点）
                    if random.random() < 0.05:  # 5%的概率在每一帧添加闪光
                        drop_x = screen_x + random.randint(0, width) - width//2
                        drop_y = screen_y + random.randint(0, height//2) - height//4
                        drop_size = random.randint(1, 3)
                        pygame.draw.circle(screen, (220, 220, 255), (drop_x, drop_y), drop_size)
    
    def handle_event(self, event):
        """处理输入事件
        
        Args:
            event: pygame事件
        """
        if self.show_menu:
            # 处理菜单选择
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_menu_option = (self.selected_menu_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_menu_option = (self.selected_menu_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    self.select_menu_option()
                elif event.key == pygame.K_ESCAPE:
                    self.show_menu = False
            return
        
        # 处理物品栏事件
        if self.inventory.handle_event(event):
            return
        
        # 处理玩家输入
        if event.type == pygame.KEYDOWN:
            # 移动（不受农场边界限制，玩家可以自由移动）
            if event.key == pygame.K_w:
                self.player.y -= TILE_SIZE
            elif event.key == pygame.K_s:
                self.player.y += TILE_SIZE
            elif event.key == pygame.K_a:
                self.player.x -= TILE_SIZE
                self.player.direction = "left"
            elif event.key == pygame.K_d:
                self.player.x += TILE_SIZE
                self.player.direction = "right"
            # 使用工具/物品
            elif event.key == pygame.K_SPACE:
                self.use_selected_item()
            # 打开菜单
            elif event.key == pygame.K_ESCAPE:
                self.show_menu = True
        # 新增：处理鼠标点击动物
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            # 转换为世界坐标
            world_x = mouse_x + self.camera_x
            world_y = mouse_y + self.camera_y
            for animal in self.animals:
                animal_rect = pygame.Rect(animal.x, animal.y, TILE_SIZE * 1.5, TILE_SIZE * 1.5)
                if animal_rect.collidepoint(world_x, world_y):
                    # 检查是否在饲养区内
                    tile_x = int(animal.x / TILE_SIZE)
                    tile_y = int(animal.y / TILE_SIZE)
                    in_breeding_area = False
                    for area in self.areas:
                        if area.area_type == Area.BREEDING and area.contains_point(tile_x, tile_y):
                            in_breeding_area = True
                            break
                    
                    if not in_breeding_area:
                        self.show_status(f"{animal.name}不在饲养区内，无法互动！")
                        return
                    
                    # 优先检查动物是否可以产出产品
                    if animal.can_produce():
                        # 动物可以产出产品，尝试收集
                        result = animal.collect_product()
                        if result:
                            product_name, qty, exp = result
                            self.db.add_inventory_item(self.game.player_id, product_name, qty, "动物产品")
                            self.show_status(f"收获{animal.name}的{product_name}！")
                            return
                    
                    # 如果没有产品可收集，检查是否需要喂食
                    if not animal.is_fed:
                        # 获取当前选中的物品
                        selected_item = self.inventory.get_selected_item()
                        if not selected_item or "item_type" not in selected_item or selected_item["item_type"] != "饲料":
                            self.show_status(f"请选择正确的饲料来喂食{animal.name}！")
                            return
                            
                        if "item_name" in selected_item and animal.feed(selected_item["item_name"]):
                            # 消耗一个饲料
                            if "id" in selected_item:
                                self.inventory.remove_item(selected_item["id"], 1)
                            self.show_status(f"成功给{animal.name}喂食！")
                        else:
                            self.show_status(f"这不是{animal.name}的专用饲料！")
                    else:
                        # 动物已经喂过食了，但没有产品可收集
                        selected_item = self.inventory.get_selected_item()
                        if selected_item and "item_type" in selected_item and selected_item["item_type"] == "饲料":
                            self.show_status(f"{animal.name}今天已经喂过食了！")
                        else:
                            self.show_status(f"{animal.name}暂时没有可收获的产品！")
                    break
    
    def select_menu_option(self):
        """处理菜单选项选择"""
        option = self.menu_options[self.selected_menu_option]
        
        if option == "前往市场":
            # 保存玩家状态
            self.player.save()
            self.save_tilled_land()
            # 保存天数
            self.db.update_player(self.game.player_id, day=self.day)
            # 播放成功音效
            audio_manager.play_sound("success")
            # 切换到市场场景
            self.game.change_scene("market")
        
        elif option == "睡觉 (结束当天)":
            # 结束当天
            self.end_day()
            # 播放成功音效
            audio_manager.play_sound("success")
        
        elif option == "保存并退出":
            # 保存玩家状态
            self.player.save()
            self.save_tilled_land()
            # 保存天数
            self.db.update_player(self.game.player_id, day=self.day)
            # 播放成功音效
            audio_manager.play_sound("success")
            # 返回主菜单
            self.game.player_id = None
            self.game.change_scene("main_menu")
        
        # 关闭菜单
        self.show_menu = False
    
    def use_selected_item(self):
        """使用当前选中的物品或工具"""
        selected_item = self.inventory.get_selected_item()
        if not selected_item:
            return
        # 获取玩家前方的瓦片坐标
        tile_x = int(self.player.x / TILE_SIZE)
        tile_y = int(self.player.y / TILE_SIZE)
        # 根据玩家朝向调整目标瓦片
        if self.player.direction == "right":
            tile_x += 1
        elif self.player.direction == "left":
            tile_x -= 1
        # 检查坐标是否在农场范围内
        if not (0 <= tile_x < FARM_WIDTH and 0 <= tile_y < FARM_HEIGHT):
            self.show_status("超出农场范围！")
            return
        # 检查是否在动物附近
        for animal in self.animals:
            animal_tile_x = int(animal.x / TILE_SIZE)
            animal_tile_y = int(animal.y / TILE_SIZE)
            # 如果在动物旁边
            if abs(tile_x - animal_tile_x) <= 1 and abs(tile_y - animal_tile_y) <= 1:
                # 如果是饲料
                if "item_type" in selected_item and selected_item["item_type"] == "饲料":
                    # 检查动物是否已经喂过食
                    if animal.is_fed:
                        self.show_status(f"{animal.name}今天已经喂过食了！")
                        return
                    # 尝试喂食，传入饲料名称进行检查
                    if "item_name" in selected_item and animal.feed(selected_item["item_name"]):
                        # 成功喂食，减少饲料数量
                        if "id" in selected_item:
                            self.inventory.remove_item(selected_item["id"], 1)
                        self.show_status(f"成功给{animal.name}喂食！")
                        return
                    else:
                        self.show_status(f"这不是{animal.name}的专用饲料！")
                        return
        # 优先判断是否为种子，处理种植逻辑
        if "item_type" in selected_item and selected_item["item_type"] == "种子":
            self.use_item(selected_item, tile_x, tile_y)
            return
        # 工具使用逻辑
        if "tool_name" in selected_item:
            self.use_tool(selected_item, tile_x, tile_y)
            return
        # 其他物品（如作物等）
        if "item_type" in selected_item:
            self.use_item(selected_item, tile_x, tile_y)
    
    def use_tool(self, tool, tile_x, tile_y):
        """使用工具
        
        Args:
            tool: 工具信息
            tile_x: 目标X坐标
            tile_y: 目标Y坐标
        """
        # 检查工具信息是否完整
        if "tool_name" not in tool:
            self.show_status("无法使用此工具！")
            return
            
        # 检查能量是否足够
        energy_cost = 0
        
        if tool["tool_name"] == "锄头":
            # 严格检查是否在种植区内
            in_planting_area = False
            for area in self.areas:
                if area.area_type == Area.PLANTING and area.contains_point(tile_x, tile_y):
                    in_planting_area = True
                    break
            
            if not in_planting_area:
                self.show_status("只能在种植区内使用锄头！")
                return
                
            energy_cost = ENERGY_COSTS["till"]
            if not self.player.use_energy(energy_cost):
                self.show_status("能量不足！")
                return
            
            # 检查瓦片是否为空
            if self.grid[tile_y][tile_x] is None:
                # 耕地
                self.grid[tile_y][tile_x] = {"type": "tilled", "watered": False}
                # 播放锄地音效
                audio_manager.play_sound("hoe")
                self.show_status("耕地成功！")
            else:
                self.show_status("这里已经有东西了！")
        
        elif tool["tool_name"] == "水壶":
            energy_cost = ENERGY_COSTS["water"]
            if not self.player.use_energy(energy_cost):
                self.show_status("能量不足！")
                return
            
            # 检查是否有作物或耕地
            tile = self.grid[tile_y][tile_x]
            if tile and tile["type"] == "tilled":
                # 浇水
                tile["watered"] = True
                # 播放浇水音效
                audio_manager.play_sound("water")
                self.show_status("浇水成功！")
            elif tile and tile["type"] == "crop":
                # 找到对应的作物对象
                for crop in self.crops:
                    if crop.id == tile["id"]:
                        if crop.is_fully_grown():
                            self.show_status("这株作物已经成熟，不需要浇水！")
                        elif crop.water():
                            # 播放浇水音效
                            audio_manager.play_sound("water")
                            self.show_status("浇水成功！")
                        else:
                            self.show_status("这株作物今天已经浇过水了！")
                        break
            else:
                self.show_status("这里没有需要浇水的地方！")
        
        elif tool["tool_name"] == "镰刀":
            energy_cost = ENERGY_COSTS["harvest"]
            if not self.player.use_energy(energy_cost):
                self.show_status("能量不足！")
                return
            
            # 检查是否有成熟的作物
            tile = self.grid[tile_y][tile_x]
            if tile and tile["type"] == "crop":
                # 找到对应的作物对象
                for i, crop in enumerate(self.crops):
                    if crop.id == tile["id"] and crop.is_fully_grown():
                        # 收获作物
                        harvest_result = crop.harvest()
                        if harvest_result:
                            crop_name, quantity, exp = harvest_result
                            
                            # 添加到物品栏
                            self.player.add_item(crop_name, quantity, "作物")
                            
                            # 增加经验
                            level_up = self.player.add_exp(exp)
                            
                            # 从列表中移除作物
                            self.crops.pop(i)
                            
                            # 清除网格
                            self.grid[tile_y][tile_x] = {"type": "tilled", "watered": False}
                            
                            # 播放收获音效
                            audio_manager.play_sound("axe")
                            
                            if level_up:
                                # 播放升级音效
                                audio_manager.play_sound("success")
                                self.show_status(f"收获了 {crop_name}！升级了！")
                            else:
                                self.show_status(f"收获了 {crop_name}！+{exp}经验")
                        break
                else:
                    self.show_status("这株作物还没有成熟！")
            else:
                self.show_status("这里没有可收获的作物！")
    
    def use_item(self, item, tile_x, tile_y):
        """使用物品
        
        Args:
            item: 物品信息
            tile_x: 目标X坐标
            tile_y: 目标Y坐标
        """
        if "item_type" not in item:
            self.show_status("无法使用此物品！")
            return
            
        if item["item_type"] == "种子":
            # 严格检查是否在种植区内
            in_planting_area = False
            for area in self.areas:
                if area.area_type == Area.PLANTING and area.contains_point(tile_x, tile_y):
                    in_planting_area = True
                    break
            
            if not in_planting_area:
                self.show_status("只能在种植区内种植作物！")
                return
                
            # 检查瓦片是否为耕地
            tile = self.grid[tile_y][tile_x]
            if tile and tile["type"] == "tilled":
                # 获取作物类型（去掉"种子"后缀）
                if "item_name" not in item:
                    self.show_status("种子信息不完整！")
                    return
                    
                crop_type = item["item_name"].replace("种子", "")
                
                # 创建新作物
                crop = Crop(
                    self.db, 
                    player_id=self.game.player_id, 
                    crop_type=crop_type, 
                    x=tile_x, 
                    y=tile_y,
                    game=self.game
                )
                
                # 添加到作物列表
                self.crops.append(crop)
                
                # 更新网格
                self.grid[tile_y][tile_x] = {"type": "crop", "id": crop.id}
                
                # 从物品栏移除种子
                if "id" in item:
                    self.inventory.remove_item(item["id"], 1)
                    
                    # 刷新物品栏
                    self.inventory.refresh()
                
                # 播放种植音效
                audio_manager.play_sound("plant")
                
                self.show_status(f"种植了 {crop_type}！")
            else:
                self.show_status("只能在耕地上种植！")
        
        elif item["item_type"] == "食物":
            # 恢复能量
            energy_restore = 20  # 默认恢复量
            self.player.restore_energy(energy_restore)
            
            # 从物品栏移除食物
            if "id" in item:
                self.inventory.remove_item(item["id"], 1)
                
                # 刷新物品栏
                self.inventory.refresh()
            
            self.show_status(f"恢复了 {energy_restore} 点能量！")
    
    def update(self):
        """更新场景状态"""
        # 更新游戏时间
        self.game_time += 1
        
        # 检查是否需要结束当天（游戏时间超过一天）
        if self.game_time >= 24 * 60:  # 24小时 * 60分钟
            self.end_day()
        
        # 检查玩家是否进入房屋
        player_tile_x = int(self.player.x / TILE_SIZE)
        player_tile_y = int(self.player.y / TILE_SIZE)
        
        # 检查玩家是否在住宅区内
        self.player.in_house = False
        for area in self.areas:
            if area.area_type == Area.HOUSING and area.contains_point(player_tile_x, player_tile_y):
                self.player.in_house = True
                break
        
        # 更新相机位置（始终跟随玩家，保持玩家在屏幕中心）
        screen_width = self.game.screen.get_width()
        screen_height = self.game.screen.get_height()
        
        # 相机直接跟随玩家，不受农场边界限制
        self.camera_x = self.player.x - screen_width // 2
        self.camera_y = self.player.y - screen_height // 2
        
        # 更新雨滴效果
        if self.weather == "雨天":
            self.update_rain_drops(1)  # 传入默认时间增量
            # 雨天自动浇水
            self.auto_water_crops()
    
    def auto_water_crops(self):
        """雨天自动浇水所有耕地和作物"""
        if self.weather != "雨天":
            return
            
        # 遍历所有耕地，将其标记为已浇水
        for y in range(FARM_HEIGHT):
            for x in range(FARM_WIDTH):
                tile = self.grid[y][x]
                if tile and tile["type"] == "tilled":
                    tile["watered"] = True
        
        # 遍历所有作物，将其标记为已浇水
        for crop in self.crops:
            crop.is_watered = True
            # 更新数据库中的浇水状态
            self.db.update_crop(crop.id, is_watered=True)
    
    def init_rain_drops(self):
        """初始化雨滴效果"""
        self.rain_drops = []
        import random
        screen_width, screen_height = self.game.screen.get_size()
        
        # 根据雨的强度生成雨滴
        for _ in range(self.rain_intensity):
            # 随机生成雨滴位置
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            # 随机生成雨滴大小和速度
            size = random.randint(1, 3)
            speed = random.randint(self.rain_speed - 2, self.rain_speed + 2)
            # 添加雨滴
            self.rain_drops.append({
                "x": x,
                "y": y,
                "size": size,
                "speed": speed
            })
    
    def update_rain_drops(self, dt):
        """更新雨滴位置
        
        Args:
            dt: 时间增量
        """
        if self.weather != "雨天":
            return
            
        import random
        screen_width, screen_height = self.game.screen.get_size()
        
        # 更新每个雨滴的位置
        for drop in self.rain_drops:
            # 雨滴下落
            drop["y"] += drop["speed"]
            
            # 如果雨滴超出屏幕底部，重新放置到顶部
            if drop["y"] > screen_height:
                drop["y"] = random.randint(-20, 0)
                drop["x"] = random.randint(0, screen_width)
    
    def render_rain_drops(self, screen):
        """渲染雨滴效果
        
        Args:
            screen: 游戏屏幕
        """
        if self.weather != "雨天":
            return
            
        import pygame
        
        # 绘制每个雨滴
        for drop in self.rain_drops:
            # 使用浅蓝色绘制雨滴
            pygame.draw.line(
                screen,
                (200, 200, 255),  # 浅蓝色
                (drop["x"], drop["y"]),
                (drop["x"], drop["y"] + drop["size"] * 2),
                drop["size"]
            )
    
    def end_day(self):
        """结束当天，进入下一天"""
        # 重置游戏时间
        self.game_time = 0
        self.day += 1
        
        # 如果是雨天，确保所有作物都被浇水
        if self.weather == "雨天":
            self.auto_water_crops()
        
        # 作物生长
        for crop in self.crops:
            crop.grow()
        
        # 动物年龄增长和产出重置
        for animal in self.animals:
            animal.age_up()
        
        # 恢复玩家能量
        self.player.energy = self.player.max_energy
        
        # 随机生成天气
        import random
        weather_choices = ["晴天", "雨天"]
        weights = [0.7, 0.3]  # 70%概率晴天，30%概率雨天
        self.weather = random.choices(weather_choices, weights=weights, k=1)[0]
        
        # 如果是雨天，初始化雨滴效果
        if self.weather == "雨天":
            self.init_rain_drops()
            # 新的一天如果是雨天，立即浇水
            self.auto_water_crops()
        else:
            self.rain_drops = []
        
        # 保存玩家状态
        self.player.save()
        
        # 保存天数和天气
        self.db.update_player(self.game.player_id, day=self.day, weather=self.weather)
        
        weather_text = "雨天" if self.weather == "雨天" else "晴天"
        self.show_status(f"新的一天开始了！第 {self.day} 天，今天是{weather_text}。")
    
    def show_status(self, message, duration=3000):
        """显示状态消息
        
        Args:
            message: 消息内容
            duration: 显示时间（毫秒）
        """
        self.status_message = message
        self.status_time = pygame.time.get_ticks() + duration
    
    def render(self, screen):
        """渲染场景
        
        Args:
            screen: pygame屏幕对象
        """
        # 首先填充整个屏幕为草地背景色，避免黑色背景
        grass_color = (124, 218, 124) if self.weather == "雨天" else (144, 238, 144)
        screen.fill(grass_color)
        
        # 绘制农场外的花草装饰（在农场背景之前绘制，确保它们在最底层）
        self.render_decorations(screen)
        
        # 绘制农场背景（像素风格草地）
        for y in range(FARM_HEIGHT):
            for x in range(FARM_WIDTH):
                # 计算屏幕位置
                screen_x = x * TILE_SIZE - self.camera_x
                screen_y = y * TILE_SIZE - self.camera_y
                
                # 扩大渲染范围，确保即使玩家移动到农场边界外，农场边界仍然可见
                if (-TILE_SIZE * 5 < screen_x < screen.get_width() + TILE_SIZE * 5 and
                    -TILE_SIZE * 5 < screen_y < screen.get_height() + TILE_SIZE * 5):
                    # 绘制像素风格草地 - 雨天时颜色更深
                    grass_color = (124, 218, 124) if self.weather == "雨天" else (144, 238, 144)
                    grass_rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(screen, grass_color, grass_rect)  # 浅绿色草地
                    
                    # 添加草地纹理（小白点）
                    if (x + y) % 7 == 0:  # 随机分布小白点
                        dot_size = 2
                        dot_x = screen_x + (x * 13) % (TILE_SIZE - dot_size)
                        dot_y = screen_y + (y * 17) % (TILE_SIZE - dot_size)
                        dot_color = (200, 235, 200) if self.weather == "雨天" else (220, 255, 220)
                        pygame.draw.rect(screen, dot_color, (dot_x, dot_y, dot_size, dot_size))
                    
                    # 绘制耕地
                    tile = self.grid[y][x]
                    if tile and tile["type"] == "tilled":
                        tilled_rect = pygame.Rect(
                            screen_x + 2, screen_y + 2, 
                            TILE_SIZE - 4, TILE_SIZE - 4
                        )
                        pygame.draw.rect(screen, (139, 69, 19), tilled_rect)  # 棕色
                        
                        # 如果已浇水，绘制深色
                        if tile.get("watered", False):
                            watered_rect = pygame.Rect(
                                screen_x + 4, screen_y + 4, 
                                TILE_SIZE - 8, TILE_SIZE - 8
                            )
                            pygame.draw.rect(screen, (101, 67, 33), watered_rect)  # 深棕色
                
                # 绘制木栅栏边界
                # 左边界
                if x == 0:
                    fence_color = (139, 69, 19)  # 棕色木栅栏
                    # 绘制垂直木栅栏
                    fence_width = TILE_SIZE // 8
                    pygame.draw.rect(screen, fence_color, (screen_x, screen_y, fence_width, TILE_SIZE))
                    # 添加木栅栏细节
                    if y % 2 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), (screen_x, screen_y + TILE_SIZE // 4, fence_width, TILE_SIZE // 8))
                
                # 右边界
                if x == FARM_WIDTH - 1:
                    fence_color = (139, 69, 19)  # 棕色木栅栏
                    # 绘制垂直木栅栏
                    fence_width = TILE_SIZE // 8
                    pygame.draw.rect(screen, fence_color, (screen_x + TILE_SIZE - fence_width, screen_y, fence_width, TILE_SIZE))
                    # 添加木栅栏细节
                    if y % 2 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), (screen_x + TILE_SIZE - fence_width, screen_y + TILE_SIZE // 4, fence_width, TILE_SIZE // 8))
                
                # 上边界
                if y == 0:
                    fence_color = (139, 69, 19)  # 棕色木栅栏
                    # 绘制水平木栅栏
                    fence_height = TILE_SIZE // 8
                    pygame.draw.rect(screen, fence_color, (screen_x, screen_y, TILE_SIZE, fence_height))
                    # 添加木栅栏细节
                    if x % 2 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), (screen_x + TILE_SIZE // 4, screen_y, TILE_SIZE // 8, fence_height))
                
                # 下边界
                if y == FARM_HEIGHT - 1:
                    fence_color = (139, 69, 19)  # 棕色木栅栏
                    # 绘制水平木栅栏
                    fence_height = TILE_SIZE // 8
                    pygame.draw.rect(screen, fence_color, (screen_x, screen_y + TILE_SIZE - fence_height, TILE_SIZE, fence_height))
                    # 添加木栅栏细节
                    if x % 2 == 0:
                        pygame.draw.rect(screen, (160, 82, 45), (screen_x + TILE_SIZE // 4, screen_y + TILE_SIZE - fence_height, TILE_SIZE // 8, fence_height))
        
        # 绘制装饰树木（在区域和作物之前，确保它们在背景层）
        self.render_trees(screen)
        
        # 绘制区域边界
        for area in self.areas:
            area.render(screen, (self.camera_x, self.camera_y))
        
        # 绘制作物
        for crop in self.crops:
            crop.render(screen, TILE_SIZE, (self.camera_x, self.camera_y))
        
        # 绘制动物
        for i, animal in enumerate(self.animals):
            # 只在第一次加载或位置为0时设置动物位置
            if animal.x == 0 and animal.y == 0:
                # 尝试将动物放置在饲养区内
                breeding_areas = [area for area in self.areas if area.area_type == Area.BREEDING]
                if breeding_areas:
                    # 选择第一个饲养区
                    area = breeding_areas[0]
                    # 计算动物在区域内的位置
                    offset_x = (i % 3) * TILE_SIZE * 2
                    offset_y = (i // 3) * TILE_SIZE * 2
                    animal.x = (area.x + 1) * TILE_SIZE + offset_x
                    animal.y = (area.y + 1) * TILE_SIZE + offset_y
                else:
                    # 如果没有饲养区，使用默认位置
                    animal.x = (i % 5) * TILE_SIZE * 2 + TILE_SIZE * 2
                    animal.y = (i // 5) * TILE_SIZE * 2 + TILE_SIZE * 8
                animal.save()  # 保存动物位置到数据库
            animal.render(screen, animal.x, animal.y, TILE_SIZE * 1.5, (self.camera_x, self.camera_y))
            
        # 单独绘制住宅区的房屋，确保房屋显示在最上层
        for area in self.areas:
            if area.area_type == Area.HOUSING:
                # 使用区域的render方法绘制房屋
                # 区域类已经包含了加载和渲染房屋图像的逻辑
                # 这样可以确保使用SVG图像而不是简单的矩形
                area.render(screen, (self.camera_x, self.camera_y))
                
                # 注意：不再使用矩形绘制房屋，而是使用SVG图像
                # 这样可以避免出现看起来像人脸的问题
        

        
        # 绘制玩家（如果不在房子内）- 确保在房屋渲染之后绘制
        if not hasattr(self.player, 'in_house') or not self.player.in_house:
            self.player.render(screen, (self.camera_x, self.camera_y))
        else:
            # 玩家在房子内，显示提示信息
            house_text = self.font_medium.render("玩家在房子内", True, (255, 255, 255))
            text_rect = house_text.get_rect(center=(screen.get_width() // 2, 50))
            screen.blit(house_text, text_rect)
        
        # 如果是雨天，渲染雨滴
        if self.weather == "雨天":
            self.render_rain_drops(screen)
        
        # 绘制UI
        self.render_ui(screen)
        
        # 绘制菜单（如果打开）
        if self.show_menu:
            self.render_menu(screen)
    
    def render_ui(self, screen):
        """渲染UI元素
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制物品栏
        inventory_x = 10
        inventory_y = screen.get_height() - 74
        self.inventory.render(screen, inventory_x, inventory_y)
        
        # 绘制玩家信息
        info_x = 10
        info_y = 10
        
        # 玩家名称和等级
        name_text = self.font_medium.render(
            f"{self.player.name} (等级 {self.player.level})", 
            True, 
            (255, 255, 255)
        )
        screen.blit(name_text, (info_x, info_y))
        
        # 经验条
        exp_bar_width = 200
        exp_bar_height = 15
        exp_x = info_x
        exp_y = info_y + 35
        
        # 计算经验百分比
        from config import LEVEL_EXP_REQUIREMENTS
        if self.player.level < len(LEVEL_EXP_REQUIREMENTS):
            current_level_exp = LEVEL_EXP_REQUIREMENTS[self.player.level - 1]
            next_level_exp = LEVEL_EXP_REQUIREMENTS[self.player.level]
            exp_percent = (self.player.exp - current_level_exp) / (next_level_exp - current_level_exp)
        else:
            exp_percent = 1.0
        
        # 绘制经验条背景
        pygame.draw.rect(screen, (50, 50, 50), (exp_x, exp_y, exp_bar_width, exp_bar_height))
        
        # 绘制经验条
        if exp_percent > 0:
            pygame.draw.rect(
                screen, 
                (0, 255, 255), 
                (exp_x, exp_y, int(exp_bar_width * exp_percent), exp_bar_height)
            )
        
        # 经验文本
        exp_text = self.font.render(
            f"经验: {self.player.exp}", 
            True, 
            (255, 255, 255)
        )
        screen.blit(exp_text, (exp_x, exp_y + exp_bar_height + 5))
        
        # 金钱
        money_text = self.font.render(
            f"金钱: {self.player.money}", 
            True, 
            (255, 255, 0)
        )
        screen.blit(money_text, (info_x, info_y + 70))
        
        # 能量条
        energy_bar_width = 200
        energy_bar_height = 15
        energy_x = info_x
        energy_y = info_y + 95
        
        # 计算能量百分比
        energy_percent = self.player.energy / self.player.max_energy
        
        # 绘制能量条背景
        pygame.draw.rect(screen, (50, 50, 50), (energy_x, energy_y, energy_bar_width, energy_bar_height))
        
        # 根据能量百分比选择颜色
        if energy_percent > 0.6:
            energy_color = (0, 255, 0)  # 绿色
        elif energy_percent > 0.3:
            energy_color = (255, 255, 0)  # 黄色
        else:
            energy_color = (255, 0, 0)  # 红色
        
        # 绘制能量条
        if energy_percent > 0:
            pygame.draw.rect(
                screen, 
                energy_color, 
                (energy_x, energy_y, int(energy_bar_width * energy_percent), energy_bar_height)
            )
        
        # 能量文本
        energy_text = self.font.render(
            f"能量: {int(self.player.energy)}/{self.player.max_energy}", 
            True, 
            (255, 255, 255)
        )
        screen.blit(energy_text, (energy_x, energy_y + energy_bar_height + 5))
        
        # 游戏时间
        hours = self.game_time // 60
        minutes = self.game_time % 60
        time_text = self.font.render(
            f"时间: {hours:02d}:{minutes:02d} (第 {self.day} 天)", 
            True, 
            (255, 255, 255)
        )
        screen.blit(time_text, (screen.get_width() - 200, 10))
        
        # 状态消息
        if self.status_message and pygame.time.get_ticks() < self.status_time:
            status_text = self.font_medium.render(
                self.status_message, 
                True, 
                (255, 255, 255)
            )
            status_rect = status_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 100))
            
            # 绘制背景
            bg_rect = status_rect.inflate(20, 10)
            pygame.draw.rect(screen, (0, 0, 0, 128), bg_rect)
            
            screen.blit(status_text, status_rect)
    
    def render_menu(self, screen):
        """渲染游戏菜单
        
        Args:
            screen: pygame屏幕对象
        """
        # 半透明背景
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 黑色半透明
        screen.blit(overlay, (0, 0))
        
        # 菜单背景
        menu_width = 300
        menu_height = 250
        menu_x = (screen.get_width() - menu_width) // 2
        menu_y = (screen.get_height() - menu_height) // 2
        
        pygame.draw.rect(screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # 菜单标题
        title_text = self.font_medium.render("菜单", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 30))
        screen.blit(title_text, title_rect)
        
        # 菜单选项
        for i, option in enumerate(self.menu_options):
            # 计算位置
            option_y = menu_y + 80 + i * 40
            
            # 选中项使用不同颜色
            if i == self.selected_menu_option:
                color = (255, 255, 0)  # 黄色
                # 绘制选中背景
                pygame.draw.rect(
                    screen, 
                    (100, 100, 100), 
                    (menu_x + 20, option_y - 5, menu_width - 40, 30)
                )
            else:
                color = (200, 200, 200)  # 灰色
            
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(menu_x + menu_width // 2, option_y))
            screen.blit(option_text, option_rect)
        
        # 提示
        hint_text = self.font.render("按上下键选择，Enter确认，Esc取消", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(menu_x + menu_width // 2, menu_y + menu_height - 30))
        screen.blit(hint_text, hint_rect)