import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os


def save_combined_model_to_file():
    # 1. 核心数据
    v = 18  # 隐形牛（草每天减少的速度）
    total_area = 1680

    cases = [
        {"label": "10 Cows (60 Days)", "cows": 10, "days": 60, "color": "#34A853"},
        {"label": "12 Cows (56 Days)", "cows": 12, "days": 56, "color": "#4285F4"},
        {"label": "30 Cows (35 Days)", "cows": 30, "days": 35, "color": "#EA4335"},
    ]

    # 2. 设置绘图环境（使用无窗口后端，防止弹窗错误）
    # plt.switch_backend('Agg')

    fig, ax = plt.subplots(figsize=(10, 8))

    # 3. 绘制长方形
    for case in cases:
        total_width = case["cows"] + v
        height = case["days"]

        # 绘制总面积长方形
        rect = patches.Rectangle((0, 0), total_width, height,
                                 linewidth=2, edgecolor=case["color"],
                                 facecolor=case["color"], alpha=0.1,
                                 label=case['label'])
        ax.add_patch(rect)

        # 标注坐标点
        ax.text(total_width, height + 0.8, f"({total_width}, {height})",
                color=case["color"], fontsize=10, ha='center', fontweight='bold')

        # 绘制辅助虚线
        ax.plot([total_width, total_width], [0, height], color=case["color"], linestyle='--', alpha=0.4)
        ax.plot([0, total_width], [height, height], color=case["color"], linestyle='--', alpha=0.4)

    # 4. 绘制隐形牛分界线
    ax.axvline(x=v, color='gray', linestyle=':', linewidth=2, label=f'Hidden Rate (v={v})')
    ax.fill_betweenx([0, 75], 0, v, color='gray', alpha=0.05)
    ax.text(v / 2, 72, "Hidden Zone\n(Natural Decay)", ha='center', color='gray', fontsize=9)

    # 5. 图形修饰
    ax.set_title('Combined Area Model: Cow-Grass Problem', fontsize=14, pad=20)
    ax.set_xlabel('Total Consumption Rate (Cows + Hidden Rate)', fontsize=12)
    ax.set_ylabel('Days to Finish', fontsize=12)
    ax.set_xlim(0, 55)
    ax.set_ylim(0, 75)
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='upper right')

    # 核心原理标注框
    principle_text = f"Principle: All Areas = {total_area}\nArea = (Cows + {v}) × Days"
    ax.text(32, 15, principle_text, bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'), fontsize=11)

    # 6. 保存图片到指定路径
    output_dir = "output_images"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, "cow_grass_model.png")
    plt.tight_layout()
    plt.savefig(file_path, dpi=300)  # 设置 300 DPI 保证打印清晰
    print(f"Success! Image saved to: {os.path.abspath(file_path)}")

    plt.close(fig)  # 释放内存


if __name__ == "__main__":
    save_combined_model_to_file()