import { RefObject, useEffect, useState } from 'react';

const useMousePosition = <T extends HTMLElement = HTMLElement>(ref: RefObject<T>) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const updateMousePosition = (e: MouseEvent) => {
      const offsetTop = ref.current?.getBoundingClientRect().top || 0;
      const offsetLeft = ref.current?.getBoundingClientRect().left || 0;
      setMousePosition({ x: e.clientX - offsetLeft, y: e.clientY - offsetTop });
    };

    window.addEventListener('mousemove', updateMousePosition);

    return () => {
      window.removeEventListener('mousemove', updateMousePosition);
    };
  }, [ref]);

  return mousePosition;
};

export default useMousePosition;
