import React from 'react';
import { Moon, Sun } from 'lucide-react';

function ThemeToggle({ theme, onToggle }) {
  return (
    <button onClick={onToggle} className="theme-toggle" aria-label="Toggle theme">
      {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
    </button>
  );
}

export default ThemeToggle;
