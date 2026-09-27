import json
import os

# 强排除词列表，可根据需要继续补充
STRONG_REMOVE_PATTERNS = [
    "本研究中", "作者提到", "教材", "课后", "章节", "节中", "实验中", "项目申请", "资金", "事前项目申请", "教材中", "书中", "文章中", "论文中", "综上所述", "如图所示", "如表所示", "如上所述", "如前所述", "如前文所述", "如后文所述", "如本章所述", "如本节所述", "如本书所述", "如本研究所述", "如本论文所述", "如本项目所述", "如本课题所述"
]

# 需要清洗的文件路径
file_path = os.path.join(os.path.dirname(__file__), "data", "ocean_restoration_cleaned.json")

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

cleaned = []
for item in data:
    text = item.get('content', '') or item.get('text', '') or str(item)
    if any(pat in text for pat in STRONG_REMOVE_PATTERNS):
        continue
    cleaned.append(item)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f"强排除清洗后数据量: {len(cleaned)}")
