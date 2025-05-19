# 游戏配置文件

# 窗口设置
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
TILE_SIZE = 64  # 每个瓦片的像素大小

# 游戏设置
FPS = 60
GAME_TITLE = "星露谷物语克隆版"

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)

# 游戏内时间设置
DAY_LENGTH = 24 * 60  # 一天的游戏内分钟数
TIME_SCALE = 30  # 现实1秒 = 游戏内60秒

# 农场设置
FARM_WIDTH = 16  # 农场宽度（瓦片数）
FARM_HEIGHT = 12  # 农场高度（瓦片数）

# 作物设置
CROP_TYPES = {
    "小麦": {
        "growth_time": 4,  # 生长阶段数
        "days_per_stage": 1,  # 每个阶段的天数
        "sell_price": 25,  # 售价
        "seed_price": 10,  # 种子价格
        "exp_reward": 5  # 收获经验
    },
    "番茄": {
        "growth_time": 5,
        "days_per_stage": 1,
        "sell_price": 40,
        "seed_price": 20,
        "exp_reward": 10
    },
    "胡萝卜": {
        "growth_time": 3,
        "days_per_stage": 1,
        "sell_price": 30,
        "seed_price": 15,
        "exp_reward": 7
    },
    "土豆": {
        "growth_time": 6,
        "days_per_stage": 1,
        "sell_price": 60,
        "seed_price": 30,
        "exp_reward": 15
    }
}

# 动物设置
ANIMAL_TYPES = {
    "牛": {
        "product": "牛奶",
        "days_to_produce": 2,  # 产出周期（天）
        "product_price": 120,  # 产品售价
        "purchase_price": 1500,  # 购买价格
        "exp_reward": 20,  # 收获经验
        "feed_name": "牛饲料",  # 饲料名称
        "feed_price": 50  # 饲料价格
    },
    "羊": {
        "product": "羊毛",
        "days_to_produce": 3,
        "product_price": 150,
        "purchase_price": 2000,
        "exp_reward": 25,
        "feed_name": "羊饲料",
        "feed_price": 60
    },
    "鸡": {
        "product": "鸡蛋",
        "days_to_produce": 1,
        "product_price": 50,
        "purchase_price": 800,
        "exp_reward": 10,
        "feed_name": "鸡饲料",
        "feed_price": 30
    }
}

# 工具设置
TOOL_TYPES = {
    "锄头": {
        "durability": 100,
        "upgrade_cost": [500, 1500, 3000],  # 各级升级费用
        "efficiency": [1, 1.2, 1.5, 2.0]  # 各级效率
    },
    "水壶": {
        "durability": 150,
        "upgrade_cost": [400, 1200, 2500],
        "efficiency": [1, 1.3, 1.6, 2.0]
    },
    "镰刀": {
        "durability": 120,
        "upgrade_cost": [450, 1300, 2800],
        "efficiency": [1, 1.2, 1.5, 1.8]
    }
}

# 玩家等级设置
LEVEL_EXP_REQUIREMENTS = [
    0,      # 1级所需经验
    100,    # 2级所需经验
    300,    # 3级
    600,    # 4级
    1000,   # 5级
    1500,   # 6级
    2100,   # 7级
    2800,   # 8级
    3600,   # 9级
    4500    # 10级
]

# 初始玩家设置
INITIAL_PLAYER = {
    "name": "新玩家",
    "level": 1,
    "exp": 0,
    "money": 1000,
    "energy": 100  # 初始能量值
}

# 每日能量消耗
ENERGY_COSTS = {
    "till": 2,     # 耕地
    "water": 1,    # 浇水
    "harvest": 1,  # 收获
    "feed": 1      # 喂食
}