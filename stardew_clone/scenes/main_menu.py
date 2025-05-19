import pygame
import os
import sys
from utils.font_manager import font_manager
from utils.audio_manager import audio_manager 

class MainMenu:
    """游戏主菜单场景"""
    
    def __init__(self, game):
        """初始化主菜单
        
        Args:
            game: 游戏实例
        """
        self.game = game
        # self.font_large = pygame.font.SysFont("NotoSansTC-VariableFont_wght", 72)
        # self.font_medium = pygame.font.SysFont("NotoSansTC-VariableFont_wght", 48)
        # self.font_small = pygame.font.SysFont("NotoSansTC-VariableFont_wght", 36)
        self.font_large = font_manager.get_font(72)
        self.font_medium = font_manager.get_font(48)
        self.font_small = font_manager.get_font(36)
        
        # 菜单选项
        self.options = ["新游戏", "加载游戏", "退出"]
        self.selected_option = 0
        
        # 输入框状态
        self.input_active = False
        self.input_text = ""
        
        # 玩家选择状态
        self.player_selection_active = False
        self.players = []
        self.selected_player = 0
        
        # 加载现有玩家列表
        self.load_players()
    
    def setup(self, **kwargs):
        """设置场景参数"""
        # 播放背景音乐
        audio_manager.play_music()
    
    def load_players(self):
        """从数据库加载玩家列表"""
        # 查询所有玩家
        self.game.db.cursor.execute("SELECT id, name, level FROM player ORDER BY last_login DESC")
        self.players = [dict(row) for row in self.game.db.cursor.fetchall()]
    
    def handle_event(self, event):
        """处理输入事件
        
        Args:
            event: pygame事件
        """
        if self.input_active:
            # 处理名称输入
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # 创建新玩家并开始游戏
                    if self.input_text.strip():
                        player_id = self.game.db.create_new_player(self.input_text)
                        self.game.set_player(player_id)
                        # 播放成功音效
                        audio_manager.play_sound("success")
                        self.game.change_scene("farm")
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.input_active = False
                else:
                    # 限制名称长度为15个字符
                    if len(self.input_text) < 15:
                        self.input_text += event.unicode
        
        elif self.player_selection_active:
            # 处理玩家选择
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_player = (self.selected_player - 1) % len(self.players)
                elif event.key == pygame.K_DOWN:
                    self.selected_player = (self.selected_player + 1) % len(self.players)
                elif event.key == pygame.K_RETURN:
                    # 加载选中的玩家并开始游戏
                    if self.players:
                        player_id = self.players[self.selected_player]["id"]
                        self.game.set_player(player_id)
                        # 播放成功音效
                        audio_manager.play_sound("success")
                        self.game.change_scene("farm")
                elif event.key == pygame.K_ESCAPE:
                    self.player_selection_active = False
                elif event.key == pygame.K_d:
                    self.delete_selected_player()
        
        else:
            # 处理主菜单选择
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()

    def select_option(self):
        """处理菜单选项选择"""
        if self.options[self.selected_option] == "新游戏":
            # 激活名称输入
            self.input_active = True
            self.input_text = ""
        
        elif self.options[self.selected_option] == "加载游戏":
            # 刷新玩家列表
            self.load_players()
            if self.players:
                # 激活玩家选择
                self.player_selection_active = True
                self.selected_player = 0
        
        elif self.options[self.selected_option] == "退出":
            # 播放成功音效
            audio_manager.play_sound("success")
            # 退出游戏
            self.game.quit()
    
    def update(self):
        """更新场景状态"""
        pass
    
    def render(self, screen):
        """渲染场景
        
        Args:
            screen: pygame屏幕对象
        """
        # 绘制渐变背景
        for y in range(screen.get_height()):
            # 从顶部的深绿色渐变到底部的浅绿色
            gradient_color = (100, 180 + (y * 50 // screen.get_height()), 100)
            pygame.draw.line(screen, gradient_color, (0, y), (screen.get_width(), y))
        
        # 绘制像素风格草地
        for y in range(0, screen.get_height(), 64):
            for x in range(0, screen.get_width(), 64):
                # 绘制草地纹理
                grass_rect = pygame.Rect(x, y, 64, 64)
                # 添加半透明的纹理层
                texture = pygame.Surface((64, 64), pygame.SRCALPHA)
                texture.fill((255, 255, 255, 30))  # 半透明白色
                
                # 添加随机草叶
                for _ in range(5):
                    grass_x = x + (x * 13 + _) % 60
                    grass_y = y + (y * 17 + _) % 60
                    grass_height = 4 + (_ * 2)
                    pygame.draw.line(texture, (50, 150, 50, 200), 
                                   (grass_x, grass_y + grass_height), 
                                   (grass_x, grass_y), 2)
                
                screen.blit(texture, grass_rect)
        
        # 绘制装饰性木栅栏边界
        fence_color = (120, 60, 20)  # 深棕色木栅栏
        fence_highlight = (160, 100, 60)  # 浅棕色高光
        fence_width = 12
        fence_post_size = 20
        
        # 绘制栅栏底部阴影
        shadow_color = (50, 50, 50, 100)
        shadow_offset = 4
        
        # 绘制栅栏柱子
        for x in range(0, screen.get_width(), 120):
            # 上边界柱子
            pygame.draw.rect(screen, fence_color, (x, 0, fence_post_size, fence_post_size))
            pygame.draw.rect(screen, fence_highlight, (x+2, 2, fence_post_size-4, 5))
            
            # 下边界柱子
            post_y = screen.get_height() - fence_post_size
            shadow = pygame.Surface((fence_post_size+shadow_offset, shadow_offset), pygame.SRCALPHA)
            shadow.fill(shadow_color)
            screen.blit(shadow, (x-shadow_offset//2, post_y+fence_post_size))
            pygame.draw.rect(screen, fence_color, (x, post_y, fence_post_size, fence_post_size))
            pygame.draw.rect(screen, fence_highlight, (x+2, post_y+2, fence_post_size-4, 5))
        
        for y in range(0, screen.get_height(), 120):
            # 左边界柱子
            pygame.draw.rect(screen, fence_color, (0, y, fence_post_size, fence_post_size))
            pygame.draw.rect(screen, fence_highlight, (2, y+2, 5, fence_post_size-4))
            
            # 右边界柱子
            post_x = screen.get_width() - fence_post_size
            shadow = pygame.Surface((shadow_offset, fence_post_size+shadow_offset), pygame.SRCALPHA)
            shadow.fill(shadow_color)
            screen.blit(shadow, (post_x+fence_post_size, y-shadow_offset//2))
            pygame.draw.rect(screen, fence_color, (post_x, y, fence_post_size, fence_post_size))
            pygame.draw.rect(screen, fence_highlight, (post_x+2, y+2, 5, fence_post_size-4))
        
        # 绘制栅栏横条
        # 上边界
        pygame.draw.rect(screen, fence_color, (0, fence_post_size//2-fence_width//2, screen.get_width(), fence_width))
        # 下边界
        pygame.draw.rect(screen, fence_color, (0, screen.get_height()-fence_post_size//2-fence_width//2, screen.get_width(), fence_width))
        # 左边界
        pygame.draw.rect(screen, fence_color, (fence_post_size//2-fence_width//2, 0, fence_width, screen.get_height()))
        # 右边界
        pygame.draw.rect(screen, fence_color, (screen.get_width()-fence_post_size//2-fence_width//2, 0, fence_width, screen.get_height()))
        
        # 绘制像素风格小房子作为装饰
        house_x = screen.get_width() // 2 - 120
        house_y = 160
        
        # 绘制房屋阴影
        shadow_color = (50, 50, 50, 100)
        shadow = pygame.Surface((240, 20), pygame.SRCALPHA)
        shadow.fill(shadow_color)
        screen.blit(shadow, (house_x - 10, house_y + 140))
        
        # 绘制房屋主体（带纹理的浅棕色）
        house_width = 220
        house_height = 140
        house_rect = pygame.Rect(house_x, house_y, house_width, house_height)
        
        # 绘制墙壁底色
        wall_color = (210, 180, 140)
        pygame.draw.rect(screen, wall_color, house_rect)
        
        # 添加墙壁纹理
        for i in range(0, house_width, 20):
            pygame.draw.line(screen, (190, 160, 120), (house_x + i, house_y), (house_x + i, house_y + house_height), 2)
        
        # 绘制房屋屋顶（带纹理的深棕色）
        roof_height = 50
        roof_width = house_width + 40
        roof_points = [
            (house_x - 20, house_y),  # 左下
            (house_x + house_width + 20, house_y),  # 右下
            (house_x + house_width // 2, house_y - roof_height)  # 顶部
        ]
        pygame.draw.polygon(screen, (139, 69, 19), roof_points)  # 深棕色屋顶
        
        # 添加屋顶纹理
        for i in range(1, 4):
            y_offset = roof_height * i // 4
            x_offset = 20 * i
            pygame.draw.line(screen, (120, 60, 20), 
                           (house_x - 20 + x_offset, house_y - y_offset), 
                           (house_x + house_width + 20 - x_offset, house_y - y_offset), 
                           2)
        
        # 绘制烟囱
        chimney_width = 20
        chimney_height = 40
        chimney_x = house_x + house_width - 60
        chimney_y = house_y - 30
        pygame.draw.rect(screen, (120, 60, 20), (chimney_x, chimney_y - chimney_height, chimney_width, chimney_height))
        
        # 添加烟雾效果（根据当前时间变化）
        import time
        current_time = int(time.time() * 2) % 10
        for i in range(3):
            smoke_size = 10 + (i * 5) + (current_time % 5)
            smoke_x = chimney_x + chimney_width // 2 - smoke_size // 2
            smoke_y = chimney_y - chimney_height - 10 - (i * 15) - (current_time % 10)
            smoke = pygame.Surface((smoke_size, smoke_size), pygame.SRCALPHA)
            smoke.fill((255, 255, 255, 100 - i * 20))
            screen.blit(smoke, (smoke_x, smoke_y))
        
        # 绘制门（带纹理和把手）
        door_width = 40
        door_height = 70
        door_x = house_x + house_width // 2 - door_width // 2
        door_y = house_y + house_height - door_height
        pygame.draw.rect(screen, (101, 67, 33), (door_x, door_y, door_width, door_height))  # 棕色门
        
        # 门框
        pygame.draw.rect(screen, (80, 50, 20), (door_x, door_y, door_width, door_height), 3)
        # 门把手
        pygame.draw.circle(screen, (220, 220, 180), (door_x + door_width - 10, door_y + door_height // 2), 5)
        
        # 绘制窗户（带窗框和反光效果）
        window_size = 36
        window_color = (173, 216, 230)  # 浅蓝色窗户
        
        # 左窗户
        left_window_x = house_x + 40
        left_window_y = house_y + 40
        pygame.draw.rect(screen, (80, 50, 20), (left_window_x-2, left_window_y-2, window_size+4, window_size+4))  # 窗框
        pygame.draw.rect(screen, window_color, (left_window_x, left_window_y, window_size, window_size))
        # 窗户十字框
        pygame.draw.line(screen, (80, 50, 20), (left_window_x, left_window_y + window_size//2), (left_window_x + window_size, left_window_y + window_size//2), 2)
        pygame.draw.line(screen, (80, 50, 20), (left_window_x + window_size//2, left_window_y), (left_window_x + window_size//2, left_window_y + window_size), 2)
        # 窗户反光
        pygame.draw.line(screen, (255, 255, 255, 150), (left_window_x + 5, left_window_y + 5), (left_window_x + 15, left_window_y + 5), 2)
        
        # 右窗户
        right_window_x = house_x + house_width - 40 - window_size
        right_window_y = house_y + 40
        pygame.draw.rect(screen, (80, 50, 20), (right_window_x-2, right_window_y-2, window_size+4, window_size+4))  # 窗框
        pygame.draw.rect(screen, window_color, (right_window_x, right_window_y, window_size, window_size))
        # 窗户十字框
        pygame.draw.line(screen, (80, 50, 20), (right_window_x, right_window_y + window_size//2), (right_window_x + window_size, right_window_y + window_size//2), 2)
        pygame.draw.line(screen, (80, 50, 20), (right_window_x + window_size//2, right_window_y), (right_window_x + window_size//2, right_window_y + window_size), 2)
        # 窗户反光
        pygame.draw.line(screen, (255, 255, 255, 150), (right_window_x + 5, right_window_y + 5), (right_window_x + 15, right_window_y + 5), 2)
        
        # 绘制花坛
        flower_box_width = 50
        flower_box_height = 20
        # 左花坛
        pygame.draw.rect(screen, (120, 60, 20), (left_window_x - 5, left_window_y + window_size + 5, window_size + 10, flower_box_height))
        # 右花坛
        pygame.draw.rect(screen, (120, 60, 20), (right_window_x - 5, right_window_y + window_size + 5, window_size + 10, flower_box_height))
        
        # 添加花朵
        flower_colors = [(255, 50, 50), (255, 255, 50), (255, 150, 50), (200, 50, 255)]
        for i in range(4):
            # 左花坛的花
            flower_x = left_window_x + 5 + (i * 10)
            flower_y = left_window_y + window_size + 5
            pygame.draw.circle(screen, flower_colors[i % len(flower_colors)], (flower_x, flower_y), 5)
            pygame.draw.rect(screen, (50, 150, 50), (flower_x-1, flower_y, 2, 10))
            
            # 右花坛的花
            flower_x = right_window_x + 5 + (i * 10)
            flower_y = right_window_y + window_size + 5
            pygame.draw.circle(screen, flower_colors[(i+2) % len(flower_colors)], (flower_x, flower_y), 5)
            pygame.draw.rect(screen, (50, 150, 50), (flower_x-1, flower_y, 2, 10))
        
        # 渲染标题（带阴影效果）
        title = "星露谷物语克隆版"
        # 阴影
        shadow_text = self.font_large.render(title, True, (50, 50, 50))
        shadow_rect = shadow_text.get_rect(center=(screen.get_width() // 2 + 4, 104))
        screen.blit(shadow_text, shadow_rect)
        # 主标题
        title_text = self.font_large.render(title, True, (255, 255, 200))
        title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title_text, title_rect)
        
        if self.input_active:
            # 绘制半透明背景
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # 绘制输入面板背景
            panel_width, panel_height = 500, 200
            panel_x = screen.get_width() // 2 - panel_width // 2
            panel_y = 350
            
            # 面板阴影
            shadow = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            screen.blit(shadow, (panel_x - 5 + 8, panel_y - 5 + 8))
            
            # 面板主体
            panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(screen, (240, 230, 200), panel, border_radius=10)
            pygame.draw.rect(screen, (180, 150, 100), panel, 3, border_radius=10)
            
            # 面板标题背景
            title_bg = pygame.Rect(panel_x, panel_y, panel_width, 50)
            pygame.draw.rect(screen, (180, 150, 100), title_bg, border_top_left_radius=10, border_top_right_radius=10)
            
            # 绘制提示文本
            prompt_text = self.font_medium.render("请输入你的名字", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
            screen.blit(prompt_text, prompt_rect)
            
            # 绘制输入框
            input_box = pygame.Rect(panel_x + 50, panel_y + 80, panel_width - 100, 50)
            pygame.draw.rect(screen, (255, 255, 255), input_box, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), input_box, 2, border_radius=5)
            
            # 绘制输入文本
            input_text = self.font_small.render(self.input_text, True, (0, 0, 0))
            # 添加闪烁的光标效果
            cursor_text = self.input_text
            if int(pygame.time.get_ticks() / 500) % 2 == 0:  # 每0.5秒闪烁一次
                cursor_text += "|"
            input_text_with_cursor = self.font_small.render(cursor_text, True, (0, 0, 0))
            
            # 确保文本在输入框内居中显示
            text_rect = input_text_with_cursor.get_rect(midleft=(input_box.left + 10, input_box.centery))
            screen.blit(input_text_with_cursor, text_rect)
            
            # 添加提示信息
            hint_text = self.font_small.render("按回车确认，ESC取消", True, (100, 100, 100))
            hint_rect = hint_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
            screen.blit(hint_text, hint_rect)
        
        elif self.player_selection_active:
            # 绘制半透明背景
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # 绘制选择面板背景
            panel_width, panel_height = 500, 400
            panel_x = screen.get_width() // 2 - panel_width // 2
            panel_y = 200
            
            # 面板阴影
            shadow = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 100))
            screen.blit(shadow, (panel_x - 5 + 8, panel_y - 5 + 8))
            
            # 面板主体
            panel = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
            pygame.draw.rect(screen, (240, 230, 200), panel, border_radius=10)
            pygame.draw.rect(screen, (180, 150, 100), panel, 3, border_radius=10)
            
            # 面板标题背景
            title_bg = pygame.Rect(panel_x, panel_y, panel_width, 50)
            pygame.draw.rect(screen, (180, 150, 100), title_bg, border_top_left_radius=10, border_top_right_radius=10)
            
            # 渲染标题
            title_text = self.font_medium.render("选择角色", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 25))
            screen.blit(title_text, title_rect)
            
            # 玩家列表区域
            list_area = pygame.Rect(panel_x + 20, panel_y + 70, panel_width - 40, panel_height - 130)
            pygame.draw.rect(screen, (255, 255, 255, 150), list_area, border_radius=5)
            
            # 玩家列表
            if self.players:
                # 使用更小的字体
                font_player = font_manager.get_font(24)  # 减小字体大小
                font_level = font_manager.get_font(18)   # 等级使用更小的字体
                
                # 增加每个玩家条目之间的间距
                player_spacing = 70  # 增加间距
                
                for i, player in enumerate(self.players):
                    # 计算位置，增加垂直间距
                    y_pos = panel_y + 100 + i * player_spacing
                    
                    # 选中状态
                    if i == self.selected_player:
                        # 绘制选中背景 - 带动画效果
                        pulse = (pygame.time.get_ticks() % 1000) / 1000  # 0到1的脉冲值
                        pulse_alpha = int(100 + 50 * pulse)  # 透明度在100-150之间脉动
                        
                        # 调整选择框高度
                        select_rect = pygame.Rect(panel_x + 30, y_pos - 10, panel_width - 60, 40)
                        select_surface = pygame.Surface((select_rect.width, select_rect.height), pygame.SRCALPHA)
                        select_surface.fill((180, 220, 255, pulse_alpha))
                        screen.blit(select_surface, select_rect)
                        
                        # 添加选中指示器
                        indicator_size = 8
                        pygame.draw.polygon(screen, (255, 200, 0), [
                            (panel_x + 40, y_pos + 10),  # 调整指示器位置
                            (panel_x + 40 + indicator_size, y_pos + 10 - indicator_size),
                            (panel_x + 40 + indicator_size, y_pos + 10 + indicator_size)
                        ])
                    
                    # 玩家信息 - 带图标
                    # 等级图标 - 减小尺寸
                    level_icon = pygame.Surface((20, 20), pygame.SRCALPHA)  # 减小图标尺寸
                    pygame.draw.circle(level_icon, (255, 215, 0), (10, 10), 10)  # 金色圆圈
                    pygame.draw.circle(level_icon, (0, 0, 0), (10, 10), 10, 2)  # 黑色边框
                    screen.blit(level_icon, (panel_x + 60, y_pos - 10))  # 调整位置
                    
                    # 等级文本 - 使用更小的字体
                    level_text = font_level.render(str(player['level']), True, (0, 0, 0))
                    level_rect = level_text.get_rect(center=(panel_x + 60 + 10, y_pos - 10 + 10))  # 调整位置
                    screen.blit(level_text, level_rect)
                    
                    # 玩家名称 - 使用更小的字体
                    player_text = font_player.render(player['name'], True, (50, 50, 50))
                    player_rect = player_text.get_rect(midleft=(panel_x + 100, y_pos))
                    screen.blit(player_text, player_rect)
            else:
                # 没有玩家时显示提示
                no_player_text = self.font_small.render("没有保存的角色", True, (100, 100, 100))
                no_player_rect = no_player_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 150))
                screen.blit(no_player_text, no_player_rect)
            
            # 控制提示
            hint_bg = pygame.Rect(panel_x, panel_y + panel_height - 50, panel_width, 50)
            pygame.draw.rect(screen, (180, 150, 100, 150), hint_bg, border_bottom_left_radius=10, border_bottom_right_radius=10)
            
            # 使用更小的字体
            font_hint = font_manager.get_font(18)  # 进一步减小提示文本字体
            
            # 提示图标和文本
            key_size = 24  # 进一步减小按键尺寸
            key_margin = 20  # 增加按键间距
            
            # 计算按键起始位置，使三个按键均匀分布
            total_width = panel_width - 40  # 总可用宽度
            button_width = key_size * 2  # 第一个按钮宽度
            text_width = 40  # 估计文本宽度
            group_width = button_width + text_width  # 一组按钮+文本的宽度
            
            # 第一组：Enter键
            start_x = panel_x + 30
            
            # Enter键图标
            enter_key = pygame.Rect(start_x, panel_y + panel_height - 37, key_size * 2, key_size)
            pygame.draw.rect(screen, (220, 220, 220), enter_key, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), enter_key, 2, border_radius=5)
            enter_text = font_hint.render("↵", True, (0, 0, 0))
            enter_rect = enter_text.get_rect(center=enter_key.center)
            screen.blit(enter_text, enter_rect)
            
            # Enter键文本
            select_text = font_hint.render("选择", True, (255, 255, 255))
            select_rect = select_text.get_rect(midleft=(enter_key.right + 5, enter_key.centery))
            screen.blit(select_text, select_rect)
            
            # 第二组：Esc键
            start_x = panel_x + panel_width // 2 - key_size // 2
            
            # Esc键图标
            esc_key = pygame.Rect(start_x - 30, panel_y + panel_height - 37, key_size, key_size)
            pygame.draw.rect(screen, (220, 220, 220), esc_key, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), esc_key, 2, border_radius=5)
            esc_text = font_hint.render("Esc", True, (0, 0, 0))
            esc_rect = esc_text.get_rect(center=esc_key.center)
            screen.blit(esc_text, esc_rect)
            
            # Esc键文本
            back_text = font_hint.render("返回", True, (255, 255, 255))
            back_rect = back_text.get_rect(midleft=(esc_key.right + 5, esc_key.centery))
            screen.blit(back_text, back_rect)
            
            # 第三组：D键
            start_x = panel_x + panel_width - 30 - key_size - 40
            
            # D键图标
            d_key = pygame.Rect(start_x, panel_y + panel_height - 37, key_size, key_size)
            pygame.draw.rect(screen, (220, 220, 220), d_key, border_radius=5)
            pygame.draw.rect(screen, (100, 100, 100), d_key, 2, border_radius=5)
            d_text = font_hint.render("D", True, (0, 0, 0))
            d_rect = d_text.get_rect(center=d_key.center)
            screen.blit(d_text, d_rect)
            
            # D键文本
            delete_text = font_hint.render("删除", True, (255, 255, 255))
            delete_rect = delete_text.get_rect(midleft=(d_key.right + 5, d_key.centery))
            screen.blit(delete_text, delete_rect)
        
        else:
            # 渲染主菜单选项
            menu_width = 300
            menu_height = len(self.options) * 70 + 20
            menu_x = screen.get_width() // 2 - menu_width // 2
            menu_y = 350
            
            # 菜单背景
            menu_bg = pygame.Surface((menu_width, menu_height), pygame.SRCALPHA)
            menu_bg.fill((0, 0, 0, 80))
            screen.blit(menu_bg, (menu_x, menu_y))
            pygame.draw.rect(screen, (255, 255, 255, 50), (menu_x, menu_y, menu_width, menu_height), 2, border_radius=10)
            
            for i, option in enumerate(self.options):
                # 计算位置
                y_pos = menu_y + 40 + i * 70
                
                # 选中状态 - 带动画效果
                if i == self.selected_option:
                    # 计算动画效果
                    pulse = (pygame.time.get_ticks() % 1000) / 1000  # 0到1的脉冲值
                    pulse_width = int(menu_width * 0.9 + 20 * pulse)  # 宽度在90%-100%之间脉动
                    pulse_alpha = int(150 + 50 * pulse)  # 透明度在150-200之间脉动
                    
                    # 绘制选中背景
                    select_x = menu_x + (menu_width - pulse_width) // 2
                    select_rect = pygame.Rect(select_x, y_pos - 15, pulse_width, 60)
                    select_surface = pygame.Surface((pulse_width, 60), pygame.SRCALPHA)
                    select_surface.fill((255, 255, 200, pulse_alpha))
                    screen.blit(select_surface, select_rect)
                    
                    # 绘制边框
                    pygame.draw.rect(screen, (255, 215, 0), select_rect, 2, border_radius=10)
                    
                    # 绘制装饰性箭头
                    arrow_size = 15
                    arrow_margin = 20
                    # 左箭头
                    pygame.draw.polygon(screen, (255, 215, 0), [
                        (select_x - arrow_margin, y_pos + 15),
                        (select_x - arrow_margin + arrow_size, y_pos + 15 - arrow_size),
                        (select_x - arrow_margin + arrow_size, y_pos + 15 + arrow_size)
                    ])
                    # 右箭头
                    pygame.draw.polygon(screen, (255, 215, 0), [
                        (select_x + pulse_width + arrow_margin, y_pos + 15),
                        (select_x + pulse_width + arrow_margin - arrow_size, y_pos + 15 - arrow_size),
                        (select_x + pulse_width + arrow_margin - arrow_size, y_pos + 15 + arrow_size)
                    ])
                
                # 选项文本 - 选中时使用金色，未选中时使用白色
                text_color = (255, 215, 0) if i == self.selected_option else (255, 255, 255)
                option_text = self.font_medium.render(option, True, text_color)
                
                # 为选中项添加文字阴影效果
                if i == self.selected_option:
                    shadow_text = self.font_medium.render(option, True, (100, 50, 0))
                    shadow_rect = shadow_text.get_rect(center=(menu_x + menu_width // 2 + 2, y_pos + 2))
                    screen.blit(shadow_text, shadow_rect)
                
                option_rect = option_text.get_rect(center=(menu_x + menu_width // 2, y_pos))
                screen.blit(option_text, option_rect)
            
            # 添加控制提示
            hint_text = self.font_small.render("使用↑↓键选择，回车确认", True, (220, 220, 220))
            hint_rect = hint_text.get_rect(center=(screen.get_width() // 2, menu_y + menu_height + 30))
            screen.blit(hint_text, hint_rect)

    def delete_selected_player(self):
        """删除选中的玩家"""
        if self.players:
            player_id = self.players[self.selected_player]["id"]
            self.game.db.delete_player(player_id)
            self.load_players()
            self.selected_player = min(self.selected_player, len(self.players) - 1)