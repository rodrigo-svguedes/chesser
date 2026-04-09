
const STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'

const whiteEvalBar = document.getElementsByClassName('white-bar')[0]
const blackEvalBar = document.getElementsByClassName('black-bar')[0]
const spanWhiteVal = whiteEvalBar.querySelectorAll('span')[0]
const spanBlackVal = blackEvalBar.querySelectorAll('span')[0]

const isDigit = value => "0123456789".includes(value)

const expandAndReverseFenRanks = fen => 
    fen.split("/")
       .map(element => element.split("").reverse().join(""))
       .reduce((acc, ele) => acc.concat(ele))
       .split("")
       .map(chr => isDigit(chr)? '#'.repeat(parseInt(chr)) : chr)
       .reduce((acc, chr) => acc.concat(chr))

const cleanBoard = squares =>
    Object.values(squares).forEach(square => {
        const imagens = square.querySelectorAll('img')
        for (const img of imagens) img.remove()
    })      

const loadPieces = (squares, pieces, fen) => {
    cleanBoard(squares)
    Array.from(expandAndReverseFenRanks(fen)).forEach((chr, index) => {
        if (chr !== '#') 
            squares[63-index].appendChild(createImgPiece(pieces, chr))
    })
}

const createImgPiece = (pieces, pieceChar) => {
    const piece_img = document.createElement('img')
    piece_img.src = `/static/images/pieces/${pieces[pieceChar]}.svg`
    piece_img.draggable = true
    return piece_img
}

const handleHighlight = (squares, fromSquare, toSquare, onlyClean=false) => {
    for (const square of Object.values(squares))
        if (square.classList.contains('highlight'))
            square.classList.toggle('highlight')
    if (onlyClean) return
    squares[fromSquare].classList.toggle('highlight')
    squares[toSquare].classList.toggle('highlight')
}

const handleCastling = (isFoward, squares, fromSquare, toSquare) => {
    if ((toSquare - fromSquare) > 0) {
        const rook = squares[isFoward? fromSquare+3 :toSquare-1].querySelectorAll(':scope > img')[0]
        const rookSquare = squares[isFoward? toSquare-1 :fromSquare+3]
        pieceTransitionHandler(rook, rookSquare)
        rookSquare.appendChild(rook)
    } else {
        const rook = squares[isFoward? fromSquare-4 :toSquare+1].querySelectorAll(':scope > img')[0]
        const rookSquare = squares[isFoward? toSquare+1 :fromSquare-4]
        pieceTransitionHandler(rook, rookSquare)
        rookSquare.appendChild(rook)
    }
}

const handleClassificationIcon = (isFoward, squares, classMove, toSquare, oldToSquare) => {
    
    const oldImgSquare = squares[isFoward? oldToSquare : toSquare]
    const oldImg = oldImgSquare? oldImgSquare.querySelector('span > img') : null
    if (oldImg) oldImg.remove()

    if (classMove) {
        const moveClassImg = document.createElement('img')
        moveClassImg.src = `/static/images/classification_icons/${classMove}.svg`
        const divClass = squares[isFoward? toSquare : oldToSquare].getElementsByClassName('classificons')[0]
        divClass.appendChild(moveClassImg)
    }
}

const handleEnPassant = (isFoward, isWhiteTurn, squares, fromSquare, toSquare, pieces) => {
    if (isFoward) {
        if (Math.abs(toSquare - fromSquare) == 7) {
            console.log(fromSquare + (isWhiteTurn? -1 : 1))
            squares[fromSquare + (isWhiteTurn? -1 : 1)].querySelector(':scope > img').remove()
        } else {
            console.log(fromSquare + (isWhiteTurn? 1 : -1))
            squares[fromSquare + (isWhiteTurn? 1 : -1)].querySelector(':scope > img').remove()
        }
    } else {
        const previousImg = createImgPiece(pieces, (isWhiteTurn? 'p' : 'P'))
        if (Math.abs(toSquare - fromSquare) == 7) {
            squares[fromSquare + (isWhiteTurn? -1 : 1)].appendChild(previousImg)
        } else {
            squares[fromSquare + (isWhiteTurn? 1 : -1)].appendChild(previousImg)
        }
    }
}

