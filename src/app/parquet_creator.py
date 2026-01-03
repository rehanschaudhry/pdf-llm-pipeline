import pandas as pd
import os
from typing import List, Dict

class ParquetCreator:
    """Create Parquet files from text chunks"""
    
    def __init__(self):
        pass
    
    def create_parquet(self, chunks: List[Dict], output_path: str, metadata: Dict = None) -> bool:
        """
        Create a Parquet file from text chunks
        
        Args:
            chunks: List of chunk dictionaries
            output_path: Where to save the parquet file
            metadata: Optional metadata to include
            
        Returns:
            True if successful, False otherwise
        """
        print(f"\n📦 Creating Parquet file...")
        
        try:
            # Convert chunks to DataFrame
            df = pd.DataFrame(chunks)
            
            # Add metadata columns if provided
            if metadata:
                for key, value in metadata.items():
                    df[f'doc_{key}'] = value
            
            # Save as Parquet
            df.to_parquet(output_path, engine='pyarrow', index=False)
            
            file_size = os.path.getsize(output_path)
            
            print(f"✓ Parquet file created: {output_path}")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Size: {file_size} bytes")
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating Parquet: {e}")
            return False
    
    def read_parquet(self, parquet_path: str) -> pd.DataFrame:
        """
        Read a Parquet file
        
        Args:
            parquet_path: Path to parquet file
            
        Returns:
            DataFrame with data
        """
        try:
            df = pd.read_parquet(parquet_path, engine='pyarrow')
            print(f"✓ Read Parquet file: {parquet_path}")
            print(f"  Rows: {len(df)}")
            return df
            
        except Exception as e:
            print(f"✗ Error reading Parquet: {e}")
            return None
    
    def get_parquet_info(self, parquet_path: str) -> Dict:
        """
        Get information about a Parquet file
        
        Args:
            parquet_path: Path to parquet file
            
        Returns:
            Dict with file info
        """
        try:
            df = pd.read_parquet(parquet_path, engine='pyarrow')
            
            info = {
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'file_size': os.path.getsize(parquet_path),
                'sample_row': df.iloc[0].to_dict() if len(df) > 0 else {}
            }
            
            return info
            
        except Exception as e:
            print(f"✗ Error getting Parquet info: {e}")
            return {}