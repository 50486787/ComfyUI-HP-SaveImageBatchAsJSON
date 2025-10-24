# 1. 导入主代码文件中的类。
try:
    # 尝试导入新的 JSON 节点
    from .HP_SaveImageBatchAsJSON import HP_SaveImageBatchAsJSON

    # 如果您还需要旧的文本节点，可以保留下面这行并确保文件存在：
    # from .HP_SaveTextListToFile import HP_SaveTextListToFile

except ImportError as e:
    print(f"--- 致命错误: 无法导入自定义节点 ---")
    print(f"错误信息: {e}")
    HP_SaveImageBatchAsJSON = None
    # HP_SaveTextListToFile = None

# 2. 注册节点类映射
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

if HP_SaveImageBatchAsJSON is not None:
    NODE_CLASS_MAPPINGS["HP_SaveImageBatchAsJSON"] = HP_SaveImageBatchAsJSON
    NODE_DISPLAY_NAME_MAPPINGS["HP_SaveImageBatchAsJSON"] = "HP-图像Batch保存为JSON"

# 如果您保留了 HP_SaveTextListToFile，请取消下面注释
# if HP_SaveTextListToFile is not None:
#     NODE_CLASS_MAPPINGS["HP_SaveTextListToFile"] = HP_SaveTextListToFile
#     NODE_DISPLAY_NAME_MAPPINGS["HP_SaveTextListToFile"] = "HP-文本列表保存为多个文档"


# 3. 导出映射
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]