# Mini Game Portal (Streamlit)
This repository contains a Streamlit-based multi-game portal including 12 mini-games:
- Color Find, Number Find, Gomoku, Dots & Boxes (simple), Mastermind-style, Question Cards,
  Up & Down, Chosung quiz, Word Chain, Trivia, Clicker (Tycoon), Rhythm Defense (simplified).

## Run locally
1. Install Python 3.8+
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run:
```
streamlit run app.py
```

## Deploy to Streamlit Cloud / GitHub
- Push this folder to a GitHub repository, then link to Streamlit Cloud and set the main file to `app.py`.
- Make sure `requirements.txt` is included.

## Notes
- The rhythm game is simplified for the Streamlit environment (server roundtrips limit very tight real-time input).
- Sound effects are synthesized as small WAV clips using NumPy and served via `st.audio`.

Made With : ChatGPT, macugzen, Streamlit, Python
