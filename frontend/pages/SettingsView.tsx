import React, { useState } from 'react';
import { User } from '../types';
import { Button, Input, Avatar } from '../components/UI';

interface SettingsViewProps {
  user: User;
  onUpdateUser: (user: Partial<User>) => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ user, onUpdateUser }) => {
  // Profile State
  const [name, setName] = useState(user.name);
  const [isProfileSaving, setIsProfileSaving] = useState(false);
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Password State
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isPasswordSaving, setIsPasswordSaving] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMessage(null);
    setIsProfileSaving(true);

    // Simulate API delay
    setTimeout(() => {
      onUpdateUser({ name });
      setProfileMessage({ type: 'success', text: 'Profile updated successfully!' });
      setIsProfileSaving(false);
    }, 600);
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMessage(null);
    setIsPasswordSaving(true);

    if (newPassword !== confirmPassword) {
      setPasswordMessage({ type: 'error', text: 'New passwords do not match' });
      setIsPasswordSaving(false);
      return;
    }

    // Simulate API delay
    setTimeout(() => {
      setPasswordMessage({ type: 'success', text: 'Password changed successfully!' });
      setIsPasswordSaving(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    }, 800);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Account Settings</h1>
        <p className="text-gray-500">Manage your profile and security preferences.</p>
      </header>

      {/* Profile Section */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-lg font-bold text-gray-900">Profile Information</h2>
          <p className="text-sm text-gray-500">Update your account's public profile information.</p>
        </div>
        
        <div className="p-6">
          <div className="flex items-center space-x-6 mb-8">
            <Avatar name={name} size="xl" />
            <div>
              <h3 className="text-xl font-bold text-gray-900">{name}</h3>
              <p className="text-gray-500">{user.email}</p>
            </div>
          </div>

          <form onSubmit={handleProfileSubmit} className="space-y-6">
            <Input 
              label="Full Name" 
              value={name} 
              onChange={(e) => setName(e.target.value)} 
            />
            <Input 
              label="Email Address" 
              value={user.email} 
              disabled 
              className="bg-gray-100 text-gray-500 cursor-not-allowed" 
            />

            {profileMessage && (
              <div className={`p-4 rounded-xl text-sm font-medium ${profileMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {profileMessage.text}
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit" isLoading={isProfileSaving} className="w-full sm:w-auto">
                Save Profile
              </Button>
            </div>
          </form>
        </div>
      </section>

      {/* Security Section */}
      <section className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-lg font-bold text-gray-900">Security</h2>
          <p className="text-sm text-gray-500">Ensure your account is using a long, random password to stay secure.</p>
        </div>

        <div className="p-6">
          <form onSubmit={handlePasswordSubmit} className="space-y-6">
            <Input 
              label="Current Password" 
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input 
                label="New Password" 
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="New password"
                required
                minLength={8}
              />
              <Input 
                label="Confirm New Password" 
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
                minLength={8}
              />
            </div>

            {passwordMessage && (
              <div className={`p-4 rounded-xl text-sm font-medium ${passwordMessage.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                {passwordMessage.text}
              </div>
            )}

            <div className="flex justify-end">
              <Button type="submit" variant="secondary" isLoading={isPasswordSaving} className="w-full sm:w-auto text-gray-700 border-gray-300 hover:bg-gray-50">
                Update Password
              </Button>
            </div>
          </form>
        </div>
      </section>
    </div>
  );
};