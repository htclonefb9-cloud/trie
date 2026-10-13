import os
import random
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình Database SQLite lưu trên ổ đĩa
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Định nghĩa bảng Người chơi
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Float, default=10000.0)

# Định nghĩa bảng Lịch sử ván chơi
class GameHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    multiplier = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="player1").first():
        default_user = User(username="player1", balance=10000.0)
        db.session.add(default_user)
        db.session.commit()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviator Pro - Lưu Dữ Liệu Thật</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b0e14; color: #ffffff; display: flex; justify-content: center; padding: 10px; }
        .main-container { width: 100%; max-width: 420px; background: #141820; border-radius: 12px; padding: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.7); }
        .top-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .brand-title { color: #e53935; font-size: 22px; font-weight: 900; font-style: italic; }
        .wallet-box { background: #1f242d; padding: 5px 12px; border-radius: 20px; font-size: 13px; display: flex; align-items: center; gap: 5px; border: 1px solid #2d3442; }
        .wallet-box span { color: #4caf50; font-weight: bold; }
        .history-bar { display: flex; gap: 6px; overflow-x: auto; margin-bottom: 10px; padding-bottom: 4px; scrollbar-width: none; }
        .history-pill { background: #1f242d; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600; color: #4caf50; white-space: nowrap; }
        .game-screen { width: 100%; height: 200px; background: radial-gradient(circle at center, #251025 0%, #0d1117 100%); border-radius: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; overflow: hidden; border: 1px solid #252b36; margin-bottom: 12px; }
        .multiplier-text { font-size: 42px; font-weight: 900; z-index: 2; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
        .plane-container { position: absolute; font-size: 36px; z-index: 1; transition: transform 0.05s linear; }
        .status-msg { font-size: 12px; color: #8c929d; margin-top: 4px; z-index: 2; }
        .bet-card { background: #1b202a; border-radius: 10px; padding: 10px; margin-bottom: 10px; border: 1px solid #252b36; }
        .bet-body { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
        .bet-controls { display: flex; flex-direction: column; gap: 6px; flex: 1; }
        .input-row { display: flex; align-items: center; background: #12151c; border: 1px solid #2d3442; border-radius: 6px; padding: 4px 8px; }
        .input-row input { background: none; border: none; color: white; width: 100%; font-size: 15px; font-weight: bold; text-align: center; outline: none; }
        .quick-chips { display: flex; gap: 4px; }
        .chip { background: #252b36; border: none; color: #b0bec5; font-size: 10px; padding: 3px 6px; border-radius: 4px; cursor: pointer; flex: 1; }
        .action-btn { width: 110px; height: 65px; border: none; border-radius: 8px; font-size: 15px; font-weight: 900; cursor: pointer; text-transform: uppercase; display: flex; flex-direction: column; justify-content: center; align-items: center; }
        .btn-bet-style { background-color: #2e7d32; color: white; }
        .btn-cash-style { background-color: #ef6c00; color: white; }
        .action-btn:disabled { background-color: #2d3442; color: #6c757d; cursor: not-allowed; }
    </style>
</head>
<body>

<div class="main-container">
    <div class="top-header">
        <div class="brand-title">Aviator Pro</div>
        <div class="wallet-box">
            💰 <span id="balanceDisplay">{{ balance }}</span> XU
        </div>
    </div>

    <div class="history-bar" id="historyBar">
        {% for h in history %}
        <div class="history-pill">{{ "%.2f"|format(h.multiplier) }}x</div>
        {% endfor %}
    </div>

    <div class="game-screen">
        <div class="plane-container" id="planeIcon">✈️</div>
        <div class="multiplier-text" id="multiplierView">1.00x</div>
        <div class="status-msg" id="statusView">Đang chờ cược...</div>
    </div>

    <div class="bet-card">
        <div class="bet-body">
            <div class="bet-controls">
                <div class="input-row">
                    <input type="number" id="betInput" value="100" min="10">
                </div>
                <div class="quick-chips">
                    <button class="chip" onclick="setBet(50)">50</button>
                    <button class="chip" onclick="setBet(100)">100</button>
                    <button class="chip" onclick="setBet(500)">500</button>
                    <button class="chip" onclick="setBet(1000)">1000</button>
                </div>
            </div>
            <button id="mainBtn" class="action-btn btn-bet-style" onclick="handleAction()">CƯỢC</button>
        </div>
    </div>
</div>

<script>
    let balance = parseFloat("{{ balance }}");
    let gameState = 'IDLE'; 
    let currentMultiplier = 1.00;
    let crashPoint = 1.00;
    let gameTimer = null;
    let isBetPlaced = false;
    let betAmount = 0;
    let isCashedOut = false;

    function setBet(val) {
        if (gameState === 'IDLE') document.getElementById('betInput').value = val;
    }

    function updateBalanceUI() {
        document.getElementById('balanceDisplay').innerText = balance.toFixed(2);
    }

    function handleAction() {
        let inputEl = document.getElementById('betInput');
        let btnEl = document.getElementById('mainBtn');
        let amount = parseFloat(inputEl.value);

        if (gameState === 'IDLE' || gameState === 'WAITING') {
            if (amount > balance) { alert('Không đủ xu!'); return; }
            
            fetch('/place_bet', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({amount: amount})
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    balance = data.balance;
                    updateBalanceUI();
                    betAmount = amount;
                    isBetPlaced = true;
                    isCashedOut = false;

                    inputEl.disabled = true;
                    btnEl.className = 'action-btn btn-cash-style';
                    btnEl.innerHTML = `HỦY<br><span style="font-size:11px;">CƯỢC</span>`;

                    if (gameState === 'IDLE') startCountdown();
                }
            });
        } else if (gameState === 'RUNNING' && isBetPlaced && !isCashedOut) {
            isCashedOut = true;
            let winAmt = betAmount * currentMultiplier;

            fetch('/cash_out', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({win_amount: winAmt})
            }).then(res => res.json()).then(data => {
                balance = data.balance;
                updateBalanceUI();
                btnEl.className = 'action-btn';
                btnEl.style.backgroundColor = '#1f242d';
                btnEl.style.color = '#4caf50';
                btnEl.innerHTML = `ĐÃ RÚT<br><span style="font-size:10px;">+${winAmt.toFixed(0)}</span>`;
            });
        }
    }

    function startCountdown() {
        gameState = 'WAITING';
        document.getElementById('statusView').innerText = 'Chuẩn bị cất cánh...';
        let count = 3;
        let c = setInterval(() => {
            document.getElementById('statusView').innerText = `Cất cánh sau ${count}s...`;
            count--;
            if(count < 0) { clearInterval(c); startFlight(); }
        }, 600);
    }

    function startFlight() {
        gameState = 'RUNNING';
        document.getElementById('statusView').innerText = 'Máy bay đang bay!';
        if (isBetPlaced && !isCashedOut) {
            document.getElementById('mainBtn').className = 'action-btn btn-cash-style';
        }

        crashPoint = (Math.random() < 0.05) ? 1.00 : parseFloat((1.01 + Math.pow(Math.random(), 2) * 9).toFixed(2));
        let startTime = Date.now();

        gameTimer = setInterval(() => {
            let elapsed = (Date.now() - startTime) / 1000;
            currentMultiplier = 1.00 + elapsed * 0.35 + Math.pow(elapsed, 1.4) * 0.12;

            if (currentMultiplier >= crashPoint) {
                currentMultiplier = crashPoint;
                triggerCrash();
            } else {
                document.getElementById('multiplierView').innerText = currentMultiplier.toFixed(2) + 'x';
                if (isBetPlaced && !isCashedOut) {
                    document.getElementById('mainBtn').innerHTML = `RÚT<br><span style="font-size:12px;">${(betAmount * currentMultiplier).toFixed(0)}</span>`;
                }
            }
        }, 50);
    }

    function triggerCrash() {
        clearInterval(gameTimer);
        gameState = 'CRASHED';
        document.getElementById('multiplierView').innerText = crashPoint.toFixed(2) + 'x';
        document.getElementById('statusView').innerText = '💥 Máy bay đã nổ!';

        if (isBetPlaced && !isCashedOut) {
            let btn = document.getElementById('mainBtn');
            btn.className = 'action-btn';
            btn.style.backgroundColor = '#b71c1c';
            btn.innerText = 'THUA';
        }

        fetch('/save_game', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({multiplier: crashPoint})
        }).then(() => {
            setTimeout(() => location.reload(), 3000);
        });
    }
</script>
</body>
</html>
"""

@app.route('/')
def index():
    user = User.query.filter_by(username="player1").first()
    history = GameHistory.query.order_by(GameHistory.id.desc()).limit(8).all()
    return render_template_string(HTML_TEMPLATE, balance=user.balance, history=history)

@app.route('/place_bet', methods=['POST'])
def place_bet():
    data = request.json
    amount = data.get('amount', 0)
    user = User.query.filter_by(username="player1").first()
    if user.balance >= amount:
        user.balance -= amount
        db.session.commit()
        return jsonify(success=True, balance=user.balance)
    return jsonify(success=False)

@app.route('/cash_out', methods=['POST'])
def cash_out():
    data = request.json
    win_amount = data.get('win_amount', 0)
    user = User.query.filter_by(username="player1").first()
    user.balance += win_amount
    db.session.commit()
    return jsonify(balance=user.balance)

@app.route('/save_game', methods=['POST'])
def save_game():
    data = request.json
    mul = data.get('multiplier', 1.0)
    new_h = GameHistory(multiplier=mul)
    db.session.add(new_h)
    db.session.commit()
    return jsonify(success=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
