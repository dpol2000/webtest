
var GSound = {
    context: null,
    bufferLoader: null,
    BL: [],
    
    init: function () {

  // Fix up prefixing
        window.AudioContext = window.AudioContext || window.webkitAudioContext;
        this.context = new AudioContext();

        this.bufferLoader = new BufferLoader(
            this.context,
            [
              '/static/etest/sound/success.ogg',
              '/static/etest/sound/warning.ogg',
              '/static/etest/sound/danger.ogg',
            ],
        this.finishedLoading
        );

        this.bufferLoader.load();
    },

    finishedLoading: function (bufferList) {
        for (var i=0; i<bufferList.length; i++) {
            GSound.BL[i] = bufferList[i];
        }
    },

    playSound: function (num) {
        var sound = this.context.createBufferSource();
        sound.buffer = GSound.BL[num];
        sound.connect(this.context.destination);
        sound.start(0);
    }
}

