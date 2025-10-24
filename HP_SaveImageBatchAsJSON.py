# HP_SaveImageBatchAsJSON.py (使用 Batch Index 模式)
import os
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from pathlib import Path
from datetime import datetime
import base64
import re

# --- 路径导入 (关键) ---
try:
    from nodes import folder_paths

    BASE_OUTPUT_DIR = folder_paths.get_output_directory()
except ImportError:
    BASE_OUTPUT_DIR = os.path.join(Path.cwd(), "ComfyUI/output")


class HP_SaveImageBatchAsJSON:

    @classmethod
    def IS_CHANGED(s, *args, **kwargs):
        return float("NaN")

    def __init__(self):
        os.makedirs(BASE_OUTPUT_DIR, exist_ok=True)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                # **** 新增输入：ComfyUI Batch Index 和 Size ****
                "batch_index": ("INT", {"default": 0, "min": 0}),
                "total_batch_size": ("INT", {"default": 0, "min": 0}),
                # *********************************************
                "path_template": ("STRING", {"default": "output/[time(%Y-%m-%d)]/json", "multiline": False}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "multiline": False}),
                "delimiter": ("STRING", {"default": "_", "multiline": False}),
                "number_padding": ("INT", {"default": 6, "min": 2, "max": 9, "step": 1}),
                "image_format": (["PNG", "JPEG", "WEBP"],),
                "quality": ("INT", {"default": 100, "min": 1, "max": 100, "step": 1}),
            },
        }

    # 仅输出状态和字典
    RETURN_TYPES = ("STRING", "DICTIONARY")
    RETURN_NAMES = ("status_message", "output_dictionary")
    FUNCTION = "save_json_batch"
    CATEGORY = "HP-自制节点"

    def tensor_to_base64_string(self, image_tensor, image_format="PNG", quality=80):
        # ... (辅助函数保持不变) ...
        img_np = image_tensor.cpu().numpy()
        img_np = (img_np * 255).astype(np.uint8)
        img = Image.fromarray(img_np)

        buffered = BytesIO()

        if image_format == "JPEG":
            img.save(buffered, format=image_format, quality=quality)
        elif image_format == "WEBP":
            img.save(buffered, format=image_format, quality=quality)
        else:
            img.save(buffered, format="PNG")

        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def save_json_batch(self, images, batch_index, total_batch_size, path_template, filename_prefix, delimiter,
                        number_padding, image_format, quality):

        if images is None or images.shape[0] == 0:
            return ("错误: 输入图像 Batch 为空。", {})

        # 核心计算：确定全局起始帧编号
        # ComfyUI 的 batch_index 通常从 1 开始
        # Start Index = (Batch Index) * Batch Size + 1
        start_frame_number = (batch_index) * total_batch_size + 1

        # 1. Base64 编码
        base64_batch_dict = {}
        batch_size = images.shape[0]  # 当前 Batch 中实际的图片数量

        for i, img_tensor in enumerate(images):
            # 全局帧编号 = 起始编号 + 批次内索引 (从 0 开始)
            global_frame_index = start_frame_number + i
            frame_number_str = f"{global_frame_index:06d}"

            try:
                b64_string = self.tensor_to_base64_string(img_tensor, image_format, quality)

                # 字典键名包含全局编号
                base64_batch_dict[f"image_{frame_number_str}"] = {
                    "global_index": global_frame_index,
                    "format": image_format,
                    "base64": b64_string
                }
            except Exception as e:
                base64_batch_dict[f"image_{frame_number_str}"] = {"error": f"Base64 转换失败: {e}"}

        # ... (路径处理、JSON 文件命名、保存 JSON 部分保持不变) ...
        relative_path = path_template.lstrip('./').lstrip('/')
        if '[time(' in relative_path:
            try:
                start = relative_path.find('[time(') + 6
                end = relative_path.find(')]', start)
                time_format = relative_path[start:end]
                time_string = datetime.now().strftime(time_format)
                relative_path = relative_path.replace(relative_path[relative_path.find('[time('):end + 2], time_string)
            except Exception:
                pass
        target_dir = Path(BASE_OUTPUT_DIR) / relative_path
        os.makedirs(target_dir, exist_ok=True)

        # 3. 递增逻辑 (复用之前的 JSON 文件命名逻辑)
        file_extension = ".json"
        pattern = f"^{re.escape(filename_prefix)}{re.escape(delimiter)}(\\d{{{number_padding}}}){re.escape(file_extension)}$"
        current_counter = 1

        try:
            existing_counters = [
                int(re.search(pattern, filename).group(1))
                for filename in os.listdir(target_dir)
                if re.match(pattern, filename)
            ]
            if existing_counters: current_counter = max(existing_counters) + 1
        except Exception:
            current_counter = 1

        # 4. 构造最终 JSON 文件路径
        number_str = str(current_counter).zfill(number_padding)
        final_filename = f"{filename_prefix}{delimiter}{number_str}{file_extension}"
        final_path = target_dir / final_filename

        # 5. 保存 JSON 文件
        try:
            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump(base64_batch_dict, f, indent=4)

            status = f"[成功] 成功将 {batch_size} 张图像 (全局帧 {start_frame_number} 至 {start_frame_number + batch_size - 1}) 保存到 JSON 文件: {final_path}"
        except Exception as e:
            status = f"[失败] 无法写入 JSON 文件 '{final_path}'. 错误: {e}"

        return (status, base64_batch_dict,)