# 像素风格房屋图像

这个目录包含游戏中使用的像素风格房屋图像，主要用于在住宅区域显示。

## 当前可用的房屋样式

- `pixel_house.svg` - 基本的像素风格房屋，带有红色屋顶和米色墙壁

## 如何添加新的房屋样式

1. 创建新的SVG格式房屋图像文件，建议使用矢量图形编辑器（如Inkscape、Adobe Illustrator等）
2. 将新创建的房屋图像保存在此目录中
3. 在`entities/area.py`文件的`_load_area_images`方法中添加新房屋图像的引用

```python
def _load_area_images(self):
    """加载区域特定图像，如住宅区的房屋图像"""
    # 区域特定图像映射
    area_image_types = {
        self.HOUSING: "pixel_house.svg",  # 默认房屋样式
        # self.HOUSING: "new_house_style.svg",  # 新的房屋样式
        # 其他区域类型的特定图像可以在这里添加
    }
```

## 设计建议

- 保持像素风格的一致性
- 使用SVG格式以确保图像可以无损缩放
- 建议尺寸为256x256像素
- 使用与游戏整体风格相匹配的配色方案