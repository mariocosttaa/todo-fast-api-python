import React, { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import BaseTemplate from '../components/template/BaseTemplate';
import { useAuth } from '../providers/AuthProvider';
import { useNotification } from '../components/Notifications';
import { ApiTodo, fetchTodayTodos, updateTodoCompleted, deleteTodo, updateTodo, updateTodoOrder } from '../services/todo';
import { Priority, Todo } from '../types';
import { formatIsoForUser } from '../utils/timezone';
import { Icons } from '../components/UI';

export const Today: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const { showNotification } = useNotification();

  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  
  // Infinite scroll state
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const mapApiTodoToTodo = useCallback((apiTodo: ApiTodo): Todo => {
    const createdAt = Date.now();
    return {
      id: apiTodo.id,
      text: apiTodo.title,
      completed: apiTodo.is_completed,
      createdAt,
      title: apiTodo.title,
      description: apiTodo.description ?? undefined,
      dueDate: apiTodo.due_date ?? undefined,
      order: apiTodo.order,
      priority: apiTodo.priority,
    };
  }, []);

  // derive priority from route query
  const searchParams = new URLSearchParams(location.search);
  const priorityParam = searchParams.get('priority');
  const priorityFilter: Priority | null =
    priorityParam === 'high' || priorityParam === 'medium' || priorityParam === 'low'
      ? (priorityParam as Priority)
      : null;

  const setPriorityInUrl = (value: Priority | null) => {
    const params = new URLSearchParams(location.search);
    if (value) params.set('priority', value);
    else params.delete('priority');
    const qs = params.toString();
    navigate(`${location.pathname}${qs ? `?${qs}` : ''}`);
  };

  useEffect(() => {
    const loadToday = async () => {
      if (!user) return;
      try {
        setLoading(true);
        setError(null);

        const params: { priority?: Priority; page: number; page_size: number } = {
          page: 1,
          page_size: 20,
        };
        
        if (priorityFilter) {
          params.priority = priorityFilter;
        }

        const response = await fetchTodayTodos(params);
        const mapped = response.items.map(mapApiTodoToTodo);
        setTodos(mapped);
        
        // Reset pagination state
        setCurrentPage(1);
        setHasMore(response.items.length >= params.page_size);
      } catch (e) {
        setError('Unable to load today\'s tasks right now.');
        showNotification({
          title: 'Error loading today\'s tasks',
          type: 'error',
          description: 'Please try again in a moment.',
        });
      } finally {
        setLoading(false);
      }
    };

    loadToday();
  }, [user, priorityFilter, mapApiTodoToTodo, showNotification]);

  // Infinite scroll effect
  useEffect(() => {
    const loadMoreTodos = async () => {
      if (loadingMore || !hasMore || loading) return;

      try {
        setLoadingMore(true);

        const params: { priority?: Priority; page: number; page_size: number } = {
          page: currentPage + 1,
          page_size: 20,
        };

        if (priorityFilter) {
          params.priority = priorityFilter;
        }

        const response = await fetchTodayTodos(params);
        const mapped: Todo[] = response.items.map(mapApiTodoToTodo);
        
        if (mapped.length > 0) {
          setTodos(prev => [...prev, ...mapped]);
          setCurrentPage(prev => prev + 1);
        }
        
        setHasMore(response.items.length >= params.page_size);
      } catch (e) {
        console.error('Failed to load more today todos:', e);
      } finally {
        setLoadingMore(false);
      }
    };

    const handleScroll = () => {
      const scrollTop = window.scrollY;
      const windowHeight = window.innerHeight;
      const documentHeight = document.documentElement.scrollHeight;

      // Trigger when user is 300px from bottom
      if (scrollTop + windowHeight >= documentHeight - 300) {
        loadMoreTodos();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [currentPage, hasMore, loadingMore, loading, priorityFilter, mapApiTodoToTodo]);

  const toggleTodo = async (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const nextCompleted = !todo.completed;
    setTodos(prev => prev.map(t => t.id === id ? { ...t, completed: nextCompleted } : t));

    try {
      await updateTodoCompleted(id, nextCompleted);
    } catch (e) {
      setError('Unable to update task status.');
      showNotification({ title: 'Update failed', type: 'error', description: 'Unable to update task status.' });
    }
  };

  const deleteTodoHandler = async (id: string) => {
    const previous = todos;
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await deleteTodo(id);
    } catch (e) {
      setError('Unable to delete task.');
      showNotification({ title: 'Delete failed', type: 'error', description: 'Unable to delete task.' });
      setTodos(previous);
    }
  };

  const openEditModal = (todo: Todo) => {
    setEditingTodo(todo);
    setEditTitle(todo.text);
    setEditDescription(todo.description ?? '');
  };

  const closeEditModal = () => {
    setEditingTodo(null);
    setEditTitle('');
    setEditDescription('');
  };

  const handleEditSave = async () => {
    if (!editingTodo) return;
    try {
      setError(null);

      const payload = {
        title: editTitle.trim() || editingTodo.text,
        description: editDescription.trim() || undefined,
        priority: editingTodo.priority,
        due_date: editingTodo.dueDate || null,
      };

      const updated = await updateTodo(editingTodo.id, payload);
      const mapped = mapApiTodoToTodo(updated);

      setTodos(prev => prev.map(t => (t.id === editingTodo.id ? mapped : t)));
      closeEditModal();
      showNotification({ title: 'Task updated', type: 'success', description: 'Your task was updated successfully.' });
    } catch (e) {
      setError('Unable to update task.');
      showNotification({ title: 'Update failed', type: 'error', description: 'Unable to update task.' });
    }
  };

  const moveTodo = async (id: string, direction: 'up' | 'down') => {
    const index = todos.findIndex(t => t.id === id);
    if (index === -1) return;

    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= todos.length) return;

    const newTodos = [...todos];
    const [removed] = newTodos.splice(index, 1);
    newTodos.splice(targetIndex, 0, removed);

    const reordered = newTodos.map((t, idx) => ({ ...t, order: idx + 1 }));
    setTodos(reordered);

    const movedTodo = reordered.find(t => t.id === removed.id);
    const newOrder = movedTodo ? movedTodo.order : targetIndex + 1;

    try {
      await updateTodoOrder(removed.id, newOrder);
    } catch (e) {
      setError('Unable to update task order.');
      showNotification({ title: 'Reorder failed', type: 'error', description: 'Unable to update task order.' });
    }
  };

  if (!user) return null;

  const filteredTodos = todos.filter((t) => {
    const matchesSearch = t.text.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesSearch) return false;
    if (priorityFilter && t.priority !== priorityFilter) return false;
    return true;
  });

  const pageTitle = "Today's Tasks";
  const pageDescription = `Focus mode: tasks due today for ${user.name.split(' ')[0]}.`;

  const getPriorityColor = (p: Priority) => {
    switch (p) {
      case 'high':
        return 'bg-gradient-to-r from-red-500 to-red-600 text-white border-transparent shadow-sm';
      case 'medium':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'low':
        return 'bg-sky-50 text-sky-700 border-sky-200';
    }
  };

  const formatDueDate = (value?: string) => {
    if (!value) return '';
    return formatIsoForUser(value, true, true);
  };

  return (
    <BaseTemplate
      title={pageTitle}
      description={pageDescription}
      isSettingsRoute={false}
      showSearch
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      <div className="mb-8 flex flex-wrap gap-2 items-center animate-slide-up">
        <span className="text-xs font-semibold text-gray-500 mr-2 uppercase tracking-wider">Priority</span>
        <div className="inline-flex items-center gap-1 bg-white/50 backdrop-blur-sm p-1 rounded-xl shadow-sm border border-white/60">
          <button
            type="button"
            onClick={() => setPriorityInUrl(null)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 ${
              !priorityFilter
                ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            All
          </button>
          <button
            type="button"
            onClick={() => setPriorityInUrl('high')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 ${
              priorityFilter === 'high'
                ? 'bg-red-50 text-red-700 shadow-md shadow-red-500/10'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            High
          </button>
          <button
            type="button"
            onClick={() => setPriorityInUrl('medium')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 ${
              priorityFilter === 'medium'
                ? 'bg-amber-50 text-amber-700 shadow-md shadow-amber-500/10'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            Medium
          </button>
          <button
            type="button"
            onClick={() => setPriorityInUrl('low')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 ${
              priorityFilter === 'low'
                ? 'bg-sky-50 text-sky-700 shadow-md shadow-sky-500/10'
                : 'text-gray-600 hover:bg-white/50'
            }`}
          >
            Low
          </button>
        </div>
      </div>

      <div className="space-y-4 pb-20">
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-500 text-sm font-medium">Loading today&apos;s tasks...</p>
          </div>
        )}

        {!loading && filteredTodos.length === 0 && !error && (
          <div className="text-center py-20 animate-fade-in">
            <div className="mx-auto w-24 h-24 bg-white/50 rounded-full flex items-center justify-center mb-6 text-primary-200 shadow-inner">
              <Icons.List />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No tasks for today</h3>
            <p className="text-gray-500 max-w-xs mx-auto text-sm">
              You&apos;re all caught up. Plan something or relax.
            </p>
          </div>
        )}

        {error && !loading && (
          <div className="text-center py-10 text-red-500 text-sm bg-red-50/50 rounded-xl border border-red-100">{error}</div>
        )}

        {filteredTodos.map((todo, index) => (
          <div
            key={todo.id}
            style={{ animationDelay: `${index * 0.05}s` }}
            className={`group flex items-center glass-panel p-4 rounded-2xl transition-all duration-300 hover:shadow-lg hover:shadow-primary-500/5 hover:border-primary-200 animate-slide-up ${
              todo.completed
                ? 'border-gray-100 bg-gray-50/50 opacity-60'
                : 'border-white/60'
            }`}
          >
            <button
              onClick={() => toggleTodo(todo.id)}
              className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 mr-4 ${
                todo.completed
                  ? 'bg-primary-500 border-primary-500 text-white scale-110 shadow-sm shadow-primary-500/30'
                  : 'border-gray-300 text-transparent hover:border-primary-500 hover:text-primary-500'
              }`}
              aria-label={todo.completed ? 'Mark as active' : 'Mark as completed'}
            >
              <Icons.Check />
            </button>
            <div className="flex-1 min-w-0">
              <p
                className={`text-base font-medium truncate transition-colors ${
                  todo.completed ? 'text-gray-400 line-through' : 'text-gray-900'
                }`}
              >
                {todo.text}
              </p>
              {todo.description && (
                <p className="mt-1 text-sm text-gray-500 truncate">{todo.description}</p>
              )}
              {todo.dueDate && (
                <p className="mt-2 text-xs font-medium text-primary-600 flex items-center gap-1.5 bg-primary-50 inline-flex px-2 py-0.5 rounded-md">
                  <span>🗓</span>
                  Due at {formatDueDate(todo.dueDate)}
                </p>
              )}
            </div>
            <div className="flex items-center gap-1 ml-4 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <span
                className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider border ${getPriorityColor(
                  todo.priority,
                )}`}
              >
                {todo.priority}
              </span>
              <div className="w-px h-4 bg-gray-200 mx-2"></div>
              <button
                onClick={() => moveTodo(todo.id, 'up')}
                disabled={index === 0}
                className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-30"
                aria-label="Move up"
              >
                ↑
              </button>
              <button
                onClick={() => moveTodo(todo.id, 'down')}
                disabled={index === filteredTodos.length - 1}
                className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors disabled:opacity-30"
                aria-label="Move down"
              >
                ↓
              </button>
              <button
                onClick={() => openEditModal(todo)}
                className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                aria-label="Edit task"
              >
                <Icons.Edit />
              </button>
              <button
                onClick={() => deleteTodoHandler(todo.id)}
                className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
                aria-label="Delete task"
              >
                <Icons.Trash />
              </button>
            </div>
          </div>
        ))}
        
        {/* Infinite scroll indicators */}
        {!loading && filteredTodos.length > 0 && (
          <>
            {loadingMore && (
              <div className="text-center py-8 animate-fade-in">
                <div className="inline-flex items-center gap-3 px-4 py-2 bg-white/80 backdrop-blur-sm rounded-full shadow-sm border border-gray-100">
                  <div className="w-4 h-4 border-2 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                  <span className="text-sm font-medium text-gray-600">Loading more tasks...</span>
                </div>
              </div>
            )}
            
            {!hasMore && !loadingMore && (
              <div className="text-center py-8 animate-fade-in">
                <p className="text-sm font-medium text-gray-400 bg-gray-50/50 inline-block px-4 py-1 rounded-full">
                  ✓ All tasks loaded
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {editingTodo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20 backdrop-blur-sm animate-fade-in">
          <div className="glass-panel rounded-3xl shadow-2xl w-full max-w-lg p-8 space-y-6 animate-slide-up">
            <h3 className="text-xl font-bold text-gray-900">Edit task</h3>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Title</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  placeholder="Task title"
                  className="w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl text-gray-900 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Description</label>
                <input
                  type="text"
                  value={editDescription}
                  onChange={(e) => setEditDescription(e.target.value)}
                  placeholder="Description (optional)"
                  className="w-full px-4 py-3 bg-white/50 border border-gray-200 rounded-xl text-gray-900 focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all"
                />
              </div>
            </div>
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
              <button
                type="button"
                onClick={closeEditModal}
                className="px-5 py-2.5 rounded-xl text-sm font-medium text-gray-600 hover:bg-gray-100 transition-colors"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEditSave}
                className="px-6 py-2.5 rounded-xl text-sm font-semibold bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-500/30 transition-all"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </BaseTemplate>
  );
};
