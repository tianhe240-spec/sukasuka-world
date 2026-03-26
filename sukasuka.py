import time
import streamlit as st
import random

# 1. 页面与样式配置
st.set_page_config(page_title="Sukasuka七日纪", page_icon="🔞", layout="wide")
st.markdown("""
    <style>
    .big-font { font-size:28px !important; color: #FF0000; font-weight: bold; border: 3px solid #FF0000; padding: 15px; border-radius: 10px; background-color: #ffebeb; line-height: 1.5; }
    .death-font { font-size:40px !important; color: #000000; background-color: #FF0000; font-weight: bold; text-align: center; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 初始化变量
if 'day' not in st.session_state:
    st.session_state.update({
        'day': 1, 'hp': 100, 'favor': 20, 'phase': 'setup',
        'time_of_day': '白天', 'name': "？",
        'last_result': "欢迎来到sukasuka。这里每一天都可能是你的祭日。",
        'death_reason': ""
    })
if 'day' not in st.session_state:
    st.session_state.update({
        # ... 原有的那些变量保持不变 ...
        'new_event_triggered': False  # 新增这一行
    })

# 3. 扩充剧情事件池（增加暴毙逻辑）
# 格式：(描述, 体力变化, 好感变化, 是否直接暴毙)
EVENTS = {
    "白天_老老实实待着": [
        ("女王派人送来一碗‘虎鞭鹿茸汤’，你喝完当场抱着身边的侍女摇晃起来。", 20, -10, False),
        ("你在屋里导管，不小心抠破了皮感染了‘sukasuka真菌’，吊肿得很大，弄的大家都很痛。", -10, 0, False),
        ("你正在发呆，女王突然闯入强行让你表演下体碎大石，你因基本功不扎实险些断子绝孙。", -10, 30, False),
        ("你因为太老实，被路过的壮汉当成软柿子，抓去快活了一天，肛门松弛度增加。", -20, -10, False)
    ],
    "白天_出去闲逛": [
        ("你路过禁地‘榨汁间’，好奇往里看了一眼，结果被保安发现，当场被做成了肉饼。", 0, 0, True),  # 暴毙
        ("你遇到了一个奶0，他娇媚地看着你，你的魂都要被勾走了。", 20, -20, False),
        ("你遇到了女王的贴身壮汉，他觉得你眼神太挑衅，把你按在地上揍了一顿。", -10, -10, False),
        ("你在垃圾桶旁捡到一瓶不知名的粉色液体，喝完后你发现自己长出了胸毛（且是粉色的）。", -10, 20, False),
        ("你遇到一个花枝招展的小美女，她向你撒粉，你醒来发现自己躺在手术台上准备被‘去势’，好在跑得快。", -10, 0, False)
    ],
    "白天_尝试逃跑": [
        ("你试图翻墙，结果墙上通了高压电，你被电成了焦炭。外焦里嫩。", 0, 0, True),  # 暴毙
        ("你钻狗洞被卡住，被女王养的藏獒舔了一整天的脸和屁股，很爽，但脸部严重脱皮。", -20, -10, False),
        ("你伪装成垃圾桶，结果被垃圾车司机拉到荒郊野外干了一顿又送了回来。", -10, 0, False)
    ],
    "晚上_睡觉回血": [
        ("你睡得正香，隔壁奶0爬上你的床非要给你‘讲故事’，你被折腾了一宿没合眼，但很爽，精神极佳。", 10, -10, False),
        ("你梦见自己回到了家乡，结果女王突然出现在梦里把你吓醒，吓得你阳痿了三天，女王很不满，但你这几天得到了休息。", 10, -10, False),
        ("睡得太沉，被子被路过的壮汉偷走闻，你被冻感冒了。", -10, 0, False),
        ("一个完美的深度睡眠，你梦到了壮汉给你推拿，醒来后床单湿湿的，下面硬硬的，裤子脏脏的。", 20, 10, False)
    ],
    "晚上_深夜溜达": [
        ("你误入女王的秘药室，闻到了禁忌的香气，你的身体发生了不可名状的变异。", 20, 20, False),
        ("你在池塘边遇到一个正在洗澡的壮汉，你偷走了他的内裤导管，他咆哮着追上你，狠狠干了你一顿，你欲仙欲死。", 10, -10, False),
        ("深夜遇到了正在梦游的女王，她把你当成了她死去的爱犬，对你百般羞辱。", -10, 30, False),
        ("你试图偷窥一个小美女洗澡，结果被箭弩手射中了屁股。", -20, 0, False)
    ],
    "晚上_偷情作死": [
        ("你和女王最宠爱的那个男宠偷情，被女王当场撞破，女王冷笑着把你赏给了门口的保安团。", 0, 0, True),  # 暴毙
        ("你和奶0深夜在屋顶看星星，结果屋顶塌了，你摔进了女王怀里。", 0, -10, False),
        ("你勾搭上了壮汉统领，他为了奖励你，带你练习了一整晚，精疲力尽。", -20, 0, False)
    ]
}


def handle_event(choice):
    key = f"{st.session_state.time_of_day}_{choice}"
    if key in EVENTS:
        desc, h_chg, f_chg, instant_death = random.choice(EVENTS[key])
        st.session_state.last_result = desc

        # 1. 处理【即死】陷阱
        if instant_death:
            st.session_state.hp = 0
            st.session_state.death_reason = f"【暴毙】{desc}"
            st.session_state.phase = 'end'
            return

        # 2. 更新数值
        st.session_state.hp += h_chg
        st.session_state.favor += f_chg
        st.session_state.new_event_triggered = True

        # 3. 【核心修复】增加常规死亡判定
        # 即使不是即死陷阱，如果好感度被扣完了，也要立刻结算
        if st.session_state.hp <= 0:
            st.session_state.death_reason = "你精疲力竭，倒在了 sukasuka 的走廊里..."
            st.session_state.phase = 'end'
            return # 直接跳出，不再执行后面的切换天数
        
        if st.session_state.favor <= 0:
            st.session_state.death_reason = "女王对你彻底失去了兴趣，把你扔进了焚化炉。"
            st.session_state.phase = 'end'
            return # 直接跳出

        # 4. 只有在没死的情况下，才切换时间/天数
        if st.session_state.time_of_day == '白天':
            st.session_state.time_of_day = '晚上'
        else:
            st.session_state.time_of_day = '白天'
            st.session_state.day += 1

    # 常规检查
    if st.session_state.hp <= 0:
        st.session_state.death_reason = "你在这片极乐净土中耗尽了最后一丝生命，卒。"
        st.session_state.phase = 'end'
    elif st.session_state.favor <= 0:
        st.session_state.death_reason = "女王觉得你连垃圾都不如，把你塞进炮筒发射了出去。"
        st.session_state.phase = 'end'
    elif st.session_state.favor >= 100:
        st.session_state.death_reason = "你太讨喜了，女王决定把你浸在福尔马林里永久珍藏。"
        st.session_state.phase = 'end'
    elif st.session_state.day > 7:
        st.session_state.phase = 'end'


# --- UI 渲染 ---
st.title("🏰 Sukasuka七日纪")

with st.sidebar:
    st.header(f"🕺 选手：{st.session_state.name}")
    st.metric("🩸 体力", st.session_state.hp)
    st.metric("❤️ 好感度", st.session_state.favor)
    st.divider()
    st.subheader(f"📅 第 {st.session_state.day} 天 ({st.session_state.time_of_day})")

if st.session_state.phase == 'setup':
    st.session_state.name = st.text_input("输入你的大名，准备迎接处刑：", value="")
    if st.button("进入 sukasuka"):
        st.session_state.phase = 'action'
        st.rerun()
elif st.session_state.phase == 'action':
    st.markdown("### 📢 实时奇遇：")
    result_placeholder = st.empty()  # 创建一个动态占位符

    # 打字机特效函数
    def typewriter_effect(text):
        full_text = ""
        for char in text:
            full_text += char
            # 实时更新带有大号红字样式的文本
            result_placeholder.markdown(f'<div class="big-font">{full_text}</div>', unsafe_allow_html=True)
            time.sleep(0.04)

    # 逻辑判断：有新奇遇就打字，否则直接显示
    if st.session_state.get('new_event_triggered', False):
        typewriter_effect(st.session_state.last_result)
        st.session_state.new_event_triggered = False
    else:
        result_placeholder.markdown(f'<div class="big-font">{st.session_state.last_result}</div>', unsafe_allow_html=True)

    st.write("---")


    cols = st.columns(3)
    if st.session_state.time_of_day == '白天':
        if cols[0].button("老老实实待着"): handle_event("老老实实待着"); st.rerun()
        if cols[1].button("出去闲逛"): handle_event("出去闲逛"); st.rerun()
        if cols[2].button("尝试逃跑"): handle_event("尝试逃跑"); st.rerun()
    else:
        if cols[0].button("睡觉回血"): handle_event("睡觉回血"); st.rerun()
        if cols[1].button("深夜溜达"): handle_event("深夜溜达"); st.rerun()
        if cols[2].button("偷情作死"): handle_event("偷情作死"); st.rerun()

elif st.session_state.phase == 'end':
    if st.session_state.day > 7:
        st.balloons()
        st.markdown('<div class="death-font" style="background-color:#00FF00">【通关结局：sukasuka 幸存者】</div>',
                    unsafe_allow_html=True)
        st.success(f"不可思议！{st.session_state.name} 竟然在第七天深夜，趁着保安和壮汉换班，偷了一辆三轮车逃离了现场。")
    else:
        st.markdown('<div class="death-font">【达成结局：命丧黄泉】</div>', unsafe_allow_html=True)
        st.error(st.session_state.death_reason)

    if st.button("我不服，我要重活一世"):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()
