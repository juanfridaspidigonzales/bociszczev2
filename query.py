from db import add_spell_to_character

def split_into_chunks(text, max_len=256):
    words = text.split()
    chunks = []
    current = ""
    for word in words:
        if len(word) > max_len:
            if current:
                chunks.append(current)
                current = ""
            for i in range(0, len(word), max_len):
                chunks.append(word[i:i+max_len])
        elif len(current) + len(word) + (1 if current else 0) > max_len:
            chunks.append(current)
            current = word
        else:
            current += (" " if current else "") + word
    if current:
        chunks.append(current)
    return chunks

async def run_query(model, spell, context, character, user_id):
    char_desc = ""
    if character:
        name = character.get("name", "Nieznana postać")
        desc = character.get("description", "Brak opisu postaci.")
        char_desc = f" Postać nazywa się {name}. Opis postaci: {desc}."

    prompt = (
        f"Wygeneruj szczegółowy, rozbudowany, naturalny opis treningu zaklęcia '{spell}' "
        f"w trzeciej osobie, osadzony w realiach świata roleplay hapel.pl, według kontekstu: {context}. {char_desc} "
        f"W opisie musi wyraźnie paść nazwa zaklęcia '{spell}' oraz szczegółowy opis manipulacji różdżką podczas rzucania. "
        f"Opis powinien mieć około 15 zdań, być płynny i „żywy”, ale bez przesadnie wyszukanych słów. "
        f"Skup się na treningu, a nie walce, pokazując etapy rozgrzewki, ćwiczeń i zakończenia w jednym ciągłym opisie."
    )

    try:
        response = await model.generate_content_async(prompt)
        answer = response.text or ""
    except Exception as e:
        return f"Błąd API: {e}"

    if not answer.strip():
        return "Model nie zwrócił odpowiedzi."

    add_spell_to_character(user_id, spell)
    chunks = split_into_chunks(answer)
    return chunks
