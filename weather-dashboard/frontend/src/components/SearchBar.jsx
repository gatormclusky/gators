import React, { useState } from 'react';
import { Search } from 'lucide-react';
import axios from 'axios';

function SearchBar({ onLocationSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get('/api/weather/search', {
        params: { q: value, limit: 5 }
      });
      setResults(response.data.results || []);
      setShowResults(true);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectLocation = (location) => {
    onLocationSelect({
      lat: location.lat,
      lon: location.lon,
      name: `${location.name}${location.country ? ', ' + location.country : ''}`
    });
    setQuery('');
    setShowResults(false);
  };

  return (
    <div className="search-bar">
      <div className="search-input-container">
        <Search size={20} className="search-icon" />
        <input
          type="text"
          value={query}
          onChange={handleSearch}
          placeholder="Search for a city..."
          className="search-input"
        />
      </div>

      {showResults && (
        <div className="search-results">
          {loading && <div className="result-item">Loading...</div>}
          {results.length === 0 && !loading && (
            <div className="result-item">No results found</div>
          )}
          {results.map((result, index) => (
            <div
              key={index}
              className="result-item"
              onClick={() => handleSelectLocation(result)}
            >
              {result.name}
              {result.admin1 && <span>, {result.admin1}</span>}
              {result.country && <span>, {result.country}</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchBar;
