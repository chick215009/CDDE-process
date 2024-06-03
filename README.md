# CDDE-process

## analysis

- postprocess.py 可以帮助你处理生成后的实验数据，去掉前面的序号获取真实的BLEU值。
- analysePTR.py 协助对比两个输出差异



## GPT

- gpt模板生成



## preprocess

- CSprocess 处理CS生成的数据
  - merge用于在增量更新时合并前后两次变更
  - 其他用于获取增强所需的驼峰词json
- filterdata 划分数据并对数据进行预处理与增强
- checkfrequence.py 数据观察，词频统计
- dataprocess 对原始diff进行处理
  - 获取diff，msg，hashcode与lineid的对应关系

