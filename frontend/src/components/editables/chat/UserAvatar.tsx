import { useEffect, useState } from 'react';
import ky from 'ky';
import { useAPIStore } from '@/store/useAPIStore';
import { cn } from '@/utils/common/cn';

interface UserAvatarProps {
  email?: string;
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
}

interface AvatarResponse {
  avatar_url: string;
  username: string;
  gravatar: boolean;
}

const avatarCache = new Map();

export function UserAvatar({ email, title, type, className }: UserAvatarProps) {
  const [avatarURL, setAvatarURL] = useState('');
  const getBaseURL = useAPIStore((state) => state.getBaseURL);

  useEffect(() => {
    const fetchAvatar = async () => {
      if (email && avatarCache.has(email)) {
        setAvatarURL(avatarCache.get(email));
        return;
      }
      try {
        const response = await ky
          .get(`${getBaseURL()}/profile`, { searchParams: email ? { email } : undefined })
          .json<AvatarResponse>();
        if (!response.gravatar) {
          response.avatar_url = `${getBaseURL()}/${response.avatar_url}`;
        }
        avatarCache.set(email, response.avatar_url);
        setAvatarURL(response.avatar_url);
      } catch (error) {
        console.error('Error fetching avatar URL:', error);
      }
    };

    fetchAvatar();
  }, [email, getBaseURL]);

  return (
    <img
      title={title}
      src={avatarURL}
      className={cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
        'w-20 h-20 ': type === 'large',
        'w-16 h-16': type === 'small',
        'w-6 h-6': type === 'extraSmall',
      })}
    />
  );
}
