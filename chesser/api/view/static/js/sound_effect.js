
const SOUND_URI = '/view/static/sounds';

const soundEffectPath = {
    'move-self': `${SOUND_URI}/move-self.mp3`,
    'capture': `${SOUND_URI}/capture.mp3`,
    'castle': `${SOUND_URI}/castle.mp3`,
    'promote': `${SOUND_URI}/promote.mp3`,
    'move-check': `${SOUND_URI}/move-check.mp3`,
    'game-end': `${SOUND_URI}/game-end.mp3`,
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
