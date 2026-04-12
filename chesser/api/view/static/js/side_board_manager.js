const importPGNTabBtn = document.getElementById('importPGNTabBtn')
const chessComTabBtn = document.getElementById('importChessComTabBtn')
const importPGNTab = document.getElementById('importPGNTab')
const chessComTab = document.getElementById('importChessComTab')
const importPGNBtn = document.getElementById('importPGNBtn')

const review = document.getElementsByClassName('review')[0]

importPGNTabBtn.addEventListener('click', () => {
    chessComTabBtn.classList.remove('active')
    importPGNTabBtn.classList.add('active')

    importPGNTab.style.display = 'block'
    chessComTab.style.display = 'none'
});

chessComTabBtn.addEventListener('click', () => {
    chessComTabBtn.classList.add('active')
    importPGNTabBtn.classList.remove('active')
    
    importPGNTab.style.display = 'none'
    chessComTab.style.display = 'block'
});

export const handleReviewBar = (gameMoveAnalysis) => {
    Object.entries(Object.values(gameMoveAnalysis)
            .map(data => data['move_class'])
            .reduce((acc, value, index) => {
                const pieceTurn = index % 2 == 0? 'w' : 'b'
                acc[pieceTurn+value] = (acc[pieceTurn+value] | 0) + 1
                return acc}, {}))
            .forEach(value => {
                const e = review.querySelectorAll(`.${value[0].slice(1)} .pm-review > span`)
                if (e.length == 0) return
                if (value[0].charAt(0) == 'w')
                    e[0].innerText = value[1]
                else
                    e[1].innerText = value[1]
            });
    review.style.visibility = 'visible'
}

export const addPGNBtnListener = (func) => {
    importPGNBtn.addEventListener('click', () => {
        importPGNBtn.disabled = true
        func()
        importPGNBtn.disabled = false
    })
}
