import json
import os
import random

# 读取清洗后的数据
file_path = os.path.join(os.path.dirname(__file__), "data", "ocean_restoration_cleaned.json")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

random.shuffle(data)

split_idx = int(len(data) * 0.9)
train_data = data[:split_idx]
val_data = data[split_idx:]

with open(os.path.join(os.path.dirname(__file__), "data", "mu_train.json"), 'w', encoding='utf-8') as f:
    json.dump(train_data, f, ensure_ascii=False, indent=2)

with open(os.path.join(os.path.dirname(__file__), "data", "mu_val.json"), 'w', encoding='utf-8') as f:
    json.dump(val_data, f, ensure_ascii=False, indent=2)

print(f"训练集数量: {len(train_data)}，验证集数量: {len(val_data)}")
