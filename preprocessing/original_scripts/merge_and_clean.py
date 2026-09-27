import json
import os

# 优化后的关键词列表
KEYWORDS = [
    # 基础词
    '海洋', '海域', '海水', '海岸', '沿海', '滨海',
    '修复', '恢复', '治理', '保护', '改善', '净化',
    '生态', '环境', '污染', '生物', '化学', '物理',
    '微塑料', '塑料', '污染物', '吸附', '降解',
    # 组合词
    '海洋修复', '海域修复', '海水修复', '海岸修复', '沿海修复', '滨海修复',
    '海洋恢复', '海域恢复', '海水恢复', '海岸恢复', '沿海恢复', '滨海恢复',
    '海洋治理', '海域治理', '海水治理', '海岸治理', '沿海治理', '滨海治理',
    '海洋保护', '海域保护', '海水保护', '海岸保护', '沿海保护', '滨海保护',
    '生物修复', '物理修复', '化学修复', '综合修复', '生态修复',
    '原位修复', '异位修复', '自然修复', '人工修复', '工程修复',
    '红树林', '珊瑚礁', '海草床', '滨海湿地', '海洋生态系统',
    '海洋生物多样性', '海洋栖息地', '海洋生物群落', '海洋食物网',
    '海洋生态位', '海洋生物链', '海洋生物圈', '海洋生物带',
    '增殖放流', '基因编辑', '微生物技术', '疏浚技术',
    '生物膜', '生物强化', '生物刺激', '鱼礁', '珊瑚', '海草', '湿地', '沙滩', '海岸',
    '纳米材料', '生物炭', '吸附剂', '生物填料', '生物载体',
    '生物膜材料', '生物修复剂', '生物刺激剂', '生物强化剂',
    '重金属', '营养盐', '有机物', '无机物', '污染物',
    '氮', '磷', '硫', '碳', '氧', '氢', '钠', '钾', '钙', '镁',
    '保护区', '自然保护区', '特别保护区', '海洋公园',
    '生态保护区', '生物保护区', '景观保护区',
    '国际合作', '国际公约', '国际协议', '国际条约', '国际组织',
    '国际项目', '国际计划', '国际行动',
    '重建', '生态系统', '生物多样性', '栖息地', '生物群落',
    '海洋环境', '海洋资源', '海洋生物', '海洋污染',
    '海洋生态', '海洋保护', '海洋修复', '海洋治理',
    '海水质量', '水质', '底质', '沉积物', '泥沙',
    '微塑料', '塑料污染', '塑料降解', '塑料吸附',
    '塑料治理', '塑料修复', '塑料回收', '塑料处理',
    '塑料污染治理', '塑料污染修复', '塑料污染控制',
    '塑料污染监测', '塑料污染评估', '塑料污染研究'
]

REMOVE_PATTERNS = [
    "根据文章内容", "根据研究内容", "本文主要", "文章主要", "本研究", "本论文", "本项目", "本课题"
]

def merge_json_files(file_list, output_file):
    merged_data = []
    for file in file_list:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                merged_data.extend(data)
            else:
                merged_data.append(data)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    return merged_data

def clean_data(data):
    cleaned = []
    for item in data:
        text = item.get('content', '') or item.get('text', '') or str(item)
        # 只要包含任意关键词即可保留
        if not any(kw in text for kw in KEYWORDS):
            continue
        # 去除明显无关描述
        if any(pat in text for pat in REMOVE_PATTERNS):
            continue
        cleaned.append(item)
    return cleaned

if __name__ == "__main__":
    # 保证无论脚本在哪里运行都能找到data文件夹
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    files = [
        os.path.join(data_dir, "专业海洋修复.json"),
        os.path.join(data_dir, "专业海洋修复2.json"),
        os.path.join(data_dir, "total_data.json"),
    ]
    merged = merge_json_files(files, os.path.join(data_dir, "merged_data.json"))
    cleaned = clean_data(merged)
    with open(os.path.join(data_dir, "ocean_restoration_cleaned.json"), 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
    print(f"清洗后数据量: {len(cleaned)}")
