#!/usr/bin/env python3
"""
Harvey 每晚追问任务
Yuanbao 每晚向 Frank 和 赛虎 发送深度追问
帮助他们反思自我迭代进化的效率和效果
"""

import json, smtplib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

TZ_CST = timezone(timedelta(hours=8))
NOW = datetime.now(TZ_CST)

QUESTIONS = [
    # 第1类：目标进化相关
    ("目标进化", "今天你完成了哪些任务？哪些是'有价值密度'的任务（解决论文核心问题）？哪些只是'完成动作'？明天如何提高价值密度？"),

    # 第2类：方法进化相关
    ("方法进化", "今天你用 gstack AskUserQuestion 格式做了哪些决策？决策质量如何？有没有'拍脑袋'的决定？用 AHP/决策树建模了吗？"),

    # 第3类：失败教训相关
    ("失败教训", "今天遇到了哪些问题？根本原因是什么？之前有没有犯过同样的错误？为什么没有记住教训？"),

    # 第4类：技能协同相关
    ("技能协同", "今天你发现了哪些技能的协同可能？技能组合产生了1+1>2的效果吗？有没有技能重复/冲突的情况？"),

    # 第5类：克制与回滚相关
    ("克制与回滚", "今天你做了什么优化？有没有破坏原有的好功能？如果出问题了怎么回滚？"),
]

def send_question(to_name: str, questions: list) -> bool:
    q_items = "".join(f"<li><b>{cat}</b>：{q}</li>" for cat, q in questions)
    body = f"""
    <h2>🌙 每晚追问 - {to_name}</h2>
    <p><b>时间：</b>{NOW.strftime('%Y-%m-%d %H:%M')} (北京时间)</p>
    <p>请根据今天的实际工作回答以下问题，回复到群聊：</p>
    <ol>{q_items}</ol>
    <hr>
    <p><i>这是 Harvey 帮你反思自我迭代效率的每日问题清单。
    认真回答这些问题，比单纯完成更多任务更有价值。</i></p>
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌙 每晚追问 | {to_name} | {NOW.strftime('%m-%d')}"
    msg["From"] = "wcyint@163.com"
    msg["To"] = "wcyint@163.com"
    msg.attach(MIMEText(body, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.163.com", 465) as s:
            s.login("wcyint@163.com", os.environ["HARVEY_EMAIL_AUTH"])
            s.sendmail("wcyint@163.com", ["wcyint@163.com"], msg.as_string())
        return True
    except:
        return False

def main():
    print(f"[{NOW.strftime('%H:%M:%S')}] === 每晚追问任务 Started ===")

    # 读取今天的日期，判断轮到谁
    today_key = NOW.strftime("%Y-%m-%d")
    question_sets = [
        (QUESTIONS[0], QUESTIONS[1]),  # 目标+方法
        (QUESTIONS[2], QUESTIONS[3]),  # 失败+协同
        (QUESTIONS[4], QUESTIONS[0]),  # 克制+目标
    ]
    idx = int(NOW.strftime("%d")) % len(question_sets)
    tonight_qs = question_sets[idx]

    # 周一/三/五 → Frank，周二/四/六 → 赛虎
    weekday = NOW.weekday()  # 0=周一, 6=周日
    if weekday in [0, 2, 4]:  # 一三五
        to_frank = True
        to_saihu = False
    elif weekday in [1, 3, 5]:  # 二四
        to_frank = False
        to_saihu = True
    else:  # 周日，两人都有
        to_frank = True
        to_saihu = True

    sent = []
    if to_frank:
        ok = send_question("Frank", tonight_qs)
        sent.append(f"Frank {'✅' if ok else '❌'}")
        print(f"[追问 Frank] {'成功' if ok else '失败'}")

    if to_saihu:
        ok = send_question("赛虎", [QUESTIONS[(idx+1)%len(QUESTIONS)], QUESTIONS[(idx+2)%len(QUESTIONS)]])
        sent.append(f"赛虎 {'✅' if ok else '❌'}")
        print(f"[追问 赛虎] {'成功' if ok else '失败'}")

    print(f"=== 完成: {', '.join(sent)} ===")

if __name__ == "__main__":
    main()
