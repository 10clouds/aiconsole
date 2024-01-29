import { z } from 'zod';

export const GlobalSettingsFormSchema = z.object({
  user_profile: z.object({
    username: z.string().optional(),
    email: z.string().email().optional().or(z.literal('')),
  }),
  openai_api_key: z.string().min(1, { message: 'API key cannot be empty' }),
  code_autorun: z.boolean(),
  avatar: z.instanceof(File).optional(),
  avatarUrl: z.string().optional(),
});

export type GlobalSettingsFormData = z.infer<typeof GlobalSettingsFormSchema>;
