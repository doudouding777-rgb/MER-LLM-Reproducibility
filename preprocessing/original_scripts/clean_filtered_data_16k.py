import json
import os
import re

# 文件路径
input_file = r'${DATASET_46K_PATH}\restoration_filtered_data.json'
output_file = r'${DATASET_46K_PATH}\restoration_final_cleaned.json'

# 定义需要清洗的模式
remove_patterns = [
    r'根据文中.*?[,，。；;]?',
    r'文章中.*?[,，。；;]?',
    r'参考内容.*?[,，。；;]?',
    r'文中提到.*?[,，。；;]?',
    r'根据文章.*?[,，。；;]?',
    r'文章内容.*?[,，。；;]?',
    r'文章指出.*?[,，。；;]?',
    r'文章认为.*?[,，。；;]?',
    r'文章表明.*?[,，。；;]?',
    r'文章显示.*?[,，。；;]?',
    r'文章说明.*?[,，。；;]?',
    r'文章描述.*?[,，。；;]?',
    r'文章分析.*?[,，。；;]?',
    r'文章研究.*?[,，。；;]?',
    r'文章探讨.*?[,，。；;]?',
    r'文章讨论.*?[,，。；;]?',
    r'文章阐述.*?[,，。；;]?',
    r'文章论述.*?[,，。；;]?',
    r'文章介绍.*?[,，。；;]?',
    r'文章总结.*?[,，。；;]?',
    r'文章结论.*?[,，。；;]?',
    r'文章建议.*?[,，。；;]?',
    r'文章提出.*?[,，。；;]?',
    r'文章发现.*?[,，。；;]?',
    r'文章揭示.*?[,，。；;]?',
    r'文章揭示.*?[,，。；;]?',
    r'文章揭示.*?[,，。；;]?',
    r'本文.*?[,，。；;]?',
    r'本研究中.*?[,，。；;]?',
    r'作者提到.*?[,，。；;]?',
    r'作者认为.*?[,，。；;]?',
    r'作者指出.*?[,，。；;]?',
    r'作者分析.*?[,，。；;]?',
    r'作者研究.*?[,，。；;]?',
    r'作者探讨.*?[,，。；;]?',
    r'作者讨论.*?[,，。；;]?',
    r'作者阐述.*?[,，。；;]?',
    r'作者论述.*?[,，。；;]?',
    r'作者介绍.*?[,，。；;]?',
    r'作者总结.*?[,，。；;]?',
    r'作者结论.*?[,，。；;]?',
    r'作者建议.*?[,，。；;]?',
    r'作者提出.*?[,，。；;]?',
    r'作者发现.*?[,，。；;]?',
    r'作者揭示.*?[,，。；;]?',
    r'教材.*?[,，。；;]?',
    r'课后.*?[,，。；;]?',
    r'章节.*?[,，。；;]?',
    r'节中.*?[,，。；;]?',
    r'实验中.*?[,，。；;]?',
    r'项目申请.*?[,，。；;]?',
    r'资金.*?[,，。；;]?',
    r'事前项目申请.*?[,，。；;]?',
    r'教材中.*?[,，。；;]?',
    r'书中.*?[,，。；;]?',
    r'论文中.*?[,，。；;]?',
    r'综上所述.*?[,，。；;]?',
    r'如图所示.*?[,，。；;]?',
    r'如表所示.*?[,，。；;]?',
    r'如上所述.*?[,，。；;]?',
    r'如前所述.*?[,，。；;]?',
    r'如前文所述.*?[,，。；;]?',
    r'如后文所述.*?[,，。；;]?',
    r'如本章所述.*?[,，。；;]?',
    r'如本节所述.*?[,，。；;]?',
    r'如本书所述.*?[,，。；;]?',
    r'如本研究所述.*?[,，。；;]?',
    r'如本论文所述.*?[,，。；;]?',
    r'如本项目所述.*?[,，。；;]?',
    r'如本课题所述.*?[,，。；;]?',
    r'参考.*?[,，。；;]?',
    r'参考文献.*?[,，。；;]?',
    r'参考内容.*?[,，。；;]?',
    r'参考数据.*?[,，。；;]?',
    r'参考信息.*?[,，。；;]?',
    r'参考资料.*?[,，。；;]?',
    r'参考文献.*?[,，。；;]?',
    r'参考案例.*?[,，。；;]?',
    r'参考经验.*?[,，。；;]?',
    r'参考方法.*?[,，。；;]?',
    r'参考技术.*?[,，。；;]?',
    r'参考标准.*?[,，。；;]?',
    r'参考规范.*?[,，。；;]?',
    r'参考要求.*?[,，。；;]?',
    r'参考指标.*?[,，。；;]?',
    r'参考目标.*?[,，。；;]?'
]

