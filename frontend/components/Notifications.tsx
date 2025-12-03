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
    success: 'bg-emerald-50 border-emerald-200 text-emerald-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900',
  };

  return (
    <div className={`pointer-events-auto w-full rounded-xl border shadow-lg px-4 py-3 flex items-start justify-between gap-3 ${typeStyles[type]}`}>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold truncate">{title}</p>
        {description && <p className="mt-1 text-sm leading-snug opacity-90 break-words">{description}</p>}
      </div>
      <button
        type="button"
        onClick={onClose}
        className="ml-2 inline-flex text-xs font-medium opacity-70 hover:opacity-100 transition-opacity"
      >
        Close
      </button>
    </div>
  );
};
