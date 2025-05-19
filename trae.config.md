# 一个类似星露谷物语的游戏，是一种养成类游戏，要实现对作物的耕种收割，需要一个数据库来存储这些作物和玩家的一些信息，确保下次再登录这个游戏的时候会有之前的数据。还需要添加一些畜牧类的数据，比如可以养牛羊。需要用到pygame库。然后整体的游戏不要过于简单。可以添加一些玩家的升级，对于农作物和畜牧产品的售卖等。

## 角色描述
1. 你是一个精通python, SQLite的程序员


# 技术栈
- python
- pygame
- sqlite3
- pytest

# 项目结构
stardew_clone/
│
├── assets/                     # 存放所有图像、音效等资源
│   ├── images/
│   │   ├── crops/
│   │   ├── animals/
│   │   ├── tools/
│   │   ├── tiles/
│   │   └── player/
│   └── sounds/
│
├── database/                   # 数据库和相关操作模块
│   ├── game.db                 # SQLite 数据库文件
│   └── db_manager.py          # 数据库初始化与操作方法封装
│
├── entities/                   # 游戏中各种实体
│   ├── player.py
│   ├── crop.py
│   ├── animal.py
│   ├── tool.py
│   └── inventory.py
│
├── scenes/                     # 游戏不同场景或界面
│   ├── main_menu.py
│   ├── farm_scene.py
│   └── market_scene.py
│
├── systems/                    # 游戏系统逻辑（耕种、天气、售卖、升级等）
│   ├── farming_system.py
│   ├── animal_system.py
│   ├── weather_system.py
│   ├── sell_system.py
│   └── level_system.py
│
├── utils/                      # 通用工具函数
│   └── helpers.py
│
├── config.py                   # 配置文件，如窗口尺寸、FPS 等
├── game.py                     # 游戏主入口
└── requirements.txt            # 项目依赖



# 简要说明：
assets/：你可以把所有角色、作物、动物、工具等图片和声音资源放在这里。

database/：管理和初始化 SQLite 数据库，如创建玩家表、作物表、动物表等。

entities/：用面向对象的方式封装游戏中的核心角色和物品。

scenes/：可扩展成一个状态机，处理主菜单、农场界面、市场界面等不同游戏状态。

systems/：每个系统负责一类功能，比如种植逻辑、动物饲养逻辑、交易逻辑。

game.py：是游戏的入口，负责初始化 pygame，加载资源，切换场景等。

sounds/：存放游戏中的音效文件。

# 数据库设计
🧑‍🌾 表：player（玩家信息）
| 字段名         | 类型         | 说明        |
| ----------- | ---------- | --------- |
| id          | INTEGER PK | 玩家ID，自增主键 |
| name        | TEXT       | 玩家名称      |
| level       | INTEGER    | 玩家等级      |
| exp         | INTEGER    | 当前经验值     |
| money       | INTEGER    | 当前金币      |
| last\_login | TEXT       | 上次登录时间    |

🌱 表：crops（作物种植状态）
| 字段名           | 类型         | 说明           |
| ------------- | ---------- | ------------ |
| id            | INTEGER PK | 作物ID，自增主键    |
| player\_id    | INTEGER    | 所属玩家         |
| crop\_type    | TEXT       | 作物种类（如小麦、番茄） |
| x             | INTEGER    | 农田X坐标        |
| y             | INTEGER    | 农田Y坐标        |
| growth\_stage | INTEGER    | 当前生长阶段       |
| planted\_at   | TEXT       | 种植时间（时间戳）    |
| is\_watered   | INTEGER    | 是否浇水（0/1）    |

🐮 表：animals（畜牧动物）
| 字段名           | 类型         | 说明         |
| ------------- | ---------- | ---------- |
| id            | INTEGER PK | 动物ID，自增主键  |
| player\_id    | INTEGER    | 所属玩家       |
| animal\_type  | TEXT       | 动物种类（牛、羊等） |
| name          | TEXT       | 给动物起的名字    |
| age           | INTEGER    | 天数龄        |
| is\_fed       | INTEGER    | 是否喂食（0/1）  |
| produce\_time | TEXT       | 上次产出时间     |

🎒 表：inventory（玩家背包）
| 字段名        | 类型         | 说明         |
| ---------- | ---------- | ---------- |
| id         | INTEGER PK | 背包物品ID     |
| player\_id | INTEGER    | 所属玩家       |
| item\_name | TEXT       | 物品名称       |
| quantity   | INTEGER    | 数量         |
| item\_type | TEXT       | 类型（作物、工具等） |

🛠 表：tools（工具信息）
| 字段名        | 类型         | 说明          |
| ---------- | ---------- | ----------- |
| id         | INTEGER PK | 工具ID        |
| player\_id | INTEGER    | 所属玩家        |
| tool\_name | TEXT       | 工具名称（锄头、水壶） |
| durability | INTEGER    | 耐久度         |
| level      | INTEGER    | 工具等级（升级后更快） |

💰 表：sales_log（售卖记录）
| 字段名          | 类型         | 说明        |
| ------------ | ---------- | --------- |
| id           | INTEGER PK | 记录ID      |
| player\_id   | INTEGER    | 所属玩家      |
| item\_name   | TEXT       | 售出物品名称    |
| quantity     | INTEGER    | 售出数量      |
| price\_total | INTEGER    | 总售价（金币）   |
| sold\_at     | TEXT       | 售出时间（时间戳） |
