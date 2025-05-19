import sqlite3
import os
import datetime
from pathlib import Path

class DatabaseManager:
    """数据库管理类，负责初始化数据库和提供数据操作方法"""
    
    def __init__(self, db_path="game.db"):
        """初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        # 确保数据库目录存在
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
        self.cursor = self.conn.cursor()
        
        # 初始化数据库表
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        # 创建玩家表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            exp INTEGER DEFAULT 0,
            money INTEGER DEFAULT 1000,
            last_login TEXT,
            day INTEGER DEFAULT 1,
            weather TEXT DEFAULT "晴天"
        )
        ''')
        
        # 检查并添加缺少的列
        self.cursor.execute("PRAGMA table_info(player)")
        columns = [column[1] for column in self.cursor.fetchall()]
        
        # 如果weather列不存在，添加它
        if 'weather' not in columns:
            self.cursor.execute("ALTER TABLE player ADD COLUMN weather TEXT DEFAULT '晴天'")
            self.conn.commit()
        
        # 创建作物表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            crop_type TEXT NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            growth_stage INTEGER DEFAULT 0,
            planted_at TEXT NOT NULL,
            is_watered INTEGER DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 创建动物表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            animal_type TEXT NOT NULL,
            name TEXT,
            age INTEGER DEFAULT 0,
            is_fed INTEGER DEFAULT 0,
            produce_time TEXT,
            x INTEGER DEFAULT 0,
            y INTEGER DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 创建背包表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            item_type TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 创建工具表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            tool_name TEXT NOT NULL,
            durability INTEGER DEFAULT 100,
            level INTEGER DEFAULT 1,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 创建销售记录表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_total INTEGER NOT NULL,
            sold_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 创建区域表
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            area_type TEXT NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            FOREIGN KEY (player_id) REFERENCES player(id)
        )
        ''')
        
        # 提交事务
        self.conn.commit()
    
    def create_new_player(self, name):
        """创建新玩家
        
        Args:
            name: 玩家名称
            
        Returns:
            新创建的玩家ID
        """
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO player (name, last_login, day, level, exp, money, weather) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, now, 1, 1, 0, 1000, "晴天")
        )
        self.conn.commit()
        
        player_id = self.cursor.lastrowid
        
        # 为新玩家初始化基本工具
        tools = [(player_id, "锄头"), (player_id, "水壶"), (player_id, "镰刀")]
        self.cursor.executemany(
            "INSERT INTO tools (player_id, tool_name) VALUES (?, ?)",
            tools
        )
        
        # 为新玩家初始化一些种子到背包
        seeds = [
            (player_id, "小麦种子", 5, "种子"),
            (player_id, "番茄种子", 3, "种子"),
            (player_id, "胡萝卜种子", 3, "种子")
        ]
        self.cursor.executemany(
            "INSERT INTO inventory (player_id, item_name, quantity, item_type) VALUES (?, ?, ?, ?)",
            seeds
        )
        
        self.conn.commit()
        return player_id
    
    def get_player(self, player_id):
        """获取玩家信息
        
        Args:
            player_id: 玩家ID
            
        Returns:
            玩家信息字典
        """
        self.cursor.execute("SELECT * FROM player WHERE id = ?", (player_id,))
        player_row = self.cursor.fetchone()
        if player_row is None:
            return None
        player_dict = dict(player_row)
        if "day" not in player_dict:
            player_dict["day"] = 1
        if "weather" not in player_dict:
            player_dict["weather"] = "晴天"
        return player_dict
    
    def update_player(self, player_id, **kwargs):
        """更新玩家信息
        
        Args:
            player_id: 玩家ID
            **kwargs: 要更新的字段和值
        """
        # 构建更新语句
        fields = [f"{k} = ?" for k in kwargs.keys()]
        query = f"UPDATE player SET {', '.join(fields)} WHERE id = ?"
        params = list(kwargs.values())
        params.append(player_id)
        self.cursor.execute(query, params)
        self.conn.commit()
        
    def update_weather(self, player_id, weather):
        """更新天气状态
        
        Args:
            player_id: 玩家ID
            weather: 天气状态（"晴天"或"雨天"）
        """
        self.cursor.execute(
            "UPDATE player SET weather = ? WHERE id = ?",
            (weather, player_id)
        )
        self.conn.commit()
        
    def get_weather(self, player_id):
        """获取当前天气状态
        
        Args:
            player_id: 玩家ID
            
        Returns:
            天气状态字符串
        """
        self.cursor.execute("SELECT weather FROM player WHERE id = ?", (player_id,))
        result = self.cursor.fetchone()
        if result and "weather" in result:
            return result["weather"]
        return "晴天"  # 默认为晴天
    
    def add_crop(self, player_id, crop_type, x, y):
        """添加作物
        
        Args:
            player_id: 玩家ID
            crop_type: 作物类型
            x: X坐标
            y: Y坐标
            
        Returns:
            新添加的作物ID
        """
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO crops (player_id, crop_type, x, y, planted_at) VALUES (?, ?, ?, ?, ?)",
            (player_id, crop_type, x, y, now)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_crops(self, player_id):
        """获取玩家的所有作物
        
        Args:
            player_id: 玩家ID
            
        Returns:
            作物列表
        """
        self.cursor.execute("SELECT * FROM crops WHERE player_id = ?", (player_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_crop(self, crop_id, **kwargs):
        """更新作物信息
        
        Args:
            crop_id: 作物ID
            **kwargs: 要更新的字段和值
        """
        fields = [f"{k} = ?" for k in kwargs.keys()]
        query = f"UPDATE crops SET {', '.join(fields)} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(crop_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def delete_crop(self, crop_id):
        """删除作物
        
        Args:
            crop_id: 作物ID
        """
        self.cursor.execute("DELETE FROM crops WHERE id = ?", (crop_id,))
        self.conn.commit()
    
    def add_animal(self, player_id, animal_type, name):
        """添加动物
        
        Args:
            player_id: 玩家ID
            animal_type: 动物类型
            name: 动物名称
            
        Returns:
            新添加的动物ID
        """
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO animals (player_id, animal_type, name, produce_time) VALUES (?, ?, ?, ?)",
            (player_id, animal_type, name, now)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_animals(self, player_id):
        """获取玩家的所有动物
        
        Args:
            player_id: 玩家ID
            
        Returns:
            动物列表
        """
        self.cursor.execute("SELECT * FROM animals WHERE player_id = ?", (player_id,))
        return [dict(row) for row in self.cursor.fetchall()]
        
    def get_areas(self, player_id):
        """获取玩家的所有区域
        
        Args:
            player_id: 玩家ID
            
        Returns:
            区域列表
        """
        self.cursor.execute("SELECT * FROM areas WHERE player_id = ?", (player_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def add_area(self, player_id, area_type, x, y, width, height):
        """添加区域
        
        Args:
            player_id: 玩家ID
            area_type: 区域类型
            x: X坐标
            y: Y坐标
            width: 宽度
            height: 高度
            
        Returns:
            新添加的区域ID
        """
        self.cursor.execute(
            "INSERT INTO areas (player_id, area_type, x, y, width, height) VALUES (?, ?, ?, ?, ?, ?)",
            (player_id, area_type, x, y, width, height)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_area(self, area_id, **kwargs):
        """更新区域信息
        
        Args:
            area_id: 区域ID
            **kwargs: 要更新的字段和值
        """
        # 构建更新语句
        fields = [f"{k} = ?" for k in kwargs.keys()]
        query = f"UPDATE areas SET {', '.join(fields)} WHERE id = ?"
        params = list(kwargs.values())
        params.append(area_id)
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def update_animal(self, animal_id, **kwargs):
        """更新动物信息
        
        Args:
            animal_id: 动物ID
            **kwargs: 要更新的字段和值
        """
        fields = [f"{k} = ?" for k in kwargs.keys()]
        query = f"UPDATE animals SET {', '.join(fields)} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(animal_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def add_inventory_item(self, player_id, item_name, quantity, item_type):
        """添加物品到背包
        
        Args:
            player_id: 玩家ID
            item_name: 物品名称
            quantity: 数量
            item_type: 物品类型
            
        Returns:
            物品ID
        """
        # 检查是否已有该物品
        self.cursor.execute(
            "SELECT id, quantity FROM inventory WHERE player_id = ? AND item_name = ? AND item_type = ?",
            (player_id, item_name, item_type)
        )
        existing = self.cursor.fetchone()
        
        if existing:
            # 更新现有物品数量
            new_quantity = existing['quantity'] + quantity
            self.cursor.execute(
                "UPDATE inventory SET quantity = ? WHERE id = ?",
                (new_quantity, existing['id'])
            )
            self.conn.commit()
            return existing['id']
        else:
            # 添加新物品
            self.cursor.execute(
                "INSERT INTO inventory (player_id, item_name, quantity, item_type) VALUES (?, ?, ?, ?)",
                (player_id, item_name, quantity, item_type)
            )
            self.conn.commit()
            return self.cursor.lastrowid
    
    def get_inventory(self, player_id):
        """获取玩家背包
        
        Args:
            player_id: 玩家ID
            
        Returns:
            背包物品列表
        """
        self.cursor.execute("SELECT * FROM inventory WHERE player_id = ?", (player_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_inventory_item(self, item_id, quantity):
        """更新背包物品数量
        
        Args:
            item_id: 物品ID
            quantity: 新数量
        """
        if quantity <= 0:
            # 数量为0则删除物品
            self.cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        else:
            # 更新数量
            self.cursor.execute(
                "UPDATE inventory SET quantity = ? WHERE id = ?",
                (quantity, item_id)
            )
        self.conn.commit()
    
    def get_tools(self, player_id):
        """获取玩家工具
        
        Args:
            player_id: 玩家ID
            
        Returns:
            工具列表
        """
        self.cursor.execute("SELECT * FROM tools WHERE player_id = ?", (player_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_tool(self, tool_id, **kwargs):
        """更新工具信息
        
        Args:
            tool_id: 工具ID
            **kwargs: 要更新的字段和值
        """
        fields = [f"{k} = ?" for k in kwargs.keys()]
        query = f"UPDATE tools SET {', '.join(fields)} WHERE id = ?"
        
        params = list(kwargs.values())
        params.append(tool_id)
        
        self.cursor.execute(query, params)
        self.conn.commit()
    
    def add_sale(self, player_id, item_name, quantity, price_total):
        """添加销售记录
        
        Args:
            player_id: 玩家ID
            item_name: 物品名称
            quantity: 数量
            price_total: 总价
            
        Returns:
            销售记录ID
        """
        now = datetime.datetime.now().isoformat()
        self.cursor.execute(
            "INSERT INTO sales_log (player_id, item_name, quantity, price_total, sold_at) VALUES (?, ?, ?, ?, ?)",
            (player_id, item_name, quantity, price_total, now)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_sales_history(self, player_id, limit=10):
        """获取销售历史
        
        Args:
            player_id: 玩家ID
            limit: 限制返回记录数
            
        Returns:
            销售记录列表
        """
        self.cursor.execute(
            "SELECT * FROM sales_log WHERE player_id = ? ORDER BY sold_at DESC LIMIT ?",
            (player_id, limit)
        )
        return [dict(row) for row in self.cursor.fetchall()]
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            
    def __del__(self):
        """析构函数，确保数据库连接被关闭"""
        self.close()
    
    def save_tilled_land(self, player_id, tilled_list):
        """保存玩家耕地信息（覆盖式保存）
        Args:
            player_id: 玩家ID
            tilled_list: [{"x": int, "y": int, "watered": bool}]
        """
        # 创建表（如未创建）
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tilled_land (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            x INTEGER,
            y INTEGER,
            watered INTEGER DEFAULT 0,
            UNIQUE(player_id, x, y)
        )''')
        # 先删除该玩家所有耕地记录
        self.cursor.execute("DELETE FROM tilled_land WHERE player_id = ?", (player_id,))
        # 插入新的耕地数据
        for info in tilled_list:
            self.cursor.execute(
                "INSERT INTO tilled_land (player_id, x, y, watered) VALUES (?, ?, ?, ?)",
                (player_id, info["x"], info["y"], int(info.get("watered", False)))
            )
        self.conn.commit()

    def get_tilled_land(self, player_id):
        """获取玩家所有耕地信息
        Args:
            player_id: 玩家ID
        Returns:
            [{"x": int, "y": int, "watered": bool}, ...]
        """
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS tilled_land (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER,
            x INTEGER,
            y INTEGER,
            watered INTEGER DEFAULT 0,
            UNIQUE(player_id, x, y)
        )''')
        self.cursor.execute("SELECT x, y, watered FROM tilled_land WHERE player_id = ?", (player_id,))
        rows = self.cursor.fetchall()
        return [{"x": row["x"], "y": row["y"], "watered": bool(row["watered"])} for row in rows]

    def delete_player(self, player_id):
        """删除玩家及其相关数据
        Args:
            player_id: 玩家ID
        """
        # 删除玩家相关数据
        self.cursor.execute("DELETE FROM player WHERE id = ?", (player_id,))
        self.cursor.execute("DELETE FROM crops WHERE player_id = ?", (player_id,))
        self.cursor.execute("DELETE FROM animals WHERE player_id = ?", (player_id,))
        self.cursor.execute("DELETE FROM inventory WHERE player_id = ?", (player_id,))
        self.cursor.execute("DELETE FROM tools WHERE player_id = ?", (player_id,))
        self.cursor.execute("DELETE FROM sales_log WHERE player_id = ?", (player_id,))
        self.conn.commit()