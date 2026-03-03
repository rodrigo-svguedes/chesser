
const soundEffectPath = {
    'move-self': 'static/sounds/move-self.mp3',
    'capture': 'static/sounds/capture.mp3',
    'castle': 'static/sounds/castle.mp3',
    'promote': 'static/sounds/promote.mp3',
    'move-check': 'static/sounds/move-check.mp3',
    'game-end': 'static/sounds/game-end.mp3',
}

export const soundEffectManagerFactory = async () => {
    const audioContext = new window.AudioContext()

    const soundPool = {}
    for (let key of Object.keys(soundEffectPath)) {
        const arrayBuffer = await (await fetch(soundEffectPath[key])).arrayBuffer();
        const soundBuffer = await audioContext.decodeAudioData(arrayBuffer);
        soundPool[key] = soundBuffer
    }

    return async soundName => {
        if (audioContext.state === 'suspended') 
            await audioContext.resume()
        const source = audioContext.createBufferSource();
        source.buffer = soundPool[soundName];
        source.connect(audioContext.destination);
        source.start();
    }
}
