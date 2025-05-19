import pygame
import sys
import os
from pathlib import Path

# 导入游戏配置
from config import *

# 导入数据库管理器
from database.db_manager import DatabaseManager

# 导入图像管理器
from utils.image_manager import ImageManager

# 导入场景
from scenes.main_menu import MainMenu
from scenes.farm_scene import FarmScene
from scenes.market_scene import MarketScene

class Game:
    """游戏主类，负责初始化pygame和管理游戏场景"""
    
    def __init__(self):
        """初始化游戏"""
        # 初始化pygame
        pygame.init()
        pygame.display.set_caption(GAME_TITLE)
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # 初始化数据库
        db_path = os.path.join(os.path.dirname(__file__), "database", "game.db")
        self.db = DatabaseManager(db_path)
        
        # 初始化图像管理器
        self.image_manager = ImageManager()
        
        # 设置全局图像管理器实例
        from utils.image_manager import set_image_manager
        set_image_manager(self.image_manager)
        
        # 游戏状态
        self.running = True
        self.current_scene = None
        self.player_id = None
        
        # 场景字典
        self.scenes = {
            "main_menu": lambda: MainMenu(self),
            "farm": lambda: FarmScene(self),
            "market": lambda: MarketScene(self)
        }
        
        # 默认进入主菜单
        self.change_scene("main_menu")
    
    def change_scene(self, scene_name, **kwargs):
        """切换场景
        
        Args:
            scene_name: 场景名称
            **kwargs: 传递给场景的参数
        """
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]()
            self.current_scene.setup(**kwargs)
        else:
            print(f"错误：场景 {scene_name} 不存在")
    
    def set_player(self, player_id):
        """设置当前玩家ID
        
        Args:
            player_id: 玩家ID
        """
        self.player_id = player_id
        # 更新玩家最后登录时间
        import datetime
        self.db.update_player(player_id, last_login=datetime.datetime.now().isoformat())
    
    def run(self):
        """游戏主循环"""
        while self.running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif self.current_scene:
                    self.current_scene.handle_event(event)
            
            # 更新当前场景
            if self.current_scene:
                self.current_scene.update()
            
            # 渲染当前场景
            self.screen.fill(BLACK)  # 清空屏幕
            if self.current_scene:
                self.current_scene.render(self.screen)
            
            # 更新显示
            pygame.display.flip()
            
            # 控制帧率
            self.clock.tick(FPS)
        
        # 游戏结束，清理资源
        self.quit()
    
    def quit(self):
        """退出游戏"""
        # 关闭数据库连接
        if hasattr(self, 'db'):
            self.db.close()
        
        # 退出pygame
        pygame.quit()
        sys.exit()

# 游戏入口
if __name__ == "__main__":
    # 确保当前工作目录是游戏根目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建并运行游戏
    game = Game()
    game.run()