def clean_text(text):
    """清洗文本，去除照本宣科的内容"""
    if not isinstance(text, str):
        return text
    
    # 应用所有清洗模式
    for pattern in remove_patterns:
        text = re.sub(pattern, '', text)
    
    # 去除多余的空格和换行
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    return text

def should_keep_item(item):
    """判断是否应该保留该数据项"""
    if isinstance(item, dict):
        # 如果是字典格式，检查content或text字段
        content = item.get('content', '') or item.get('text', '') or str(item)
    else:
        content = str(item)
    
    # 如果内容太短，不保留
    if len(content.strip()) < 10:
        return False
    
    # 如果包含明显的照本宣科词汇，不保留
    skip_keywords = [
        '根据文中', '文章中', '参考内容', '文中提到', '根据文章', 
        '文章内容', '文章指出', '文章认为', '文章表明', '文章显示',
        '文章说明', '文章描述', '文章分析', '文章研究', '文章探讨',
        '文章讨论', '文章阐述', '文章论述', '文章介绍', '文章总结',
        '文章结论', '文章建议', '文章提出', '文章发现', '文章揭示',
        '本文', '本研究中', '作者提到', '作者认为', '作者指出',
        '作者分析', '作者研究', '作者探讨', '作者讨论', '作者阐述',
        '作者论述', '作者介绍', '作者总结', '作者结论', '作者建议',
        '作者提出', '作者发现', '作者揭示', '教材', '课后', '章节',
        '节中', '实验中', '项目申请', '资金', '事前项目申请',
        '教材中', '书中', '论文中', '综上所述', '如图所示', '如表所示',
        '如上所述', '如前所述', '如前文所述', '如后文所述', '如本章所述',
        '如本节所述', '如本书所述', '如本研究所述', '如本论文所述',
        '如本项目所述', '如本课题所述', '参考', '参考文献', '参考内容',
        '参考数据', '参考信息', '参考资料', '参考文献', '参考案例',
        '参考经验', '参考方法', '参考技术', '参考标准', '参考规范',
        '参考要求', '参考指标', '参考目标'
    ]
    
    if any(keyword in content for keyword in skip_keywords):
        return False
    
    return True

def clean_data(data):
    """清洗数据"""
    cleaned_data = []
    
    for item in data:
        if should_keep_item(item):
            if isinstance(item, dict):
                # 清洗字典中的文本字段
                cleaned_item = {}
                for key, value in item.items():
                    if isinstance(value, str):
                        cleaned_item[key] = clean_text(value)
                    else:
                        cleaned_item[key] = value
                cleaned_data.append(cleaned_item)
            else:
                # 清洗字符串
                cleaned_text = clean_text(str(item))
                if cleaned_text:
                    cleaned_data.append(cleaned_text)
    
    return cleaned_data

def main():
    print("开始清洗筛选后的修复数据...")
    
    # 读取筛选后的数据
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"筛选后原始数据量: {len(data)}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 清洗数据
    cleaned_data = clean_data(data)
    print(f"清洗后数据量: {len(cleaned_data)}")
    
    # 保存清洗后的数据
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"清洗后的数据已保存到: {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return
    
    # 统计信息
    print(f"\n清洗统计:")
    print(f"- 筛选后原始数据: {len(data)} 条")
    print(f"- 清洗后数据: {len(cleaned_data)} 条")
    print(f"- 清洗比例: {len(cleaned_data)/len(data)*100:.2f}%")
    print(f"- 清洗掉的数据: {len(data) - len(cleaned_data)} 条")

if __name__ == "__main__":
    main() 