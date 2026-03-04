import { boardManagerFactory } from '/static/js/board_manager.js';
import { soundEffectManagerFactory } from '/static/js/sound_effect.js';


const API_BASE = '';

(async () => {
    const text_area = document.getElementById('pgn_ta')
    const playerOne = document.getElementById('bp-name-1')
    const playerTwo = document.getElementById('bp-name-2')
    const board = document.getElementsByClassName('board-chessboard')[0]
    const playerOneNameSpan = document.createElement('span')
    const playerTwoNameSpan = document.createElement('span')
    const squares = {}
    const pieces = await fetch(`${API_BASE}/board/pieces`).then(response => response.json())
    const playSoundEffect = await soundEffectManagerFactory()
    const importPGNBtnTab = document.getElementById('importPGNBtn')
    const chessComBtnTab = document.getElementById('importChessComBtn')
    const importPGNTab = document.getElementById('ImportPGNTab')
    const chessComTab = document.getElementById('ImportChessComTab')
    const btnGotoStart = document.getElementById('btn-gotostart')
    const btnGotoPrevious = document.getElementById('btn-previous')
    const btnGotoNext = document.getElementById('btn-next')
    const btnGotoEnd = document.getElementById('btn-gotoend')
    const playBtn = document.getElementById('btn-play')
    const imgPlayBtn = playBtn.getElementsByTagName('img')[0]
    
    importPGNBtnTab.addEventListener('click', () => {
        chessComBtnTab.classList.remove('active')
        importPGNBtnTab.classList.add('active')

        importPGNTab.style.display = 'block'
        chessComTab.style.display = 'none'
    });

    chessComBtnTab.addEventListener('click', () => {
        chessComBtnTab.classList.add('active')
        importPGNBtnTab.classList.remove('active')
        
        importPGNTab.style.display = 'none'
        chessComTab.style.display = 'block'
    });

    playerOne.appendChild(playerOneNameSpan)
    playerTwo.appendChild(playerTwoNameSpan)

    for (const square of document.getElementsByClassName('square')) { 
        squares[square.id] = square
        square.addEventListener('contextmenu', e => {
            e.preventDefault()
            square.classList.toggle('selected-highlight')
        })
    }

    board.addEventListener('click', () => {
        for (const square of Object.values(squares)) {
            if (square.classList.contains('selected-highlight'))
                square.classList.toggle('selected-highlight')
        }
    })

    let boardStateManager = () => true;

    document.addEventListener('keydown', event => {
        const actions = {
            'ArrowLeft': 0,
            'ArrowRight': 1,
            'ArrowUp': -1,
            'ArrowDown': 2
        }
        if (actions[event.key] != null && boardStateManager)
            boardStateManager(actions[event.key])
    });

    btnGotoStart.addEventListener("click", () => boardStateManager(-1))
    btnGotoPrevious.addEventListener("click", () => boardStateManager(0))
    btnGotoNext.addEventListener("click", () => boardStateManager(1))
    btnGotoEnd.addEventListener("click", () => boardStateManager(2))
    
    let play = false
    let interval = null

    playBtn.addEventListener("click", () => {
        if (!play) {
            interval = setInterval(() => {
                if (boardStateManager(1)) {
                    clearInterval(interval)
                    imgPlayBtn.src = 'static/images/icons/play.svg'
                    play = false
                }
            }, 500)
            imgPlayBtn.src = 'static/images/icons/pause.svg'
            play = true
        } else {
            clearInterval(interval)
            imgPlayBtn.src = 'static/images/icons/play.svg'
            play = false
        }
    })

    importPGNTab
        .addEventListener('click', () => {
            if (text_area.value) 
                fetch(`${API_BASE}/board/pgn/analyse`, {
                    method: 'POST',
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({ pgn_code: text_area.value})})
                .then(data => data.json())
                .then(data => {
                    playerOneNameSpan.innerText = data[0]['black_player']
                    playerTwoNameSpan.innerText = data[0]['white_player']
                    boardStateManager = boardManagerFactory(squares, pieces, playSoundEffect, data[1])
                })
})})()


