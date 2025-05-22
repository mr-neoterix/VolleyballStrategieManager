const canvas = document.getElementById('field');
const ctx = canvas.getContext('2d');
let players = [];
let ball = null;
let dragging = null;
let offsetX = 0;
let offsetY = 0;
let markers = [];
let formations = [];
let teams = [];

function drawField() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#000';
    ctx.strokeRect(0, 0, canvas.width, canvas.height);

    // formation markers
    markers.forEach(m => {
        ctx.beginPath();
        ctx.strokeStyle = '#ff8800';
        ctx.arc(m.x, m.y, 5, 0, Math.PI * 2);
        ctx.stroke();
    });

    // attack sector (simple triangle to bottom net)
    if (ball) {
        ctx.beginPath();
        ctx.fillStyle = 'rgba(255,0,0,0.3)';
        const netY = canvas.height / 2;
        ctx.moveTo(ball.x, ball.y);
        ctx.lineTo(0, netY);
        ctx.lineTo(canvas.width, netY);
        ctx.closePath();
        ctx.fill();
    }

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
    Promise.all([
        fetch('/api/formations').then(r => r.json()),
        fetch('/api/teams').then(r => r.json())
    ]).then(([fData, tData]) => {
        formations = fData;
        teams = tData;
        const formList = document.getElementById('formations');
        formList.innerHTML = '';
        markers = [];
        formations.forEach((f, idx) => {
            const li = document.createElement('li');
            li.textContent = f.name || 'Formation ' + (idx + 1);
            li.onclick = () => applyFormation(idx);
            formList.appendChild(li);
            markers.push({x: f.ball[0], y: f.ball[1]});
        });

        const teamList = document.getElementById('teams');
        teamList.innerHTML = '';
        teams.forEach((t, idx) => {
            const li = document.createElement('li');
            li.textContent = t.name || 'Team ' + (idx + 1);
            li.onclick = () => applyTeam(idx);
            teamList.appendChild(li);
        });

        if (formations.length > 0) {
            applyFormation(0);
        } else {
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
    if (ball && Math.hypot(ball.x - x, ball.y - y) < 15) {
        dragging = ball;
        offsetX = x - ball.x;
        offsetY = y - ball.y;
    } else {
        players.forEach(p => {
            if (Math.hypot(p.x - x, p.y - y) < 20) {
                dragging = p;
                offsetX = x - p.x;
                offsetY = y - p.y;
            }
        });
    }
}

function moveDrag(e) {
    if (!dragging) return;
    dragging.x = e.offsetX - offsetX;
    dragging.y = e.offsetY - offsetY;
    if (dragging === ball) {
        markers.forEach((m, idx) => {
            if (Math.hypot(dragging.x - m.x, dragging.y - m.y) < 15) {
                applyFormation(idx);
            }
        });
    }
    drawField();
}

function endDrag() {
    dragging = null;
}

function applyFormation(idx) {
    const f = formations[idx];
    ball = { x: f.ball[0], y: f.ball[1] };
    players = f.offsets.map((o, i) => ({
        x: ball.x + o[0],
        y: ball.y + o[1],
        name: f.names ? f.names[i] : 'P' + (i + 1)
    }));
    drawField();
}

function applyTeam(idx) {
    const t = teams[idx];
    players.forEach((p, i) => {
        if (i < t.player_names.length) {
            p.name = t.player_names[i];
        }
    });
    drawField();
}

function saveCurrentFormation() {
    if (!ball) return;
    const formation = {
        name: prompt('Name der Stellung?') || 'Neue Stellung',
        ball: [ball.x, ball.y],
        offsets: players.map(p => [p.x - ball.x, p.y - ball.y]),
        names: players.map(p => p.name)
    };
    fetch('/api/formations', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(formation)
    }).then(() => location.reload());
}

function saveCurrentTeam() {
    const team = {
        name: prompt('Teamname?') || 'Neues Team',
        player_names: players.map(p => p.name)
    };
    fetch('/api/teams', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(team)
    }).then(() => location.reload());
}

document.getElementById('saveFormation').onclick = saveCurrentFormation;
document.getElementById('saveTeam').onclick = saveCurrentTeam;

loadData();
