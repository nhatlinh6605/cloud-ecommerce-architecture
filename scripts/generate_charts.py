import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Tao thu muc luu tru neu chua co
os.makedirs("results", exist_ok=True)
os.makedirs("docs/anh", exist_ok=True)

# 2. Tong hop du lieu bang doi dau bang pandas
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
csv_path = "results/benchmark_summary.csv"
df.to_csv(csv_path, index=False, encoding="utf-8-sig")

print("=== BẢNG TỔNG HỢP HIỆU NĂNG (PANDAS DATAFRAME) ===")
print(df.to_string(index=False))
print(f"\n-> Đã lưu bảng tổng hợp: {csv_path}")

# 3. Ve bieu do bang Matplotlib tu DataFrame
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

# CHART-002: Latency p95
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
r1 = ax.bar(x - width/2, df["Latency_p95_Base_ms"], width, label='Base (Single-Node)', color='#E74C3C', edgecolor='black')
r2 = ax.bar(x + width/2, df["Latency_p95_Imp_ms"], width, label='Improved (Multi-Tier)', color='#2ECC71', edgecolor='black')
ax.set_ylabel('Latency p95 (ms)', fontweight='bold')
ax.set_title('CHART-002: So sánh Độ trễ p95 (ms)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend()
ax.set_ylim(0, 150)
for r in r1 + r2:
    h = r.get_height()
    ax.annotate(f'{h:.2f} ms', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 4),
                textcoords="offset points", ha='center', fontweight='bold', fontsize=9)
ax.annotate('Giảm 25.16% độ trễ\n(Scale-out)', xy=(2 + width/2, 94.01), xytext=(1.4, 115),
            arrowprops=dict(facecolor='black', arrowstyle='->'),
            fontweight='bold', color='#1E8449',
            bbox=dict(boxstyle="round,pad=0.3", fc="#EAFAF1", ec="#2ECC71"))
plt.tight_layout()
plt.savefig('docs/anh/chart-002-latency.png')
plt.close()

# CHART-003: Error Rate
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
r1 = ax.bar(x - width/2, df["Error_Rate_Base_%"], width, label='Base (Single-Node)', color='#4A90E2', edgecolor='black')
r2 = ax.bar(x + width/2, df["Error_Rate_Imp_%"], width, label='Improved (Multi-Tier)', color='#50E3C2', edgecolor='black')
ax.set_ylabel('HTTP Error Rate (%)', fontweight='bold')
ax.set_title('CHART-003: So sánh Tỷ lệ lỗi (%)', fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios)
ax.legend()
ax.set_ylim(0, 1.0)
for r in r1 + r2:
    h = r.get_height()
    ax.annotate(f'{h:.2f}%', xy=(r.get_x() + r.get_width()/2, h), xytext=(0, 4),
                textcoords="offset points", ha='center', fontweight='bold', fontsize=9)
plt.tight_layout()
plt.savefig('docs/anh/chart-003-error-rate.png')
plt.close()

print("-> Đã xuất 3 biểu đồ vào docs/anh/")
print("Hoàn tất tái tạo dữ liệu và biểu đồ!")
