import { useState, useCallback } from 'react';
import apiService from '../api';

export const useOptimization = () => {
  const [activities, setActivities] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [requestId, setRequestId] = useState(null);

  const startOptimization = useCallback(async () => {
    try {
      setError(null);
      setIsRunning(true);
      setProgress(0);
      setShowResults(false);
      setResults(null);

      // Start optimization
      const response = await apiService.startOptimization({
        scenario: 'laptop_procurement',
        constraints: {
          budget_limit: 500000,
          delivery_time: '2 weeks',
          quality_requirement: 'enterprise_grade'
        }
      });

      setRequestId(response.request_id);
      console.log('Optimization started:', response);

      // Poll for progress
      const progressInterval = setInterval(async () => {
        try {
          const progressData = await apiService.getOptimizationProgress(response.request_id);
          setProgress(progressData.progress || 0);

          if (progressData.status === 'completed') {
            clearInterval(progressInterval);
            setIsRunning(false);
            setProgress(100);
            
            // Get results
            const resultsData = await apiService.getOptimizationResults(response.request_id);
            setResults(resultsData);
            setShowResults(true);
          } else if (progressData.status === 'failed') {
            clearInterval(progressInterval);
            setIsRunning(false);
            setError('Optimization failed: ' + (progressData.error || 'Unknown error'));
          }
        } catch (err) {
          console.error('Error polling progress:', err);
        }
      }, 2000);

    } catch (err) {
      console.error('Failed to start optimization:', err);
      setError(err.message);
      setIsRunning(false);
    }
  }, []);

  const clearOptimization = useCallback(() => {
    setActivities([]);
    setShowResults(false);
    setResults(null);
    setError(null);
    setProgress(0);
    setRequestId(null);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    activities,
    isRunning,
    showResults,
    progress,
    results,
    error,
    requestId,
    startOptimization,
    clearOptimization,
    clearError
  };
};
