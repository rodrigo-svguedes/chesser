
/*
 1: go foward, 
 0: go backwards, 
 -1: go to the beginning, 
 2: go the end;
 */
const makeGameStream = gameId => {
    const API_BASE = ''

    let squares = {}
    for (const element of document.getElementsByClassName('square')) 
        squares[element.id] = element

    let pieces = null
    fetch(`${API_BASE}/board/pieces`)
        .then(response => response.json())
        .then(data => pieces = data)

    fetch(`${API_BASE}/board/game/${gameId}`)
        .then(response => response.json())
        .then(data => {
            const blackPlayerName = document.createElement('span')
            blackPlayerName.innerText = data['black_player']

            document.getElementById('bp-name-1').appendChild(blackPlayerName)

            const whitePlayerName = document.createElement('span')
            whitePlayerName.innerText = data['white_player']

            document.getElementById('bp-name-2').appendChild(whitePlayerName)
        })
    
    let finalIndex = -1
    let moveIndex = -1

    const isDigit = value => "0123456789".includes(value);

    const cleanBoard = () =>
        Object.values(squares).forEach(square => {
            const imagens = square.querySelectorAll('img');
            for (const img of imagens) img.remove()
        })      

    const manageBoardState = streamDirection => {
        if (streamDirection === 1 && moveIndex < finalIndex-1) { 
            moveIndex += 1
            return true
        } else if (streamDirection === 0 && moveIndex > 0) {
            moveIndex -= 1
            return true
        } else if (streamDirection === -1 && moveIndex != 0) {
            moveIndex = 0
            return true
        } else if (streamDirection === 2 && moveIndex != (finalIndex-1)) {
            moveIndex = finalIndex-1
            return true
        }
        return false
    }

    let fenList = null;

    const loadPieces = () => {
        let count = 0
        cleanBoard()
        fenList[moveIndex].split('/').forEach(element => {
            Array.from(element).forEach(character => {
                if (isDigit(character)) {
                    count += parseInt(character)
                } else {
                    const piece_img = document.createElement('img');
                    piece_img.src = `/static/images/${pieces[character]}.svg`
                    piece_img.draggable = true
                    squares[count].appendChild(piece_img)
                    count++
                }
            })
        })
    }

    fetch(`${API_BASE}/board/fen/${gameId}`)
        .then(response => response.json())
        .then(data => {
            fenList = data
            finalIndex = Object.keys(fenList).length
            if (manageBoardState(1)) 
                loadPieces(moveIndex)
        })

    return (streamDirection) => {
        if (manageBoardState(streamDirection))
            loadPieces()
    }
}

let gameStream = null;

document.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') {
        gameStream(0);
    } else if (event.key === 'ArrowRight') {
        gameStream(1);
    } else if (event.key === 'ArrowUp') {
        gameStream(-1);
    } else if (event.key === 'ArrowDown') {
        gameStream(2);
    }
});

document.getElementById('btn-gotostart')
        .addEventListener("click", () => loadChessBoard(-1))

document.getElementById('btn-previous')
        .addEventListener("click", () => loadChessBoard(0))

document.getElementById('btn-next')
        .addEventListener("click", () => loadChessBoard(1))

document.getElementById('btn-gotoend')
        .addEventListener("click", () => loadChessBoard(2))

    
document.getElementById('importPGNBtn')
        .addEventListener('click', () => gameStream = makeGameStream(0))


function openCity(evt, cityName) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
} 
/*
const svgImg = document.getElementsByTagName('img');

for (let i = 0; i < svgImg.length; i++) {

    svgImg[i].addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('svg_piece', e.target.src);
        e.target.style.opacity = '0.5';
    });

    svgImg[i].addEventListener('dragend', (e) => {
        e.target.remove();
    });
}

const board = document.getElementsByClassName('board-chessboard')[0];

board.addEventListener('dragover', e => e.preventDefault());

board.addEventListener('drop', (e) => {

    e.preventDefault();

    const src = e.dataTransfer.getData('svg_piece');

    const targetSquare = e.target.closest('.square');

    const img = document.createElement('img');
    img.src = src;
    img.className = 'piece';
    img.draggable = true;
    img.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('svg_piece', e.target.src);
        e.target.style.opacity = '0.';
    });
    targetSquare.appendChild(img);
});*/