import streamlit as st
import time
import random
from PIL import Image

# 抽卡逻辑
def draw_card():
    available = [card for card in st.session_state.cards if card[0] not in st.session_state.used_cards]
    if not available:
        return

    selected = random.choice(available)
    st.session_state.current_card = selected
    st.session_state.used_cards.append(selected[0])
    st.session_state.draw_count += 1
    st.session_state.last_draw_time = time.time()

    st.session_state.draw_log.append({
        "编号": selected[0],
        "随机数字": selected[1],
        "是否保留": None,
        "用时（秒）": 0
    })

# 保留逻辑
def keep_card():
    if st.session_state.kept_card:
        st.session_state.last_discarded_card = st.session_state.kept_card[0]

    st.session_state.kept_card = st.session_state.current_card
    st.session_state.draw_log[-1]["是否保留"] = "是"
    st.session_state.draw_log[-1]["用时（秒）"] = int(time.time() - st.session_state.last_draw_time)
    st.session_state.current_card = None

# 弃卡逻辑
def discard_card():
    st.session_state.last_discarded_card = st.session_state.current_card[0]
    st.session_state.draw_log[-1]["是否保留"] = "否"
    st.session_state.draw_log[-1]["用时（秒）"] = int(time.time() - st.session_state.last_draw_time)
    st.session_state.current_card = None

# 结算逻辑
def end_game():
    st.markdown("---")
    if st.session_state.kept_card and st.session_state.kept_card[1] == st.session_state.target_number:
        st.success(f"胜利！你保留的卡片的随机号码是 {st.session_state.kept_card[1]}，目标是 {st.session_state.target_number}")
    elif st.session_state.kept_card:
        st.error(f"失败！你保留的卡片是 {st.session_state.kept_card[1]}，目标是 {st.session_state.target_number}")
    else:
        st.error("你没有保留任何卡片，游戏失败")

    st.markdown("### 抽卡记录：")
    for i, log in enumerate(st.session_state.draw_log):
        st.write(f"第{i+1}次：编号 {log['编号']}（随机号码：{log['随机数字']}），保留：{log['是否保留']}，用时：{log['用时（秒）']} 秒")

st.set_page_config(page_title="抽卡游戏", layout="wide")

# 初始化会话状态
if "cards" not in st.session_state:
    card_numbers = list(range(1, 11))
    card_values = [1,2,3,4,5,1,2,3,4,5]
    random.shuffle(card_values)
    st.session_state.cards = list(zip(card_numbers, card_values))
    st.session_state.used_cards = []
    st.session_state.current_card = None
    st.session_state.kept_card = None
    st.session_state.draw_log = []
    st.session_state.draw_count = 0
    st.session_state.target_number = random.randint(1, 5)
    st.session_state.start_time = time.time()
    st.session_state.game_over = False
    st.session_state.last_draw_time = time.time()


# 游戏结束判断
if st.session_state.draw_count >= 10 and st.session_state.current_card is None and not st.session_state.game_over:
    st.session_state.game_over = True
    end_game()
    
# 倒计时
elapsed = int(time.time() - st.session_state.start_time)
remaining_time = 180 - elapsed
if remaining_time <= 0 and not st.session_state.game_over:
    st.session_state.game_over = True
    st.warning("时间用尽，游戏失败")
    st.stop()
    
# 布局区域
left, right = st.columns([1, 1])

# 左侧：抽卡、计时
with left:
    st.markdown("### 抽卡区域")
    if st.session_state.current_card:
        card_img = Image.open(f"card{st.session_state.current_card[0]}.jpg").resize((200, 300))
    else:
        card_img = Image.open("placeholder.jpg").resize((200, 300))
    st.image(card_img)

    st.button("抽卡", key="draw", on_click=lambda: draw_card(), disabled=st.session_state.current_card is not None or st.session_state.game_over)

    st.markdown(f"剩余时间：{remaining_time} 秒")
    st.markdown(f"剩余抽卡次数：{10 - st.session_state.draw_count}")

# 右侧：操作 + 保留卡 + 弃卡
with right:
    st.markdown("### 当前操作")

    col1, col2 = st.columns(2)
    col1.button("保留当前卡", on_click=lambda: keep_card(), disabled=st.session_state.current_card is None or st.session_state.game_over)
    col2.button("放弃当前卡", on_click=lambda: discard_card(), disabled=st.session_state.current_card is None or st.session_state.game_over)

    st.markdown("#### 当前保留的卡片")
    if st.session_state.kept_card:
        img = Image.open(f"card{st.session_state.kept_card[0]}.jpg").resize((100, 150))
        st.image(img)
    else:
        st.image("placeholder.jpg", width=100)

    st.markdown("#### 上一张弃掉的卡片")
    if "last_discarded_card" in st.session_state:
        img = Image.open(f"card{st.session_state.last_discarded_card}.jpg").resize((80, 120))
        st.image(img)
    else:
        st.image("placeholder.jpg", width=80)
