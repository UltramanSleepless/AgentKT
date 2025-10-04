import numpy as np
import pandas as pd
import torch
from collections import defaultdict
import pickle

def analyze_dataset_structure(data_path):
    """
    分析数据集的结构和内容
    """
    print("=" * 60)
    print("数据集结构分析")
    print("=" * 60)
    
    # 1. 加载主数据集
    print("\n1. 主数据集 (dataset.pkl) 分析:")
    print("-" * 40)
    dataset = pd.read_pickle(data_path + '/dataset.pkl')
    
    print(f"数据集形状: {dataset.shape}")
    print(f"列名: {list(dataset.columns)}")
    print(f"数据类型:\n{dataset.dtypes}")
    
    # 2. 分析各列的基本信息
    print(f"\n各列基本统计信息:")
    print("-" * 40)
    for col in dataset.columns:
        print(f"\n{col}:")
        if dataset[col].dtype == 'object':
            print(f"  唯一值数量: {dataset[col].nunique()}")
            print(f"  示例值: {dataset[col].iloc[:3].tolist()}")
        else:
            print(f"  最小值: {dataset[col].min()}")
            print(f"  最大值: {dataset[col].max()}")
            print(f"  平均值: {dataset[col].mean():.4f}")
            print(f"  唯一值数量: {dataset[col].nunique()}")
    
    # 3. 分析学生和问题分布
    print(f"\n学生和问题分布:")
    print("-" * 40)
    print(f"学生数量: {dataset['SubjectID'].nunique()}")
    print(f"问题数量: {dataset['ProblemID'].nunique()}")
    print(f"总记录数: {len(dataset)}")
    print(f"平均每个学生的记录数: {len(dataset) / dataset['SubjectID'].nunique():.2f}")
    
    # 4. 分析分数分布
    print(f"\n分数分布分析:")
    print("-" * 40)
    if 'Score_x' in dataset.columns:
        print(f"Score_x 分布:")
        print(dataset['Score_x'].value_counts().sort_index())
    if 'Score_y' in dataset.columns:
        print(f"Score_y 分布:")
        print(dataset['Score_y'].value_counts().sort_index())
    
    # 5. 分析时间步长分布
    print(f"\n时间步长分析:")
    print("-" * 40)
    student_lengths = dataset.groupby('SubjectID').size()
    print(f"学生记录长度统计:")
    print(f"  最短: {student_lengths.min()}")
    print(f"  最长: {student_lengths.max()}")
    print(f"  平均: {student_lengths.mean():.2f}")
    print(f"  中位数: {student_lengths.median():.2f}")
    
    # 6. 分析prompt embedding
    print(f"\nPrompt Embedding 分析:")
    print("-" * 40)
    if 'prompt-embedding' in dataset.columns:
        sample_emb = dataset['prompt-embedding'].iloc[0]
        print(f"Embedding 类型: {type(sample_emb)}")
        if hasattr(sample_emb, 'shape'):
            print(f"Embedding 维度: {sample_emb.shape}")
        elif isinstance(sample_emb, list):
            print(f"Embedding 长度: {len(sample_emb)}")
        print(f"示例 embedding: {sample_emb}")
    
    # 7. 分析代码相关字段
    print(f"\n代码相关字段分析:")
    print("-" * 40)
    code_columns = [col for col in dataset.columns if 'code' in col.lower() or 'Code' in col]
    for col in code_columns:
        print(f"\n{col}:")
        sample_values = dataset[col].iloc[:3].tolist()
        for i, val in enumerate(sample_values):
            print(f"  示例 {i+1}: {str(val)[:100]}...")
    
    # 8. 分析input字段
    if 'input' in dataset.columns:
        print(f"\nInput 字段分析:")
        print("-" * 40)
        sample_input = dataset['input'].iloc[0]
        print(f"Input 类型: {type(sample_input)}")
        if hasattr(sample_input, 'shape'):
            print(f"Input 维度: {sample_input.shape}")
        elif isinstance(sample_input, list):
            print(f"Input 长度: {len(sample_input)}")
        print(f"示例 input: {sample_input}")
    
    return dataset

def analyze_knowledge_components(data_path):
    """
    分析知识组件数据
    """
    print("\n" + "=" * 60)
    print("知识组件 (prompt_concept.xlsx) 分析")
    print("=" * 60)
    
    try:
        kc_data = pd.read_excel(data_path + '/prompt_concept.xlsx')
        
        print(f"知识组件数据形状: {kc_data.shape}")
        print(f"列名: {list(kc_data.columns)}")
        
        # 分析知识组件分布
        exclude_cols = ['AssignmentID', 'ProblemID', 'Requirement']
        kc_cols = [col for col in kc_data.columns if col not in exclude_cols]
        
        print(f"\n知识组件列数: {len(kc_cols)}")
        print(f"知识组件列名: {kc_cols}")
        
        # 分析每个知识组件的覆盖情况
        print(f"\n各知识组件覆盖情况:")
        print("-" * 40)
        for col in kc_cols:
            coverage = kc_data[col].sum()
            total = len(kc_data)
            print(f"{col}: {coverage}/{total} ({coverage/total*100:.1f}%)")
        
        # 分析问题与知识组件的关系
        print(f"\n问题与知识组件关系:")
        print("-" * 40)
        print(f"问题数量: {kc_data['ProblemID'].nunique()}")
        print(f"作业数量: {kc_data['AssignmentID'].nunique()}")
        
        # 显示几个示例
        print(f"\n示例数据:")
        print("-" * 40)
        print(kc_data.head())
        
        return kc_data
        
    except Exception as e:
        print(f"无法读取知识组件数据: {e}")
        return None

