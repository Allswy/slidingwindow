import matplotlib.pyplot as plt
import random
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation

def plot_tcp_with_rectangle_movement():
    # 参数
    total_packets = 40 # 总报文数
    window_size = 7 # 窗口大小
    data_transfer_time = 0.01 # 数据传输时间
    loss_rate = 20 # 丢包率
    timeout = 25 # 超时时间
    timer = [0] * (total_packets + window_size) # 超时计时器
    frame1 = 0
    sent_status = [False] * (total_packets + window_size) # 发送状态
    ack_sent_status = [False] * (total_packets + window_size) # 确认发送状态
    received_status = [False] * (total_packets + window_size) # 接收状态
    ack_status = [False] * (total_packets + window_size) # 确认状态
    window_start = 0
    recv_window_start = 0
    moving_packets = []
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(-1, total_packets + 1)
    ax.set_ylim(-4, 4)
    ax.axis('off')

    def update(frame):
        nonlocal window_start
        nonlocal timeout
        nonlocal timer
        nonlocal frame1
        nonlocal recv_window_start

        # 绘制背景
        ax.clear()
        ax.set_xlim(-4, total_packets + 1)
        ax.set_ylim(-4, 5)
        ax.axis('off')
        ax.text(-3.7, 2.75, 'sender', ha='center', va='center', fontsize=16)
        ax.text(-4.2, -1.5,'receiver', ha='center', va='center', fontsize=16)
        ax.text(-1, 2.25, 'sent', ha='center', va='center', fontsize=12)
        ax.text(-1, 2.75, 'ack', ha='center', va='center', fontsize=12)
        ax.text(-1, -1.5, 'recv', ha='center', va='center', fontsize=12)
        ax.text(-1, 3.25, 'timer', ha='center', va='center', fontsize=12)
        ax.text((total_packets + 1 - 5) / 2, 4, 'time = ' + str(frame1) + '   timeout = ' + str(timeout) + '   loss rate = ' + str(loss_rate), ha='center', va='center', fontsize=12)

        # 绘制缓存
        for i in range(total_packets):
            color3 = 'pink' if timer[i] == -1 else 'white'
            ax.add_patch(patches.Rectangle((i, 3), 1, 0.5, edgecolor='black', facecolor=color3))
            ax.text(i + 0.5, 3.25, timer[i], ha='center', va='center', fontsize=8)
            color1 = 'royalblue' if sent_status[i] else 'lightblue'
            ax.add_patch(patches.Rectangle((i, 2), 1, 0.5, edgecolor='black', facecolor=color1))
            color2 = 'green' if ack_status[i] else 'lightgreen'
            ax.add_patch(patches.Rectangle((i, 2.5), 1, 0.5, edgecolor='black', facecolor=color2))
            ax.text(i + 0.5, 2.25, str(i + 1), ha='center', va='center', fontsize=8)
        for i in range(total_packets):
            color = 'green' if received_status[i] else 'white'
            ax.add_patch(patches.Rectangle((i, -2), 1, 1, edgecolor='black', facecolor=color))
            ax.text(i + 0.5, -1.5, str(i + 1), ha='center', va='center', fontsize=8)
        fg = True
        for i in range(total_packets):
            if not ack_status[i]:
                fg = False
                break
        if fg:
            ax.text((total_packets + 1 - 5) / 2, 0, 'transmission completed', ha='center', va='center', fontsize=17)
            return
        frame1 += 1

        # 绘制窗口
        window_rect = patches.Rectangle((window_start, 2), window_size, 1, edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(window_rect)
        ack_window_rect = patches.Rectangle((recv_window_start, -2), window_size, 1, edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(ack_window_rect)


        # 维护超时计时器
        for i in range(total_packets):
            if (not ack_status[i]) and (sent_status[i]):
                timer[i] += 1
        for i in range(total_packets):
            if timer[i] > timeout:
                sent_status[i] = False
                ack_sent_status[i] = False
                timer[i] = 0

        new_moving_packets = []
        # 发送报文
        for i in range(window_start, window_start + window_size):
            if not sent_status[i]:
                new_moving_packets.append((i, 2, 'royalblue'))
                timer[i] = 0
                sent_status[i] = True 
                break

        # 模拟报文移动过程
        for x, y, color in moving_packets:
            if color == 'royalblue':# 蓝色报文向下移动
                new_y = y - 0.4 if y > -2 else -2
                if new_y > -2:
                    if random.randint(1, 1000) <= loss_rate:
                        continue
                    new_moving_packets.append((x, new_y, color))
                    ax.add_patch(patches.Rectangle((x, new_y), 1, 1, edgecolor='black', facecolor=color))
                else:
                    received_status[x] = True
                    if not ack_sent_status[x]:
                        new_moving_packets.append((x, -2, 'green'))
                        ack_sent_status[x] = True
            elif color == 'green':# 绿色报文向上移动
                new_y = y + 0.4 if y < 2 else 2
                if new_y < 2:
                    if random.randint(1, 1000) <= loss_rate:
                        continue
                    new_moving_packets.append((x, new_y, color))
                    ax.add_patch(patches.Rectangle((x, new_y), 1, 1, edgecolor='black', facecolor=color))
                else:
                    ack_status[x] = True
                    timer[x] = -1
        moving_packets.clear()
        moving_packets.extend(new_moving_packets)

        # 移动窗口
        if ack_status[window_start] and window_start + window_size < total_packets:# 发送窗口
            window_start += 1
        if received_status[recv_window_start] and recv_window_start + window_size < total_packets: # 接收窗口
            recv_window_start += 1
    
    ani = FuncAnimation(fig, update, frames= 20 * total_packets + 10000, interval=data_transfer_time * 1000, repeat=False)
    plt.show()

plot_tcp_with_rectangle_movement()
