# 导入所需的模块
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
import sys
import os
from getPid import get_pid
from main import *

# 定义题库类型和难度等级的字典
type_options = {
  "洛谷": "B%7CP",
  "主题库": "P",
  "入门与面试": "B",
  "CodeForces": "CF",
  "SPOJ": "SP",
  "AtCoder": "AT",
  "UVA": "UVA",
}

difficulty_options = {
  "暂无评定": 0,
  "入门": 1,
  "普及-": 2,
  "普及、提高-": 3,
  "普及+、提高": 4,
  "提高+、省选-": 5,
  "省选、NOI-": 6,
  "NOI、NOI+、CTSC": 7
}

# 定义字体样式和颜色常量
FONT_STYLE = ("微软雅黑", 18)
FONT_STYLE_WARNING = ("微软雅黑", 18, "bold")
FONT_STYLE_OUTPUT = ("微软雅黑", 13)
BG_COLOR = "white"
SELECT_COLOR = "#E0F7FF"

# 创建主窗口并设置标题和大小
root = tk.Tk()
root.title("洛谷题库爬取")
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 1100
window_height = 900
window_x = (screen_width - window_width) // 2
window_y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
root.configure(bg=BG_COLOR)

# 设置行列的权重，使得窗口大小改变时组件自动调整
for i in range(4):
    root.rowconfigure(i, weight=1)
for i in range(8):
    root.columnconfigure(i, weight=1)

# 创建题库类型标签并放置在第一行第一列
type_label = tk.Label(root, text="题库:", font=FONT_STYLE, bg=BG_COLOR)
type_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)

# 创建题库类型单选按钮并放置在第一行第二列到第八列，使用 ttk 模块来适应操作系统的风格和主题
selected_type = tk.StringVar()
selected_type.set("洛谷") # 默认选择洛谷

for i, type_key in enumerate(type_options.keys()):
    if type_key == "洛谷":
        type_button = ttk.Radiobutton(root, text="      洛谷      ", variable=selected_type, value=type_key, style="TRadiobutton")
    else:
        type_button = ttk.Radiobutton(root, text=type_key, variable=selected_type, value=type_key, style="TRadiobutton")
    type_button.grid(row=0, column=i+1, padx=10, pady=10)

# 创建关键词标签并放置在第二行第一列
keyword_label = tk.Label(root, text="关键字:", font=FONT_STYLE, bg=BG_COLOR)
keyword_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)

# 创建关键词输入框并放置在第二行第二列，增加边框和宽度
keyword_entry = tk.Entry(root, font=FONT_STYLE, borderwidth=2, relief="solid", width=21)
keyword_entry.grid(row=1, column=1, padx=(0,20), pady=10)

# 创建关键词提示信息标签并放置在第二行第三列到第八列，使用红色字体来警告用户
keyword_tip_label = tk.Label(root, text="多个关键词以顿号(、)分开！！！", font=FONT_STYLE_WARNING, bg=BG_COLOR, fg="red")
keyword_tip_label.grid(row=1, column=2, columnspan=6, padx=10, pady=10)

# 创建难度标签并放置在第三行第一列
difficulty_label = tk.Label(root, text="难度:", font=FONT_STYLE, bg=BG_COLOR)
difficulty_label.grid(row=2, column=0, sticky="w", padx=10, pady=10)

# 创建难度下拉菜单并放置在第三行第二列，使用 ttk 模块来适应操作系统的风格和主题
selected_difficulty = tk.StringVar()
difficulty_menu = ttk.OptionMenu(root, selected_difficulty, *difficulty_options.keys())
difficulty_menu.config(width=18)
difficulty_menu.grid(row=2, column=1, padx=10, pady=10)

# 创建输出文本框并放置在第四行第一列到第八列，增加滚动条和边框
output_text = scrolledtext.ScrolledText(root, font=FONT_STYLE_OUTPUT, width=80, height=20, bg=SELECT_COLOR, relief="solid", bd=2)
output_text.grid(row=3, column=0, columnspan=8, padx=10, pady=10)

# 保存原始的 stdout 和 stderr
original_stdout = sys.stdout
original_stderr = sys.stderr

# 定义一个函数来重定向控制台输出到输出文本框
def redirect_output():
    # 定义一个自定义写函数，用于将消息写入输出文本框
    def custom_write(msg):
        output_text.insert("end", msg) # 在输出文本框的末尾插入消息
        output_text.see("end") # 滚动到输出文本框的末尾，以显示最新的输出
        output_text.update() # 更新输出文本框以显示最新的输出
    
    # 将 stdout 和 stderr 重定向到自定义写函数
    sys.stdout.write = custom_write
    sys.stderr.write = custom_write

# 定义一个函数来获取用户输入并构建 URL 和文件名
def get_url_and_filename():
    keyword = keyword_entry.get() # 获取用户输入的关键词
    difficulty = difficulty_options[selected_difficulty.get()] if selected_difficulty.get() else "" # 获取用户选择的难度，如果没有选择则为空字符串
    type_value = type_options[selected_type.get()] # 获取用户选择的题库类型，用于构建 URL
    if keyword:
        keywords = keyword.replace("、", "-") # 如果有关键词，就用破折号分割，用于构建文件名
    else:
        keywords = "无关键词" # 如果没有关键词，就默认为无关键词，用于构建文件名
    if difficulty == "":
        difficult = "全部" # 如果没有选择难度，就默认为全部，用于构建文件名
    else:
        difficult = selected_difficulty.get() # 如果有选择难度，就用选择的难度，用于构建文件名
    # 构建文件名，用破折号连接难度和关键词
    filename = f"{difficult}-{keywords}"
    # 构建 URL 和参数字典，用于发送请求
    url = f"https://www.luogu.com.cn/problem/list?type={type_value}&difficulty={difficulty}&keyword={keyword}&page=1"
    params = {"difficulty": difficulty, "type": type_value, "page": 1, "_contentOnly": 1}
    return url, params, filename

# 定义一个函数来执行爬取操作，并在输出文本框中显示结果
def crawl():
    url, params, filename = get_url_and_filename() # 获取 URL 和文件名
    redirect_output() # 重定向控制台输出到输出文本框
    try: # 使用 try-except 语句来捕获可能出现的异常，并显示错误信息
        total, arr_pro = get_pid(url, params) # 调用 get_pid 函数来获取题目总数和题目编号列表
        get_problem(filename, total, arr_pro) # 调用 get_problem 函数来爬取题目内容并保存到文件中
    except Exception as e:
        print(f"发生错误：{e}")

# 定义一个函数来恢复原始的 stdout 和 stderr，并关闭窗口
def on_closing():
    if messagebox.askokcancel("退出", "你确定要退出吗？"):
        sys.stdout = original_stdout # 恢复原始的 stdout 
        sys.stderr = original_stderr # 恢复原始的 stderr
        root.destroy() # 销毁窗口

# 绑定 WM_DELETE_WINDOW 事件和 on_closing 函数，用于在用户关闭窗口时执行 on_closing 函数
root.protocol("WM_DELETE_WINDOW", on_closing)

# 创建爬取按钮并放置在第三行第三列，使用 ttk 模块来适应操作系统的风格和主题
crawl_button = ttk.Button(root, text="   开爬！ ", command=crawl)
crawl_button.grid(row=2, column=2, padx=10, pady=10)

# 运行 tkinter 应用程序
root.mainloop()