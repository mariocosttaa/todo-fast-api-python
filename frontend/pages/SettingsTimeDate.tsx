import React, { useState } from 'react';
import { SettingsLayout } from '../components/settings/SettingsLayout';
import { Button } from '../components/UI';
import { getUserTimezone, setUserTimezone, getUserHourFormat, setUserHourFormat, HourFormat } from '../utils/timezone';
import { useNotification } from '../components/Notifications';

export const SettingsTimeDate: React.FC = () => {
  const { showNotification } = useNotification();

  const [timezone, setTimezone] = useState<string>(() => getUserTimezone());
  const [hourFormat, setHourFormat] = useState<HourFormat>(() => getUserHourFormat());
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSave = () => {
    try {
      const trimmed = timezone.trim();
      if (!trimmed) {
        setMessage({ type: 'error', text: 'Timezone cannot be empty.' });
        return;
      }
      setUserTimezone(trimmed);
      setUserHourFormat(hourFormat);
      setMessage({ type: 'success', text: 'Time & date preferences saved.' });
      showNotification({
        title: 'Time & date updated',
        type: 'success',
        description: 'Your time & date preferences were updated.',
      });
    } catch {
      setMessage({ type: 'error', text: 'Failed to save timezone. Please try again.' });
    }
  };

  return (
    <SettingsLayout activeTab="time">
      <section className="glass-panel rounded-3xl overflow-hidden w-full animate-slide-up">
        <div className="p-8 border-b border-gray-100 bg-white/30 backdrop-blur-md">
          <h2 className="text-xl font-bold text-gray-900">Time &amp; Date</h2>
          <p className="text-sm text-gray-500 mt-1">Control how dates and times are displayed in your dashboard.</p>
        </div>

        <div className="p-8 space-y-8">
          <div className="animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <label className="block text-sm font-bold text-gray-700 mb-2">Timezone</label>
            <p className="text-xs text-gray-500 mb-3">We detected this from your browser. You can override it using the dropdown.</p>
            <div className="relative inline-block w-full sm:w-auto group">
              <select
                className="w-full sm:w-80 px-4 py-3 rounded-xl border border-gray-200 bg-white/50 backdrop-blur-sm text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 appearance-none pr-10 transition-all shadow-sm group-hover:shadow-md"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
              >
                <option value={timezone}>Current: {timezone}</option>
                <option disabled>──────────</option>
                <option value="UTC">UTC</option>
                <option value="Europe/Lisbon">Europe/Lisbon</option>
                <option value="Europe/London">Europe/London</option>
                <option value="Europe/Berlin">Europe/Berlin</option>
                <option value="America/Sao_Paulo">America/Sao_Paulo</option>
                <option value="America/New_York">America/New_York</option>
                <option value="America/Los_Angeles">America/Los_Angeles</option>
                <option value="America/Chicago">America/Chicago</option>
                <option value="Asia/Tokyo">Asia/Tokyo</option>
                <option value="Asia/Shanghai">Asia/Shanghai</option>
                <option value="Asia/Singapore">Asia/Singapore</option>
                <option value="Australia/Sydney">Australia/Sydney</option>
              </select>
              <span className="pointer-events-none absolute inset-y-0 right-3 flex items-center text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
              </span>
            </div>
          </div>

          <div className="animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <label className="block text-sm font-bold text-gray-700 mb-2">Hour format</label>
            <p className="text-xs text-gray-500 mb-3">Choose how hours are displayed across the app.</p>
            <div className="inline-flex items-center p-1.5 bg-gray-100/50 rounded-2xl border border-gray-200">
              <button
                type="button"
                onClick={() => setHourFormat('24')}
                className={`px-5 py-2 text-xs font-bold rounded-xl transition-all duration-300 ${
                  hourFormat === '24' 
                    ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10 scale-105' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'
                }`}
              >
                24-hour
              </button>
              <button
                type="button"
                onClick={() => setHourFormat('12')}
                className={`px-5 py-2 text-xs font-bold rounded-xl transition-all duration-300 ${
                  hourFormat === '12' 
                    ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10 scale-105' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-white/50'
                }`}
              >
                12-hour
              </button>
            </div>
          </div>

          {message && (
            <div className={`p-4 rounded-xl text-sm font-medium animate-fade-in ${message.type === 'success' ? 'bg-green-50 text-green-700 border border-green-100' : 'bg-red-50 text-red-700 border border-red-100'}`}>
              {message.text}
            </div>
          )}

          <div className="flex justify-end pt-4 border-t border-gray-100">
            <Button type="button" onClick={handleSave} className="w-full sm:w-auto px-8 py-2.5 shadow-lg shadow-primary-500/30">
              Save Time &amp; Date
            </Button>
          </div>
        </div>
      </section>
    </SettingsLayout>
  );
};
