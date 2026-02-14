"""
Data Manager - Interface to WorksheetMergeMasterSourceFile.xlsx
Provides access to names, cities, venues, jobs, etc.
"""

import pandas as pd
import random
from typing import Dict, List, Optional
from pathlib import Path


class DataManager:
    """Manages all lookup tables from the master source file"""
    
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self._tables: Dict[str, pd.DataFrame] = {}
        self._load_all_tables()
    
    def _load_all_tables(self):
        """Load all sheets into memory"""
        try:
            excel_file = pd.ExcelFile(self.excel_path)
            
            # Load each relevant sheet
            available_sheets = excel_file.sheet_names
            
            if 'Names' in available_sheets:
                self._tables['names'] = pd.read_excel(excel_file, 'Names')
            if 'PlacesCDN' in available_sheets:
                self._tables['places_cdn'] = pd.read_excel(excel_file, 'PlacesCDN')
            if 'Theaters' in available_sheets:
                self._tables['theaters'] = pd.read_excel(excel_file, 'Theaters')
            if 'Courses' in available_sheets:
                self._tables['courses'] = pd.read_excel(excel_file, 'Courses')
            if 'SummerJobs' in available_sheets:
                self._tables['summer_jobs'] = pd.read_excel(excel_file, 'SummerJobs')
            if 'Vehicles' in available_sheets:
                self._tables['vehicles'] = pd.read_excel(excel_file, 'Vehicles')
            if 'Currency' in available_sheets:
                self._tables['currency'] = pd.read_excel(excel_file, 'Currency')
            if 'Municipalities' in available_sheets:
                self._tables['municipalities'] = pd.read_excel(excel_file, 'Municipalities')
            if 'Businesses' in available_sheets:
                self._tables['businesses'] = pd.read_excel(excel_file, 'Businesses')
                
            print(f"✓ Loaded {len(self._tables)} lookup tables")
            
        except Exception as e:
            print(f"Warning: Could not load lookup tables: {e}")
            # Initialize empty tables as fallback
            self._initialize_fallback_data()
    
    def _initialize_fallback_data(self):
        """Create minimal fallback data if Excel file not available"""
        self._tables = {
            'names': pd.DataFrame({
                'Code': range(1, 6),
                'FullName': ['Alex Chen', 'Jordan Smith', 'Taylor Brown', 'Morgan Lee', 'Casey Park'],
                'FirstName': ['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey'],
                'LastName': ['Chen', 'Smith', 'Brown', 'Lee', 'Park'],
                'Title': ['Mr.', 'Ms.', 'Dr.', 'Ms.', 'Mr.']
            }),
            'places_cdn': pd.DataFrame({
                'City': ['Winnipeg', 'Brandon', 'Thompson', 'Portage la Prairie', 'Steinbach'],
                'Province/Territory': ['Manitoba'] * 5,
                'Abbr': ['MB'] * 5
            }),
            'theaters': pd.DataFrame({
                'BusinessName': ['The Grand Theatre', 'Royal Concert Hall', 'City Auditorium', 
                               'Community Playhouse', 'Arts Centre']
            }),
            'courses': pd.DataFrame({
                'Course Title': ['Mathematics', 'English', 'Science', 'History', 'Art']
            }),
            'summer_jobs': pd.DataFrame({
                'Summer Job Descriptions': ['mowing lawns', 'babysitting', 'tutoring', 
                                           'dog walking', 'retail sales']
            })
        }
    
    def get_name(self, gender: Optional[str] = None, with_title: bool = True) -> Dict:
        """
        Get random name with details
        
        Returns:
            {
                'full_name': 'Ms. Chen',
                'first_name': 'Alex',
                'last_name': 'Chen',
                'title': 'Ms.'
            }
        """
        if 'names' not in self._tables or len(self._tables['names']) == 0:
            return {
                'full_name': 'Alex Chen',
                'first_name': 'Alex',
                'last_name': 'Chen',
                'title': 'Mr.'
            }
        
        df = self._tables['names']
        
        if gender and 'Gender' in df.columns:
            filtered = df[df['Gender'] == gender]
            if len(filtered) > 0:
                df = filtered
        
        row = df.sample(n=1).iloc[0]
        
        # Build name
        if with_title and 'Title' in df.columns:
            full_name = f"{row['Title']} {row['LastName']}"
        elif 'FullName' in df.columns:
            full_name = row['FullName']
        else:
            full_name = f"{row.get('FirstName', 'Alex')} {row.get('LastName', 'Chen')}"
        
        return {
            'full_name': full_name,
            'first_name': row.get('FirstName', 'Alex'),
            'last_name': row.get('LastName', 'Chen'),
            'title': row.get('Title', 'Mr.')
        }
    
    def get_place_cdn(self, province: Optional[str] = None) -> Dict:
        """Get random Canadian city"""
        if 'places_cdn' not in self._tables or len(self._tables['places_cdn']) == 0:
            return {
                'city': 'Winnipeg',
                'province': 'Manitoba',
                'full_name': 'Winnipeg, MB'
            }
        
        df = self._tables['places_cdn']
        
        if province and 'Province/Territory' in df.columns:
            filtered = df[df['Province/Territory'] == province]
            if len(filtered) > 0:
                df = filtered
        
        row = df.sample(n=1).iloc[0]
        
        city = row.get('City', 'Winnipeg')
        province_name = row.get('Province/Territory', 'Manitoba')
        abbr = row.get('Abbr', 'MB')
        
        return {
            'city': city,
            'province': province_name,
            'full_name': f"{city}, {abbr}"
        }
    
    def get_theater(self) -> str:
        """Get random theater name"""
        if 'theaters' not in self._tables or len(self._tables['theaters']) == 0:
            return "The Grand Theatre"
        
        df = self._tables['theaters']
        return df.sample(n=1).iloc[0]['BusinessName']
    
    def get_course(self) -> str:
        """Get random course name"""
        if 'courses' not in self._tables or len(self._tables['courses']) == 0:
            return "Mathematics"
        
        df = self._tables['courses']
        return df.sample(n=1).iloc[0]['Course Title']
    
    def get_summer_job(self) -> str:
        """Get random summer job description"""
        if 'summer_jobs' not in self._tables or len(self._tables['summer_jobs']) == 0:
            return "mowing lawns"
        
        df = self._tables['summer_jobs']
        return df.sample(n=1).iloc[0]['Summer Job Descriptions']
    
    def get_vehicle(self) -> Dict:
        """Get random vehicle"""
        if 'vehicles' not in self._tables or len(self._tables['vehicles']) == 0:
            return {
                'make': 'Honda',
                'model': 'Civic',
                'full_name': 'Honda Civic'
            }
        
        df = self._tables['vehicles']
        row = df.sample(n=1).iloc[0]
        
        make = row.get('Make', 'Honda')
        model = row.get('Model', 'Civic')
        
        return {
            'make': make,
            'model': model,
            'full_name': f"{make} {model}"
        }
    
    def get_business(self) -> str:
        """Get random business name"""
        if 'businesses' not in self._tables or len(self._tables['businesses']) == 0:
            return "Local Business"
        
        df = self._tables['businesses']
        return df.sample(n=1).iloc[0]['BusinessName']


# Test function
if __name__ == "__main__":
    # Test with fallback data
    dm = DataManager("nonexistent.xlsx")
    
    print("\n=== Testing Data Manager ===")
    print(f"Name: {dm.get_name()}")
    print(f"Place: {dm.get_place_cdn()}")
    print(f"Theater: {dm.get_theater()}")
    print(f"Course: {dm.get_course()}")
    print(f"Job: {dm.get_summer_job()}")
