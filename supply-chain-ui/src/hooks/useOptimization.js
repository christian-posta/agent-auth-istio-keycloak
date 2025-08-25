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
          console.log('Progress data received:', progressData);
          setProgress(progressData.progress_percentage || 0);
          
          // Update activities from progress data
          if (progressData.activities) {
            setActivities(progressData.activities);
          }

          if (progressData.status === 'completed') {
            clearInterval(progressInterval);
            setIsRunning(false);
            setProgress(100);
            
            // Always use the request_id from the progress data
            const completedRequestId = progressData.request_id;
            console.log('Optimization completed, fetching results for:', completedRequestId);
            console.log('Original request ID was:', response.request_id);
            
            if (!completedRequestId) {
              console.error('No request_id in progress data:', progressData);
              return;
            }
            
            // Wait a moment for results to be generated, then get results
            setTimeout(async () => {
              try {
                const resultsData = await apiService.getOptimizationResults(completedRequestId);
                setResults(resultsData);
                setShowResults(true);
              } catch (resultsErr) {
                console.error('Error fetching results:', resultsErr);
                // Don't show error to user, just log it
              }
            }, 1000);
            
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
