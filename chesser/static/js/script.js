
const API_BASE = ''
const STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'

/*
 1: go foward, 
 0: go backwards, 
-1: go to the beginning, 
 2: go the end;
 */
const makeGameStream = (squares, pieces, gameMoveAnalysis) => {

    let finalIndex = Object.keys(gameMoveAnalysis).length
    let moveIndex = -1

    let whiteEvalBar = document.getElementsByClassName('white-bar')[0]
    let blackEvalBar = document.getElementsByClassName('black-bar')[0]
    let spanWhiteVal = whiteEvalBar.querySelectorAll('span')[0]
    let spanBlackVal = blackEvalBar.querySelectorAll('span')[0]

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

    const manageEvalBar = (mate_in, evaluation, win_advantage) => {
        if (mate_in === 0) {
            if (moveIndex % 2 == 0) {
                spanWhiteVal.innerText = "1-0"
                blackEvalBar.style.height = "0%"
            } else {
                spanBlackVal.innerText = "0-1"
                blackEvalBar.style.height = "100%"
            }
        } else {
            blackEvalBar.style.height = 100-win_advantage*100+"%"
            
            if (evaluation >= 0) {
                spanWhiteVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
                spanBlackVal.innerText = ""
            } else {
                spanBlackVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
                spanWhiteVal.innerText = ""
            }
        }
    }

    const manageEnPassant = (dirct, fromSquare, toSquare) => {
        if (dirct === 1) {
            if (Math.abs(toSquare - fromSquare) == 7) {
                squares[fromSquare + (moveIndex % 2 == 0? -1 : 1)].querySelector('img').remove()
            } else {
                squares[fromSquare + (moveIndex % 2 == 0? 1 : -1)].querySelector('img').remove()
            }
        } else {
            let previousImg = createImgPiece((moveIndex % 2 == 0? 'p' : 'P'))
            if (Math.abs(toSquare - fromSquare) == 7) {
                squares[fromSquare + (moveIndex % 2 == 0? -1 : 1)].appendChild(previousImg)
            } else {
                squares[fromSquare + (moveIndex % 2 == 0? 1 : -1)].appendChild(previousImg)
            }
        }
    }

    const manageCastling = (dirct, fromSquare, toSquare) => {
        if ((toSquare - fromSquare) > 0) {
            const rook = squares[dirct === 1? fromSquare+3 :toSquare-1].querySelectorAll('img')[0]
            squares[dirct === 1? toSquare-1 :fromSquare+3].appendChild(rook)
        } else {
            const rook = squares[dirct === 1? fromSquare-4 :toSquare+1].querySelectorAll('img')[0]
            squares[dirct === 1? toSquare+1 :fromSquare-4].appendChild(rook)
        }
    }

    loadPieces(STARTING_FEN)
    manageEvalBar(null, 0.2, 0.51)

    return direction => {

        if (direction === 1 && moveIndex < finalIndex-1) { 
            moveIndex++

            const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
            const toSquare = gameMoveAnalysis[moveIndex]['to_square']
            
            const imgOrigin = squares[fromSquare].querySelector('img')

            const imgDestiny = squares[toSquare].querySelector('img')
            if (imgDestiny) imgDestiny.remove()

            const promotion_to = gameMoveAnalysis[moveIndex]['promotion_to']
            if (promotion_to)
                imgOrigin.src = `/static/images/${pieces[promotion_to]}.svg`

            if (gameMoveAnalysis[moveIndex]['en_passant_move'])
                manageEnPassant(direction, fromSquare, toSquare)

            squares[toSquare].appendChild(imgOrigin)
            
            if (gameMoveAnalysis[moveIndex]['is_castling'])
                manageCastling(direction, fromSquare, toSquare)
            
            manageEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                          gameMoveAnalysis[moveIndex]['evaluation'], 
                          gameMoveAnalysis[moveIndex]['win_advantage'])

        } else if (direction === 0 && moveIndex >= 0) {
            
            const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
            const toSquare = gameMoveAnalysis[moveIndex]['to_square']
            
            let img = squares[toSquare].querySelectorAll('img')[0]

            if (gameMoveAnalysis[moveIndex]['promotion_to']) 
                img.src = `/static/images/${pieces[moveIndex % 2 == 0? 'P':'p']}.svg`

            squares[fromSquare].appendChild(img)

            if (gameMoveAnalysis[moveIndex]['en_passant_move'])
                manageEnPassant(direction, fromSquare, toSquare)

            if (gameMoveAnalysis[moveIndex]['is_castling'])
                manageCastling(direction, fromSquare, toSquare)
            
            if (moveIndex != 0) {
                const previousFen = gameMoveAnalysis[moveIndex-1]['fen']
                const pieceChr = expandAndReverseFenRanks(previousFen).replaceAll('/', '')[63-toSquare]
                if (pieceChr !== "#") squares[toSquare].appendChild(createImgPiece(pieceChr))
            }

            moveIndex--

            if (moveIndex === -1)
                manageEvalBar(null, 0.2, 0.51)
            else
                manageEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                              gameMoveAnalysis[moveIndex]['evaluation'], 
                              gameMoveAnalysis[moveIndex]['win_advantage'])

        } else if (direction === -1 && moveIndex != 0) {
            moveIndex = -1
            loadPieces(STARTING_FEN)
            manageEvalBar(null, 0.2, 0.51)

        } else if (direction === 2 && moveIndex != (finalIndex-1)) {
            moveIndex = finalIndex-1
            loadPieces(gameMoveAnalysis[moveIndex]['fen'])

            manageEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                          gameMoveAnalysis[moveIndex]['evaluation'], 
                          gameMoveAnalysis[moveIndex]['win_advantage'])
        }
    }
}

    
(async () => {
    const text_area = document.getElementById('pgn_ta')

    let squares = {}
    for (const element of document.getElementsByClassName('square')) 
        squares[element.id] = element

    const playerOne = document.getElementById('bp-name-1')
    const playerTwo = document.getElementById('bp-name-2')

    const playerOneNameSpan = document.createElement('span')
    const playerTwoNameSpan = document.createElement('span')

    playerOne.appendChild(playerOneNameSpan)
    playerTwo.appendChild(playerTwoNameSpan)

    let pieces = await fetch(`${API_BASE}/board/pieces`).then(response => response.json())

    let manageBoardState = null;

    document.addEventListener('keydown', event => {
        const actions = {
            'ArrowLeft': 0,
            'ArrowRight': 1,
            'ArrowUp': -1,
            'ArrowDown': 2
        }
        if (actions[event.key] != null && manageBoardState)
            manageBoardState(actions[event.key])
    });

    document.getElementById('btn-gotostart')
            .addEventListener("click", () => {
                if (manageBoardState) manageBoardState(-1)
            })
    document.getElementById('btn-previous')
            .addEventListener("click", () => {
                if (manageBoardState) manageBoardState(0)
            })
    document.getElementById('btn-next')
            .addEventListener("click", () => {
                if (manageBoardState) manageBoardState(1)
            })
    document.getElementById('btn-gotoend')
            .addEventListener("click", () => {
                if (manageBoardState) manageBoardState(2)
            })

    document
        .getElementById('importPGNBtn')
        .addEventListener('click', () => {
            fetch(`${API_BASE}/board/pgn/analyse`, {
                method: 'POST',
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({ pgn_code: text_area.value})})
            .then(data => data.json())
            .then(data => {
                playerOneNameSpan.innerText = data[0]['black_player']
                playerTwoNameSpan.innerText = data[0]['white_player']
                manageBoardState = makeGameStream(squares, pieces, data[1])
            })
})})()


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