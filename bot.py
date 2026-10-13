import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aviator Fun - Giải Trí Điểm Vô Trị</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        body {
            background-color: #0b0e14;
            color: #ffffff;
            display: flex;
            justify-content: center;
            padding: 10px;
        }
        .main-container {
            width: 100%;
            max-width: 420px;
            background: #141820;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.7);
        }
        /* Header */
        .top-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .brand-title {
            color: #e53935;
            font-size: 22px;
            font-weight: 900;
            font-style: italic;
            letter-spacing: 0.5px;
        }
        .wallet-box {
            background: #1f242d;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 5px;
            border: 1px solid #2d3442;
        }
        .wallet-box span {
            color: #4caf50;
            font-weight: bold;
        }

        /* History bar */
        .history-bar {
            display: flex;
            gap: 6px;
            overflow-x: auto;
            margin-bottom: 10px;
            padding-bottom: 4px;
            scrollbar-width: none;
        }
        .history-bar::-webkit-scrollbar { display: none; }
        .history-pill {
            background: #1f242d;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            color: #4caf50;
            white-space: nowrap;
        }

        /* Game Screen */
        .game-screen {
            width: 100%;
            height: 200px;
            background: radial-gradient(circle at center, #251025 0%, #0d1117 100%);
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
            overflow: hidden;
            border: 1px solid #252b36;
            margin-bottom: 12px;
        }
        .multiplier-text {
            font-size: 42px;
            font-weight: 900;
            z-index: 2;
            letter-spacing: 1px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .plane-container {
            position: absolute;
            font-size: 36px;
            z-index: 1;
            transition: transform 0.05s linear;
        }
        .status-msg {
            font-size: 12px;
            color: #8c929d;
            margin-top: 4px;
            z-index: 2;
        }

        /* Betting Panels */
        .bet-card {
            background: #1b202a;
            border-radius: 10px;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #252b36;
        }
        .bet-tabs {
            display: flex;
            background: #12151c;
            border-radius: 6px;
            padding: 2px;
            margin-bottom: 8px;
            width: fit-content;
        }
        .tab-btn {
            background: none;
            border: none;
            color: #8c929d;
            font-size: 11px;
            padding: 4px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        .tab-btn.active {
            background: #252b36;
            color: white;
        }
        .bet-body {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        .bet-controls {
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1;
        }
        .input-row {
            display: flex;
            align-items: center;
            background: #12151c;
            border: 1px solid #2d3442;
            border-radius: 6px;
            padding: 4px 8px;
        }
        .input-row input {
            background: none;
            border: none;
            color: white;
            width: 100%;
            font-size: 15px;
            font-weight: bold;
            text-align: center;
            outline: none;
        }
        .quick-chips {
            display: flex;
            gap: 4px;
        }
        .chip {
            background: #252b36;
            border: none;
            color: #b0bec5;
            font-size: 10px;
            padding: 3px 6px;
            border-radius: 4px;
            cursor: pointer;
            flex: 1;
        }
        .chip:hover { background: #323a4a; }
        
        .action-btn {
            width: 110px;
            height: 65px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 900;
            cursor: pointer;
            transition: 0.1s;
            text-transform: uppercase;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            line-height: 1.2;
        }
        .btn-bet-style {
            background-color: #2e7d32;
            color: white;
        }
        .btn-bet-style:hover { background-color: #388e3c; }
        
        .btn-cash-style {
            background-color: #ef6c00;
            color: white;
        }
        .btn-cash-style:hover { background-color: #f57c00; }
        
        .action-btn:disabled {
            background-color: #2d3442;
            color: #6c757d;
            cursor: not-allowed;
        }
    </style>
</head>
<body>

<div class="main-container">
    <!-- Header -->
    <div class="top-header">
        <div class="brand-title">Aviator</div>
        <div class="wallet-box">
            💰 <span id="balanceDisplay">10,000.00</span> XU
        </div>
    </div>

    <!-- Lịch sử hệ số -->
    <div class="history-bar" id="historyBar">
        <div class="history-pill" style="color: #90caf9;">2.15x</div>
        <div class="history-pill" style="color: #4caf50;">5.09x</div>
        <div class="history-pill" style="color: #ce93d8;">24.25x</div>
    </div>

    <!-- Màn hình game -->
    <div class="game-screen">
        <div class="plane-container" id="planeIcon">✈️</div>
        <div class="multiplier-text" id="multiplierView">1.00x</div>
        <div class="status-msg" id="statusView">Đang chờ cược...</div>
    </div>

    <!-- Bảng Cược 1 -->
    <div class="bet-card">
        <div class="bet-tabs">
            <button class="tab-btn active">Cược</button>
            <button class="tab-btn">Tự động</button>
        </div>
        <div class="bet-body">
            <div class="bet-controls">
                <div class="input-row">
                    <input type="number" id="betInput1" value="100" min="10">
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
        <div class="bet-tabs">
            <button class="tab-btn active">Cược</button>
            <button class="tab-btn">Tự động</button>
        </div>
        <div class="bet-body">
            <div class="bet-controls">
                <div class="input-row">
                    <input type="number" id="betInput2" value="100" min="10">
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
    let balance = 10000.00;
    let gameState = 'IDLE'; 
    let currentMultiplier = 1.00;
    let crashPoint = 1.00;
    let gameTimer = null;

    let bets = {
        1: { active: false, amount: 0, cashedOut: false },
        2: { active: false, amount: 0, cashedOut: false }
    };

    const balanceDisplay = document.getElementById('balanceDisplay');
    const multiplierView = document.getElementById('multiplierView');
    const statusView = document.getElementById('statusView');
    const planeIcon = document.getElementById('planeIcon');
    const historyBar = document.getElementById('historyBar');

    function updateUI() {
        balanceDisplay.innerText = balance.toFixed(2);
    }

    function setBet(slot, val) {
        if (gameState === 'IDLE' || gameState === 'WAITING') {
            document.getElementById(`betInput${slot}`).value = val;
        }
    }

    function toggleBet(slot) {
        let inputEl = document.getElementById(`betInput${slot}`);
        let btnEl = document.getElementById(`mainBtn${slot}`);
        let amount = parseFloat(inputEl.value);

        if (gameState === 'IDLE' || gameState === 'WAITING') {
            if (isNaN(amount) || amount <= 0) {
                alert('Số tiền cược không hợp lệ!');
                return;
            }
            if (amount > balance && !bets[slot].active) {
                alert('Không đủ số dư xu ảo!');
                return;
            }

            if (!bets[slot].active) {
                balance -= amount;
                bets[slot].amount = amount;
                bets[slot].active = true;
                bets[slot].cashedOut = false;
                updateUI();

                inputEl.disabled = true;
                btnEl.className = 'action-btn btn-cash-style';
                btnEl.innerHTML = `HỦY<br><span style="font-size:11px;">CƯỢC</span>`;

                if (gameState === 'IDLE') {
                    startCountdown();
                }
            } else {
                balance += bets[slot].amount;
                bets[slot].active = false;
                updateUI();

                inputEl.disabled = false;
                btnEl.className = 'action-btn btn-bet-style';
                btnEl.innerText = 'CƯỢC';
            }
        } else if (gameState === 'RUNNING' && bets[slot].active && !bets[slot].cashedOut) {
            bets[slot].cashedOut = true;
            let winAmt = bets[slot].amount * currentMultiplier;
            balance += winAmt;
            updateUI();

            btnEl.className = 'action-btn';
            btnEl.style.backgroundColor = '#1f242d';
            btnEl.style.color = '#4caf50';
            btnEl.innerHTML = `ĐÃ RÚT<br><span style="font-size:10px;">+${winAmt.toFixed(0)}</span>`;
        }
    }

    function startCountdown() {
        gameState = 'WAITING';
        statusView.innerText = 'Đang chuẩn bị cất cánh...';
        currentMultiplier = 1.00;
        multiplierView.innerText = '1.00x';
        planeIcon.style.transform = 'translate(0px, 0px)';

        let count = 3;
        let cInterval = setInterval(() => {
            statusView.innerText = `Cất cánh sau ${count}s...`;
            count--;
            if (count < 0) {
                clearInterval(cInterval);
                startFlight();
            }
        }, 600);
    }

    function startFlight() {
        gameState = 'RUNNING';
        statusView.innerText = 'Máy bay đang bay!';
        
        for (let i = 1; i <= 2; i++) {
            if (bets[i].active && !bets[i].cashedOut) {
                let btnEl = document.getElementById(`mainBtn${i}`);
                btnEl.className = 'action-btn btn-cash-style';
            }
        }

        let r = Math.random();
        crashPoint = (r < 0.05) ? 1.00 : parseFloat((1.01 + Math.pow(Math.random(), 2) * 9).toFixed(2));

        let startTime = Date.now();
        gameTimer = setInterval(() => {
            let elapsed = (Date.now() - startTime) / 1000;
            currentMultiplier = 1.00 + elapsed * 0.35 + Math.pow(elapsed, 1.4) * 0.12;

            if (currentMultiplier >= crashPoint) {
                currentMultiplier = crashPoint;
                triggerCrash();
            } else {
                multiplierView.innerText = currentMultiplier.toFixed(2) + 'x';
                
                for (let i = 1; i <= 2; i++) {
                    if (bets[i].active && !bets[i].cashedOut) {
                        let btnEl = document.getElementById(`mainBtn${i}`);
                        let currentWin = bets[i].amount * currentMultiplier;
                        btnEl.innerHTML = `RÚT<br><span style="font-size:12px;">${currentWin.toFixed(0)}</span>`;
                    }
                }

                let px = Math.min(elapsed * 12, 100);
                let py = Math.min(elapsed * 8, 50);
                planeIcon.style.transform = `translate(${px}px, -${py}px)`;
            }
        }, 50);
    }

    function triggerCrash() {
        clearInterval(gameTimer);
        gameState = 'CRASHED';
        multiplierView.innerText = crashPoint.toFixed(2) + 'x';
        statusView.innerText = '💥 Máy bay đã bay đi!';

        for (let i = 1; i <= 2; i++) {
            let btnEl = document.getElementById(`mainBtn${i}`);
            if (bets[i].active && !bets[i].cashedOut) {
                btnEl.className = 'action-btn';
                btnEl.style.backgroundColor = '#b71c1c';
                btnEl.style.color = 'white';
                btnEl.innerText = 'THUA';
            }
        }

        addHistory(crashPoint);
        setTimeout(resetGame, 3500);
    }

    function resetGame() {
        gameState = 'IDLE';
        statusView.innerText = 'Đang chờ cược...';
        multiplierView.innerText = '1.00x';
        planeIcon.style.transform = 'translate(0px, 0px)';

        for (let i = 1; i <= 2; i++) {
            bets[i].active = false;
            bets[i].cashedOut = false;
            let btnEl = document.getElementById(`mainBtn${i}`);
            let inputEl = document.getElementById(`betInput${i}`);
            
            inputEl.disabled = false;
            btnEl.className = 'action-btn btn-bet-style';
            btnEl.style.backgroundColor = '';
            btnEl.style.color = 'white';
            btnEl.innerText = 'CƯỢC';
        }

        if (balance <= 0) {
            balance = 5000;
            updateUI();
            alert('Hết xu! Hệ thống đã tặng thêm 5,000 xu để bạn tiếp tục giải trí.');
        }
    }

    function addHistory(val) {
        const pill = document.createElement('div');
        pill.className = 'history-pill';
        pill.innerText = val.toFixed(2) + 'x';
        if (val >= 5.0) pill.style.color = '#ce93d8';
        else if (val < 2.0) pill.style.color = '#90caf9';
        
        historyBar.prepend(pill);
        if (historyBar.children.length > 7) {
            historyBar.lastChild.remove();
        }
    }
</script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    # Đọc trực tiếp cổng từ môi trường hệ thống của Bot-Hosting cấp phát động
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
