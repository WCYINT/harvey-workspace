import os
import subprocess
import re
import sys
import time

# 处理任务摘要（将空格替换为下划线，用于任务名称）
def process_task_summary(summary):
    # 替换空格为下划线，用于任务名称
    return summary.replace(" ", "_")

# 创建一次性任务
def create_once_task(time_spec, description, message):
    # 解析时间
    time_parts = time_spec.split(":")
    if len(time_parts) != 2:
        raise ValueError("时间格式错误")
    hour = time_parts[0]
    minute = time_parts[1]

    # 处理任务摘要，用于任务名称
    task_summary = process_task_summary(description)
    # 生成任务名称，按照格式：guixu_task_{时间戳}_{任务英文名}
    timestamp = time.strftime("%Y%m%d%H%M%S")
    task_name = f"guixu_task_{timestamp}_{task_summary}"

    # 生成消息内容
    full_message = f"提醒: {message}"

    # 构造schtasks命令
    cmd = ["schtasks", "/create", "/tn", task_name, "/tr", f"cmd /c msg * \"{full_message}\"", "/sc", "once", "/st", f"{hour}:{minute}", "/f"]

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print(f"已创建一次性提醒任务: {task_name}，将在今天 {time_spec} 提醒您 {message}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"创建任务失败: {e}")

# 创建每天任务
def create_daily_task(time_spec, description, message):
    # 解析时间
    time_parts = time_spec.split(":")
    if len(time_parts) != 2:
        raise ValueError("时间格式错误")
    hour = time_parts[0]
    minute = time_parts[1]

    # 处理任务摘要，用于任务名称
    task_summary = process_task_summary(description)
    # 生成任务名称，按照格式：guixu_task_{时间戳}_{任务英文名}
    timestamp = time.strftime("%Y%m%d%H%M%S")
    task_name = f"guixu_task_{timestamp}_daily_{task_summary}"

    # 生成消息内容
    full_message = f"提醒: {message}"

    # 构造schtasks命令
    cmd = ["schtasks", "/create", "/tn", task_name, "/tr", f"cmd /c msg * \"{full_message}\"", "/sc", "daily", "/st", f"{hour}:{minute}", "/f"]

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print(f"已创建每天提醒任务: {task_name}，将在每天 {time_spec} 提醒您 {message}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"创建任务失败: {e}")

# 创建每周任务
def create_weekly_task(time_spec, description, message):
    # 解析时间
    time_parts = time_spec.split(" ")
    if len(time_parts) != 2:
        raise ValueError("时间格式错误")
    day = time_parts[0]
    time_str = time_parts[1]

    # 转换星期
    day_map = {
        "日": "1",
        "一": "2",
        "二": "3",
        "三": "4",
        "四": "5",
        "五": "6",
        "六": "7"
    }

    day_num = day_map.get(day, day)

    # 处理任务摘要，用于任务名称
    task_summary = process_task_summary(description)
    # 生成任务名称，按照格式：guixu_task_{时间戳}_{任务英文名}
    timestamp = time.strftime("%Y%m%d%H%M%S")
    task_name = f"guixu_task_{timestamp}_weekly_{task_summary}_{day}"

    # 生成消息内容
    full_message = f"提醒: {message}"

    # 构造schtasks命令
    cmd = ["schtasks", "/create", "/tn", task_name, "/tr", f"cmd /c msg * \"{full_message}\"", "/sc", "weekly", "/d", day_num, "/st", time_str, "/f"]

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print(f"已创建每周提醒任务: {task_name}，将在每周 {day} {time_str} 提醒您 {message}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"创建任务失败: {e}")

# 创建每月任务
def create_monthly_task(time_spec, description, message):
    # 解析时间
    time_parts = time_spec.split(" ")
    if len(time_parts) != 2:
        raise ValueError("时间格式错误")
    day = time_parts[0]
    time_str = time_parts[1]

    # 处理任务摘要，用于任务名称
    task_summary = process_task_summary(description)
    # 生成任务名称，按照格式：guixu_task_{时间戳}_{任务英文名}
    timestamp = time.strftime("%Y%m%d%H%M%S")
    task_name = f"guixu_task_{timestamp}_monthly_{task_summary}_{day}"

    # 生成消息内容
    full_message = f"提醒: {message}"

    # 构造schtasks命令
    cmd = ["schtasks", "/create", "/tn", task_name, "/tr", f"cmd /c msg * \"{full_message}\"", "/sc", "monthly", "/d", day, "/st", time_str, "/f"]

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print(f"已创建每月提醒任务: {task_name}，将在每月 {day} 号 {time_str} 提醒您 {message}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"创建任务失败: {e}")

# 创建每月末任务
def create_month_end_task(time_spec, description, message):
    # 解析时间
    time_parts = time_spec.split(":")
    if len(time_parts) != 2:
        raise ValueError("时间格式错误")
    hour = time_parts[0]
    minute = time_parts[1]

    # 处理任务摘要，用于任务名称
    task_summary = process_task_summary(description)
    # 生成任务名称，按照格式：guixu_task_{时间戳}_{任务英文名}
    timestamp = time.strftime("%Y%m%d%H%M%S")
    task_name = f"guixu_task_{timestamp}_monthend_{task_summary}"

    # 生成消息内容
    full_message = f"提醒: {message}"

    # 构造schtasks命令 - 每月1号提醒，实际使用时需要调整
    # 注意：Windows任务计划程序不直接支持每月末，这里使用每月1号作为近似
    cmd = ["schtasks", "/create", "/tn", task_name, "/tr", f"cmd /c msg * \"{full_message}\"", "/sc", "monthly", "/d", "1", "/st", f"{hour}:{minute}", "/f"]

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
        print(f"已创建每月末提醒任务: {task_name}，将在每月1号 {time_spec} 提醒您 {message}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"创建任务失败: {e}")

# 列出所有任务
def list_tasks():
    # 构造schtasks命令，使用详细格式
    cmd = ["schtasks", "/query", "/fo", "list", "/v"]

    # 执行命令并获取输出
    try:
        output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise Exception(f"列出任务失败: {e}")

    # 过滤出提醒任务并解析详细信息
    lines = output.split("\n")
    print("当前系统中的提醒任务:")
    print("====================================")

    current_task = ""
    for line in lines:
        line = line.strip()
        if "guixu_task_" in line:
            # 提取任务名称
            if ":" in line:
                task_name = line.split(":", 1)[1].strip()
                current_task = task_name
                print(f"任务名称: {task_name}")
        elif current_task and ("触发器:" in line or "操作:" in line):
            # 显示触发器和操作信息
            print(line)
        elif current_task and line == "":
            # 任务信息结束，重置当前任务
            print("------------------------------------")
            current_task = ""

    print("====================================")

# 删除任务
def delete_task(keyword):
    # 先列出所有任务
    cmd = ["schtasks", "/query", "/fo", "list"]
    try:
        output = subprocess.check_output(cmd, universal_newlines=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise Exception(f"列出任务失败: {e}")

    # 查找所有提醒任务
    lines = output.split("\n")
    tasks_to_delete = []
    for line in lines:
        if "guixu_task_" in line:
            # 提取任务名称
            parts = line.split("\t")
            if parts:
                task_name = parts[0].strip()
                tasks_to_delete.append(task_name)

    if not tasks_to_delete:
        raise Exception("未找到提醒任务")

    # 显示所有提醒任务
    print("当前系统中的提醒任务:")
    for i, task in enumerate(tasks_to_delete, 1):
        print(f"{i}. {task}")

    # 尝试将关键词解析为任务编号
    task_index = -1
    if keyword:
        # 尝试解析为数字
        try:
            index = int(keyword)
            if 1 <= index <= len(tasks_to_delete):
                task_index = index - 1
        except ValueError:
            # 尝试通过关键词匹配任务
            for i, task in enumerate(tasks_to_delete):
                if keyword in task:
                    task_index = i
                    break

    # 如果没有指定关键词或匹配失败，让用户选择
    if task_index == -1:
        print("请输入要删除的任务编号:")
        input_str = input().strip()

        # 解析用户输入
        try:
            index = int(input_str)
            if 1 <= index <= len(tasks_to_delete):
                task_index = index - 1
            else:
                raise Exception("无效的任务编号")
        except ValueError:
            raise Exception("无效的任务编号")

    # 删除指定的任务
    target_task = tasks_to_delete[task_index]
    # 尝试使用任务名称的完整路径
    delete_cmd = ["schtasks", "/delete", "/tn", target_task, "/f"]
    try:
        subprocess.run(delete_cmd, check=True)
    except subprocess.CalledProcessError:
        # 如果失败，尝试使用简化的任务名称
        task_name_only = os.path.basename(target_task)
        delete_cmd = ["schtasks", "/delete", "/tn", task_name_only, "/f"]
        try:
            subprocess.run(delete_cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f"删除任务失败: {e}")

    print(f"已删除任务: {target_task}")

# 任务配置结构
class TaskConfig:
    def __init__(self):
        self.type = ""
        self.time = ""
        self.date = ""
        self.day = ""
        self.day_of_month = ""
        self.description = ""  # 英文任务描述，用于任务名称
        self.message = ""  # 中文任务描述，用于提醒消息
        self.keyword = ""

# 解析AI模型输出的固定格式
def parse_ai_format(input_str):
    lines = input_str.split("\n")
    config = TaskConfig()

    # 跳过空行
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    if not non_empty_lines:
        raise Exception("输入为空")

    # 解析命令类型
    command = non_empty_lines[0]

    if command == "CREATE TASK":
        # 解析创建任务的参数
        for line in non_empty_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "TYPE":
                    config.type = value
                elif key == "TIME":
                    config.time = value
                elif key == "DATE":
                    config.date = value
                elif key == "DAY":
                    config.day = value
                elif key == "DAY_OF_MONTH":
                    config.day_of_month = value
                elif key == "DESCRIPTION":
                    config.description = value
                elif key == "MESSAGE":
                    config.message = value

        # 验证必要参数
        if not config.type or not config.time or not config.description:
            raise Exception("缺少必要参数")

        # 如果没有提供MESSAGE，使用DESCRIPTION作为默认值
        if not config.message:
            config.message = config.description

        # 验证类型特定的参数
        if config.type == "once" and not config.date:
            raise Exception("一次性任务需要指定DATE")
        elif config.type == "weekly" and not config.day:
            raise Exception("每周任务需要指定DAY")
        elif config.type == "monthly" and not config.day_of_month:
            raise Exception("每月任务需要指定DAY_OF_MONTH")

    elif command == "LIST TASKS":
        # 列出任务不需要额外参数
        pass

    elif command == "DELETE TASK":
        # 解析删除任务的参数
        for line in non_empty_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key == "KEYWORD":
                    config.keyword = value

        # 验证必要参数
        if not config.keyword:
            raise Exception("删除任务需要指定KEYWORD")

    else:
        raise Exception(f"未知命令类型: {command}")

    return command, config

def main():
    # 检查操作系统
    if os.name != "nt":
        print("此技能仅支持Windows操作系统")
        sys.exit(1)

    # 获取用户输入（AI模型输出的固定格式）
    input_str = ""
    if len(sys.argv) > 1:
        # 从命令行参数获取输入
        # 处理命令行参数中的多行输入
        input_str = " ".join(sys.argv[1:])
        # 替换分号为换行符，以便解析多行格式
        input_str = input_str.replace(";" , "\n")
    else:
        # 从标准输入获取输入
        print("请输入AI模型输出的固定格式内容:")
        input_str = input().strip()

    if not input_str:
        print("输入为空，请输入AI模型输出的固定格式内容")
        sys.exit(1)

    # 解析AI模型输出的固定格式
    try:
        command, config = parse_ai_format(input_str)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

    # 执行相应操作
    try:
        if command == "CREATE TASK":
            if config.type == "once":
                create_once_task(config.time, config.description, config.message)
            elif config.type == "daily":
                create_daily_task(config.time, config.description, config.message)
            elif config.type == "weekly":
                time_spec = f"{config.day} {config.time}"
                create_weekly_task(time_spec, config.description, config.message)
            elif config.type == "monthly":
                time_spec = f"{config.day_of_month} {config.time}"
                create_monthly_task(time_spec, config.description, config.message)
            elif config.type == "monthend":
                create_month_end_task(config.time, config.description, config.message)
            else:
                raise Exception(f"未知任务类型: {config.type}")
        elif command == "LIST TASKS":
            list_tasks()
        elif command == "DELETE TASK":
            delete_task(config.keyword)
        else:
            raise Exception(f"未知命令类型: {command}")
    except Exception as e:
        print(f"操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()