import streamlit as st
import cohere

st.title("💬 Chatbot")
st.write(
    "Este é um chatbot simples que usa o modelo Command da Cohere para gerar respostas. "
    "Para usar este app, forneça sua chave de API da Cohere, que você pode obter [aqui](https://dashboard.cohere.com/api-keys)."
)

cohere_api_key = st.text_input("Cohere API Key", type="password")
if not cohere_api_key:
    st.info("Por favor, adicione sua chave de API da Cohere para continuar.", icon="🗝️")
else:
    client = cohere.Client(cohere_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Garante que só roles válidos estejam no histórico
    valid_roles = {"User", "Chatbot"}
    st.session_state.messages = [
        m for m in st.session_state.messages if m["role"] in valid_roles
    ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("O que deseja perguntar?"):
        st.session_state.messages.append({"role": "User", "content": prompt})
        with st.chat_message("User"):
            st.markdown(prompt)
            
        system_message = {"role": "System", "message": "Você é um assistente especializado em geofísica."}
        chat_history = [system_message] + [
            {"role": m["role"], "message": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        # Chama a API da Cohere
        response = client.chat(
            message=prompt,
            chat_history=chat_history,
            model="command-r-plus",
        )

        with st.chat_message("Chatbot"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "Chatbot", "content": response.text})