import hoverSound from "./assets/hover_sound.mp3";
import selectSound from "./assets/select_sound.mp3";
import backgroundMusic1 from "./assets/background_music_1.mp3";
import backgroundMusic2 from "./assets/background_music_2.mp3";
import backgroundMusic3 from "./assets/background_music_3.mp3";
import win1 from "./assets/win1.mp3";
import disappointment from "./assets/disappointment.mp3";
import oof from "./assets/oof.mp3";
import pop from "./assets/pop.mp3";

const concurrentSoundLimit = 5;

type Sound = {
  playing: boolean;
  sound: HTMLAudioElement;
};

interface SoundOptions {
  importedSound: string;
  volume?: number;
  maxSounds?: number;
  autoLoop?: boolean;
  chooseFrom?: string[];
}

function initializeSound({
  importedSound,
  volume = 1,
  maxSounds = concurrentSoundLimit,
  autoLoop = false,
  chooseFrom = [],
}: SoundOptions): Sound[] {
  return new Array(maxSounds).fill(null).map(() => {
    const record = {
      playing: false,
      sound: new Audio(importedSound),
    };
    record.sound.volume = volume;
    record.sound.loop = autoLoop;
    record.sound.onplay = () => {
      record.playing = true;
    };
    record.sound.onended = () => {
      record.playing = false;
      if (chooseFrom.length) {
        (SoundLoader as any)[chooseFrom[Math.floor(Math.random() * chooseFrom.length)]];
      }
    };
    return record;
  });
}

export class SoundLoader {
  public static soundEnabled: boolean = true;
  public static stopAllSounds() {
    this._hover.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._select.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._backgroundMusic1.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._backgroundMusic2.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._backgroundMusic3.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._win1.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._disappointment.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._oof.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._bigPop.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
    this._smallPop.forEach((s) => {
      if (s.playing && !s.sound.paused) {
        s.sound.pause();
      }
    });
  }
  public static resumeAllSounds() {
    this._hover.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._select.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._backgroundMusic1.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._backgroundMusic2.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._backgroundMusic3.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._win1.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._disappointment.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._oof.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._bigPop.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
    this._smallPop.forEach((s) => {
      if (s.sound.paused && s.playing) {
        s.sound.play();
      }
    });
  }
  private static playSound(sound: Sound[]) {
    if (!this.soundEnabled) {
      return null;
    }
    const soundToPlay = sound.find((s) => !s.playing);
    if (soundToPlay) {
      soundToPlay.sound.play();
    }
    return null;
  }
  private static _hover: Sound[] = initializeSound({
    importedSound: hoverSound,
    volume: 0.2,
    maxSounds: 5,
  });
  private static _select: Sound[] = initializeSound({
    importedSound: selectSound,
    volume: 0.6,
    maxSounds: 5,
  });
  private static _backgroundMusic1: Sound[] = initializeSound({
    importedSound: backgroundMusic1,
    volume: 0.6,
    maxSounds: 1,
    chooseFrom: ["backgroundMusic3", "backgroundMusic2"],
  });
  private static _backgroundMusic2: Sound[] = initializeSound({
    importedSound: backgroundMusic2,
    volume: 1,
    maxSounds: 1,
    chooseFrom: ["backgroundMusic1", "backgroundMusic3"],
  });
  private static _backgroundMusic3: Sound[] = initializeSound({
    importedSound: backgroundMusic3,
    volume: 0.6,
    maxSounds: 1,
    chooseFrom: ["backgroundMusic1", "backgroundMusic2"],
  });
  private static _win1: Sound[] = initializeSound({
    importedSound: win1,
    volume: 0.4,
    maxSounds: 1,
  });
  private static _disappointment: Sound[] = initializeSound({
    importedSound: disappointment,
    volume: 0.4,
    maxSounds: 1,
  });
  private static _oof: Sound[] = initializeSound({
    importedSound: oof,
    volume: 0.4,
    maxSounds: 1,
  });
  private static _bigPop: Sound[] = initializeSound({
    importedSound: pop,
    volume: 0.4,
    maxSounds: 1,
  });
  private static _smallPop: Sound[] = initializeSound({
    importedSound: pop,
    volume: 0.2,
    maxSounds: 10,
  });
  static numConcurrentSounds() {
    return this._hover.filter((s) => s.playing).length;
  }
  static get hover() {
    return this.playSound(this._hover);
  }
  static get select() {
    return this.playSound(this._select);
  }
  static get backgroundMusic() {
    let soundAlreadyPlaying = false;
    this._backgroundMusic1.forEach((s) => {
      if (s.playing) {
        soundAlreadyPlaying = true;
      }
    });
    this._backgroundMusic2.forEach((s) => {
      if (s.playing) {
        soundAlreadyPlaying = true;
      }
    });
    this._backgroundMusic3.forEach((s) => {
      if (s.playing) {
        soundAlreadyPlaying = true;
      }
    });
    if (soundAlreadyPlaying) {
      return null;
    }
    return this.playSound(
      [this._backgroundMusic1, this._backgroundMusic2, this._backgroundMusic3][
        Math.floor(Math.random() * 3)
      ]
    );
  }
  static get win1() {
    return this.playSound(this._win1);
  }
  static get disappointment() {
    return this.playSound(this._disappointment);
  }
  static get oof() {
    return this.playSound(this._oof);
  }
  static get bigPop() {
    return this.playSound(this._bigPop);
  }
  static get smallPop() {
    return this.playSound(this._smallPop);
  }
}
