import React, { useEffect, useState } from 'react';
import { SettingsLayout } from '../components/settings/SettingsLayout';
import { Input, Avatar, Button } from '../components/UI';
import { useAuth } from '../providers/AuthProvider';
import { useNotification } from '../components/Notifications';
import { updateProfile } from '../services/user';

export const SettingsProfile: React.FC = () => {
  const { user, setUser } = useAuth();
  const { showNotification } = useNotification();

  const [name, setName] = useState(user?.name ?? '');
  const [email, setEmail] = useState(user?.email ?? '');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (user?.name) setName(user.name);
    if (user?.email) setEmail(user.email);
  }, [user?.name, user?.email]);

  if (!user) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setFieldErrors({});
    setIsSaving(true);

    try {
      const trimmedName = name.trim();
      const [first, ...rest] = trimmedName.split(' ');
      const surname = rest.join(' ') || first;

      const updatedUser = await updateProfile({
        name: first,
        surname,
        email: email.trim(),
      });

      setUser(prev => (prev ? { ...prev, name: updatedUser.name, email: updatedUser.email } : prev));
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      showNotification({ title: 'Profile updated', type: 'success', description: 'Your profile information was updated.' });
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      if (Array.isArray(detail)) {
        const errors: Record<string, string> = {};
        detail.forEach((error: any) => {
          const field = error.loc?.[1];
          if (field) errors[field] = error.msg;
        });
        setFieldErrors(errors);
        setMessage(null);
      } else {
        const msg = typeof detail === 'string' ? detail : 'Failed to update profile. Please try again.';
        setMessage({ type: 'error', text: msg });
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SettingsLayout activeTab="profile">
      <section className="glass-panel rounded-3xl overflow-hidden w-full animate-slide-up">
        <div className="p-8 border-b border-gray-100 bg-white/30 backdrop-blur-md">
          <h2 className="text-2xl font-bold text-gray-900">Profile Information</h2>
          <p className="text-sm text-gray-500 mt-1">Update your account's public profile information.</p>
        </div>

        <div className="p-8">
          <div className="flex items-center space-x-6 mb-10 animate-fade-in">
            <Avatar name={name} size="xl" className="shadow-lg shadow-primary-500/20" />
            <div>
              <h3 className="text-2xl font-bold text-gray-900">{name}</h3>
              <p className="text-gray-500">{user.email}</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
            <div className="grid gap-6">
              <Input
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                error={fieldErrors.name}
              />
              <Input
                label="Email Address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={fieldErrors.email}
              />
            </div>

            {message && (
              <div className={`p-4 rounded-xl text-sm font-medium animate-fade-in ${message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
                {message.text}
              </div>
            )}

            <div className="flex justify-end pt-4">
              <Button type="submit" isLoading={isSaving} className="w-full sm:w-auto px-8 py-2.5 shadow-lg shadow-primary-500/30">
                Save Profile
              </Button>
            </div>
          </form>
        </div>
      </section>
    </SettingsLayout>
  );
};
