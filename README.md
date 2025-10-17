# 🌞 AI Stock Analyzer (Red-Themed)

A **modern, attractive, and responsive Stock Analyzer** built with **Streamlit, OpenAI GPT, and yFinance**.  
Analyze stocks with **technical indicators, fundamental metrics, price charts**, and get **AI-powered BUY/HOLD/SELL recommendations**.

---

## 🔥 Features

- Red-themed **glowing title and subtitle**  
- **Animated gradient background**  
- Hoverable **technical and fundamental metric cards**  
- **Color-coded BUY/HOLD/SELL banners**  
- **Price charts with Streamlit line charts**  
- **AI-powered recommendation** using OpenAI GPT (`gpt-4o`)  
- Fully responsive layout for desktop and mobile  
- Clean and intuitive user interface  

---

## 🛠️ Tech Stack

- Python 3.x  
- [Streamlit](https://streamlit.io/) for web UI  
- [yFinance](https://pypi.org/project/yfinance/) for stock data  
- [TA-Lib via `ta`](https://pypi.org/project/ta/) for technical indicators (RSI, MACD)  
- [OpenAI API](https://platform.openai.com/) for AI recommendations  
- `.env` file for **secure API key storage**  

---

## 💾 Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/stock_analyzer.git
cd stock_analyzer


2)Create a virtual environment (optional but recommended):
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

3)Install dependencies:
pip install -r requirements.txt

4)Create a .env file in the project root:
OPENAI_API_KEY=your_openai_api_key_here
