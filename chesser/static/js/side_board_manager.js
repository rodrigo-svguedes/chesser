const importPGNBtnTab = document.getElementById('importPGNBtn')
const chessComBtnTab = document.getElementById('importChessComBtn')
const importPGNTab = document.getElementById('ImportPGNTab')
const chessComTab = document.getElementById('ImportChessComTab')

const review = document.getElementsByClassName('review')[0]

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

export const addPGNTabListener = (func) => importPGNTab.addEventListener('click', func)