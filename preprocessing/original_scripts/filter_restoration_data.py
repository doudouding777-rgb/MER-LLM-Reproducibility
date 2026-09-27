import json
import os
import re

# 文件路径
input_file = r'${DATASET_46K_PATH}\merged_cleaned_data.json'
output_file = r'${DATASET_46K_PATH}\restoration_filtered_data.json'

# 定义修复相关的关键词
restoration_keywords = [
    '修复', '修复措施', '修复技术', '修复方法', '修复方案', '修复工程',
    '生态修复', '环境修复', '生物修复', '物理修复', '化学修复', '综合修复',
    '原位修复', '异位修复', '自然修复', '人工修复', '工程修复',
    '修复效果', '修复效果评估', '修复效果监测', '修复效果评价',
    '修复机制', '修复原理', '修复机理', '修复过程', '修复阶段',
    '修复材料', '修复设备', '修复工具', '修复剂', '修复剂配方',
    '修复成本', '修复费用', '修复投资', '修复预算', '修复经济性',
    '修复时间', '修复周期', '修复工期', '修复进度', '修复计划',
    '修复标准', '修复规范', '修复要求', '修复指标', '修复目标',
    '修复设计', '修复规划', '修复策略', '修复对策', '修复建议',
    '修复实践', '修复案例', '修复经验', '修复教训', '修复总结',
    '修复研究', '修复实验', '修复试验', '修复测试', '修复验证',
    '修复应用', '修复推广', '修复示范', '修复试点', '修复项目',
    '修复管理', '修复监督', '修复检查', '修复验收', '修复维护',
    '修复更新', '修复改造', '修复重建', '修复恢复', '修复改善',
    '修复治理', '修复保护', '修复保育', '修复养护', '修复维护',
    '修复技术路线', '修复技术方案', '修复技术规范', '修复技术标准',
    '修复技术体系', '修复技术框架', '修复技术平台', '修复技术系统',
    '修复技术装备', '修复技术设备', '修复技术工具', '修复技术材料',
    '修复技术工艺', '修复技术流程', '修复技术步骤', '修复技术方法',
    '修复技术手段', '修复技术措施', '修复技术对策', '修复技术策略',
    '修复技术路线图', '修复技术发展规划', '修复技术实施方案',
    '修复技术操作规程', '修复技术质量要求', '修复技术验收标准',
    '修复技术评价体系', '修复技术监测体系', '修复技术管理体系'
]

def contains_restoration_keywords(text):
    """检查文本是否包含修复相关关键词"""
    if not isinstance(text, str):
        return False
    
    # 检查是否包含修复相关关键词
    for keyword in restoration_keywords:
        if keyword in text:
            return True
    
    return False

def filter_restoration_data(data):
    """筛选包含修复关键词的数据"""
    filtered_data = []
    
    for item in data:
        if isinstance(item, dict):
            # 如果是字典格式，检查content或text字段
            content = item.get('content', '') or item.get('text', '') or str(item)
        else:
            content = str(item)
        
        # 检查是否包含修复关键词
        if contains_restoration_keywords(content):
            filtered_data.append(item)
    
    return filtered_data

def main():
    print("开始筛选修复相关数据...")
    
    # 读取原始数据
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"原始数据量: {len(data)}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 筛选数据
    filtered_data = filter_restoration_data(data)
    print(f"筛选后数据量: {len(filtered_data)}")
    
    # 保存筛选后的数据
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)
        print(f"筛选后的数据已保存到: {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return
    
    # 统计信息
    print(f"\n筛选统计:")
    print(f"- 原始数据: {len(data)} 条")
    print(f"- 筛选后数据: {len(filtered_data)} 条")
    print(f"- 筛选比例: {len(filtered_data)/len(data)*100:.2f}%")
    
    # 显示一些关键词统计
    keyword_counts = {}
    for item in filtered_data:
        if isinstance(item, dict):
            content = item.get('content', '') or item.get('text', '') or str(item)
        else:
            content = str(item)
        
        for keyword in restoration_keywords:
            if keyword in content:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    print(f"\n关键词出现频次统计 (前20个):")
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    for keyword, count in sorted_keywords[:20]:
        print(f"- {keyword}: {count} 次")

if __name__ == "__main__":
    main() 