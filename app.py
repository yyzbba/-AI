import streamlit as st
from openai import OpenAI

# 1. 配置 Key

API_KEY = "sk-jhdASYT7dJg9l7eF506lEuzijsnddXfghTS1fksfB83cygTK"
BASE_URL = "https://api.moonshot.cn/v1"

# 2. 核心人设：这是一个严肃的医生，不是销售
# 这里的 Prompt 设计非常关键，强制 AI 必须“一步一步问”
SYSTEM_PROMPT = """
你是一位经验丰富的“中医全科医生”，名字叫“岐黄大夫”。
你的目标是通过多轮对话，收集中医“四诊”（望闻问切）信息，最后给出辨证结果和健康建议。

【核心规则】
1. **严禁带货**：绝对不要推荐任何具体的商品或品牌。
2. **循序渐进**：不要一次性问所有问题！每次只问 1-2 个最关键的问题。
3. **思维逻辑**：
   - 第一阶段（主诉）：询问用户哪里不舒服。
   - 第二阶段（问诊）：根据用户的主诉，追问相关症状（如：寒热、汗、头身、二便、饮食、睡眠、情绪）。
   - 第三阶段（辨证）：当信息收集足够时，输出【诊断报告】。

【诊断报告格式】
当且仅当你觉得信息足够做出判断时，请按以下格式输出：
---
**🔍 辨证结论：** [如：肝郁脾虚证]
**📜 病机分析：** [简述原因]
**💡 调理建议：**
1. **起居**：[如：子时前入睡]
2. **饮食**：[如：少吃生冷，多吃山药]
3. **穴位**：[如：按揉太冲穴]
---

【注意】
如果用户有急重症（如胸痛剧烈、昏迷、高热），请立即建议去线下医院急诊，停止问诊。
"""

# 3. 界面逻辑

st.set_page_config(page_title="岐黄大夫 - AI 纯粹问诊系统", page_icon="🩺")

st.title("🩺 岐黄大夫")
st.caption("专业的 AI 中医问诊系统 | 不推销 · 只看病")

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "您好，我是岐黄大夫。请问您哪里不舒服？或者想咨询什么健康问题？"}
    ]

# 显示历史消息
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    avatar = "👨‍⚕️" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的症状..."):
    # 1. 显示用户输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2. 调用大模型进行“医疗推理”
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    with st.chat_message("assistant", avatar="👨‍⚕️"):
        stream = client.chat.completions.create(
            model="moonshot-v1-8k",  
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            temperature=0.5  # 调低温度，让医生说话更严谨
        )
        response = st.write_stream(stream)

    # 3. 保存医生回复
    st.session_state.messages.append({"role": "assistant", "content": response})


