import { SVGProps } from 'react';

const NoInternet = (props: SVGProps<SVGSVGElement>): React.ReactElement => {
  return (
    <svg {...props} width="48" height="49" viewBox="0 0 48 49" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M24 44.668C35.0457 44.668 44 35.7137 44 24.668C44 13.6223 35.0457 4.66797 24 4.66797C12.9543 4.66797 4 13.6223 4 24.668C4 35.7137 12.9543 44.668 24 44.668Z"
        stroke="#737373"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M24 4.66797C18.8645 10.0603 16 17.2214 16 24.668C16 32.1145 18.8645 39.2757 24 44.668C29.1355 39.2757 32 32.1145 32 24.668C32 17.2214 29.1355 10.0603 24 4.66797Z"
        stroke="#737373"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M4 24.668H44" stroke="#737373" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d="M45.3871 3.28076L2.6123 46.0551"
        stroke="#737373"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default NoInternet;
