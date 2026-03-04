
const STARTING_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR'



const pieceTransitionHandler = (image, destino) => {
    
    const clone = image.cloneNode(true);
    
    image.style.opacity = '0';

    clone.id = 'animatedClone';
    
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
    
    document.body.appendChild(clone);

    // Calcula posição de destino
    const destRect = destino.getBoundingClientRect();
    setTimeout(() => {
        clone.style.left = (destRect.left + (destRect.width / 2) - (imgRect.width / 2)) + 'px';
        clone.style.top = (destRect.top + (destRect.height / 2) - (imgRect.height / 2)) + 'px';
    }, 10);

    // Finaliza a transição
    clone.addEventListener('transitionend', function() {
        clone.remove();
        image.style.opacity = '1';
    });
}

/*
 1: go foward, 
 0: go backwards, 
-1: go to the beginning, 
 2: go the end;
 */
export const boardManagerFactory = (squares, pieces, playSoundEffect, gameMoveAnalysis) => {

    const finalIndex = Object.keys(gameMoveAnalysis).length
    let moveIndex = -1

    const whiteEvalBar = document.getElementsByClassName('white-bar')[0]
    const blackEvalBar = document.getElementsByClassName('black-bar')[0]
    const spanWhiteVal = whiteEvalBar.querySelectorAll('span')[0]
    const spanBlackVal = blackEvalBar.querySelectorAll('span')[0]

    const isDigit = value => "0123456789".includes(value);

    const cleanBoard = () =>
        Object.values(squares).forEach(square => {
            const imagens = square.querySelectorAll('img');
            for (const img of imagens) img.remove()
        })      

    const expandAndReverseFenRanks = fen => 
        fen.split("/")
           .map(element => element.split("").reverse().join(""))
           .reduce((acc, ele) => acc.concat(ele))
           .split("")
           .map(chr => isDigit(chr)? '#'.repeat(parseInt(chr)) : chr)
           .reduce((acc, chr) => acc.concat(chr))

    const createImgPiece = pieceChar => {
        const piece_img = document.createElement('img');
        piece_img.src = `/static/images/pieces/${pieces[pieceChar]}.svg`
        piece_img.draggable = true
        return piece_img
    }

    const loadPieces = fen => {
        cleanBoard()
        Array.from(expandAndReverseFenRanks(fen)).forEach((chr, index) => {
            if (chr !== '#') 
                squares[63-index].appendChild(createImgPiece(chr))
        })
    }

    const handleEvalBar = (mate_in, evaluation, win_advantage) => {
        if (mate_in === 0) {
            if (moveIndex % 2 == 0) {
                spanWhiteVal.innerText = "1-0"
                blackEvalBar.style.height = "0%"
            } else {
                spanBlackVal.innerText = "0-1"
                blackEvalBar.style.height = "100%"
            }
        } else {
            blackEvalBar.style.height = 100-win_advantage+"%"
            
            if (evaluation >= 0) {
                spanWhiteVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
                spanBlackVal.innerText = ""
            } else {
                spanBlackVal.innerText = mate_in ? "M"+Math.abs(mate_in) : Math.abs(evaluation).toFixed(1)
                spanWhiteVal.innerText = ""
            }
        }
    }

    const handleEnPassant = (isFoward, fromSquare, toSquare) => {
        const even = moveIndex % 2 == 0
        if (isFoward) {
            if (Math.abs(toSquare - fromSquare) == 7) {
                squares[fromSquare + (even? -1 : 1)].querySelector('img').remove()
            } else {
                squares[fromSquare + (even? 1 : -1)].querySelector('img').remove()
            }
        } else {
            const previousImg = createImgPiece((even? 'p' : 'P'))
            if (Math.abs(toSquare - fromSquare) == 7) {
                squares[fromSquare + (even? -1 : 1)].appendChild(previousImg)
            } else {
                squares[fromSquare + (even? 1 : -1)].appendChild(previousImg)
            }
        }
    }

    const handleCastling = (isFoward, fromSquare, toSquare) => {
        if ((toSquare - fromSquare) > 0) {
            const rook = squares[isFoward? fromSquare+3 :toSquare-1].querySelectorAll('img')[0]
            const rookSquare = squares[isFoward? toSquare-1 :fromSquare+3]
            pieceTransitionHandler(rook, rookSquare)
            rookSquare.appendChild(rook)
        } else {
            const rook = squares[isFoward? fromSquare-4 :toSquare+1].querySelectorAll('img')[0]
            const rookSquare = squares[isFoward? toSquare+1 :fromSquare-4]
            pieceTransitionHandler(rook, rookSquare)
            rookSquare.appendChild(rook)
        }
    }

    const handleHighlight = (fromSquare, toSquare, onlyClean=false) => {
        for (const square of Object.values(squares))
            if (square.classList.contains('highlight'))
                square.classList.toggle('highlight')
        if (onlyClean) return
        squares[fromSquare].classList.toggle('highlight')
        squares[toSquare].classList.toggle('highlight')
    }

    const moveFoward = () => {
        moveIndex++
        const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
        const toSquare = gameMoveAnalysis[moveIndex]['to_square']
        
        const imgOrigin = squares[fromSquare].querySelector('img')
        const promotionTo = gameMoveAnalysis[moveIndex]['promotion_to']
        const isEnPassant = gameMoveAnalysis[moveIndex]['en_passant_move']
        const isCastling = gameMoveAnalysis[moveIndex]['is_castling']
        const isCheck = gameMoveAnalysis[moveIndex]['is_check']
        const imgDestiny = squares[toSquare].querySelector('img')

        if (promotionTo) {
            imgOrigin.src = `/static/images/pieces/${pieces[promotionTo]}.svg`
            playSoundEffect('promotion')
        } else if (isEnPassant) {
            handleEnPassant(true, fromSquare, toSquare)
            playSoundEffect('capture')
        } else if (isCastling) {
            handleCastling(true, fromSquare, toSquare)
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
        
        handleEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                      gameMoveAnalysis[moveIndex]['evaluation'], 
                      gameMoveAnalysis[moveIndex]['win_advantage'])
        
        handleHighlight(fromSquare, toSquare)
    }

    const moveBackwards = () => {
        const fromSquare = gameMoveAnalysis[moveIndex]['from_square']
        const toSquare = gameMoveAnalysis[moveIndex]['to_square']
        
        const img = squares[toSquare].querySelectorAll('img')[0]
        const promotionTo = gameMoveAnalysis[moveIndex]['promotion_to']
        const isEnPassant = gameMoveAnalysis[moveIndex]['en_passant_move']
        const isCastling = gameMoveAnalysis[moveIndex]['is_castling']
        const isCheck = gameMoveAnalysis[moveIndex]['is_check']

        if (promotionTo) {
            img.src = `/static/images/pieces/${pieces[moveIndex % 2 == 0? 'P':'p']}.svg`
            playSoundEffect('promotion')
        } else if (isEnPassant) {
            handleEnPassant(false, fromSquare, toSquare)
            playSoundEffect('capture')
        } else if (isCastling) {
            handleCastling(false, fromSquare, toSquare)
            playSoundEffect('castle')
        } else if (isCheck) {
            playSoundEffect('move-check')
        }
        
        if (moveIndex != 0) {
            const previousFen = gameMoveAnalysis[moveIndex-1]['fen']
            const pieceChr = expandAndReverseFenRanks(previousFen)[63-toSquare]
            if (pieceChr !== "#") {
                squares[toSquare].appendChild(createImgPiece(pieceChr))
                 if (!isCheck) playSoundEffect('capture')
            } else if (!isCheck) playSoundEffect('move-self')
        } else playSoundEffect('move-self')

        pieceTransitionHandler(img, squares[fromSquare])
        squares[fromSquare].appendChild(img)
        
        moveIndex--

        if (moveIndex >= 0) {
            handleHighlight(gameMoveAnalysis[moveIndex]['from_square'], 
                            gameMoveAnalysis[moveIndex]['to_square'])
            handleEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                          gameMoveAnalysis[moveIndex]['evaluation'], 
                          gameMoveAnalysis[moveIndex]['win_advantage'])
        } else {
            handleHighlight(null, null, true)
            handleEvalBar(null, 0.2, 51)
        }
    }

    const goToStart = () => {
        moveIndex = -1
        loadPieces(STARTING_FEN)
        handleEvalBar(null, 0.2, 51)
        handleHighlight(null, null, true)
    }

    const goToEnd = () => {
        moveIndex = finalIndex-1
        loadPieces(gameMoveAnalysis[moveIndex]['fen'])
        handleHighlight(gameMoveAnalysis[moveIndex]['from_square'], 
                        gameMoveAnalysis[moveIndex]['to_square'])
        handleEvalBar(gameMoveAnalysis[moveIndex]['mate_in'],
                      gameMoveAnalysis[moveIndex]['evaluation'], 
                      gameMoveAnalysis[moveIndex]['win_advantage'])
    }

    loadPieces(STARTING_FEN)
    handleEvalBar(null, 0.2, 51)

    return direction => {
        if (direction === 1 && moveIndex < finalIndex-1) { 
            moveFoward()
        } else if (direction === 0 && moveIndex >= 0) {
            moveBackwards()
        } else if (direction === -1 && moveIndex != 0) {
            goToStart()
        } else if (direction === 2 && moveIndex != (finalIndex-1)) {
            goToEnd()
        }
        return (moveIndex === finalIndex-1)
    }
}