def analyze_data_processing_simulation(configs):
    """
    模拟数据处理过程，分析不同配置下的数据变化
    """
    print("\n" + "=" * 60)
    print("数据处理过程模拟分析")
    print("=" * 60)
    
    # 模拟配置
    class MockConfigs:
        def __init__(self):
            self.data_path = '/data2/liyu/KT/OKT/data'
            self.label_type = 'binary'  # 可以改为 'ternery' 或 'raw'
            self.max_len = 50
            self.testing = False
            self.first_ast_convertible = False
            self.use_kc = True
            self.data_for = 'okt'  # 可以改为 'lstm'
            self.split_method = 'student'  # 可以改为 'entry'
            self.test_size = 0.2
            self.seed = 42
    
    configs = MockConfigs()
    
    # 加载数据
    dataset = pd.read_pickle(configs.data_path + '/dataset.pkl')
    print(f"原始数据形状: {dataset.shape}")
    
    # 模拟标签处理
    print(f"\n标签处理 (label_type={configs.label_type}):")
    print("-" * 40)
    if configs.label_type == 'binary':
        scores_y = []
        for item in dataset['Score_y']:
            if item >= 2:
                scores_y.append(1)
            else:
                scores_y.append(0)
        dataset['Score'] = scores_y
        print(f"二值化后 Score 分布: {pd.Series(scores_y).value_counts().sort_index()}")
    elif configs.label_type == 'ternery':
        dataset['Score'] = dataset['Score_y']
        print(f"三元标签 Score 分布: {dataset['Score'].value_counts().sort_index()}")
    elif configs.label_type == 'raw':
        dataset['Score'] = dataset['Score_x']
        print(f"原始标签 Score 分布: {dataset['Score'].value_counts().sort_index()}")
    
    # 模拟学生记录分割
    print(f"\n学生记录分割 (max_len={configs.max_len}):")
    print("-" * 40)
    prev_subject_id = 0
    subjectid_appedix = []
    timesteps = []
    
    for i in range(len(dataset)):
        if prev_subject_id != dataset.iloc[i].SubjectID:
            prev_subject_id = dataset.iloc[i].SubjectID
            accumulated = 0
            id_appendix = 1
        else:
            accumulated += 1
            if accumulated >= configs.max_len:
                id_appendix += 1
                accumulated = 0
        timesteps.append(accumulated)
        subjectid_appedix.append(id_appendix)
    
    dataset['timestep'] = timesteps
    dataset['SubjectID_appendix'] = subjectid_appedix
    dataset['SubjectID'] = [dataset.iloc[i].SubjectID + \
                '_{}'.format(dataset.iloc[i].SubjectID_appendix) for i in range(len(dataset))]
    
    print(f"分割后学生数量: {dataset['SubjectID'].nunique()}")
    print(f"分割后记录数: {len(dataset)}")
    
    # 分析时间步分布
    timestep_dist = pd.Series(timesteps).value_counts().sort_index()
    print(f"时间步分布: {timestep_dist.head(10)}")
    
    # 模拟数据分割
    from sklearn.model_selection import train_test_split
    students = dataset['SubjectID'].unique()
    
    if configs.data_for == 'okt':
        # 移除第一个时间步的记录
        dropped_dataset = dataset.copy()
        dropped_dataset = dropped_dataset.drop(dropped_dataset.index[dropped_dataset['timestep'] == 0]).reset_index(drop=True)
        print(f"\n移除第一个时间步后数据形状: {dropped_dataset.shape}")
        
        if configs.split_method == "student":
            train_students, test_students = train_test_split(students, test_size=configs.test_size, random_state=configs.seed)
            valid_students, test_students = train_test_split(test_students, test_size=0.5, random_state=configs.seed)
            trainset = dropped_dataset[dropped_dataset['SubjectID'].isin(train_students)]
            validset = dropped_dataset[dropped_dataset['SubjectID'].isin(valid_students)]
            testset = dropped_dataset[dropped_dataset['SubjectID'].isin(test_students)]
            
            print(f"训练集: {trainset.shape}")
            print(f"验证集: {validset.shape}")
            print(f"测试集: {testset.shape}")

def main():
    """
    主函数：执行完整的数据分析
    """
    data_path = '/data2/liyu/KT/OKT/data'
    
    # 1. 分析主数据集
    dataset = analyze_dataset_structure(data_path)
    
    # 2. 分析知识组件
    kc_data = analyze_knowledge_components(data_path)
    
    # 3. 模拟数据处理过程
    analyze_data_processing_simulation(None)
    
    print("\n" + "=" * 60)
    print("分析完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
