enum State {
  Bypass,
  PotentialImageLink,
  LinkText,
  LinkUrlStart,
  LinkUrl,
  ImageLinkText,
  ImageLinkUrlStart,
  ImageLinkUrl,
}

export class MessageBuffer {
  private state: State = State.Bypass;
  public message: string;
  public buffer: string = '';

  constructor(initialMessage: string = '') {
    this.message = initialMessage;
  }

  reinitialize(initialMessage: string = '') {
    this.state = State.Bypass;
    this.message = initialMessage;
    this.buffer = '';
  }

  public processDelta(delta: string) {
    for (const char of delta) {
      this.buffer += char;

      switch (this.state) {
        case State.Bypass:
          if (char === '[') {
            this.state = State.LinkText;
          } else if (char === '!') {
            this.state = State.PotentialImageLink;
          }
          break;
        case State.PotentialImageLink:
          if (char === '[') {
            this.state = State.ImageLinkText;
          } else {
            this.state = State.Bypass;
          }
          break;
        case State.LinkText:
          if (char === ']') {
            this.state = State.LinkUrlStart;
          }
          break;
        case State.LinkUrlStart:
          if (char === '(') {
            this.state = State.LinkUrl;
          } else {
            this.state = State.Bypass;
          }
          break;
        case State.LinkUrl:
          if (char === ')') {
            this.state = State.Bypass;
          }
          break;
        case State.ImageLinkText:
          if (char === ']') {
            this.state = State.ImageLinkUrlStart;
          }
          break;
        case State.ImageLinkUrlStart:
          if (char === '(') {
            this.state = State.ImageLinkUrl;
          } else {
            this.state = State.Bypass;
          }
          break;
        case State.ImageLinkUrl:
          if (char === ')') {
            this.state = State.Bypass;
          }
          break;
      }

      if (this.state === State.Bypass) {
        this.message += this.buffer;
        this.buffer = '';
      }
    }
  }
}
