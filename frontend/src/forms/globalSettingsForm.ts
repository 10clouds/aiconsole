import { z } from 'zod';

export const GlobalSettingsFormSchema = z.object({
  user_profile: z.object({
    display_name: z.string().optional(),
    avatarBase64: z.string().optional(),
  }),
  openai_api_key: z.string().min(1, { message: 'API key cannot be empty' }),
  code_autorun: z.boolean(),
  avatar: z.instanceof(File).optional(),
});

export type GlobalSettingsFormData = z.infer<typeof GlobalSettingsFormSchema>;
