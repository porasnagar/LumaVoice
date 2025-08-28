
import { useState, useEffect } from 'react';

interface TestVideoStructure {
  folders: string[];
  videos: Record<string, string[]>;
}

export const useTestVideos = () => {
  const [testData, setTestData] = useState<TestVideoStructure>({
    folders: [],
    videos: {}
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTestVideos = async () => {
      try {
        setLoading(true);
        
        const response = await fetch('http://localhost:5000/test-videos');
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        setTestData(data);
        setError(null);
      } catch (err) {
        setError('Failed to load test videos. Make sure the backend is running and the data/recordings/data directory exists.');
        console.error('Error fetching test videos:', err);
        
        // Fallback to empty structure
        setTestData({ folders: [], videos: {} });
      } finally {
        setLoading(false);
      }
    };

    fetchTestVideos();
  }, []);

  return { testData, loading, error };
};
