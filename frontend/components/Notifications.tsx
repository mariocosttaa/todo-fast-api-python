import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  title: string;
  type: NotificationType;
  description?: string;
  duration?: number;
}

interface NotificationContextValue {
  notifications: Notification[];
  showNotification: (options: {
    title: string;
    type: NotificationType;
    description?: string;
    duration?: number;
  }) => void;
  removeNotification: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const showNotification = useCallback(
    ({ title, type, description, duration }: { title: string; type: NotificationType; description?: string; duration?: number }) => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      const timeout = duration ?? 5000;

      const notification: Notification = {
        id,
        title,
        type,
        description,
        duration: timeout,
      };

      setNotifications(prev => [...prev, notification]);

      if (timeout > 0) {
        window.setTimeout(() => {
          removeNotification(id);
        }, timeout);
      }
    },
    [removeNotification]
  );

  const value = useMemo(
    () => ({ notifications, showNotification, removeNotification }),
    [notifications, showNotification, removeNotification]
  );

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationList />
    </NotificationContext.Provider>
  );
};

export const useNotification = (): NotificationContextValue => {
  const ctx = useContext(NotificationContext);
  if (!ctx) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return ctx;
};

const NotificationList: React.FC = () => {
  const { notifications, removeNotification } = useNotification();

  if (!notifications.length) return null;

  return (
    <div className="fixed inset-0 pointer-events-none flex items-start justify-end px-4 py-6 sm:p-6 z-50">
      <div className="w-full max-w-sm space-y-3">
        {notifications.map(notification => (
          <NotificationItem
            key={notification.id}
            notification={notification}
            onClose={() => removeNotification(notification.id)}
          />
        ))}
      </div>
    </div>
  );
};

const NotificationItem: React.FC<{ notification: Notification; onClose: () => void }> = ({ notification, onClose }) => {
  const { title, description, type } = notification;

  const typeStyles: Record<NotificationType, string> = {
    success: 'bg-emerald-50/90 border-emerald-200 text-emerald-900 shadow-emerald-500/10',
    error: 'bg-red-50/90 border-red-200 text-red-900 shadow-red-500/10',
    warning: 'bg-amber-50/90 border-amber-200 text-amber-900 shadow-amber-500/10',
    info: 'bg-blue-50/90 border-blue-200 text-blue-900 shadow-blue-500/10',
  };

  const iconStyles: Record<NotificationType, React.ReactNode> = {
    success: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-600"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>,
    error: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-600"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>,
    warning: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
    info: <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-blue-600"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
  };

  return (
    <div className={`pointer-events-auto w-full rounded-2xl border shadow-lg backdrop-blur-md px-4 py-4 flex items-start gap-3 animate-slide-up ${typeStyles[type]}`}>
      <div className="flex-shrink-0 mt-0.5">
        {iconStyles[type]}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold truncate">{title}</p>
        {description && <p className="mt-1 text-sm leading-snug opacity-90 break-words">{description}</p>}
      </div>
      <button
        type="button"
        onClick={onClose}
        className="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
  );
};
