import hoverSound from "./assets/hover_sound.mp3";
import selectSound from "./assets/select_sound.mp3";
import backgroundMusic from "./assets/background_music.mp3";
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
}

function initializeSound({
  importedSound,
  volume = 1,
  maxSounds = concurrentSoundLimit,
  autoLoop = false,
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
    };
    return record;
  });
}

export class SoundLoader {
  private static playSound(sound: Sound[]) {
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
  private static _backgroundMusic: Sound[] = initializeSound({
    importedSound: backgroundMusic,
    volume: 0.4,
    maxSounds: 1,
    autoLoop: true,
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
    return this.playSound(this._backgroundMusic);
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
