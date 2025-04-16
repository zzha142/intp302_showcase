# 🎓 College Simulator: Werewolf Mode

A text-based simulation game where you play as a college student trying to balance your studies, social life, and uncover a hidden werewolf on campus.  
The game integrates OpenAI's GPT to generate dynamic NPC dialogue!

---

## 🚀 Features

- 🧠 Smart NPCs powered by OpenAI ChatGPT (GPT-3.5)
- 🐺 Behavior tree for werewolf attacks
- 🎓 Stat management: GPA, stamina, intelligence, social
- 🔍 Clue discovery and mystery-solving mechanics
- 🗨️ Optional AI or fallback to simulated responses

---

## 📦 Installation

1. Clone this repository:

```bash
git clone https://github.com/your-repo/college-werewolf.git
cd college-werewolf
```

2. Install dependencies:

```bash
pip install openai python-dotenv
```

3. Set up your `.env` file:

- Create a file named `.env` in the root directory.
- Add the following line with your own API key:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ **Do not share your API key or commit it to GitHub!**

> If you do not have an API key, the game will still run using simulated AI responses.

---

## 🧪 Usage

```bash
python college_simulation_eng_API_gpt_finalfix3.py
```

- You will be prompted to enter your player name.
- Each day, you can attend class, study, socialize, investigate, rest, or accuse someone.
- Talk to classmates and collect clues to uncover the werewolf before it's too late.

---

## 👥 For Group Members

- If you don't have an OpenAI API key:
  - You can still run the game, it will automatically use fake AI responses for a smooth experience.
- If you want to use the real AI:
  - Sign up at [https://platform.openai.com](https://platform.openai.com)
  - Create an API key and paste it into your `.env` file as shown above.

---

## 🔒 Safety Notes

- `.env` is **excluded from Git** via `.gitignore`.
- Your OpenAI key is kept private.
- No API usage will occur unless a valid key is provided.
- If you’re the project owner, consider setting a daily limit at:
  [https://platform.openai.com/account/billing/limits](https://platform.openai.com/account/billing/limits)

---

## 📄 License

This project is for educational use and portfolio showcase only.
