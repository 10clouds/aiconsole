enum State {
  Bypass,
  LinkText,
  LinkUrlStart,
  LinkUrl,
}

export const bufferMessage = (message: string) => {
  let buffer = '';
  let state = State.Bypass;

  return (delta: string) => {
    for (const char of delta) {
      buffer += char;

      console.log('processing char: ', char);

      switch (state) {
        case State.Bypass:
          if (char === '[') {
            console.log('bypass -> link text');
            state = State.LinkText;
          }
          break;
        case State.LinkText:
          if (char === ']') {
            console.log('link text -> link url start');
            state = State.LinkUrlStart;
          }
          break;
        case State.LinkUrlStart:
          if (char === '(') {
            console.log('link url start -> link url');
            state = State.LinkUrl;
          } else {
            console.log('link url start -> bypass');
            state = State.Bypass;
          }
          break;
        case State.LinkUrl:
          console.log('link url -> bypass');
          if (char === ')') {
            state = State.Bypass;
          }
          break;
      }

      if (state === State.Bypass) {
        message += buffer;
        buffer = '';
      }
    }

    return message;
  };
};
