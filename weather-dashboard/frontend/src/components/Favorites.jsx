import React, { useState, useEffect } from 'react';
import { Star, Trash2 } from 'lucide-react';

function Favorites({ currentLocation, onLocationSelect }) {
  const [favorites, setFavorites] = useState([]);

  useEffect(() => {
    const stored = localStorage.getItem('favorites');
    if (stored) {
      setFavorites(JSON.parse(stored));
    }
  }, []);

  const addFavorite = () => {
    const newFavorites = [
      ...favorites,
      currentLocation
    ].filter((fav, index, self) => 
      index === self.findIndex(f => f.lat === fav.lat && f.lon === fav.lon)
    );
    setFavorites(newFavorites);
    localStorage.setItem('favorites', JSON.stringify(newFavorites));
  };

  const removeFavorite = (location) => {
    const newFavorites = favorites.filter(
      fav => !(fav.lat === location.lat && fav.lon === location.lon)
    );
    setFavorites(newFavorites);
    localStorage.setItem('favorites', JSON.stringify(newFavorites));
  };

  const isFavorited = favorites.some(
    fav => fav.lat === currentLocation.lat && fav.lon === currentLocation.lon
  );

  return (
    <div className="favorites">
      <div className="favorites-header">
        <h3>Favorites</h3>
        <button 
          onClick={addFavorite}
          className={`favorite-btn ${isFavorited ? 'favorited' : ''}`}
        >
          <Star size={20} />
        </button>
      </div>

      <div className="favorites-list">
        {favorites.length === 0 ? (
          <div className="no-favorites">No favorites yet</div>
        ) : (
          favorites.map((fav, index) => (
            <div key={index} className="favorite-item">
              <button
                onClick={() => onLocationSelect(fav)}
                className="favorite-name"
              >
                {fav.name}
              </button>
              <button
                onClick={() => removeFavorite(fav)}
                className="favorite-remove"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Favorites;
