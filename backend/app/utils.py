"""
工具函数
"""
import re
from typing import Optional


def extract_number(text: str) -> Optional[float]:
    """从文本中提取数字"""
    if not text:
        return None
    
    # 移除逗号（千位分隔符）
    text = text.replace(',', '').replace('，', '')
    
    # 提取数字（支持小数）
    numbers = re.findall(r'\d+\.?\d*', text)
    if numbers:
        return float(numbers[0])
    
    return None


def clean_dorm_number(dorm: str) -> str:
    """清理宿舍号格式"""
    if not dorm:
        return ""
    
    # 移除空格和特殊字符，只保留数字和字母
    cleaned = re.sub(r'[^\w]', '', str(dorm))
    return cleaned.strip()
