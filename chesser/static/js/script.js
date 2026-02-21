
const API_BASE = ''
const STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'

/*
 1: go foward, 
 0: go backwards, 
-1: go to the beginning, 
 2: go the end;
 */
const makeGameStream = async (squares, gameMoveAnalysis) => {

    let pieces = await fetch(`${API_BASE}/board/pieces`)
                        .then(response => response.json())

    let finalIndex = Object.keys(gameMoveAnalysis).length
    let moveIndex = -1

    const isDigit = value => "0123456789".includes(value);

    const cleanBoard = () =>
        Object.values(squares).forEach(square => {
            const imagens = square.querySelectorAll('img');
            for (const img of imagens) img.remove()
        })      

    const expandAndReverseFenRanks = fen => {
        let expandedFen = ''
        fen.split('/').forEach(element => {
            Array.from(element).reverse().forEach(chr => {
                expandedFen += isDigit(chr)? '#'.repeat(parseInt(chr)) : chr
            })
            expandedFen += '/'
        })
        return expandedFen
    }

    const createImgPiece = pieceChar => {
        const piece_img = document.createElement('img');
        piece_img.src = `/static/images/${pieces[pieceChar]}.svg`
        piece_img.draggable = true
        return piece_img
    }

    const loadPieces = fen => {
        cleanBoard()
        let count = 63
        expandAndReverseFenRanks(fen).split('/').forEach(element => {
            Array.from(element).forEach(character => {
                if (character !== '#') 
                    squares[count].appendChild(createImgPiece(character))
                count--
            })
        })
    }

    const manageBoardState = direction => {

        if (direction === 1 && moveIndex < finalIndex-1) { 
            moveIndex += 1

            const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
            const toSquare = gameMoveAnalysis[moveIndex]['to_square']
            
            const imgOrigin = squares[fromSquare].querySelectorAll('img')[0]

            const imgDestiny = squares[toSquare].querySelectorAll('img')
            if (imgDestiny.length != 0) imgDestiny[0].remove()

            const promotion_to = gameMoveAnalysis[moveIndex]['promotion_to']
            if (promotion_to)
                imgOrigin.src = `/static/images/${pieces[promotion_to]}.svg`

            squares[toSquare].appendChild(imgOrigin)
            
            if (gameMoveAnalysis[moveIndex]['is_castling']) {
                if ((toSquare - fromSquare) > 0) {
                    let rook = squares[fromSquare+3].querySelectorAll('img')[0]
                    squares[toSquare-1].appendChild(rook)
                } else {
                    let rook = squares[fromSquare-4].querySelectorAll('img')[0]
                    squares[toSquare+1].appendChild(rook)
                }
            }
            
        } else if (direction === 0 && moveIndex >= 0) {
            
            const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
            const toSquare = gameMoveAnalysis[moveIndex]['to_square']
            
            let img = squares[toSquare].querySelectorAll('img')[0]

            const promotion_to = gameMoveAnalysis[moveIndex]['promotion_to']
            if (promotion_to) 
                img.src = `/static/images/${pieces[moveIndex % 2 == 0? 'P':'p']}.svg`

            squares[fromSquare].appendChild(img)

            if (gameMoveAnalysis[moveIndex]['is_castling']) {
                if ((toSquare - fromSquare) > 0) {
                    let rook = squares[toSquare-1].querySelectorAll('img')[0]
                    squares[fromSquare+3].appendChild(rook)
                } else {
                    let rook = squares[toSquare+1].querySelectorAll('img')[0]
                    squares[fromSquare-4].appendChild(rook)
                }
            }
            
            if (moveIndex != 0) {
                const previousFen = gameMoveAnalysis[moveIndex-1]['fen']
                const pieceChr = expandAndReverseFenRanks(previousFen).replaceAll('/', '')[63-toSquare]
                if (pieceChr !== "#") squares[toSquare].appendChild(createImgPiece(pieceChr))
            }
            moveIndex -= 1

        } else if (direction === -1 && moveIndex != 0) {
            moveIndex = -1
            loadPieces(STARTING_FEN)
        } else if (direction === 2 && moveIndex != (finalIndex-1)) {
            moveIndex = finalIndex-1
            loadPieces(gameMoveAnalysis[moveIndex]['fen'])
        }
    }

    loadPieces(STARTING_FEN)
    
    document.addEventListener('keydown', event => {
        if (event.key === 'ArrowLeft') {
            manageBoardState(0);
        } else if (event.key === 'ArrowRight') {
            manageBoardState(1);
        } else if (event.key === 'ArrowUp') {
            manageBoardState(-1);
        } else if (event.key === 'ArrowDown') {
            manageBoardState(2);
        }
    });

    document.getElementById('btn-gotostart')
            .addEventListener("click", () => manageBoardState(-1))
    document.getElementById('btn-previous')
            .addEventListener("click", () => manageBoardState(0))
    document.getElementById('btn-next')
            .addEventListener("click", () => manageBoardState(1))
    document.getElementById('btn-gotoend')
            .addEventListener("click", () => manageBoardState(2))
}

    
(() => {
    const text_area = document.getElementById('pgn_ta')

    let squares = {}
    for (const element of document.getElementsByClassName('square')) 
        squares[element.id] = element

    const setPlayerName = (elementName, playerName) => {
        const blackPlayerName = document.createElement('span')
        blackPlayerName.innerText = playerName
        document.getElementById(elementName).appendChild(blackPlayerName)
    }

    return () => document
        .getElementById('importPGNBtn')
        .addEventListener('click', () => {
            fetch(`${API_BASE}/board/pgn/analyse`, {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ pgn_code: text_area.value})})
            .then(data => data.json())
            .then(data => {
                setPlayerName('bp-name-1', data[0]['black_player'])
                setPlayerName('bp-name-2', data[0]['white_player'])
                makeGameStream(squares, data[1])
            })
    })})()()


function openTab(evt, tabName) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}