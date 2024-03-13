import { useAssetStore } from '@/store/assets/useAssetStore';
import { useSettingsStore } from '@/store/settings/useSettingsStore';
import { useAPIStore } from '@/store/useAPIStore';
import { AICUserProfile } from '@/types/assets/assetTypes';
import { cn } from '@/utils/common/cn';

interface ActorAvatarProps {
  actorId?: string;
  title?: string;
  type: 'large' | 'small' | 'extraSmall';
  className?: string;
  actorType: 'agent' | 'user';
}

export function ActorAvatar({ actorId, title, type, className, actorType }: ActorAvatarProps) {
  const getBaseURL = useAPIStore((state) => state.getBaseURL);
  const actor = useAssetStore((state) => state.getAsset(actorId || ''));
  const userProfile = useSettingsStore((state) => state.settings.user_profile);
  const userID = userProfile.id;

  let src: string | undefined = '';

  if (actorType === 'agent') {
    src = `${getBaseURL()}/api/assets/${actorId}/image?version=${actor?.version}`;
    className = cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
      'w-20 h-20 ': type === 'large',
      'w-16 h-16': type === 'small',
      'w-6 h-6': type === 'extraSmall',
      'border-[2px] border-agent shadow-agent': false,
      'shadow-md': true,
      hidden: !actorId,
    });
  } else if (actorType === 'user') {
    if (actorId && (actorId === userID || actorId === 'user')) {
      src = userProfile?.profile_picture;
    } else {
      const user = actor as AICUserProfile | undefined;
      if (user) {
        src = user.profile_picture;
      } else {
        src = `${getBaseURL()}/api/assets/0/image?version=0`;
      }
    }
    className = cn(className, 'rounded-full mb-[10px] mt-[5px] border border-slate-800', {
      'w-20 h-20 ': type === 'large',
      'w-16 h-16': type === 'small',
      'w-6 h-6': type === 'extraSmall',
    });
  }

  return <img title={title} src={src} className={className} />;
}
