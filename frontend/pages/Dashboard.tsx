import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { FilterType, Todo, User, Priority } from '../types';
import { Button, Input, Icons, InputError } from '../components/UI';
import { useNotification } from '../components/Notifications';
import { useAuth } from '../providers/AuthProvider';
import { Setting } from './Setting';
import BaseTemplate from '../components/template/BaseTemplate';
import { fetchTodos, fetchTodayTodos, createTodo, updateTodoCompleted, deleteTodo, updateTodoOrder, updateTodo, ApiTodo } from '../services/todo';
import { localInputToUtcIso, formatIsoForUser, getTodayEndLocalInput, getTomorrowEndLocalInput, getNextWeekdayEndLocalInput } from '../utils/timezone';

export const Dashboard: React.FC = () => {
  // --- Routing ---
  const location = useLocation();

  const isSettingsRoute = location.pathname.endsWith('/settings');

  // --- Auth ---
  const { user, setUser } = useAuth();
  const { showNotification } = useNotification();

  // --- State ---

  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [formInputError, setFormInputError] = useState<Record<string, string>>({});
  
  // Infinite scroll state
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const [inputValue, setInputValue] = useState('');
  const [inputDescription, setInputDescription] = useState('');
  const [inputDueDate, setInputDueDate] = useState('');
  const [inputPriority, setInputPriority] = useState<Priority>('medium');
  const [filter, setFilter] = useState<FilterType>(FilterType.ALL);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Drag and Drop State
  const [draggedItemId, setDraggedItemId] = useState<string | null>(null);
  
  // Track tasks that were recently completed
  const [recentlyCompleted, setRecentlyCompleted] = useState<Set<string>>(new Set());
  const [showUndoToast, setShowUndoToast] = useState(false);
  const [lastCompletedId, setLastCompletedId] = useState<string | null>(null);
  const { logout } = useAuth();
  const [isDueDatePickerOpen, setIsDueDatePickerOpen] = useState(false);
  const [tempDueDate, setTempDueDate] = useState(''); // YYYY-MM-DD
  const [tempDueTime, setTempDueTime] = useState(''); // HH:MM
  const [editingTodo, setEditingTodo] = useState<Todo | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPriority, setEditPriority] = useState<Priority>('medium');
  const [editDueDate, setEditDueDate] = useState(''); // YYYY-MM-DDTHH:MM

  // priority from route query (?priority=high|medium|low)
  const searchParams = new URLSearchParams(location.search);
  const priorityParam = searchParams.get('priority');
  const priorityFilter: Priority | null =
    priorityParam === 'high' || priorityParam === 'medium' || priorityParam === 'low'
      ? (priorityParam as Priority)
      : null;

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
 
  useEffect(() => {
    const loadTodos = async () => {
      try {
        setLoading(true);
        setError(null);

        // map UI filter state to backend query params
        let completed: boolean | undefined;
        if (filter === FilterType.ACTIVE) {
          completed = false; // active = not completed
        } else if (filter === FilterType.COMPLETED) {
          completed = true;
        }

        const params: {
          page: number;
          page_size: number;
          completed?: boolean;
          search?: string;
          priority?: Priority;
        } = {
          page: 1,
          page_size: 20,
        };

        if (typeof completed === 'boolean') {
          params.completed = completed;
        }

        if (searchQuery.trim()) {
          params.search = searchQuery.trim();
        }

        if (priorityFilter) {
          params.priority = priorityFilter;
        }

        const response = await fetchTodos(params);
        const mapped: Todo[] = response.items.map(mapApiTodoToTodo);
        setTodos(mapped);
        
        // Reset pagination state
        setCurrentPage(1);
        setHasMore(response.items.length >= params.page_size);
      } catch (e) {
        setError('Unable to load your tasks right now.');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      loadTodos();
    }
  }, [user, filter, searchQuery, priorityFilter, mapApiTodoToTodo]);

  // Infinite scroll effect
  useEffect(() => {
    const loadMoreTodos = async () => {
      if (loadingMore || !hasMore || loading) return;

      try {
        setLoadingMore(true);

        let completed: boolean | undefined;
        if (filter === FilterType.ACTIVE) {
          completed = false;
        } else if (filter === FilterType.COMPLETED) {
          completed = true;
        }

        const params: {
          page: number;
          page_size: number;
          completed?: boolean;
          search?: string;
          priority?: Priority;
        } = {
          page: currentPage + 1,
          page_size: 20,
        };

        if (typeof completed === 'boolean') {
          params.completed = completed;
        }

        if (searchQuery.trim()) {
          params.search = searchQuery.trim();
        }

        if (priorityFilter) {
          params.priority = priorityFilter;
        }

        const response = await fetchTodos(params);
        const mapped: Todo[] = response.items.map(mapApiTodoToTodo);
        
        if (mapped.length > 0) {
          setTodos(prev => [...prev, ...mapped]);
          setCurrentPage(prev => prev + 1);
        }
        
        setHasMore(response.items.length >= params.page_size);
      } catch (e) {
        console.error('Failed to load more todos:', e);
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
  }, [currentPage, hasMore, loadingMore, loading, filter, searchQuery, priorityFilter, mapApiTodoToTodo]);

  // --- Handlers ---
  const addTodo = async (text: string, priority: Priority = 'medium') => {
    if (!text.trim()) return;

    try {
      // clear any previous create error
      setError(null);
      setFormInputError({});

      // validate due date: must be strictly in the future (date + optional time)
      if (inputDueDate) {
        const now = new Date();
        const selected = new Date(inputDueDate);

        if (isNaN(selected.getTime()) || selected <= now) {
          const message = 'Due date must be after today.';
          setError(message);
          showNotification({ title: 'Invalid due date', type: 'error', description: message });
          return;
        }
      }

      const payload = {
        title: text.trim(),
        description: inputDescription.trim() || undefined,
        priority,
        due_date: localInputToUtcIso(inputDueDate) ,
      };

      const apiTodo = await createTodo(payload);
      const newTodo = mapApiTodoToTodo(apiTodo);
      setTodos(prev => [newTodo, ...prev]);
      // clear inputs only on successful create
      setInputValue('');
      setInputDescription('');
      setInputDueDate('');
      setError(null);
    } catch (err: any) {
      const erros = err?.response?.data?.detail;

      if (Array.isArray(erros)) {
        const fieldErrors: Record<string, string> = {};
        erros.forEach((error: any) => {
          const field = error.loc?.[1];
          if (field) {
            fieldErrors[field] = error.msg;
          }
        });
        setFormInputError(fieldErrors);
        setError(null);
        return;
      }

      const message = 'Unable to create task. Please try again.';
      setError(message);
      showNotification({ title: 'Task creation failed', type: 'error', description: message });
    }
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    // clear error when the user tries again
    setError(null);
    setFormInputError({});
    addTodo(inputValue, inputPriority);
  };

  const toggleTodo = async (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    const nextCompleted = !todo.completed;

    setTodos(prev => prev.map(t => t.id === id ? { ...t, completed: nextCompleted } : t));

    if (nextCompleted) {
      setRecentlyCompleted(prev => new Set(prev).add(id));
      setLastCompletedId(id);
      setShowUndoToast(true);

      setTimeout(() => {
        setRecentlyCompleted(prev => {
          const next = new Set(prev);
          next.delete(id);
          return next;
        });
        setShowUndoToast(false);
      }, 5000);
    } else {
      setRecentlyCompleted(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      setShowUndoToast(false);
    }

    try {
      await updateTodoCompleted(id, nextCompleted);
    } catch (e) {
      const message = 'Unable to update task status.';
      setError(message);
      showNotification({ title: 'Update failed', type: 'error', description: message });
    }
  };

  const cyclePriority = (id: string) => {
    setTodos(prev => prev.map(t => {
      if (t.id !== id) return t;
      const nextPriority: Priority = 
        t.priority === 'low' ? 'medium' : 
        t.priority === 'medium' ? 'high' : 'low';
      return { ...t, priority: nextPriority };
    }));
  };

  const undoLastCompletion = () => {
    if (lastCompletedId) {
      toggleTodo(lastCompletedId);
      setShowUndoToast(false);
      setLastCompletedId(null);
    }
  };

  const deleteTodoHandler = async (id: string) => {
    const previous = todos;
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await deleteTodo(id);
    } catch (e) {
      const message = 'Unable to delete task.';
      setError(message);
      showNotification({ title: 'Delete failed', type: 'error', description: message });
      setTodos(previous);
    }
  };

  const toLocalInputFromIso = (value?: string | null) => {
    if (!value) return '';
    const d = new Date(value);
    if (isNaN(d.getTime())) return '';
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60000);
    return local.toISOString().slice(0, 16);
  };

  const openEditModal = (todo: Todo) => {
    setEditingTodo(todo);
    setEditTitle(todo.text);
    setEditDescription(todo.description ?? '');
    setEditPriority(todo.priority);
    setEditDueDate(toLocalInputFromIso(todo.dueDate ?? undefined));
  };

  const closeEditModal = () => {
    setEditingTodo(null);
    setEditTitle('');
    setEditDescription('');
    setEditDueDate('');
  };

  const handleEditSave = async () => {
    if (!editingTodo) return;

    try {
      setError(null);

      if (editDueDate) {
        const now = new Date();
        const selected = new Date(editDueDate);
        if (isNaN(selected.getTime()) || selected <= now) {
          const message = 'Due date must be after today.';
          setError(message);
          showNotification({ title: 'Invalid due date', type: 'error', description: message });
          return;
        }
      }

      const payload = {
        title: editTitle.trim() || editingTodo.text,
        description: editDescription.trim() || undefined,
        priority: editPriority,
        due_date: localInputToUtcIso(editDueDate),
      };

      const updated = await updateTodo(editingTodo.id, payload);
      const mapped = mapApiTodoToTodo(updated);

      setTodos(prev => prev.map(t => (t.id === editingTodo.id ? mapped : t)));
      closeEditModal();
      showNotification({ title: 'Task updated', type: 'success', description: 'Your task was updated successfully.' });
    } catch (e) {
      const message = 'Unable to update task.';
      setError(message);
      showNotification({ title: 'Update failed', type: 'error', description: message });
    }
  };

  const updateUser = (updates: Partial<User>) => {
    setUser(prev => (prev ? { ...prev, ...updates } : prev));
  };

  // --- Drag and Drop Logic ---
  const handleDragStart = (e: React.DragEvent, id: string) => {
    setDraggedItemId(id);
    e.dataTransfer.effectAllowed = 'move';
    // Make transparent image or handle if needed
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedItemId || draggedItemId === targetId) return;

    const sourceIndex = todos.findIndex(t => t.id === draggedItemId);
    const targetIndex = todos.findIndex(t => t.id === targetId);

    if (sourceIndex === -1 || targetIndex === -1) return;

    const newTodos = [...todos];
    const [removed] = newTodos.splice(sourceIndex, 1);
    newTodos.splice(targetIndex, 0, removed);

    // recompute order locally so it matches the visual position
    const reordered = newTodos.map((t, index) => ({
      ...t,
      order: index + 1,
    }));

    setTodos(reordered);

    const movedTodo = reordered.find(t => t.id === removed.id);
    const newOrder = movedTodo ? movedTodo.order : targetIndex + 1;
    try {
      await updateTodoOrder(removed.id, newOrder);
      showNotification({
        title: 'Task reordered',
        type: 'success',
        description: 'Task position was updated successfully.',
      });
    } catch (e) {
      const message = 'Unable to update task order.';
      setError(message);
      showNotification({ title: 'Reorder failed', type: 'error', description: message });
    }
    setDraggedItemId(null);
  };

  // --- Filtering Logic ---
  const filteredTodos = todos.filter(t => {
    const matchesSearch = t.text.toLowerCase().includes(searchQuery.toLowerCase());
    if (!matchesSearch) return false;

    if (filter === FilterType.ACTIVE) {
      return !t.completed || recentlyCompleted.has(t.id);
    }
    if (filter === FilterType.COMPLETED) return t.completed;
    return true;
  });

  const activeCount = todos.filter(t => !t.completed).length;

  const pageTitle = isSettingsRoute
    ? 'Settings'
    : filter === FilterType.ALL
      ? 'All Tasks'
      : filter === FilterType.ACTIVE
        ? 'Active Tasks'
        : 'Completed Tasks';

  const pageDescription = isSettingsRoute
    ? user
      ? `Manage your profile and preferences, ${user.name.split(' ')[0]}.`
      : 'Manage your profile and preferences.'
      : user
      ? `Hi ${user.name.split(' ')[0]}, you have ${activeCount} pending ${activeCount === 1 ? 'task' : 'tasks'}.`
      : `You have ${activeCount} pending ${activeCount === 1 ? 'task' : 'tasks'}.`;

  // Helper for priority visual
  const getPriorityColor = (p: Priority) => {
    switch (p) {
      case 'high':
        return 'bg-gradient-to-r from-red-500 to-red-600 text-white border-transparent shadow-sm hover:from-red-600 hover:to-red-700';
      case 'medium':
        return 'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200';
      case 'low':
        return 'bg-sky-50 text-sky-700 border-sky-200 hover:bg-sky-100';
    }
  };

  const getDueDateLabel = () => {
    if (!inputDueDate) return 'No due date';
    const iso = localInputToUtcIso(inputDueDate);
    if (!iso) return 'Invalid date';
    return formatIsoForUser(iso, true);
  };

  const formatDueDate = (value?: string) => {
    if (!value) return '';
    return formatIsoForUser(value, true);
  };

  if (!user) {
    return null;
  }

  return (
    <BaseTemplate
      title={pageTitle}
      description={pageDescription}
      isSettingsRoute={isSettingsRoute}
      showSearch={!isSettingsRoute}
      searchValue={searchQuery}
      onSearchChange={setSearchQuery}
    >
      {isSettingsRoute ? (
        <Setting />
      ) : (
        <>
          <div className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4 animate-slide-up">
            <div className="inline-flex items-center gap-1 bg-white/50 backdrop-blur-sm p-1 rounded-2xl shadow-sm border border-white/60">
              <button
                type="button"
                onClick={() => setFilter(FilterType.ALL)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                  filter === FilterType.ALL
                    ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10'
                    : 'text-gray-600 hover:bg-white/50'
                }`}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => setFilter(FilterType.ACTIVE)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                  filter === FilterType.ACTIVE
                    ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10'
                    : 'text-gray-600 hover:bg-white/50'
                }`}
              >
                Active
              </button>
              <button
                type="button"
                onClick={() => setFilter(FilterType.COMPLETED)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all duration-300 ${
                  filter === FilterType.COMPLETED
                    ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10'
                    : 'text-gray-600 hover:bg-white/50'
                }`}
              >
                Completed
              </button>
            </div>
          </div>

          <div className="glass-panel p-6 rounded-3xl mb-8 sticky top-4 z-20 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <form onSubmit={handleAdd} className="flex flex-col gap-4">
              <div className="flex items-center gap-3">
                <div className="w-6 h-6 rounded-full border-2 border-primary-200 flex-shrink-0" />
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="What needs to be done?"
                  className="flex-1 bg-transparent border-none focus:ring-0 text-gray-900 placeholder-gray-400 text-xl font-medium p-0"
                />
              </div>

              <InputError message={formInputError} field="title" />

              <div className="pl-9 flex flex-col gap-4">
                <input
                  type="text"
                  value={inputDescription}
                  onChange={(e) => setInputDescription(e.target.value)}
                  placeholder="Add details..."
                  className="w-full bg-transparent border-none focus:ring-0 text-gray-600 placeholder-gray-400 text-sm p-0"
                />
                <InputError message={formInputError} field="description" />
                
                <div className="flex flex-wrap items-center justify-between gap-4 pt-2 border-t border-gray-100/50">
                  <div className="flex items-center gap-3">
                    <div className="relative">
                      <button
                        type="button"
                        onClick={() => {
                          if (inputDueDate) {
                            const [d, t] = inputDueDate.split('T');
                            setTempDueDate(d || '');
                            setTempDueTime(t || '');
                          } else {
                            setTempDueDate('');
                            setTempDueTime('');
                          }
                          setIsDueDatePickerOpen((prev) => !prev);
                        }}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                          inputDueDate 
                            ? 'bg-primary-50 text-primary-700 font-medium' 
                            : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                        }`}
                      >
                        <span>🗓</span>
                        <span>{getDueDateLabel()}</span>
                      </button>

                      {isDueDatePickerOpen && (
                        <div className="absolute top-full left-0 z-30 mt-2 w-72 glass-panel rounded-2xl p-4 animate-fade-in">
                          <div className="space-y-4">
                            <div className="space-y-2">
                              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Date</label>
                              <input
                                type="date"
                                value={tempDueDate}
                                onChange={(e) => setTempDueDate(e.target.value)}
                                className="w-full px-3 py-2 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-sm text-gray-900"
                              />
                            </div>
                            
                            <div className="flex flex-wrap gap-2">
                              <button
                                type="button"
                                onClick={() => {
                                  const v = getTodayEndLocalInput();
                                  setTempDueDate(v.split('T')[0]);
                                  setTempDueTime(v.split('T')[1]);
                                  setInputDueDate(v);
                                }}
                                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors"
                              >
                                Today
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  const v = getTomorrowEndLocalInput();
                                  setTempDueDate(v.split('T')[0]);
                                  setTempDueTime(v.split('T')[1]);
                                  setInputDueDate(v);
                                }}
                                className="px-3 py-1.5 rounded-lg text-xs font-medium bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors"
                              >
                                Tomorrow
                              </button>
                            </div>

                            <div className="space-y-2">
                              <label className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Time</label>
                              <input
                                type="time"
                                value={tempDueTime}
                                onChange={(e) => setTempDueTime(e.target.value)}
                                className="w-full px-3 py-2 bg-white/50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 text-sm text-gray-900"
                              />
                            </div>

                            <div className="flex justify-end gap-2 pt-2 border-t border-gray-100">
                              <button
                                type="button"
                                onClick={() => {
                                  setInputDueDate('');
                                  setTempDueDate('');
                                  setTempDueTime('');
                                  setIsDueDatePickerOpen(false);
                                }}
                                className="px-3 py-1.5 text-xs font-medium text-gray-500 hover:text-gray-700"
                              >
                                Clear
                              </button>
                              <button
                                type="button"
                                onClick={() => {
                                  if (tempDueDate && tempDueTime) {
                                    setInputDueDate(`${tempDueDate}T${tempDueTime}`);
                                  }
                                  setIsDueDatePickerOpen(false);
                                }}
                                className="px-4 py-1.5 text-xs font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg shadow-lg shadow-primary-500/30 transition-all"
                              >
                                Done
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                    <InputError message={formInputError} field="due_date" />

                    <div className="flex gap-1 bg-gray-50 p-1 rounded-lg">
                      <button
                        type="button"
                        onClick={() => setInputPriority('low')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                          inputPriority === 'low'
                            ? 'bg-white text-sky-600 shadow-sm'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        Low
                      </button>
                      <button
                        type="button"
                        onClick={() => setInputPriority('medium')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                          inputPriority === 'medium'
                            ? 'bg-white text-amber-600 shadow-sm'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        Medium
                      </button>
                      <button
                        type="button"
                        onClick={() => setInputPriority('high')}
                        className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                          inputPriority === 'high'
                            ? 'bg-white text-red-600 shadow-sm'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        High
                      </button>
                    </div>
                  </div>

                  <Button 
                    type="submit" 
                    disabled={!inputValue.trim()} 
                    className="shadow-lg shadow-primary-500/30 hover:shadow-primary-500/40 transition-all duration-300 transform hover:-translate-y-0.5 px-6 py-2 rounded-xl"
                  >
                    <span className="mr-2">+</span>
                    Add Task
                  </Button>
                </div>
              </div>
            </form>
          </div>

          <div className="space-y-4 pb-20">
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500 text-sm font-medium">Loading your tasks...</p>
              </div>
            )}

            {!loading && filteredTodos.length === 0 && !error && (
              <div className="text-center py-20 animate-fade-in">
                <div className="mx-auto w-24 h-24 bg-white/50 rounded-full flex items-center justify-center mb-6 text-primary-200 shadow-inner">
                  <Icons.List />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">No tasks found</h3>
                <p className="text-gray-500 max-w-xs mx-auto">
                  {searchQuery
                    ? 'Try adjusting your search terms'
                    : filter === FilterType.COMPLETED
                    ? 'Start completing tasks to see them here'
                    : 'Add a new task above to get started'}
                </p>
              </div>
            )}

            {filteredTodos.map((todo, index) => (
              <div
                key={todo.id}
                draggable={!searchQuery && filter === FilterType.ALL}
                onDragStart={(e) => handleDragStart(e, todo.id)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, todo.id)}
                style={{ animationDelay: `${index * 0.05}s` }}
                className={`group flex items-center glass-panel p-4 rounded-2xl transition-all duration-300 hover:shadow-lg hover:shadow-primary-500/5 hover:border-primary-200 animate-slide-up ${
                  todo.completed
                    ? 'border-gray-100 bg-gray-50 opacity-75'
                    : 'border-gray-200 hover:border-primary-300 hover:shadow-lg hover:scale-[1.01]'
                } ${draggedItemId === todo.id ? 'opacity-40 border-dashed border-primary-400' : ''}`}
              >
                {!searchQuery && filter === FilterType.ALL && (
                  <div className="mr-2 text-gray-300 cursor-grab hover:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Icons.Grip />
                  </div>
                )}

                <button
                  onClick={() => toggleTodo(todo.id)}
                  className={`flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center transition-all duration-300 mr-4 ${
                    todo.completed
                      ? 'bg-emerald-500 border-emerald-500 text-white scale-110 shadow-sm'
                      : 'border-emerald-300 text-emerald-500 hover:bg-emerald-50 hover:border-emerald-500'
                  }`}
                  aria-label={todo.completed ? 'Mark as active' : 'Mark as completed'}
                >
                  <Icons.Check />
                </button>

                <div className="flex-1 min-w-0 flex flex-col sm:flex-row sm:items-center gap-3">
                  <div className="flex-1 min-w-0">
                    <p
                      className={`text-base truncate transition-all duration-300 ${
                        todo.completed ? 'text-gray-400 line-through' : 'text-gray-900'
                      }`}
                    >
                      {todo.text}
                    </p>

                    {todo.description && (
                      <p className="mt-1 text-xs text-gray-500 truncate">
                        {todo.description}
                      </p>
                    )}

                    {todo.dueDate && (
                      <p className="mt-1 text-[11px] font-medium text-gray-500 flex items-center gap-1">
                        <span className="inline-block w-2 h-2 rounded-full bg-gray-300" />
                        Due {formatDueDate(todo.dueDate)}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-2 mt-1 sm:mt-0 flex-shrink-0">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        cyclePriority(todo.id);
                      }}
                      className={`inline-flex items-center px-3 py-0.5 rounded-full text-[11px] font-bold uppercase tracking-wider border transition-colors ${getPriorityColor(
                        todo.priority,
                      )}`}
                      title="Click to change priority"
                    >
                      {todo.priority}
                    </button>
                  </div>
                </div>

                <button
                  onClick={() => openEditModal(todo)}
                  className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-gray-700 hover:bg-gray-50 rounded-lg transition-all ml-2"
                  aria-label="Edit task"
                >
                  <Icons.Edit />
                </button>
                <button
                  onClick={() => deleteTodoHandler(todo.id)}
                  className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all ml-1"
                  aria-label="Delete task"
                >
                  <Icons.Trash />
                </button>
              </div>
            ))}
            
            {/* Infinite scroll indicators */}
            {!loading && filteredTodos.length > 0 && (
              <>
                {loadingMore && (
                  <div className="text-center py-6">
                    <div className="inline-flex items-center gap-2 text-sm text-gray-500">
                      <div className="w-4 h-4 border-2 border-gray-300 border-t-gray-600 rounded-full animate-spin"></div>
                      <span>Loading more tasks...</span>
                    </div>
                  </div>
                )}
                
                {!hasMore && !loadingMore && (
                  <div className="text-center py-6">
                    <p className="text-sm text-gray-400">
                      ✓ All tasks loaded
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      {showUndoToast && (
        <div className="fixed bottom-6 right-6 md:right-10 z-50 animate-in fade-in slide-in-from-bottom-4 duration-300">
          <div className="bg-gray-900 text-white px-5 py-3 rounded-xl shadow-2xl flex items-center gap-4">
            <span>Task completed</span>
            <button
              onClick={undoLastCompletion}
              className="text-primary-300 hover:text-white font-medium flex items-center gap-1 transition-colors"
            >
              <Icons.Undo />
              Undo
            </button>
          </div>
        </div>
      )}
      {editingTodo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-6 space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Edit task</h3>
            <div className="space-y-3">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="Task title"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-900 bg-white focus:ring-1 focus:ring-gray-900"
              />
              <input
                type="text"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="Description (optional)"
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-900 bg-white focus:ring-1 focus:ring-gray-900"
              />
              <div className="flex gap-2">
                <input
                  type="datetime-local"
                  value={editDueDate}
                  onChange={(e) => setEditDueDate(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm text-gray-900 bg-white focus:ring-1 focus:ring-gray-900"
                />
              </div>
              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setEditPriority('low')}
                  className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                    editPriority === 'low'
                      ? 'bg-blue-100 text-blue-700 border-blue-200'
                      : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  Low
                </button>
                <button
                  type="button"
                  onClick={() => setEditPriority('medium')}
                  className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                    editPriority === 'medium'
                      ? 'bg-amber-100 text-amber-700 border-amber-200'
                      : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  Medium
                </button>
                <button
                  type="button"
                  onClick={() => setEditPriority('high')}
                  className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                    editPriority === 'high'
                      ? 'bg-red-100 text-red-700 border-red-200'
                      : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  High
                </button>
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={closeEditModal}
                className="px-3 py-1.5 rounded-lg text-sm text-gray-500 hover:text-gray-800 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleEditSave}
                className="px-4 py-1.5 rounded-lg text-sm font-medium text-white bg-gray-900 hover:bg-black"
              >
                Save changes
              </button>
            </div>
          </div>
        </div>
      )}
    </BaseTemplate>
  );
};