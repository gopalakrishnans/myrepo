import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchProcedures } from '../api/client';
import styles from '../styles/components/SearchBar.module.css';

export default function SearchBar({ initialValue = '', autoFocus = false }) {
  const [query, setQuery] = useState(initialValue);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const navigate = useNavigate();
  const wrapperRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(async () => {
      try {
        const data = await searchProcedures({ q: query, limit: 8 });
        setSuggestions(data.items || []);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      }
    }, 250);
    return () => clearTimeout(timerRef.current);
  }, [query]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    if (query.trim()) {
      setShowSuggestions(false);
      navigate(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  }

  function handleSelect(procedure) {
    setShowSuggestions(false);
    navigate(`/procedure/${procedure.id}`);
  }

  return (
    <div className={styles.wrapper} ref={wrapperRef}>
      <form onSubmit={handleSubmit}>
        <input
          className={styles.input}
          type="text"
          placeholder='Search for a procedure (e.g., "MRI", "blood test", "knee surgery")'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
          autoFocus={autoFocus}
        />
      </form>
      {showSuggestions && suggestions.length > 0 && (
        <div className={styles.suggestions}>
          {suggestions.map((proc) => (
            <div
              key={proc.id}
              className={styles.suggestion}
              onClick={() => handleSelect(proc)}
            >
              <div>
                <div className={styles.suggestionName}>{proc.plain_language_name}</div>
                <div className={styles.suggestionCode}>CPT {proc.billing_code}</div>
              </div>
              <span className={styles.suggestionCategory}>{proc.category}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
