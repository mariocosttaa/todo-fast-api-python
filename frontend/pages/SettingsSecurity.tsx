import React, { useState } from 'react';
import { SettingsLayout } from '../components/settings/SettingsLayout';
import { Input, Button } from '../components/UI';
import { useNotification } from '../components/Notifications';
import { updatePassword } from '../services/user';

export const SettingsSecurity: React.FC = () => {
  const { showNotification } = useNotification();

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setFieldErrors({});
    setIsSaving(true);

    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      setIsSaving(false);
      return;
    }

    try {
      await updatePassword({
        old_password: currentPassword,
        password: newPassword,
        password_confirm: confirmPassword,
      });

      setMessage({ type: 'success', text: 'Password changed successfully!' });
      showNotification({
        title: 'Password updated',
        type: 'success',
        description: 'Your password was changed successfully.',
      });
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
        const msg = typeof detail === 'string' ? detail : 'Failed to change password. Please try again.';
        setMessage({ type: 'error', text: msg });
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <SettingsLayout activeTab="security">
      <section className="glass-panel rounded-3xl overflow-hidden w-full animate-slide-up">
        <div className="p-8 border-b border-gray-100 bg-white/30 backdrop-blur-md">
          <h2 className="text-xl font-bold text-gray-900">Security</h2>
          <p className="text-sm text-gray-500 mt-1">Ensure your account is using a long, random password to stay secure.</p>
        </div>

        <div className="p-8">
          <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
            <Input
              label="Current Password"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
              required
              error={fieldErrors.old_password}
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
                required
                minLength={8}
                error={fieldErrors.password}
              />
              <Input
                label="Confirm New Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter new password"
                required
                minLength={8}
                error={fieldErrors.password_confirm}
              />
            </div>

            {message && (
              <div className={`p-4 rounded-xl text-sm font-medium animate-fade-in ${message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
                {message.text}
              </div>
            )}

            <div className="flex justify-end pt-4">
              <Button
                type="submit"
                variant="secondary"
                isLoading={isSaving}
                className="w-full sm:w-auto px-8 py-2.5 shadow-sm hover:shadow-md"
              >
                Update Password
              </Button>
            </div>
          </form>
        </div>
      </section>
    </SettingsLayout>
  );
};
