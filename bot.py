# -*- coding: utf-8 -*-
import requests
import feedparser
import time
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ====== TELEGRAM DETAILS ======
TOKEN = "8473210589:AAHvRQq7ZSlpBQt17MfnKH5v1w54kqC7idQ"
CHAT_ID = "651399128"

# ====== NEWS SOURCE ======
rss_url = "https://www.moneycontrol.com/rss/business.xml"

# ====== SECTORS ======
sectors = {
    "Banking": ["ICICI", "SBI", "HDFC", "Axis", "Kotak", "IndusInd"],
    "IT": ["TCS", "Infosys", "Wipro", "HCL", "Tech Mahindra"],
    "Energy": ["Reliance", "ONGC", "BPCL", "HPCL", "Adani"],
    "Auto": ["Tata Motors", "Maruti", "Mahindra", "Bajaj Auto", "Eicher"],
    "Pharma": ["Sun Pharma", "Dr Reddy", "Cipla", "Lupin"],
    "FMCG": ["HUL", "ITC", "Nestle", "Tata Consumer", "Britannia"],
    "Infra": ["L&T", "Adani Ports", "GMR", "IRB"],
    "Metals": ["Tata Steel", "JSW Steel", "Hindalco"],
    "Telecom": ["Bharti Airtel", "Vodafone Idea"]
}

# ====== HIGH IMPACT KEYWORDS ======
impact_keywords = [
    "profit", "loss", "results", "earnings",
    "dividend", "acquisition", "merger",
    "order", "contract", "approval",
    "regulation", "policy",
    "upgrade", "downgrade",
    "stake", "deal"
]

# ====== SETUP ======
daily_alerts = []
sent_links = set()
analyzer = SentimentIntensityAnalyzer()

# ====== LOOP ======
def run_bot():
    while True:
    feed = feedparser.parse(rss_url)

    for entry in feed.entries:
        if entry.link in sent_links:
            continue

        title_lower = entry.title.lower()

        for sector, companies in sectors.items():
            for company in companies:

                if company.lower() in title_lower:

                    if any(keyword in title_lower for keyword in impact_keywords):

                        score = analyzer.polarity_scores(entry.title)
                        compound = score['compound']

                        # Strong signals only
                        if compound >= 0.3:
                            sentiment = "🟢 Strong Bullish"
                        elif compound <= -0.3:
                            sentiment = "🔴 Strong Bearish"
                        else:
                            continue

                        # Store alert
                        daily_alerts.append((sector, company, compound))

                        # Message
                        message = f"""📢 POSITIONAL ALERT

Sector: {sector}
Company: {company}

{entry.title}

Sentiment: {sentiment}
Score: {round(compound, 2)}

{entry.link}
"""

                        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        data = {
                            "chat_id": CHAT_ID,
                            "text": message
                        }

                        requests.post(url, data=data)
                        sent_links.add(entry.link)

    # ====== DAILY SUMMARY (9PM) ======
    current_hour = time.localtime().tm_hour

    if current_hour == 21 and daily_alerts:

        bullish = sorted(daily_alerts, key=lambda x: x[2], reverse=True)
        bearish = sorted(daily_alerts, key=lambda x: x[2])

        summary_message = "📊 DAILY POSITIONAL SUMMARY\n\n"

        summary_message += "🟢 Top Bullish:\n"
        for item in bullish[:3]:
            summary_message += f"- {item[1]} ({round(item[2],2)})\n"

        summary_message += "\n🔴 Top Bearish:\n"
        for item in bearish[:3]:
            summary_message += f"- {item[1]} ({round(item[2],2)})\n"

        summary_message += f"\nTotal Alerts Today: {len(daily_alerts)}"

        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {
            "chat_id": CHAT_ID,
            "text": summary_message
        }

        requests.post(url, data=data)

        daily_alerts.clear()

    time.sleep(900)  # 15 minutes
run_bot()