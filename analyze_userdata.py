#!/usr/bin/env python3
"""
分析 Project_CodeNet userdata 文件夹下每个代码语言的用户数量
"""

import os
import pandas as pd
from collections import defaultdict

def analyze_userdata_languages(userdata_path):
    """
    分析 userdata 文件夹下每个语言文件夹的CSV文件数量
    
    Args:
        userdata_path (str): userdata 文件夹路径
    
    Returns:
        dict: 语言名称到CSV文件数量的映射
    """
    language_counts = {}
    
    # 获取所有语言文件夹
    language_dirs = [d for d in os.listdir(userdata_path) 
                    if os.path.isdir(os.path.join(userdata_path, d))]
    
    print(f"发现 {len(language_dirs)} 个语言文件夹")
    print("=" * 50)
    
    total_users = 0
    
    for lang_dir in sorted(language_dirs):
        lang_path = os.path.join(userdata_path, lang_dir)
        
        # 统计该语言文件夹下的CSV文件数量
        csv_files = [f for f in os.listdir(lang_path) if f.endswith('.csv')]
        csv_count = len(csv_files)
        
        language_counts[lang_dir] = csv_count
        total_users += csv_count
        
        print(f"{lang_dir:15} : {csv_count:6} 个用户")
    
    print("=" * 50)
    print(f"总计用户数: {total_users}")
    
    return language_counts

def create_summary_dataframe(language_counts):
    """
    创建汇总的DataFrame
    
    Args:
        language_counts (dict): 语言到用户数的映射
    
    Returns:
        pd.DataFrame: 汇总数据
    """
    # 按用户数降序排列
    sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
    
    df = pd.DataFrame(sorted_languages, columns=['编程语言', '用户数量'])
    df['排名'] = range(1, len(df) + 1)
    
    # 计算百分比
    total_users = df['用户数量'].sum()
    df['占比(%)'] = (df['用户数量'] / total_users * 100).round(2)
    
    return df

def main():
    userdata_path = "/data2/liyu/KT/OKT/Project_CodeNet/userdata"
    
    print("Project_CodeNet 用户数据分析")
    print("=" * 50)
    
    # 分析各语言用户数量
    language_counts = analyze_userdata_languages(userdata_path)
    
    print("\n详细统计表格:")
    print("=" * 80)
    
    # 创建汇总DataFrame
    summary_df = create_summary_dataframe(language_counts)
    
    # 显示前20名
    print("前20名编程语言:")
    print(summary_df.head(20).to_string(index=False))
    
    print(f"\n完整统计信息:")
    print(f"- 总语言数: {len(language_counts)}")
    print(f"- 总用户数: {summary_df['用户数量'].sum()}")
    print(f"- 平均每语言用户数: {summary_df['用户数量'].mean():.1f}")
    print(f"- 用户数最多的语言: {summary_df.iloc[0]['编程语言']} ({summary_df.iloc[0]['用户数量']} 用户)")
    print(f"- 用户数最少的语言: {summary_df.iloc[-1]['编程语言']} ({summary_df.iloc[-1]['用户数量']} 用户)")
    
    # 保存结果到CSV
    output_file = "/data2/liyu/KT/OKT/language_user_analysis.csv"
    summary_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n结果已保存到: {output_file}")
    
    return summary_df

if __name__ == "__main__":
    result_df = main()
