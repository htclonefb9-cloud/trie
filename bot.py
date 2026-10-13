import os
import random
from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.Float, default=10000.0)

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aviator - Hoang Trieu Pro (1000x Edition)</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b0e14; color: #ffffff; display: flex; justify-content: center; padding: 6px; }
        .main-container { width: 100%; max-width: 420px; background: #12151c; border-radius: 12px; padding: 10px; box-shadow: 0 4px 25px rgba(0,0,0,0.8); }
        
        .top-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; border-bottom: 1px solid #1f242d; padding-bottom: 8px; }
        .brand-logo-area { display: flex; align-items: center; gap: 6px; }
        .site-brand { color: #4caf50; font-size: 18px; font-weight: 900; }
        .aviator-logo { color: #e53935; font-size: 16px; font-weight: 900; font-style: italic; }
        
        .wallet-actions { display: flex; gap: 6px; align-items: center; }
        .wallet-display { background: #1f242d; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; border: 1px solid #2d3442; color: #4caf50; }
        .mini-btn { background: #2196F3; color: white; border: none; padding: 4px 8px; border-radius: 6px; font-size: 10px; font-weight: bold; cursor: pointer; }
        .mini-btn.withdraw { background: #ff9800; }

        .history-bar { display: flex; gap: 6px; overflow-x: auto; margin-bottom: 8px; padding-bottom: 4px; scrollbar-width: none; }
        .history-bar::-webkit-scrollbar { display: none; }
        .history-pill { background: #1a1f29; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; color: #4caf50; white-space: nowrap; border: 1px solid #262c38; }

        .game-screen { width: 100%; height: 200px; background: radial-gradient(circle at center, #2e1028 0%, #0d1117 100%); border-radius: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; overflow: hidden; border: 1px solid #252b36; margin-bottom: 10px; }
        .multiplier-text { font-size: 42px; font-weight: 900; z-index: 2; color: #ffffff; text-shadow: 0 2px 12px rgba(0,0,0,0.7); }
        .plane-container { position: absolute; font-size: 36px; z-index: 1; transition: transform 0.05s linear; transform: rotate(15deg); }
        .status-msg { font-size: 11px; color: #8c929d; margin-top: 2px; z-index: 2; text-transform: uppercase; }
        .red-line { position: absolute; bottom: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(45deg, rgba(229, 57, 53, 0.3) 0%, transparent 60%); z-index: 1; pointer-events: none; }

        .bet-card { background: #171b24; border-radius: 10px; padding: 8px; margin-bottom: 8px; border: 1px solid #212836; }
        .bet-tabs { display: flex; background: #0f1218; border-radius: 6px; padding: 2px; margin-bottom: 6px; width: fit-content; }
        .tab-btn { background: none; border: none; color: #8c929d; font-size: 10px; padding: 3px 8px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .tab-btn.active { background: #212836; color: white; }

        .bet-body { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
        .bet-controls { display: flex; flex-direction: column; gap: 5px; flex: 1; }
        
        .input-row { display: flex; align-items: center; background: #0f1218; border: 1px solid #262c38; border-radius: 6px; padding: 3px 6px; justify-content: space-between; }
        .input-row input { background: none; border: none; color: white; width: 70px; font-size: 14px; font-weight: bold; text-align: left; outline: none; }
        .step-btn { background: #212836; color: #b0bec5; border: none; width: 18px; height: 18px; border-radius: 50%; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 11px; }

        .quick-chips { display: flex; gap: 3px; }
        .chip { background: #212836; border: none; color: #b0bec5; font-size: 9px; padding: 3px 2px; border-radius: 4px; cursor: pointer; flex: 1; font-weight: 600; text-align: center; }
        .chip:hover { background: #2d3646; color: #fff; }

        .action-btn { width: 110px; height: 55px; border: none; border-radius: 8px; font-size: 13px; font-weight: 900; cursor: pointer; text-transform: uppercase; display: flex; flex-direction: column; justify-content: center; align-items: center; line-height: 1.2; box-shadow: 0 4px 10px rgba(0,0,0,0.3); transition: 0.1s; }
        .btn-bet-style { background-color: #2e7d32; color: white; }
        .btn-cash-style { background-color: #ef6c00; color: white; }
        .action-btn:disabled { background-color: #212836; color: #5c6370; cursor: not-allowed; box-shadow: none; }
    </style>
</head>
<body>

<div class="main-container">
    <div class="top-header">
        <div class="brand-logo-area">
            <span class="site-brand">Hoang Trieu</span>
            <span class="aviator-logo">Aviator</span>
        </div>
        <div class="wallet-actions">
            <div class="wallet-display">💰 <span id="balanceDisplay">{{ balance }}</span></div>
            <button class="mini-btn" onclick="openDeposit()">Nạp</button>
            <button class="mini-btn withdraw" onclick="openWithdraw()">Rút</button>
        </div>
    </div>

    <div class="history-bar" id="historyBar">
        {% for h in history %}
        <div class="history-pill">{{ "%.2f"|format(h.multiplier) }}x</div>
        {% endfor %}
    </div>

    <div class="game-screen">
        <div class="red-line"></div>
        <div class="plane-container" id="planeIcon">✈️</div>
        <div class="multiplier-text" id="multiplierView">1.00x</div>
        <div class="status-msg" id="statusView">Đang chờ cược...</div>
    </div>

    <!-- Bảng Cược 1 -->
    <div class="bet-card">
        <div class="bet-tabs"><button class="tab-btn active">Cược 1</button></div>
        <div class="bet-body">
            <div class="bet-controls">
                <div class="input-row">
                    <button class="step-btn" onclick="adjustBet(1, -50)">-</button>
                    <input type="number" id="betInput1" value="100" min="10">
                    <button class="step-btn" onclick="adjustBet(1, 50)">+</button>
                </div>
                <div class="quick-chips">
                    <button class="chip" onclick="setBet(1, 50)">50</button>
                    <button class="chip" onclick="setBet(1, 100)">100</button>
                    <button class="chip" onclick="setBet(1, 500)">500</button>
                    <button class="chip" onclick="setBet(1, 1000)">1000</button>
                </div>
            </div>
            <button id="mainBtn1" class="action-btn btn-bet-style" onclick="toggleBet(1)">CƯỢC</button>
        </div>
    </div>

    <!-- Bảng Cược 2 -->
    <div class="bet-card">
        <div class="bet-tabs"><button class="tab-btn active">Cược 2</button></div>
        <div class="bet-body">
            <div class="bet-controls">
                <div class="input-row">
                    <button class="step-btn" onclick="adjustBet(2, -50)">-</button>
                    <input type="number" id="betInput2" value="100" min="10">
                    <button class="step-btn" onclick="adjustBet(2, 50)">+</button>
                </div>
                <div class="quick-chips">
                    <button class="chip" onclick="setBet(2, 50)">50</button>
                    <button class="chip" onclick="setBet(2, 100)">100</button>
                    <button class="chip" onclick="setBet(2, 500)">500</button>
                    <button class="chip" onclick="setBet(2, 1000)">1000</button>
                </div>
            </div>
            <button id="mainBtn2" class="action-btn btn-bet-style" onclick="toggleBet(2)">CƯỢC</button>
        </div>
    </div>
</div>

<script>
    let balance = parseFloat("{{ balance }}");
    let gameState = 'IDLE'; 
    let currentMultiplier = 1.00;
    let crashPoint = 1.00;
    let gameTimer = null;

    let bets = {
        1: { active: false, amount: 0, cashedOut: false },
        2: { active: false, amount: 0, cashedOut: false }
    };

    function setBet(slot, val) {
        if (gameState === 'IDLE' || gameState === 'WAITING') {
            document.getElementById(`betInput${slot}`).value = val;
        }
    }

    function adjustBet(slot, delta) {
        if (gameState === 'IDLE' || gameState === 'WAITING') {
            let inputEl = document.getElementById(`betInput${slot}`);
            inputEl.value = Math.max(10, parseInt(inputEl.value) + delta);
        }
    }

    function updateBalanceUI() {
        document.getElementById('balanceDisplay').innerText = balance.toFixed(2);
    }

    function openDeposit() {
        let amt = prompt("Nhập số xu muốn nạp thêm:", "5000");
        if (amt && !isNaN(amt)) {
            fetch('/update_balance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'deposit', amount: parseFloat(amt)})
            }).then(res => res.json()).then(data => {
                balance = data.balance;
                updateBalanceUI();
                alert(`Đã nạp thành công ${amt} xu!`);
            });
        }
    }

    function openWithdraw() {
        let amt = prompt("Nhập số xu muốn rút:", "1000");
        if (amt && !isNaN(amt)) {
            fetch('/update_balance', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: 'withdraw', amount: parseFloat(amt)})
            }).then(res => res.json()).then(data => {
                if(data.success) {
                    balance = data.balance;
                    updateBalanceUI();
                    alert(`Đã rút thành công ${amt} xu!`);
                } else {
                    alert('Số dư không đủ để rút!');
                }
            });
        }
    }

    function toggleBet(slot) {
        let inputEl = document.getElementById(`betInput${slot}`);
        let btnEl = document.getElementById(`mainBtn${slot}`);
        let amount = parseFloat(inputEl.value);

        if (gameState === 'IDLE' || gameState === 'WAITING') {
            if (!bets[slot].active) {
                if (amount > balance) { alert('Không đủ xu!'); return; }
                
                fetch('/place_bet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({amount: amount})
                }).then(res => res.json()).then(data => {
                    if(data.success) {
                        balance = data.balance;
                        updateBalanceUI();
                        bets[slot].amount = amount;
                        bets[slot].active = true;
                        bets[slot].cashedOut = false;

                        inputEl.disabled = true;
                        btnEl.className = 'action-btn btn-cash-style';
                        btnEl.innerHTML = `HỦY<br><span style="font-size:10px;">CƯỢC</span>`;

                        if (gameState === 'IDLE') startCountdown();
                    }
                });
            } else {
                fetch('/refund_bet', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({amount: bets[slot].amount})
                }).then(res => res.json()).then(data => {
                    balance = data.balance;
                    updateBalanceUI();
                    bets[slot].active = false;

                    inputEl.disabled = false;
                    btnEl.className = 'action-btn btn-bet-style';
                    btnEl.innerText = 'CƯỢC';
                });
            }
        } else if (gameState === 'RUNNING' && bets[slot].active && !bets[slot].cashedOut) {
            bets[slot].cashedOut = true;
            let winAmt = bets[slot].amount * currentMultiplier;

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
        
        for (let i = 1; i <= 2; i++) {
            if (bets[i].active && !bets[i].cashedOut) {
                document.getElementById(`mainBtn${i}`).className = 'action-btn btn-cash-style';
            }
        }

        // Cập nhật khoảng nhân từ 1x đến 1000x
        let rand = Math.random();
        if (rand < 0.02) {
            crashPoint = 1.00;
        } else {
            crashPoint = parseFloat((1.01 + Math.pow(Math.random(), 4) * 999).toFixed(2));
            if (crashPoint > 1000) crashPoint = 1000.00;
        }

        let startTime = Date.now();

        gameTimer = setInterval(() => {
            let elapsed = (Date.now() - startTime) / 1000;
            // Cho phép hệ số tăng mượt mà theo thời gian để có cơ hội đạt tới 1000x nếu ván đó siêu cao
            currentMultiplier = 1.00 + elapsed * 0.4 + Math.pow(elapsed, 1.8) * 0.15;
            if (currentMultiplier > crashPoint) currentMultiplier = crashPoint;

            if (currentMultiplier >= crashPoint) {
                currentMultiplier = crashPoint;
                triggerCrash();
            } else {
                document.getElementById('multiplierView').innerText = currentMultiplier.toFixed(2) + 'x';
                
                for (let i = 1; i <= 2; i++) {
                    if (bets[i].active && !bets[i].cashedOut) {
                        let liveWin = (bets[i].amount * currentMultiplier).toFixed(0);
                        document.getElementById(`mainBtn${i}`).innerHTML = `RÚT<br><span style="font-size:11px;">${liveWin}</span>`;
                    }
                }
                
                let px = Math.min(elapsed * 12, 110);
                let py = Math.min(elapsed * 8, 55);
                document.getElementById('planeIcon').style.transform = `translate(${px}px, -${py}px) rotate(15deg)`;
            }
        }, 50);
    }

    function triggerCrash() {
        clearInterval(gameTimer);
        gameState = 'CRASHED';
        document.getElementById('multiplierView').innerText = crashPoint.toFixed(2) + 'x';
        document.getElementById('statusView').innerText = '💥 Máy bay đã bay đi!';

        for (let i = 1; i <= 2; i++) {
            if (bets[i].active && !bets[i].cashedOut) {
                let btn = document.getElementById(`mainBtn${i}`);
                btn.className = 'action-btn'; 
                btn.style.backgroundColor = '#b71c1c'; 
                btn.innerText = 'THUA';
            }
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

@app.route('/refund_bet', methods=['POST'])
def refund_bet():
    data = request.json
    amount = data.get('amount', 0)
    user = User.query.filter_by(username="player1").first()
    user.balance += amount
    db.session.commit()
    return jsonify(balance=user.balance)

@app.route('/cash_out', methods=['POST'])
def cash_out():
    data = request.json
    win_amount = data.get('win_amount', 0)
    user = User.query.filter_by(username="player1").first()
    user.balance += win_amount
    db.session.commit()
    return jsonify(balance=user.balance)

@app.route('/update_balance', methods=['POST'])
def update_balance():
    data = request.json
    action = data.get('action')
    amount = data.get('amount', 0)
    user = User.query.filter_by(username="player1").first()
    
    if action == 'deposit':
        user.balance += amount
        db.session.commit()
        return jsonify(success=True, balance=user.balance)
    elif action == 'withdraw':
        if user.balance >= amount:
            user.balance -= amount
            db.session.commit()
            return jsonify(success=True, balance=user.balance)
        return jsonify(success=False)
    return jsonify(success=False)

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
