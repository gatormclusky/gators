#!/usr/bin/env python3
"""
Generate GeoJSON from processed interview data.
Creates geographic features that can be used in mapping and 3D visualization.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

def parse_coordinates(coord_str):
    """Parse coordinate string to [lon, lat] format."""
    try:
        coords = [float(x.strip()) for x in coord_str.split(',')]
        if len(coords) == 2:
            # If looks like [lat, lon], swap to [lon, lat] for GeoJSON
            if abs(coords[0]) < 90 and abs(coords[1]) < 180:
                return [coords[1], coords[0]]
            return coords
    except:
        pass
    return None

def interview_to_geojson(interview_data):
    """Convert interview data to GeoJSON features."""
    features = []
    
    for location in interview_data.get('markedLocations', []):
        coords = parse_coordinates(location.get('coordinates', ''))
        
        if not coords:
            print(f"⚠️  Skipping location without valid coordinates: {location.get('location')}")
            continue
        
        feature = {
            "type": "Feature",
            "properties": {
                "interviewNumber": interview_data.get('issueNumber'),
                "interviewee": interview_data.get('interviewee'),
                "interviewDate": interview_data.get('dateConducted'),
                "location": location.get('location'),
                "event": location.get('event'),
                "eventDate": location.get('date'),
                "significance": location.get('significance'),
                "issueURL": interview_data.get('issueURL'),
                "timestamp": datetime.now().isoformat()
            },
            "geometry": {
                "type": "Point",
                "coordinates": coords
            }
        }
        features.append(feature)
    
    return features

def create_geojson_collection(features):
    """Create a FeatureCollection from features."""
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated": datetime.now().isoformat(),
            "source": "Vietnam Active History - Interview Processing",
            "totalFeatures": len(features)
        },
        "features": features
    }

def main():
    print("🗺️  Generating GeoJSON from interview data...")
    
    try:
        os.makedirs('data/interviews/locations', exist_ok=True)
        
        all_features = []
        raw_dir = Path('data/interviews/raw')
        
        if not raw_dir.exists():
            print("❌ No raw interview data found. Run extract_interviews.py first.")
            return
        
        # Process each raw interview file
        for interview_file in sorted(raw_dir.glob('*.json')):
            print(f"📄 Processing: {interview_file.name}")
            
            with open(interview_file, 'r') as f:
                interview_data = json.load(f)
            
            # Convert to GeoJSON features
            features = interview_to_geojson(interview_data)
            all_features.extend(features)
            
            # Save individual interview GeoJSON
            if features:
                interview_num = interview_data.get('issueNumber')
                output_file = f"data/interviews/locations/locations_{interview_num}.geojson"
                
                geojson = create_geojson_collection(features)
                with open(output_file, 'w') as f:
                    json.dump(geojson, f, indent=2)
                
                print(f"✅ Created: {output_file} ({len(features)} locations)")
        
        # Create consolidated GeoJSON with all interviews
        if all_features:
            consolidated_file = 'data/interviews/locations/all_interviews.geojson'
            consolidated_geojson = create_geojson_collection(all_features)
            
            with open(consolidated_file, 'w') as f:
                json.dump(consolidated_geojson, f, indent=2)
            
            print(f"\n✅ Created consolidated: {consolidated_file}")
            print(f"📍 Total locations: {len(all_features)}")
        
        # Create summary for 3D visualization
        summary = {
            "timestamp": datetime.now().isoformat(),
            "totalInterviews": len(list(raw_dir.glob('*.json'))),
            "totalLocations": len(all_features),
            "boundingBox": calculate_bounds(all_features),
            "geojsonFile": "data/interviews/locations/all_interviews.geojson"
        }
        
        with open('geojson_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ GeoJSON generation complete!")
        print(f"📊 Summary saved to geojson_summary.json")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def calculate_bounds(features):
    """Calculate bounding box for all features."""
    if not features:
        return None
    
    lons = [f['geometry']['coordinates'][0] for f in features]
    lats = [f['geometry']['coordinates'][1] for f in features]
    
    return {
        "minLon": min(lons),
        "maxLon": max(lons),
        "minLat": min(lats),
        "maxLat": max(lats),
        "center": [(min(lons) + max(lons)) / 2, (min(lats) + max(lats)) / 2]
    }

if __name__ == '__main__':
    main()