const handleEvalBar = (isWhiteTurn, mate_in, evaluation, win_advantage) => {
    if (mate_in === 0) {
        if (isWhiteTurn) {
            spanWhiteVal.innerText = "1-0"
            blackEvalBar.style.height = "0%"
        } else {
            spanBlackVal.innerText = "0-1"
            blackEvalBar.style.height = "100%"
        }
        return
    }

    blackEvalBar.style.height = 100-win_advantage+"%"
    
    if (win_advantage > 50) {
        spanWhiteVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
        spanBlackVal.innerText = ""
    } else {
        spanBlackVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
        spanWhiteVal.innerText = ""
    }
}

const pieceTransitionHandler = (image, destino) => {
    
    const clone = image.cloneNode(true)
    clone.id = 'animatedClone'
    
    image.style.opacity = '0'
    
    // Posiciona o clone no lugar da imagem original
    const imgRect = image.getBoundingClientRect();
    clone.style.position = 'fixed';
    clone.style.left = imgRect.left + 'px';
    clone.style.top = imgRect.top + 'px';
    clone.style.width = imgRect.width + 'px';
    clone.style.height = imgRect.height + 'px';
    clone.style.margin = '0';
    clone.style.transition = 'all 0.2s ease';
    clone.style.zIndex = '1000';
    
    document.body.appendChild(clone)

    // Calcula posição de destino
    const destRect = destino.getBoundingClientRect()
    setTimeout(() => {
        clone.style.left = (destRect.left + (destRect.width / 2) - (imgRect.width / 2)) + 'px';
        clone.style.top = (destRect.top + (destRect.height / 2) - (imgRect.height / 2)) + 'px';
    }, 10)

    // Finaliza a transição
    clone.addEventListener('transitionend', () => {
        clone.remove()
        image.style.opacity = '1'
    })
}

/*
 1: go foward, 
 0: go backwards, 
-1: go to the beginning, 
 2: go the end;
 */
