# 🎯 3D AI Trading Signal Dashboard

![Status](https://img.shields.io/badge/status-active-success)
![Platform](https://img.shields.io/badge/platform-Streamlit-red)
![3D](https://img.shields.io/badge/visualization-Three.js-blue)

## 📋 Umumiy Ma'lumot

**3D AI Trading Signal Dashboard** - bu zamonaviy AI-powered stock trading signals platformasi bo'lib, real-time market ma'lumotlarini interaktiv 3D visualizatsiya orqali taqdim etadi.

### ✨ Asosiy Xususiyatlar

- 🤖 **AI Signal Generation** - Machine Learning algoritmlar yordamida BUY/SELL/HOLD signallari
- 🌐 **Interactive 3D Visualization** - Three.js asosida yaratilgan immersive 3D interfeys
- 📊 **Real-time Data** - Yahoo Finance API orqali jonli market ma'lumotlari
- 😨😃 **Fear & Greed Index** - Market sentimentni real-time monitoring
- 📱 **Mobile Responsive** - Barcha qurilmalarda optimallashgan ishlash
- 📈 **Advanced Analytics** - RSI, MACD, SMA, EMA va boshqa texnik indikatorlar

---

## 🏗️ Arxitektura

```
Stock AI Platform/
├── AI SIGNAL ENGINE
│   ├── ai_3d_signal_panel.py      # AI signal generator
│   ├── Technical Analysis (RSI, MACD, SMA)
│   └── Fear & Greed Calculator
├── 3D VISUALIZATION
│   ├── templates/
│   │   └── trading_3d_dashboard.html  # 3D frontend
│   └── static/
│       └── js/
│           └── mobile-optimizer.js     # Mobile optimization
└── STREAMLIT INTEGRATION
    └── app.py                      # Main Streamlit app
```

---

## 🚀 Quick Start

### 1. Dependencies Installation

```bash
# UV package manager bilan
uv sync

# Yoki pip bilan
pip install -r requirements.txt
```

### 2. Launch Streamlit App

```bash
streamlit run app.py
```

### 3. Navigate to 3D Dashboard

Streamlit sidebar da **"🎯 3D AI Signal Dashboard"** ni tanlang.

---

## 🎨 3D Visualization Komponentlari

### 1️⃣ Signal Towers (Signal Minoralari)

- **Yashil Towers** 🟢 - BUY signals
- **Qizil Towers** 🔴 - SELL signals
- **Moviy Towers** 🔵 - HOLD signals

**Interaktiv xususiyatlar:**
- Balandlik = Signal confidence (%)
- Pulsing animation = Signal strength
- Click to view details

### 2️⃣ Fear & Greed Gauge

Real-time market sentiment visualization:
- 😨 **Fear Zone** (0-40%) - Qizil
- 😐 **Neutral Zone** (40-60%) - Sariq
- 😃 **Greed Zone** (60-100%) - Yashil

### 3️⃣ Trading Panels

3D floating panels with:
- Signal screener
- Market overview
- Settings

### 4️⃣ Interactive Platform

Glass-style base platform with:
- Glowing edges
- Fog effects
- Grid helpers

---

## 🤖 AI Signal Generation

### Texnik Indikatorlar

1. **Moving Averages**
   - SMA 20, SMA 50
   - EMA 12, EMA 26

2. **Momentum Indicators**
   - RSI (Relative Strength Index)
   - MACD (Moving Average Convergence Divergence)

3. **Volume Analysis**
   - Volume ratio
   - Volume spikes

4. **Price Action**
   - 1-day, 5-day, 20-day changes
   - Support/Resistance levels

### Scoring System

```python
# AI Signal Score = Weighted sum of:
- Moving Average Signals (30%)
- RSI Signals (25%)
- MACD Signals (20%)
- Volume Confirmation (15%)
- Price Momentum (10%)

# Decision Logic:
if buy_confidence >= 65%:  action = "BUY"
elif sell_confidence >= 65%:  action = "SELL"
else:  action = "HOLD"
```

---

## 📊 Foydalanish

### Sidebar Settings

1. **Stock Symbols**
   ```
   AAPL,TSLA,NVDA,META,GOOGL,AMZN,MSFT
   ```

2. **Timeframe Selection**
   - 1d (kunlik)
   - 1h (soatlik)
   - 5m, 15m, 30m (daqiqalik)

3. **Signal Filters**
   - Minimum confidence: 50-100%
   - Show/Hide BUY/SELL/HOLD signals

4. **Auto-refresh**
   - Enable 60-second auto-refresh

### 3D Controls

| Control | Action |
|---------|--------|
| 🖱️ **Left Click + Drag** | Rotate 3D scene |
| 🖱️ **Right Click + Drag** | Pan camera |
| 🖱️ **Scroll Wheel** | Zoom in/out |
| 🎯 **Click on Tower** | View signal details |
| 📊 **Control Buttons** | Switch views |

---

## 📱 Mobile Optimization

### Device Detection

```javascript
- Mobile: iPhone, Android phones
- Tablet: iPad, Android tablets
- Desktop: All other devices
```

### Performance Levels

| Device | Settings |
|--------|----------|
| **Mobile** | Low poly, 30 FPS, no shadows, basic materials |
| **Tablet** | Medium poly, 45 FPS, simplified shadows |
| **Desktop** | High poly, 60 FPS, full effects |

### Touch Gestures

- ☝️ **Single finger drag** - Rotate
- ✌️ **Two finger pinch** - Zoom
- 👆 **Tap** - Select signal tower

---

## 💾 Data Export

### CSV Export
```csv
symbol,action,confidence,price,target,rsi,volume_ratio
AAPL,BUY,92,178.50,195.00,45.2,1.8
```

### JSON Export
```json
{
  "signals": [...],
  "fear_greed": {"fear": 45, "greed": 55},
  "market_sentiment": "GREEDY",
  "timestamp": "2025-11-13T19:00:00"
}
```

---

## 🔧 Configuration

### AI Signal Parameters

Edit `ai_3d_signal_panel.py`:

```python
class AI3DSignalPanel:
    # RSI thresholds
    RSI_OVERSOLD = 30
    RSI_OVERBOUGHT = 70

    # Confidence thresholds
    MIN_CONFIDENCE = 65
    HIGH_CONFIDENCE = 80

    # Target calculation
    BUY_TARGET_MULTIPLIER = 1.10  # 10% upside
    SELL_TARGET_MULTIPLIER = 0.90  # 10% downside
```

### 3D Visual Settings

Edit `templates/trading_3d_dashboard.html`:

```javascript
// Colors
const BUY_COLOR = 0x00FF88;    // Green
const SELL_COLOR = 0xFF3750;   // Red
const HOLD_COLOR = 0x1FB6FF;   // Blue

// Animation speeds
const PULSE_SPEED = 0.005;
const ROTATION_SPEED = 0.002;
```

---

## 🎯 Use Cases

### 1. Day Trading
- Real-time signals har 5-15 daqiqada
- Quick entry/exit points
- Volume spike alerts

### 2. Swing Trading
- Daily/hourly signals
- Trend following
- Support/resistance levels

### 3. Long-term Investment
- Weekly signals
- Fundamental + technical analysis
- Market sentiment tracking

---

## ⚠️ Disclaimer

**MUHIM OGOHLANTIRISH:**

- ✅ Bu tool faqat **educational purposes** uchun
- ❌ **Financial advice emas** - har doim o'z tadqiqotingizni o'tkazing
- 📚 Professional financial advisor bilan maslahatlashing
- 💰 Faqat yo'qotishga qodir bo'lgan pulni invest qiling
- 📊 Past performance ≠ future results

---

## 🔮 Future Enhancements

- [ ] WebSocket real-time data feed
- [ ] Broker API integration (Alpaca, IBKR)
- [ ] Backtesting functionality
- [ ] Portfolio management
- [ ] Multi-timeframe analysis
- [ ] News sentiment analysis
- [ ] Social media sentiment tracking
- [ ] Custom alert notifications

---

## 📚 Technologies Used

| Category | Technology |
|----------|-----------|
| **Frontend** | Three.js, HTML5, CSS3, JavaScript |
| **Backend** | Python 3.11, Streamlit |
| **Data** | yfinance, pandas, numpy |
| **AI/ML** | Custom algorithms, Technical Analysis |
| **Optimization** | Mobile Optimizer, Performance Tuning |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/YourFeature`)
3. Commit changes (`git commit -m 'Add YourFeature'`)
4. Push to branch (`git push origin feature/YourFeature`)
5. Open Pull Request

---

## 📧 Support

Issues yoki savollar uchun GitHub Issues ochish.

---

## 📄 License

This project is for educational purposes only.

---

## 🙏 Acknowledgments

- **Three.js** - 3D visualization library
- **Streamlit** - Web app framework
- **yfinance** - Market data API
- **GSAP** - Animation library

---

**Made with ❤️ for Stock Traders**

*Disclaimer: Always do your own research before investing.*
