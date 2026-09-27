import json
import os
import random

# 文件路径
input_file = r'${DATASET_46K_PATH}\restoration_final_cleaned.json'
train_file = r'${DATASET_46K_PATH}\restoration_train.json'
val_file = r'${DATASET_46K_PATH}\restoration_val.json'

def split_data(data, train_ratio=0.9):
    """按比例划分数据"""
    # 打乱数据
    random.shuffle(data)
    
    # 计算分割点
    total = len(data)
    split_idx = int(total * train_ratio)
    
    # 划分数据
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    return train_data, val_data

def main():
    print("开始划分最终清洗后的修复数据...")
    
    # 读取数据
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"原始数据量: {len(data)}")
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 划分数据
    train_data, val_data = split_data(data, train_ratio=0.9)
    
    print(f"训练集数据量: {len(train_data)}")
    print(f"验证集数据量: {len(val_data)}")
    
    # 保存训练集
    try:
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, ensure_ascii=False, indent=2)
        print(f"训练集已保存到: {train_file}")
    except Exception as e:
        print(f"保存训练集时出错: {e}")
        return
    
    # 保存验证集
    try:
        with open(val_file, 'w', encoding='utf-8') as f:
            json.dump(val_data, f, ensure_ascii=False, indent=2)
        print(f"验证集已保存到: {val_file}")
    except Exception as e:
        print(f"保存验证集时出错: {e}")
        return
    
    # 统计信息
    print(f"\n数据划分统计:")
    print(f"- 原始数据: {len(data)} 条")
    print(f"- 训练集: {len(train_data)} 条 ({len(train_data)/len(data)*100:.2f}%)")
    print(f"- 验证集: {len(val_data)} 条 ({len(val_data)/len(data)*100:.2f}%)")
    print(f"- 划分比例: 9:1")

if __name__ == "__main__":
    main() 