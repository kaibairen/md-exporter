"""
学术表格样式配置

定义不同类型的学术表格样式
"""

# 表格样式配置
TABLE_STYLES = {
    # ==================== 学术三线表 ====================
    "academic_three_line": {
        "name": "三线表",
        "description": "学术三线表样式 - 顶粗、中细、底粗，无竖线（中国学术标准）",
        "header": {
            "background": "F8F8F8",  # 极浅灰色背景
            "bold": True,
            "align": "center",
            "font_size": 11,  # 稍大
        },
        "borders": {
            "top": {"size": "12", "color": "000000", "style": "single"},      # 顶线 - 粗 (1.5pt)
            "bottom": {"size": "12", "color": "000000", "style": "single"},   # 底线 - 粗 (1.5pt)
            "header_bottom": {"size": "6", "color": "000000", "style": "single"},  # 栏目线 (0.75pt)
            "inner_horizontal": {"size": "0", "color": "000000", "style": "none"},  # 内部横线 - 无
            "left": {"size": "0", "color": "000000", "style": "none"},       # 左边线 - 无
            "right": {"size": "0", "color": "000000", "style": "none"},      # 右边线 - 无
            "vertical": {"size": "0", "color": "000000", "style": "none"},   # 竖线 - 无
        },
        "rows": {
            "odd": {"background": "FFFFFF"},  # 奇数行 - 白色
            "even": {"background": "FFFFFF"}, # 偶数行 - 白色
        }
    },

    # ==================== 学术条纹表 ====================
    "academic_striped": {
        "name": "条纹表",
        "description": "学术条纹表样式 - 斑马纹，完整边框，适合大量数据的表格",
        "header": {
            "background": "D9E1F2",  # 蓝灰色表头
            "bold": True,
            "align": "center",
            "font_size": 11,
        },
        "borders": {
            "top": {"size": "12", "color": "000000", "style": "single"},      # 表顶粗线
            "bottom": {"size": "12", "color": "000000", "style": "single"},   # 表底粗线
            "header_bottom": {"size": "12", "color": "000000", "style": "single"},  # 表底粗线
            "inner_horizontal": {"size": "4", "color": "666666", "style": "single"},  # 内部横线
            "left": {"size": "4", "color": "666666", "style": "single"},       # 左边线
            "right": {"size": "4", "color": "666666", "style": "single"},      # 右边线
            "vertical": {"size": "4", "color": "666666", "style": "single"},   # 竖线
        },
        "rows": {
            "odd": {"background": "E8EDF5"},   # 浅蓝色
            "even": {"background": "FFFFFF"},  # 白色
        }
    },

    # ==================== 简单网格表 ====================
    "simple_grid": {
        "name": "简单网格",
        "description": "简单网格表样式 - 所有线条一致，简洁清晰",
        "header": {
            "background": "F2F2F2",  # 浅灰色表头
            "bold": True,
            "align": "center",
            "font_size": 11,
        },
        "borders": {
            "top": {"size": "6", "color": "000000", "style": "single"},      # 稍粗
            "bottom": {"size": "6", "color": "000000", "style": "single"},   # 稍粗
            "header_bottom": {"size": "6", "color": "000000", "style": "single"},
            "inner_horizontal": {"size": "4", "color": "000000", "style": "single"},  # 标准细线
            "left": {"size": "4", "color": "000000", "style": "single"},
            "right": {"size": "4", "color": "000000", "style": "single"},
            "vertical": {"size": "4", "color": "000000", "style": "single"},
        },
        "rows": {
            "odd": {"background": "FFFFFF"},  # 白色
            "even": {"background": "FAFAFA"}, # 极浅灰色
        }
    },

    # ==================== 极简表格 ====================
    "minimal": {
        "name": "极简表格",
        "description": "极简表格样式 - 仅表头和表底有边框，现代简洁",
        "header": {
            "background": "FFFFFF",
            "bold": True,
            "align": "left",  # 左对齐
            "font_size": 11,
        },
        "borders": {
            "top": {"size": "12", "color": "000000", "style": "single"},
            "bottom": {"size": "12", "color": "000000", "style": "single"},
            "header_bottom": {"size": "8", "color": "000000", "style": "single"},
            "inner_horizontal": {"size": "0", "color": "000000", "style": "none"},
            "left": {"size": "0", "color": "000000", "style": "none"},
            "right": {"size": "0", "color": "000000", "style": "none"},
            "vertical": {"size": "0", "color": "000000", "style": "none"},
        },
        "rows": {
            "odd": {"background": "FFFFFF"},
            "even": {"background": "FFFFFF"},
        }
    },
}

# 默认样式
DEFAULT_TABLE_STYLE = "academic_three_line"


def get_table_style(style_name=None):
    """
    获取表格样式配置

    Args:
        style_name: 样式名称，如果为None则使用默认样式

    Returns:
        样式配置字典
    """
    if style_name is None:
        style_name = DEFAULT_TABLE_STYLE

    if style_name not in TABLE_STYLES:
        # 如果样式不存在，返回默认样式
        style_name = DEFAULT_TABLE_STYLE

    return TABLE_STYLES[style_name]


def list_available_styles():
    """列出所有可用的表格样式"""
    return [
        {
            "id": style_id,
            "name": config["name"],
            "description": config["description"]
        }
        for style_id, config in TABLE_STYLES.items()
    ]
