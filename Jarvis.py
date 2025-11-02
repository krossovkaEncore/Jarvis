from groq import Groq
import config

def jarvis(chat_id, user_message, chat_history={}):
    client = Groq(api_key=config.tokenGroq)
    chat_history[chat_id] = [{"role": "system", "content": f"Правила / промт:\n{config.promt}"}]
    chat_history[chat_id].append({"role": "user", "content": user_message})
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=chat_history[chat_id]
    )
    answer = resp.choices[0].message.content
    chat_history[chat_id].append({"role": "assistant", "content": answer})
    return answer