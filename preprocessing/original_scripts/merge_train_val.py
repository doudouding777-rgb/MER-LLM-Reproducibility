import json
import os
import re

# 文件路径
train_file = r'${DATASET_46K_PATH}\train.json'
val_file = r'${DATASET_46K_PATH}\val.json'
output_file = r'${DATASET_46K_PATH}\merged_cleaned_data.json'

# 定义需要清洗的模式
remove_patterns = [
    r'文中提到.*?[,，。；;]?',
    r'根据文中.*?[,，。；;]?',
    r'第八到九章主要讨论了哪些重大问题.*?[,，。；;]?',
    r'本文.*?[,，。；;]?',
    r'文章.*?[,，。；;]?',
    r'本研究中.*?[,，。；;]?',
    r'作者提到.*?[,，。；;]?',
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
    r'文章中.*?[,，。；;]?',
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
    r'如本课题所述.*?[,，。；;]?'
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
    skip_keywords = ['文中提到', '根据文中', '第八到九章', '本文', '文章', '本研究中']
    if any(keyword in content for keyword in skip_keywords):
        return False
    
    return True

def load_and_clean_data(file_path):
    """加载并清洗数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
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
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return []

# 合并和清洗数据
print("开始合并和清洗数据...")

# 加载训练集
train_data = load_and_clean_data(train_file)
print(f"训练集清洗后数据量: {len(train_data)}")

# 加载验证集
val_data = load_and_clean_data(val_file)
print(f"验证集清洗后数据量: {len(val_data)}")

# 合并数据
merged_data = train_data + val_data
print(f"合并后总数据量: {len(merged_data)}")

# 去重
unique_data = []
seen = set()
for item in merged_data:
    if isinstance(item, dict):
        # 对于字典，使用content或text字段作为唯一标识
        content = item.get('content', '') or item.get('text', '') or str(item)
    else:
        content = str(item)
    
    if content not in seen:
        seen.add(content)
        unique_data.append(item)

print(f"去重后数据量: {len(unique_data)}")

# 保存清洗后的数据
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(unique_data, f, ensure_ascii=False, indent=2)

print(f"数据已保存到: {output_file}") 