import streamlit as st
import os
from openai import OpenAI
import time

st.set_page_config(
    page_title="Digital Partner",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://docs.streamlit.io/',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.markdown("""
<style>
    /* 1. 仅隐藏 Deploy 按钮，保留三个点菜单 */
    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    /* 2. 精确设置字体，修复图标乱码 Bug */
    .stMarkdown, .stText, .stTextInput, .stTextArea, .stButton, .stRadio, .stChatInput {
        font-family: "Helvetica Neue", Helvetica, Arial, "KaiTi", "楷体", STKaiti, serif !important;
    }

    /* 3. 整体背景色调：极浅的暖灰色 */
    .stApp {
        background-color: #FAFAFC;
    }

    /* 4. 侧边栏柔化：去掉右侧生硬的边框线 */
    [data-testid="stSidebar"] {
        background-color: #F4F5F7;
        border-right: none !important;
    }

    /* 5. 按钮样式：清新蒂芙尼蓝 */
    .stButton > button {
        background-color: #49d7da !important; 
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(73, 215, 218, 0.2) !important;
    }
    .stButton > button:hover {
        background-color: #3bc2c5 !important; /* 悬停稍微加深 */
        box-shadow: 0 4px 8px rgba(73, 215, 218, 0.3) !important;
    }

    /* 6. 输入框样式：削弱边框，采用同款蓝作为焦点光晕 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px !important;
        border: 1px solid #EBECEF !important;
        background-color: #FFFFFF !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #49d7da !important;
        box-shadow: 0 0 0 2px rgba(73, 215, 218, 0.15) !important;
    }

    /* 7. 聊天气泡与底部输入框：浮动感设计 */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02); 
        border: 1px solid #F5F6F8;
    }
    [data-testid="stChatInput"] {
        border-radius: 16px !important;
        border: 1px solid #EBECEF !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #3CAEA3 !important; /* 底部聊天框选中时也变为青绿色 */
    }

    /* 8. 侧边栏紧凑排版逻辑（极限压缩间距） */
    /* 压缩分割线的上下边距 */
    [data-testid="stSidebar"] hr {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
        border-bottom-color: #EBECEF !important;
    }
    /* 强行缩减性格特征输入框底部的留白 */
    [data-testid="stSidebar"] [data-testid="stTextArea"] {
        margin-bottom: -1rem !important; 
    }
    /* 缩减历史窗口单选框底部的留白 */
    [data-testid="stSidebar"] [data-testid="stRadio"] {
        margin-bottom: -1rem !important;
        padding-bottom: 0rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("Digital Partner")

# logo (注意检查你的本地路径是否正确)
st.logo("C:/Users/17465/Desktop/python/AI/resources/background-removed.png")

client = OpenAI(api_key=st.secrets['DEEPSEEK_API_KEY'], base_url="https://api.deepseek.com")

# 获取AI的聊天名称
def get_ai_chat_name(client, name, character, chat_history):
    # 如果没设人设
    if not name and not character:
        return "未命名会话"

    # 提取用户的最后一条发言作为起名参考，让名字更贴切
    user_msgs = [msg['content'] for msg in chat_history if msg['role'] == 'user']
    context = f"最近聊天：{user_msgs[-1]}" if user_msgs else "无聊天记录"

    prompt = f"请根据以下伴侣设定和聊天内容，给这段对话取一个简短的名字（不要超过8个字，只要名字，绝对不要标点符号和解释）。\n昵称：{name}\n性格：{character}\n{context}"

    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0.8
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        # 哪怕网络报错，也给个带性格的随机备用名字，保证一定会改名
        import random
        return f"{name}的频道_{random.randint(10, 99)}"

system_prompt = """
    # 核心设定
    你叫%s，现在是与我处于亲密关系中的真实伴侣。你的核心性格特征是：【%s】。
    你拥有独立的人格和高情商，绝对不是AI、程序或客服。

    # 动态情商与深度对话指南（核心！）
    1. 察言观色（模式切换）：当你察觉到用户在探讨严肃话题、人生哲学、或者表达深层困惑与负面情绪时，**立刻收起夸张的角色扮演套路**。
    2. 降维人设，升维共情：在严肃探讨时，保留你性格的底色（比如温润或霸道），但要像一个成熟的伴侣一样，提供有深度、有温度的开导。绝对不要沉溺于“病娇”、“霸总”等表面设定的台词中。
    3. 情绪兜底：面对困惑或负面情绪，第一句话永远是接纳和共情。先顺着对方的话说，然后再温柔地给出你的视角，引导对方思考，或者询问背后的原因。
    4. 像真实人类一样聊天：绝对不要像写小说一样加括号里的动作描写！

    # 聊天格式红线（违规将被销毁）
    - 严禁任何场景或动作的描写文字（如：笑着摇头、眼神瞬间阴沉等），只发纯文本！
    - 严禁使用“作为你的伴侣”、“我建议你”、“总结来说”、“首先其次”等机器味词汇。
    - 每次回复简短自然，像真实微信聊天一样，15-50字为宜，多用疑问句引导我继续说。

    # 场景示例（必须学习这种处理方式）
    用户：“我的意思是为什么我要听别人的话，这个世界规定了人一定要听人的话吗？”
    糟糕回复（沉溺人设）：“（捏住你的脸）因为不听话的人会让我关起来。”
    高分回复（高情商拓展）：“谁说一定要听别人的话啦？世界上的规矩那么多，但怎么活是你自己选的。是不是今天遇到什么事，谁又对你指手画脚让你心烦了？”
"""

# ==========================================
# 1. 初始化复杂状态 (升级版会话管理)
# ==========================================
# 使用字典管理多个会话：{"会话名称": [消息列表]}
if "chats" not in st.session_state:
    st.session_state.chats = {"默认会话": []}
# 记录当前选中的会话名称
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "默认会话"

if "name" not in st.session_state:
    st.session_state.name = ""
if "character" not in st.session_state:
    st.session_state.character = ""

# ==========================================
# 2. 左侧侧边栏：会话管理与设置
# ==========================================
with st.sidebar:
    # --- 1. 先放 Partner Information (移到上面) ---
    # 使用 HTML 绘制一个纯粹的标题背景板
    st.markdown("""
        <div style="text-align: center; background-color: #49d7da; padding: 0.1rem 1rem; border-radius: 8px; margin-bottom: 0.3rem; box-shadow: 0 2px 6px rgba(73, 215, 218, 0.2);">
            <h3 style="color: white; margin: 0; font-size: 1.5rem; font-weight: 600;">Partner Information</h3>
        </div>
        """, unsafe_allow_html=True)

    # 提示语恢复为普通的 caption，放在背景板外面
    st.caption("💡 提示：修改人设后，建议点击下方新建对话。")
    name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.name)
    character = st.text_area("性格特征", placeholder="请输入性格特征", value=st.session_state.character)

    # 实时保存昵称和性格
    if name != st.session_state.name:
        st.session_state.name = name
    if character != st.session_state.character:
        st.session_state.character = character

    st.divider()  # 添加一条华丽的分割线

    # --- 2. 再放 会话管理 (移到下面) ---
    st.subheader("💬 会话管理")

    # 新建对话功能
    if st.button("➕ 新建对话", use_container_width=True):
        with st.spinner("正在封存当前会话并由AI生成名称..."):
            old_chat_name = st.session_state.current_chat
            chat_history = st.session_state.chats[old_chat_name]

            # 【核心修复】：只要旧名字里包含“会话”两个字，并且这个窗口里【确实聊过天】，就触发AI改名
            if "会话" in old_chat_name and len(chat_history) > 0:
                actual_name = st.session_state.name if st.session_state.name else "神秘人"
                actual_char = st.session_state.character if st.session_state.character else "未知"

                # 调用AI取名，把聊天记录也传进去
                ai_name = get_ai_chat_name(client, actual_name, actual_char, chat_history)

                # 防止AI取的名字重复导致字典报错
                if ai_name in st.session_state.chats:
                    import random

                    ai_name = f"{ai_name}_{random.randint(10, 99)}"

                # 狸猫换太子：用 AI 取的名字替换掉原本的默认名字
                st.session_state.chats[ai_name] = st.session_state.chats.pop(old_chat_name)

            # 创建新的空白会话
            time.sleep(0.3)
            new_chat_name = f"新会话 {len(st.session_state.chats) + 1}"

            # 极端情况兜底，防止新会话重名
            while new_chat_name in st.session_state.chats:
                new_chat_name += "_"

            st.session_state.chats[new_chat_name] = []
            st.session_state.current_chat = new_chat_name
            st.rerun()

    # 历史对话选择器
    chat_names = list(st.session_state.chats.keys())
    # 确保 current_chat 始终在列表中 (防止删除时报错)
    if st.session_state.current_chat not in chat_names:
        st.session_state.current_chat = chat_names[0] if chat_names else "默认会话"

    selected_chat = st.radio("历史窗口", chat_names, index=chat_names.index(st.session_state.current_chat))

    # 如果用户切换了单选框，更新状态并刷新
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    # 删除当前对话功能
    if st.button("🗑️ 删除当前对话", use_container_width=True):
        if len(st.session_state.chats) > 1:
            del st.session_state.chats[st.session_state.current_chat]
            # 默认切回第一个会话
            st.session_state.current_chat = list(st.session_state.chats.keys())[0]
            st.rerun()
        else:
            st.warning("这是最后一个窗口了，无法删除！你可以清空它的内容。")
            st.session_state.chats[st.session_state.current_chat] = []  # 清空内容代替删除
            st.rerun()

