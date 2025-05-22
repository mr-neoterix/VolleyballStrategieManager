const canvas = document.getElementById('field');
const ctx = canvas.getContext('2d');
let players = [];
let ball = null;
let dragging = null;
let offsetX = 0;
let offsetY = 0;

function drawField() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000';
    ctx.strokeRect(0, 0, canvas.width, canvas.height);

    players.forEach(p => {
        ctx.beginPath();
        ctx.fillStyle = '#007acc';
        ctx.arc(p.x, p.y, 15, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(p.name, p.x, p.y);
    });

    if (ball) {
        ctx.beginPath();
        ctx.fillStyle = '#e63946';
        ctx.arc(ball.x, ball.y, 10, 0, Math.PI * 2);
        ctx.fill();
    }
}

function loadData() {
    fetch('/api/formations')
        .then(r => r.json())
        .then(data => {
            if (data.length > 0) {
                const f = data[0];
                ball = { x: f.ball[0], y: f.ball[1] };
                players = f.offsets.map((o, i) => ({
                    x: ball.x + o[0],
                    y: ball.y + o[1],
                    name: 'P' + (i + 1)
                }));
                drawField();
            }
        });
}

canvas.addEventListener('mousedown', startDrag);
canvas.addEventListener('touchstart', e => startDrag(e.touches[0]));
canvas.addEventListener('mousemove', moveDrag);
canvas.addEventListener('touchmove', e => { e.preventDefault(); moveDrag(e.touches[0]); });
canvas.addEventListener('mouseup', endDrag);
canvas.addEventListener('touchend', endDrag);

function startDrag(e) {
    const x = e.offsetX;
    const y = e.offsetY;
    players.forEach(p => {
        if (Math.hypot(p.x - x, p.y - y) < 20) {
            dragging = p;
            offsetX = x - p.x;
            offsetY = y - p.y;
        }
    });
}

function moveDrag(e) {
    if (!dragging) return;
    dragging.x = e.offsetX - offsetX;
    dragging.y = e.offsetY - offsetY;
    drawField();
}

function endDrag() {
    dragging = null;
}

loadData();
