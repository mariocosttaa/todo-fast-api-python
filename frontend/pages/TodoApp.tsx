import React, { useState, useEffect } from 'react';
import { FilterType, Todo, User, Priority } from '../types';
import { Button, Input, Icons, Avatar } from '../components/UI';
import { SettingsView } from './SettingsView';

interface TodoAppProps {
  onLogout: () => void;
}

type Tab = 'tasks' | 'settings';

export const TodoApp: React.FC<TodoAppProps> = ({ onLogout }) => {
  // --- State ---
  const [activeTab, setActiveTab] = useState<Tab>('tasks');
  const [user, setUser] = useState<User>({
    id: 'u1',
    name: 'Alex Johnson',
    email: 'alex.j@example.com'
  });

  const [todos, setTodos] = useState<Todo[]>(() => {
    const saved = localStorage.getItem('martaks_todos');
    return saved ? JSON.parse(saved) : [
      { id: '1', text: 'Welcome to MarTaks', completed: false, createdAt: Date.now(), category: 'personal', priority: 'medium' },
      { id: '2', text: 'Add your first task to get started', completed: false, createdAt: Date.now() - 1000, category: 'work', priority: 'high' },
    ];
  });
  
  const [inputValue, setInputValue] = useState('');
  const [inputPriority, setInputPriority] = useState<Priority>('medium');
  const [filter, setFilter] = useState<FilterType>(FilterType.ALL);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Drag and Drop State
  const [draggedItemId, setDraggedItemId] = useState<string | null>(null);
  
  // Track tasks that were recently completed
  const [recentlyCompleted, setRecentlyCompleted] = useState<Set<string>>(new Set());
  const [showUndoToast, setShowUndoToast] = useState(false);
  const [lastCompletedId, setLastCompletedId] = useState<string | null>(null);

  // --- Effects ---
  useEffect(() => {
    localStorage.setItem('martaks_todos', JSON.stringify(todos));
  }, [todos]);

  // --- Handlers ---
  const addTodo = (text: string, priority: Priority = 'medium') => {
    if (!text.trim()) return;
    const newTodo: Todo = {
      id: crypto.randomUUID(),
      text: text.trim(),
      completed: false,
      createdAt: Date.now(),
      priority: priority
    };
    setTodos(prev => [newTodo, ...prev]);
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    addTodo(inputValue, inputPriority);
    setInputValue('');
  };

  const toggleTodo = (id: string) => {
    const todo = todos.find(t => t.id === id);
    if (!todo) return;

    if (!todo.completed) {
      setTodos(prev => prev.map(t => t.id === id ? { ...t, completed: true } : t));
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
      setTodos(prev => prev.map(t => t.id === id ? { ...t, completed: false } : t));
      setRecentlyCompleted(prev => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
      setShowUndoToast(false);
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

  const deleteTodo = (id: string) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  };

  const updateUser = (updates: Partial<User>) => {
    setUser(prev => ({ ...prev, ...updates }));
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

  const handleDrop = (e: React.DragEvent, targetId: string) => {
    e.preventDefault();
    if (!draggedItemId || draggedItemId === targetId) return;

    const sourceIndex = todos.findIndex(t => t.id === draggedItemId);
    const targetIndex = todos.findIndex(t => t.id === targetId);

    if (sourceIndex === -1 || targetIndex === -1) return;

    const newTodos = [...todos];
    const [removed] = newTodos.splice(sourceIndex, 1);
    newTodos.splice(targetIndex, 0, removed);

    setTodos(newTodos);
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

  // Helper for priority visual
  const getPriorityColor = (p: Priority) => {
    switch(p) {
      case 'high': return 'bg-red-50 text-red-600 border-red-200 hover:bg-red-100';
      case 'medium': return 'bg-amber-50 text-amber-600 border-amber-200 hover:bg-amber-100';
      case 'low': return 'bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col md:flex-row font-sans">
      {/* Sidebar */}
      <aside className="w-full md:w-72 bg-white border-r border-gray-200 flex flex-col justify-between h-auto md:h-screen sticky top-0 z-30 shadow-sm">
        <div className="p-6">
          <div className="flex items-center space-x-3 mb-10">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary-500/30">
              <Icons.Sparkles />
            </div>
            <span className="text-2xl font-bold text-gray-900 tracking-tight">MarTaks</span>
          </div>

          <nav className="space-y-2">
             <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-4">Menu</div>
            <button 
              onClick={() => setActiveTab('tasks')}
              className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'tasks' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <Icons.List />
              <span className="ml-3">My Tasks</span>
            </button>
             <button 
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all ${activeTab === 'settings' ? 'bg-primary-50 text-primary-700 shadow-sm' : 'text-gray-600 hover:bg-gray-50'}`}
            >
              <Icons.Settings />
              <span className="ml-3">Settings</span>
            </button>
          </nav>

           <div className="mt-8 space-y-2">
              <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 px-4">Filters</div>
              <button 
                onClick={() => { setFilter(FilterType.ALL); setActiveTab('tasks'); }}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-sm rounded-lg transition-colors ${activeTab === 'tasks' && filter === FilterType.ALL ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:bg-gray-50'}`}
              >
                <span>All</span>
                <span className="bg-gray-200 px-2 py-0.5 rounded text-xs text-gray-700 font-bold">{todos.length}</span>
              </button>
              <button 
                onClick={() => { setFilter(FilterType.ACTIVE); setActiveTab('tasks'); }}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-sm rounded-lg transition-colors ${activeTab === 'tasks' && filter === FilterType.ACTIVE ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:bg-gray-50'}`}
              >
                <span>Active</span>
                <span className="bg-primary-100 text-primary-700 px-2 py-0.5 rounded text-xs font-bold">{activeCount}</span>
              </button>
              <button 
                onClick={() => { setFilter(FilterType.COMPLETED); setActiveTab('tasks'); }}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-sm rounded-lg transition-colors ${activeTab === 'tasks' && filter === FilterType.COMPLETED ? 'bg-gray-100 text-gray-900 font-medium' : 'text-gray-500 hover:bg-gray-50'}`}
              >
                <span>Completed</span>
              </button>
           </div>
        </div>

        <div className="p-4 border-t border-gray-100 bg-gray-50/50">
          <div className="flex items-center space-x-3 mb-4 px-2">
             <Avatar name={user.name} size="sm" />
             <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">{user.name}</p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
             </div>
          </div>
          <button 
            onClick={onLogout}
            className="flex items-center space-x-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all w-full px-3 py-2 text-sm font-medium"
          >
            <Icons.LogOut />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-10 w-full overflow-y-auto h-screen relative scroll-smooth">
        {activeTab === 'settings' ? (
          <SettingsView user={user} onUpdateUser={updateUser} />
        ) : (
          <div className="max-w-4xl mx-auto">
            <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {filter === FilterType.ALL ? "All Tasks" : filter === FilterType.ACTIVE ? "Active Tasks" : "Completed Tasks"}
                </h1>
                <p className="text-gray-500">
                  Hi {user.name.split(' ')[0]}, you have {activeCount} pending {activeCount === 1 ? 'task' : 'tasks'}.
                </p>
              </div>
              <div className="w-full md:w-64">
                <Input 
                  placeholder="Search tasks..." 
                  icon={<Icons.Search />}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-white"
                />
              </div>
            </header>

            {/* Input Area */}
            <div className="bg-white/90 backdrop-blur-xl p-4 rounded-2xl shadow-lg border border-white/50 ring-1 ring-gray-200 mb-8 sticky top-4 z-20 transition-shadow hover:shadow-xl">
              <form onSubmit={handleAdd} className="flex flex-col gap-3">
                <div className="flex items-center gap-2">
                   <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="What needs to be done?"
                    className="flex-1 px-2 py-2 bg-transparent border-none focus:ring-0 text-gray-900 placeholder-gray-400 text-lg font-medium"
                  />
                </div>
                
                <div className="flex justify-between items-center border-t border-gray-100 pt-3">
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={() => setInputPriority('low')}
                        className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${inputPriority === 'low' ? 'bg-blue-100 text-blue-700 border-blue-200' : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`}
                      >
                        Low
                      </button>
                       <button
                        type="button"
                        onClick={() => setInputPriority('medium')}
                        className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${inputPriority === 'medium' ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`}
                      >
                        Medium
                      </button>
                       <button
                        type="button"
                        onClick={() => setInputPriority('high')}
                        className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${inputPriority === 'high' ? 'bg-red-100 text-red-700 border-red-200' : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`}
                      >
                        High
                      </button>
                    </div>

                    <div className="flex gap-2">
                        <Button type="submit" disabled={!inputValue.trim()} className="shadow-none py-1.5 px-4 text-sm">
                            <Icons.Plus />
                            <span className="ml-2">Add</span>
                        </Button>
                    </div>
                </div>
              </form>
            </div>

            {/* List */}
            <div className="space-y-3 pb-20">
                {filteredTodos.length === 0 && (
                    <div className="text-center py-20">
                        <div className="mx-auto w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6 text-gray-300">
                            <Icons.List />
                        </div>
                        <h3 className="text-lg font-medium text-gray-900">No tasks found</h3>
                        <p className="text-gray-500 mt-1">
                            {searchQuery 
                              ? "Try adjusting your search terms" 
                              : filter === FilterType.COMPLETED 
                                ? "Start completing tasks to see them here" 
                                : "Add a new task to get started"}
                        </p>
                    </div>
                )}
                
                {filteredTodos.map((todo) => (
                    <div 
                        key={todo.id}
                        draggable={!searchQuery && filter === FilterType.ALL} // Only allow drag when viewing all tasks in order
                        onDragStart={(e) => handleDragStart(e, todo.id)}
                        onDragOver={handleDragOver}
                        onDrop={(e) => handleDrop(e, todo.id)}
                        className={`group flex items-center bg-white p-4 rounded-xl border transition-all duration-200 ${
                            todo.completed 
                            ? 'border-gray-100 bg-gray-50 opacity-75' 
                            : 'border-gray-200 hover:border-primary-300 hover:shadow-lg hover:scale-[1.01]'
                        } ${draggedItemId === todo.id ? 'opacity-40 border-dashed border-primary-400' : ''}`}
                    >
                         {/* Drag Handle */}
                        {!searchQuery && filter === FilterType.ALL && (
                          <div className="mr-2 text-gray-300 cursor-grab hover:text-gray-500 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Icons.Grip />
                          </div>
                        )}

                        <button
                            onClick={() => toggleTodo(todo.id)}
                            className={`flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all duration-300 mr-4 ${
                                todo.completed 
                                    ? 'bg-primary-500 border-primary-500 text-white scale-110' 
                                    : 'border-gray-300 hover:border-primary-500'
                            }`}
                        >
                            {todo.completed && <Icons.Check />}
                        </button>
                        
                        <div className="flex-1 min-w-0 flex flex-col sm:flex-row sm:items-center gap-2">
                            <p className={`text-base truncate transition-all duration-300 flex-1 ${todo.completed ? 'text-gray-400 line-through' : 'text-gray-900'}`}>
                                {todo.text}
                            </p>
                            
                            <div className="flex items-center gap-2 mt-1 sm:mt-0">
                                <button 
                                  onClick={(e) => { e.stopPropagation(); cyclePriority(todo.id); }}
                                  className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider border transition-colors ${getPriorityColor(todo.priority)}`}
                                  title="Click to change priority"
                                >
                                  {todo.priority}
                                </button>
                            </div>
                        </div>

                        <button 
                            onClick={() => deleteTodo(todo.id)}
                            className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all ml-2"
                            aria-label="Delete task"
                        >
                            <Icons.Trash />
                        </button>
                    </div>
                ))}
            </div>
          </div>
        )}

        {/* Undo Toast */}
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
      </main>
    </div>
  );
};