export const boardManagerFactory = (squares, pieces, playSoundEffect, gameMoveAnalysis) => {

    const gameLength = Object.keys(gameMoveAnalysis).length
    let moveIndex = -1

    const moveFoward = () => {
        moveIndex++
        const move = gameMoveAnalysis[moveIndex]
        const fromSquare = move['from_square']
        const toSquare = move['to_square']
        const promotionTo = move['promotion_to']
        const isEnPassant = move['is_en_passant']
        const isCastling = move['is_castling']
        const isCheck = move['is_check']
        const classMove = move['move_class']
        const previousMove = gameMoveAnalysis[moveIndex-1]
        const previousToSquare = previousMove? previousMove['to_square']: null
        const imgOrigin = squares[fromSquare].querySelector(':scope > img')
        const imgDestiny = squares[toSquare].querySelector(':scope > img')

        if (moveIndex >= 0)
            handleClassificationIcon(true, squares, classMove, toSquare, previousToSquare)

        if (promotionTo) {
            imgOrigin.src = `/static/images/pieces/${pieces[promotionTo]}.svg`
            playSoundEffect('promotion')
        } else if (isEnPassant) {
            handleEnPassant(true, moveIndex % 2 == 0, squares, fromSquare, toSquare, pieces)
            playSoundEffect('capture')
        } else if (isCastling) {
            handleCastling(true, squares, fromSquare, toSquare)
            playSoundEffect('castle')
        } else if (isCheck) {
            playSoundEffect('move-check')
        }

        if (imgDestiny) {
            imgDestiny.remove()
            if(!isCheck) playSoundEffect('capture')
        } else if(!isCheck) {
            playSoundEffect('move-self')
        }

        pieceTransitionHandler(imgOrigin, squares[toSquare])
        squares[toSquare].appendChild(imgOrigin)
        
        handleEvalBar(moveIndex % 2 == 0,
                      move['mate_in'],
                      move['evaluation'], 
                      move['win_advantage'])
        
        handleHighlight(squares, fromSquare, toSquare)
    }

    const moveBackwards = () => {
        const move = gameMoveAnalysis[moveIndex]
        const fromSquare = move['from_square']
        const toSquare = move['to_square']
        const promotionTo = move['promotion_to']
        const isEnPassant = move['is_en_passant']
        const isCastling = move['is_castling']
        const isCheck = move['is_check']
        const previousMove = gameMoveAnalysis[moveIndex-1]
        const moveClass = previousMove? previousMove['move_class'] : null
        const previousToSquare = previousMove? previousMove['to_square'] : null
        const img = squares[toSquare].querySelectorAll(':scope > img')[0]

        if (moveIndex >= 0)
            handleClassificationIcon(false, squares, moveClass, toSquare, previousToSquare)

        if (promotionTo) {
            img.src = `/static/images/pieces/${pieces[moveIndex % 2 == 0? 'P':'p']}.svg`
            playSoundEffect('promotion')
        } else if (isEnPassant) {
            handleEnPassant(false, moveIndex % 2 == 0, squares, fromSquare, toSquare, pieces)
            playSoundEffect('capture')
        } else if (isCastling) {
            handleCastling(false, squares, fromSquare, toSquare)
            playSoundEffect('castle')
        } else if (isCheck) {
            playSoundEffect('move-check')
        }
       
        if (moveIndex != 0) {
            const previousFen = previousMove['fen']
            const pieceChr = expandAndReverseFenRanks(previousFen)[63-toSquare]
            if (pieceChr !== "#") {
                squares[toSquare].appendChild(createImgPiece(pieces, pieceChr))
                 if (!isCheck) playSoundEffect('capture')
            } else if (!isCheck) playSoundEffect('move-self')
        } else playSoundEffect('move-self')

        pieceTransitionHandler(img, squares[fromSquare])
        squares[fromSquare].appendChild(img)
        
        if (moveIndex > 0) {
            handleHighlight(squares, fromSquare, toSquare)
            handleEvalBar(moveIndex % 2 == 0, 
                          previousMove['mate_in'], 
                          previousMove['evaluation'], 
                          previousMove['win_advantage'])
        } else {
            handleHighlight(squares, null, null, true)
            handleEvalBar(null, null, 0.2, 51)
        }

        moveIndex--
    }

    const goToStart = () => {
        moveIndex = -1
        loadPieces(squares, pieces, STARTING_FEN)
        handleEvalBar(null, null, 0.2, 51)
        handleHighlight(squares, null, null, true)
    }

    const goToEnd = () => {
        moveIndex = gameLength-1
        
        const move = gameMoveAnalysis[moveIndex]
        const previousMove = gameMoveAnalysis[moveIndex-1]

        loadPieces(squares, pieces, move['fen'])

        handleClassificationIcon(true, squares, move['move_class'], move['to_square'], previousMove['to_square'])

        handleHighlight(squares, move['from_square'], move['to_square'])

        handleEvalBar(moveIndex % 2 == 0, move['mate_in'], move['evaluation'], move['win_advantage'])
    }

    loadPieces(squares, pieces, STARTING_FEN)
    handleEvalBar(null, null, 0.2, 51)

    return direction => {
        if (direction === 1 && moveIndex < gameLength-1) { 
            moveFoward()
        } else if (direction === 0 && moveIndex >= 0) {
            moveBackwards()
        } else if (direction === -1 && moveIndex != 0) {
            goToStart()
        } else if (direction === 2 && moveIndex != (gameLength-1)) {
            goToEnd()
        }
        return (moveIndex === gameLength-1)
    }
}