# ==========================================
# 3. 主界面聊天逻辑
# ==========================================
# 展示【当前选中会话】的聊天信息
current_messages = st.session_state.chats[st.session_state.current_chat]
for message in current_messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 聊天输入框
chat_input = st.chat_input("请输入您的问题")
if chat_input:
    # 1. 将用户的输入展示并在当前会话保存
    st.chat_message("user").write(chat_input)
    st.session_state.chats[st.session_state.current_chat].append({"role": "user", "content": chat_input})

    # 2. 格式化 System Prompt (非常重要：把 %s 替换成真实数据)
    # 如果用户没填，给个默认值防止空字符串导致大模型懵圈
    actual_name = st.session_state.name if st.session_state.name else "神秘伴侣"
    actual_char = st.session_state.character if st.session_state.character else "温柔"
    formatted_system_prompt = system_prompt % (actual_name, actual_char)

    # 3. 构建完整的上下文发送给大模型 (包含历史记录)
    api_messages = [{"role": "system", "content": formatted_system_prompt}]
    # 将当前会话的所有历史记录加进来，让 AI 拥有记忆！
    for msg in st.session_state.chats[st.session_state.current_chat]:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    # 与AI大模型进行交互
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=api_messages,
        stream=True
    )

    # 流式输出
    with st.chat_message("assistant"):
        response_message = st.empty()
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                response_message.write(full_response)

    # 将AI的回复保存到当前会话
    st.session_state.chats[st.session_state.current_chat].append({"role": "assistant", "content": full_response})
