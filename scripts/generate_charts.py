import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("results", exist_ok=True)
os.makedirs("docs/anh", exist_ok=True)

# 1. Bảng dữ liệu tổng hợp
benchmark_data = {
    "Kịch bản": ["LOAD-NORMAL (20 VUs)", "LOAD-PEAK (100 VUs)", "LOAD-SPIKE (200 VUs)"],
    "Throughput_Base_RPS": [86.51, 429.83, 518.94],
    "Throughput_Imp_RPS": [85.23, 427.24, 524.36],
    "Latency_p95_Base_ms": [5.06, 6.94, 125.61],
    "Latency_p95_Imp_ms": [10.18, 11.16, 94.01],
    "Error_Rate_Base_%": [0.00, 0.00, 0.00],
    "Error_Rate_Imp_%": [0.00, 0.00, 0.00]
}

df = pd.DataFrame(benchmark_data)
df.to_csv("results/benchmark_summary.csv", index=False, encoding="utf-8-sig")

scenarios = ['LOAD-NORMAL\n(20 VUs)', 'LOAD-PEAK\n(100 VUs)', 'LOAD-SPIKE\n(200 VUs)']
x = np.arange(len(scenarios))
width = 0.32

# CHART-001: Throughput
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
r1 = ax.bar(x - width/2, df["Throughput_Base_RPS"], width, label='Base (Single-Node)', color='#4A90E2', edgecolor='black')
r2 = ax.bar(x + width/2, df["Throughput_Imp_RPS"], width, label='Improved (Multi-Tier)', color='#50E3C2', edgecolor='black')
ax.set_ylabel('Throughput (RPS)', fontweight='bold')
ax.set_title('CHART-001: So sánh Throughput (RPS)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend()
ax.set_ylim(0, 620)
for r in r1 + r2:
    h = r.get_height()
    ax.annotate(f'{h:.1f}', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 4),
                textcoords="offset points", ha='center', fontweight='bold', fontsize=9)
plt.tight_layout()
plt.savefig('docs/anh/chart-001-throughput.png')
plt.close()

# CHART-002: Latency p95 (Điều chỉnh mũi tên không đè số)
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
r1 = ax.bar(x - width/2, df["Latency_p95_Base_ms"], width, label='Base (Single-Node)', color='#E74C3C', edgecolor='black')
r2 = ax.bar(x + width/2, df["Latency_p95_Imp_ms"], width, label='Improved (Multi-Tier)', color='#2ECC71', edgecolor='black')
ax.set_ylabel('Latency p95 (ms)', fontweight='bold')
ax.set_title('CHART-002: So sánh Độ trễ p95 (ms)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend()
ax.set_ylim(0, 155)
for r in r1 + r2:
    h = r.get_height()
    ax.annotate(f'{h:.2f} ms', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 4),
                textcoords="offset points", ha='center', fontweight='bold', fontsize=9)
# Đặt vị trí text lệch cao hơn và hướng mũi tên rõ ràng
ax.annotate('Giảm 25.16% độ trễ\n(Scale-out)', xy=(2 + width/2, 98), xytext=(1.2, 125),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.2),
            fontweight='bold', color='#1E8449',
            bbox=dict(boxstyle="round,pad=0.3", fc="#EAFAF1", ec="#2ECC71"))
plt.tight_layout()
plt.savefig('docs/anh/chart-002-latency.png')
plt.close()

# CHART-003: Error Rate (Thêm đường ngưỡng SLO)
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
r1 = ax.bar(x - width/2, df["Error_Rate_Base_%"], width, label='Base (Single-Node)', color='#4A90E2', edgecolor='black')
r2 = ax.bar(x + width/2, df["Error_Rate_Imp_%"], width, label='Improved (Multi-Tier)', color='#50E3C2', edgecolor='black')
ax.axhline(y=1.0, color='r', linestyle='--', linewidth=1.5, label='SLO Ngưỡng lỗi (≤ 1.0%)')
ax.set_ylabel('HTTP Error Rate (%)', fontweight='bold')
ax.set_title('CHART-003: So sánh Tỷ lệ lỗi (%)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend(loc='upper right')
ax.set_ylim(0, 1.5)
for r in r1 + r2:
    h = r.get_height()
    ax.annotate(f'{h:.2f}%', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 4),
                textcoords="offset points", ha='center', fontweight='bold', fontsize=9)
plt.tight_layout()
plt.savefig('docs/anh/chart-003-error-rate.png')
plt.close()

print("-> Đã xuất lại 3 biểu đồ chuẩn hóa vào docs/anh/")
