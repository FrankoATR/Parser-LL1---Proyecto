import sys
try:
    import spacy
except Exception:
    print("spaCy no está instalado. Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

try:
    nlp = spacy.load("es_core_news_sm")
except Exception:
    print("Modelo 'es_core_news_sm' no está descargado.")
    print("Instálalo con: python -m spacy download es_core_news_sm")
    sys.exit(1)

text = "Juan come manzanas en el parque los domingos por la mañana."
doc = nlp(text)

print("=== Tokens / PoS / Dep / Head ===")
for t in doc:
    print(f"{t.text:12}  {t.pos_:6}  {t.dep_:12}  -> {t.head.text}")
