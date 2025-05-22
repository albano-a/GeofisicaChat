import streamlit as st
import cohere

st.title("💬 GeofisicaChat with Token Billing")

st.write(
    "Use your Cohere API key to chat. "
    "You have a monthly token quota deducted per message. "
    "Upgrade plans to get more tokens."
)

# Simulated user token data (replace with DB or real user auth)
if "tokens" not in st.session_state:
    st.session_state.tokens = 1000_000  # 1 million tokens free tier example

cohere_api_key = st.text_input("Cohere API Key", type="password")
if not cohere_api_key:
    st.info("Please provide your Cohere API key to continue.")
else:
    client = cohere.Client(cohere_api_key)

    # Display remaining tokens
    st.sidebar.metric("Tokens Left", f"{st.session_state.tokens:,}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    valid_roles = {"User", "Chatbot"}
    st.session_state.messages = [
        m for m in st.session_state.messages if m["role"] in valid_roles
    ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    def estimate_token_cost(msg: str) -> int:
        # Simplified token cost: 1 token per 4 chars roughly
        return max(1, len(msg) // 4)

    if prompt := st.chat_input("O que deseja perguntar?"):
        cost = estimate_token_cost(prompt)
        if st.session_state.tokens < cost:
            st.error(
                f"Tokens insuficientes para processar essa mensagem. "
                f"Você precisa de {cost} tokens, mas só tem {st.session_state.tokens}."
            )
        else:
            st.session_state.tokens -= cost
            st.session_state.messages.append({"role": "User", "content": prompt})
            with st.chat_message("User"):
                st.markdown(prompt)

            system_message = {
                "role": "System",
                "message": "Você é um assistente especializado em geofísica.",
            }
            chat_history = [system_message] + [
                {"role": m["role"], "message": m["content"]}
                for m in st.session_state.messages[:-1]
            ]

            response = client.chat(
                message=prompt,
                chat_history=chat_history,
                model="command-r-plus",
            )

            # Deduct tokens for the response too (estimate)
            cost_resp = estimate_token_cost(response.text)
            if st.session_state.tokens < cost_resp:
                st.error(
                    "Tokens insuficientes para receber resposta completa. "
                    "Considere adquirir mais tokens."
                )
                response_text = response.text[: st.session_state.tokens * 4]  # partial?
                st.session_state.tokens = 0
            else:
                st.session_state.tokens -= cost_resp
                response_text = response.text

            with st.chat_message("Chatbot"):
                st.markdown(response_text)
            st.session_state.messages.append(
                {"role": "Chatbot", "content": response_text}
            )
