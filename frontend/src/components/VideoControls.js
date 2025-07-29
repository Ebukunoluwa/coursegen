import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Play, Pause, SkipBack, SkipForward, RotateCcw, RotateCw, Maximize2 } from 'lucide-react';

const VideoControls = ({ videoId, timestamp, onTimeUpdate }) => {
  const [player, setPlayer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const [currentVideoId, setCurrentVideoId] = useState(videoId);
  const [error, setError] = useState(null);
  const playerRef = useRef(null);
  const intervalRef = useRef(null);
  const [isSeeking, setIsSeeking] = useState(false);

  // Debug logging
  console.log('VideoControls props:', { videoId, timestamp, onTimeUpdate });

  const timestampToSeconds = (timestamp) => {
    if (!timestamp) return 0;
    const parts = timestamp.split(':');
    if (parts.length === 2) {
      const minutes = parts[0];
      const seconds = parts[1];
      return parseInt(minutes) * 60 + parseInt(seconds);
    } else if (parts.length === 3) {
      const hours = parts[0];
      const minutes = parts[1];
      const seconds = parts[2];
      return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds);
    }
    return 0;
  };

  const initializePlayer = useCallback(() => {
    console.log('initializePlayer called with:', { videoId, timestamp });
    
    if (!videoId) {
      console.error('No videoId provided');
      setError('No video ID provided');
      return;
    }
    
    if (!window.YT || !window.YT.Player) {
      console.error('YouTube API not available');
      setError('YouTube API not available');
      return;
    }

    try {
      const startTime = timestamp ? timestampToSeconds(timestamp) : 0;
      console.log('Creating YouTube player with:', { videoId, startTime });
      
      // Check if the player element exists
      const playerElement = document.getElementById('youtube-player');
      if (!playerElement) {
        console.error('YouTube player element not found');
        setError('Player element not found');
        return;
      }
      
      // Clear any existing player
      if (playerRef.current) {
        try {
          playerRef.current.destroy();
        } catch (error) {
          console.log('Error destroying existing player:', error);
        }
      }
      
      const newPlayer = new window.YT.Player('youtube-player', {
        videoId: videoId,
        playerVars: {
          start: startTime,
          controls: 0, // Hide default controls
          modestbranding: 1,
          rel: 0,
          showinfo: 0,
          fs: 0, // Disable fullscreen button
          autoplay: 0, // Don't autoplay initially
        },
        height: '100%',
        width: '100%',
        events: {
          onReady: (event) => {
            try {
              console.log('YouTube player ready!', { videoId, startTime });
              const playerInstance = event.target;
              
              // Set both state and ref for maximum reliability
              setPlayer(playerInstance);
              playerRef.current = playerInstance;
              setIsReady(true);
              setDuration(playerInstance.getDuration());
              setCurrentTime(startTime);
              setError(null);
              console.log('Player initialized successfully');
              
              // Verify player methods are available
              console.log('Player methods available:', {
                seekTo: typeof playerInstance.seekTo === 'function',
                playVideo: typeof playerInstance.playVideo === 'function',
                pauseVideo: typeof playerInstance.pauseVideo === 'function',
                getCurrentTime: typeof playerInstance.getCurrentTime === 'function',
                getDuration: typeof playerInstance.getDuration === 'function'
              });
              
              // Test seek functionality immediately
              setTimeout(() => {
                try {
                  if (playerInstance && playerInstance.seekTo) {
                    console.log('Testing seek functionality on ready...');
                    const testTime = Math.min(playerInstance.getDuration(), 10);
                    playerInstance.seekTo(testTime, true);
                    console.log('Initial seek test completed');
                  }
                } catch (error) {
                  console.error('Error in initial seek test:', error);
                }
              }, 1000);
              
              // Seek to timestamp if provided
              if (timestamp) {
                setTimeout(() => {
                  try {
                    if (playerInstance && playerInstance.seekTo) {
                      console.log('Seeking to initial timestamp:', startTime);
                      playerInstance.seekTo(startTime, true);
                      setCurrentTime(startTime);
                    }
                  } catch (error) {
                    console.error('Error in onReady event:', error);
                    setError('Failed to seek to timestamp');
                  }
                }, 500);
              }
            } catch (error) {
              console.error('Error in onReady callback:', error);
              setError('Failed to initialize player');
            }
          },
          onStateChange: (event) => {
            try {
              console.log('Player state changed:', event.data);
              if (event.data === window.YT.PlayerState.PLAYING) {
                setIsPlaying(true);
              } else if (event.data === window.YT.PlayerState.PAUSED) {
                setIsPlaying(false);
              } else if (event.data === window.YT.PlayerState.ENDED) {
                setIsPlaying(false);
              }
            } catch (error) {
              console.error('Error in onStateChange:', error);
            }
          },
          onError: (event) => {
            console.error('YouTube player error:', event.data);
            setError('Video playback error');
          }
        },
      });
      
      console.log('Player creation initiated');
    } catch (error) {
      console.error('Error initializing YouTube player:', error);
      setError('Failed to initialize video player');
    }
  }, [videoId, timestamp]);

  // Load YouTube IFrame API
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check if YouTube API is already loaded
    if (window.YT && window.YT.Player) {
      console.log('YouTube API already loaded');
      // Initialize player immediately if API is ready
      if (videoId) {
        setTimeout(() => initializePlayer(), 100);
      }
      return;
    }

    // Load YouTube IFrame API
    const tag = document.createElement('script');
    tag.src = 'https://www.youtube.com/iframe_api';
    const firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    // Set up global callback
    window.onYouTubeIframeAPIReady = () => {
      console.log('YouTube IFrame API ready');
      // Initialize player when API is ready
      if (videoId) {
        setTimeout(() => initializePlayer(), 100);
      }
    };

    return () => {
      // Cleanup
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [videoId, initializePlayer]);

  // Initialize player when videoId changes
  useEffect(() => {
    if (videoId !== currentVideoId) {
      setCurrentVideoId(videoId);
      setIsReady(false);
      setPlayer(null);
      setError(null);
      
      // Initialize player if API is ready
      if (window.YT && window.YT.Player && videoId) {
        setTimeout(() => initializePlayer(), 100);
      }
    }
  }, [videoId, currentVideoId, initializePlayer]);

  // Seek to timestamp when player is ready
  useEffect(() => {
    if (player && isReady && timestamp) {
      try {
        const seconds = timestampToSeconds(timestamp);
        if (seconds >= 0) {
          console.log('Seeking to timestamp:', timestamp, 'seconds:', seconds);
          player.seekTo(seconds, true);
          setCurrentTime(seconds);
          // Auto-play when seeking to timestamp
          setTimeout(() => {
            if (player && player.playVideo) {
              player.playVideo();
              setIsPlaying(true);
            }
          }, 500);
        }
      } catch (error) {
        console.error('Error seeking to timestamp:', error);
        setError('Failed to seek to timestamp');
      }
    }
  }, [player, isReady, timestamp]);

  // Handle new video loading
  useEffect(() => {
    if (videoId && videoId !== currentVideoId) {
      try {
        setCurrentVideoId(videoId);
        setIsReady(false);
        setPlayer(null);
        setError(null);
        
        // Small delay to ensure DOM is ready
        setTimeout(() => {
          initializePlayer();
        }, 100);
      } catch (error) {
        console.error('Error loading new video:', error);
        setError('Failed to load video');
      }
    }
  }, [videoId, currentVideoId, initializePlayer]);

  // Time update interval
  useEffect(() => {
    if (player && isReady) {
      // Update time every 50ms for smoother progress bar
      intervalRef.current = setInterval(() => {
        try {
          if (player && player.getCurrentTime) {
            const time = player.getCurrentTime();
            // Only update if the time has actually changed significantly
            if (Math.abs(time - currentTime) > 0.1) {
              setCurrentTime(time);
              if (onTimeUpdate) onTimeUpdate(time);
            }
          }
        } catch (error) {
          console.error('Error updating time:', error);
          // Clear interval on error to prevent further issues
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        }
      }, 50); // More frequent updates for smoother progress
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [player, isReady, onTimeUpdate, currentTime]);

  // Cleanup and reset mechanism
  useEffect(() => {
    if (player && isReady) {
      // Reset seeking state periodically to ensure responsiveness
      const cleanupInterval = setInterval(() => {
        if (isSeeking) {
          setIsSeeking(false);
        }
      }, 5000); // Reset every 5 seconds if still seeking

      return () => {
        clearInterval(cleanupInterval);
      };
    }
  }, [player, isReady, isSeeking]);

  // Reset seeking state when player state changes
  useEffect(() => {
    if (!isPlaying && isSeeking) {
      // Reset seeking state when video stops playing
      setTimeout(() => {
        setIsSeeking(false);
      }, 500);
    }
  }, [isPlaying, isSeeking]);

  // Check player validity periodically
  useEffect(() => {
    if (player && isReady) {
      const checkInterval = setInterval(() => {
        try {
          const currentPlayer = playerRef.current || player;
          if (currentPlayer && typeof currentPlayer.getCurrentTime === 'function') {
            // Player is still valid
            const time = currentPlayer.getCurrentTime();
            if (time !== currentTime) {
              setCurrentTime(time);
            }
          } else {
            console.warn('Player methods not available, attempting to reinitialize...');
            // Try to reinitialize the player
            setTimeout(() => {
              if (videoId) {
                initializePlayer();
              }
            }, 1000);
          }
        } catch (error) {
          console.error('Error checking player validity:', error);
        }
      }, 2000); // Check every 2 seconds

      return () => clearInterval(checkInterval);
    }
  }, [player, isReady, currentTime, videoId, initializePlayer]);

  // Fullscreen change event listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isFullscreenNow = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
      console.log('Fullscreen state changed:', isFullscreenNow);
      console.log('Fullscreen element:', document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
      setIsFullscreen(isFullscreenNow);
    };

    // Check initial fullscreen state
    const initialFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
    console.log('Initial fullscreen state:', initialFullscreen);
    setIsFullscreen(initialFullscreen);

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
    };
  }, []);

  const formatTime = (seconds) => {
    if (isNaN(seconds) || seconds < 0) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        console.log('Toggling play/pause:', { isPlaying });
        if (isPlaying) {
          currentPlayer.pauseVideo();
        } else {
          currentPlayer.playVideo();
        }
      } catch (error) {
        console.error('Error toggling play/pause:', error);
        setError('Failed to control playback');
      }
    } else {
      console.error('Player not ready for play/pause');
    }
  };

  const handleRewind = () => {
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        const newTime = Math.max(0, currentTime - 10);
        console.log('Rewinding 10s:', { currentTime, newTime });
        
        // Update UI immediately
        setCurrentTime(newTime);
        setIsSeeking(true);
        
        if (currentPlayer && typeof currentPlayer.seekTo === 'function') {
          currentPlayer.seekTo(newTime, true);
          console.log('Rewind command sent to player');
        } else {
          console.error('Player or seekTo method not available for rewind');
          setError('Player not ready');
          setIsSeeking(false);
          return;
        }
        
        // Verify the seek worked
        setTimeout(() => {
          try {
            const currentPlayer = playerRef.current || player;
            if (currentPlayer && currentPlayer.getCurrentTime) {
              const actualTime = currentPlayer.getCurrentTime();
              console.log('Actual time after rewind:', actualTime);
              setCurrentTime(actualTime);
            }
            setIsSeeking(false);
          } catch (error) {
            console.error('Error in rewind verification:', error);
            setIsSeeking(false);
          }
        }, 200);
        
      } catch (error) {
        console.error('Error rewinding:', error);
        setError('Failed to rewind');
        setIsSeeking(false);
      }
    } else {
      console.error('Player not ready for rewind');
    }
  };

  const handleFastForward = () => {
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        const newTime = Math.min(duration, currentTime + 10);
        console.log('Fast forwarding 10s:', { currentTime, newTime });
        
        // Update UI immediately
        setCurrentTime(newTime);
        setIsSeeking(true);
        
        if (currentPlayer && typeof currentPlayer.seekTo === 'function') {
          currentPlayer.seekTo(newTime, true);
          console.log('Fast forward command sent to player');
        } else {
          console.error('Player or seekTo method not available for fast forward');
          setError('Player not ready');
          setIsSeeking(false);
          return;
        }
        
        // Verify the seek worked
        setTimeout(() => {
          try {
            const currentPlayer = playerRef.current || player;
            if (currentPlayer && currentPlayer.getCurrentTime) {
              const actualTime = currentPlayer.getCurrentTime();
              console.log('Actual time after fast forward:', actualTime);
              setCurrentTime(actualTime);
            }
            setIsSeeking(false);
          } catch (error) {
            console.error('Error in fast forward verification:', error);
            setIsSeeking(false);
          }
        }, 200);
        
      } catch (error) {
        console.error('Error fast forwarding:', error);
        setError('Failed to fast forward');
        setIsSeeking(false);
      }
    } else {
      console.error('Player not ready for fast forward');
    }
  };

  const handleSkipBack = () => {
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        const newTime = Math.max(0, currentTime - 30);
        console.log('Skipping back 30s:', { currentTime, newTime });
        
        // Update UI immediately
        setCurrentTime(newTime);
        setIsSeeking(true);
        
        if (currentPlayer && typeof currentPlayer.seekTo === 'function') {
          currentPlayer.seekTo(newTime, true);
          console.log('Skip back command sent to player');
        } else {
          console.error('Player or seekTo method not available for skip back');
          setError('Player not ready');
          setIsSeeking(false);
          return;
        }
        
        // Verify the seek worked
        setTimeout(() => {
          try {
            const currentPlayer = playerRef.current || player;
            if (currentPlayer && currentPlayer.getCurrentTime) {
              const actualTime = currentPlayer.getCurrentTime();
              console.log('Actual time after skip back:', actualTime);
              setCurrentTime(actualTime);
            }
            setIsSeeking(false);
          } catch (error) {
            console.error('Error in skip back verification:', error);
            setIsSeeking(false);
          }
        }, 200);
        
      } catch (error) {
        console.error('Error skipping back:', error);
        setError('Failed to skip back');
        setIsSeeking(false);
      }
    } else {
      console.error('Player not ready for skip back');
    }
  };

  const handleSkipForward = () => {
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        const newTime = Math.min(duration, currentTime + 30);
        console.log('Skipping forward 30s:', { currentTime, newTime });
        
        // Update UI immediately
        setCurrentTime(newTime);
        setIsSeeking(true);
        
        if (currentPlayer && typeof currentPlayer.seekTo === 'function') {
          currentPlayer.seekTo(newTime, true);
          console.log('Skip forward command sent to player');
        } else {
          console.error('Player or seekTo method not available for skip forward');
          setError('Player not ready');
          setIsSeeking(false);
          return;
        }
        
        // Verify the seek worked
        setTimeout(() => {
          try {
            const currentPlayer = playerRef.current || player;
            if (currentPlayer && currentPlayer.getCurrentTime) {
              const actualTime = currentPlayer.getCurrentTime();
              console.log('Actual time after skip forward:', actualTime);
              setCurrentTime(actualTime);
            }
            setIsSeeking(false);
          } catch (error) {
            console.error('Error in skip forward verification:', error);
            setIsSeeking(false);
          }
        }, 200);
        
      } catch (error) {
        console.error('Error skipping forward:', error);
        setError('Failed to skip forward');
        setIsSeeking(false);
      }
    } else {
      console.error('Player not ready for skip forward');
    }
  };

  const handleFullscreen = () => {
    try {
      console.log('Toggling fullscreen, current state:', isFullscreen);
      
      // Check current fullscreen state from browser
      const currentFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement);
      console.log('Browser fullscreen state:', currentFullscreen);
      
      if (currentFullscreen) {
        // Exit fullscreen
        console.log('Exiting fullscreen...');
        if (document.exitFullscreen) {
          document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen();
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen();
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen();
        }
        // Don't set state here - let the event listener handle it
      } else {
        // Enter fullscreen - try multiple approaches
        console.log('Entering fullscreen...');
        
        // Method 1: Try the video container first (more reliable)
        const videoContainer = document.querySelector('#youtube-player');
        if (videoContainer) {
          console.log('Trying video container fullscreen...');
          if (videoContainer.requestFullscreen) {
            videoContainer.requestFullscreen().catch(err => {
              console.log('Video container fullscreen failed, trying iframe...', err);
              tryIframeFullscreen();
            });
          } else if (videoContainer.webkitRequestFullscreen) {
            videoContainer.webkitRequestFullscreen().catch(err => {
              console.log('Video container webkit fullscreen failed, trying iframe...', err);
              tryIframeFullscreen();
            });
          } else {
            console.log('Video container fullscreen not supported, trying iframe...');
            tryIframeFullscreen();
          }
        } else {
          console.log('Video container not found, trying iframe...');
          tryIframeFullscreen();
        }
      }
    } catch (error) {
      console.error('Error toggling fullscreen:', error);
      setError('Fullscreen not supported in this browser');
    }
  };

  const tryIframeFullscreen = () => {
    try {
      const iframe = document.querySelector('#youtube-player iframe');
      if (!iframe) {
        console.error('YouTube iframe not found');
        return;
      }
      
      console.log('Trying iframe fullscreen...');
      if (iframe.requestFullscreen) {
        iframe.requestFullscreen().catch(err => {
          console.error('Iframe fullscreen failed:', err);
          setError('Fullscreen not available');
        });
      } else if (iframe.webkitRequestFullscreen) {
        iframe.webkitRequestFullscreen().catch(err => {
          console.error('Iframe webkit fullscreen failed:', err);
          setError('Fullscreen not available');
        });
      } else if (iframe.mozRequestFullScreen) {
        iframe.mozRequestFullScreen().catch(err => {
          console.error('Iframe moz fullscreen failed:', err);
          setError('Fullscreen not available');
        });
      } else if (iframe.msRequestFullscreen) {
        iframe.msRequestFullscreen().catch(err => {
          console.error('Iframe ms fullscreen failed:', err);
          setError('Fullscreen not available');
        });
      } else {
        console.error('No fullscreen method available on iframe');
        setError('Fullscreen not supported');
      }
    } catch (error) {
      console.error('Error in tryIframeFullscreen:', error);
      setError('Fullscreen not supported');
    }
  };

  const handleVideoClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Get fresh player reference
    const currentPlayer = playerRef.current || player;
    
    if (currentPlayer && isReady) {
      try {
        console.log('Video clicked, toggling play/pause');
        // Toggle play/pause
        if (isPlaying) {
          currentPlayer.pauseVideo();
        } else {
          currentPlayer.playVideo();
        }
      } catch (error) {
        console.error('Error handling video click:', error);
        setError('Failed to control playback');
      }
    } else {
      console.error('Player not ready for video click');
    }
  };

  const handleProgressBarClick = (e) => {
    console.log('=== PROGRESS BAR CLICKED ===');
    console.log('Event:', e);
    console.log('Player state:', { player, isReady, duration, isPlaying });
    
    // Force the click to work regardless of player state
    e.preventDefault();
    e.stopPropagation();
    
    if (!player || duration <= 0) {
      console.error('Player not ready or duration invalid');
      return;
    }

    // Get click position
    const rect = e.currentTarget.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickPercent = Math.max(0, Math.min(1, clickX / rect.width));
    const newTime = duration * clickPercent;
    
    console.log('Click details:', { clickX, rectWidth: rect.width, clickPercent, newTime, duration });
    
    // Update UI immediately
    setCurrentTime(newTime);
    setIsSeeking(true);
    
    // Force seek using multiple methods
    try {
      // Method 1: Direct seek with immediate update
      console.log('Seeking to:', newTime, 'seconds');
      
      // Ensure we have a valid player reference
      const currentPlayer = playerRef.current || player;
      if (currentPlayer && typeof currentPlayer.seekTo === 'function') {
        currentPlayer.seekTo(newTime, true);
        console.log('Seek command sent to player');
      } else {
        console.error('Player or seekTo method not available');
        setError('Player not ready');
        setIsSeeking(false);
        return;
      }
      
      // Method 2: Force update after a short delay
      setTimeout(() => {
        try {
          const currentPlayer = playerRef.current || player;
          if (currentPlayer && currentPlayer.getCurrentTime) {
            const actualTime = currentPlayer.getCurrentTime();
            console.log('Actual time after seek:', actualTime);
            setCurrentTime(actualTime);
          }
          setIsSeeking(false);
        } catch (error) {
          console.error('Error in delayed seek update:', error);
          setIsSeeking(false);
        }
      }, 200); // Increased delay for better reliability
      
    } catch (error) {
      console.error('Seek error:', error);
      setIsSeeking(false);
    }
  };

  const debugPlayer = () => {
    if (player && isReady) {
      console.log('=== PLAYER DEBUG ===');
      console.log('Player state:', {
        isReady,
        isPlaying,
        currentTime,
        duration,
        player: !!player
      });
      
      try {
        const currentTime = player.getCurrentTime();
        const duration = player.getDuration();
        console.log('Player methods test:', {
          currentTime,
          duration,
          seekToAvailable: typeof player.seekTo === 'function'
        });
        
        // Test seek functionality
        if (typeof player.seekTo === 'function') {
          console.log('Testing seek functionality...');
          const testTime = Math.min(duration, currentTime + 5);
          player.seekTo(testTime, true);
          console.log('Seek test completed');
        }
      } catch (error) {
        console.error('Player debug error:', error);
      }
    }
  };

  // Debug player on mount
  useEffect(() => {
    if (player && isReady) {
      setTimeout(debugPlayer, 1000);
    }
  }, [player, isReady]);

  // Show error state
  if (error) {
    return (
      <div className="w-full">
        <div className="bg-black aspect-video mb-2 flex items-center justify-center text-white">
          <div className="text-center">
            <Play className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p>Video Error</p>
            <p className="text-sm text-gray-400 mt-2">{error}</p>
            <button 
              onClick={() => {
                setError(null);
                initializePlayer();
              }}
              className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Add error boundary for component
  if (!videoId || typeof videoId !== 'string' || videoId.trim() === '') {
    return (
      <div className="w-full">
        <div className="bg-black aspect-video mb-2 flex items-center justify-center text-white">
          <div className="text-center">
            <Play className="h-16 w-16 mx-auto mb-4 opacity-50" />
            <p>No video available</p>
            <p className="text-sm text-gray-400 mt-2">Video ID: {videoId || 'Not provided'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      {/* Video Player with Click-to-Seek */}
      <div className="bg-black aspect-video mb-2 relative cursor-pointer" onClick={handleVideoClick} title="Click to play/pause">
        <div id="youtube-player" className="w-full h-full"></div>
        {/* Play/Pause overlay */}
        <div className="absolute inset-0 bg-transparent hover:bg-black hover:bg-opacity-20 transition-all duration-200 flex items-center justify-center">
          {!isPlaying && (
            <div className="bg-black bg-opacity-50 rounded-full p-4">
              <Play className="h-8 w-8 text-white" />
            </div>
          )}
        </div>
      </div>

      {/* Compact Controls */}
      <div className="bg-gray-900 p-3 rounded-lg">
        {/* Progress Bar - Clickable */}
        <div 
          className="relative h-2 bg-gray-700 rounded-full mb-3 cursor-pointer hover:bg-gray-600 transition-colors duration-200 border-2 border-transparent hover:border-primary-300"
          onClick={(e) => {
            console.log('PROGRESS BAR CLICKED!');
            handleProgressBarClick(e);
          }}
          title="Click to seek to position"
          style={{ 
            pointerEvents: 'auto',
            userSelect: 'none',
            WebkitUserSelect: 'none'
          }}
        >
          {/* Progress fill */}
          <div
            className={`absolute h-full bg-primary-500 rounded-full transition-all duration-200 ${
              isSeeking ? 'bg-primary-400' : ''
            }`}
            style={{ width: `${(currentTime / duration) * 100}%` }}
          ></div>
          
          {/* Progress thumb */}
          <div 
            className={`absolute top-1/2 transform -translate-y-1/2 w-3 h-3 bg-primary-500 rounded-full shadow-lg transition-all duration-200 ${
              isSeeking ? 'opacity-100 scale-110' : 'opacity-0 hover:opacity-100'
            }`}
            style={{ left: `${(currentTime / duration) * 100}%`, marginLeft: '-6px' }}
          ></div>
          
          {/* Click overlay for better responsiveness */}
          <div 
            className="absolute inset-0 bg-transparent"
            onClick={(e) => {
              console.log('OVERLAY CLICKED!');
              handleProgressBarClick(e);
            }}
          ></div>
        </div>

        {/* Time Display and Controls */}
        <div className="flex items-center justify-between">
          {/* Time Display */}
          <div className="text-xs text-gray-400">
            <span>{formatTime(currentTime)}</span>
            <span className="mx-1">/</span>
            <span>{formatTime(duration)}</span>
          </div>

          {/* Control Buttons */}
          <div className="flex items-center space-x-2">
            <button 
              onClick={handleSkipBack} 
              className="control-button p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title="Skip back 30s"
              disabled={!isReady}
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            <button 
              onClick={handleRewind} 
              className="control-button p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title="Rewind 10s"
              disabled={!isReady}
            >
              <SkipBack className="h-4 w-4" />
            </button>
            <button 
              onClick={handlePlayPause} 
              className="control-button text-primary-500 p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title={isPlaying ? "Pause" : "Play"}
              disabled={!isReady}
            >
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </button>
            <button 
              onClick={handleFastForward} 
              className="control-button p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title="Fast forward 10s"
              disabled={!isReady}
            >
              <SkipForward className="h-4 w-4" />
            </button>
            <button 
              onClick={handleSkipForward} 
              className="control-button p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title="Skip forward 30s"
              disabled={!isReady}
            >
              <RotateCw className="h-4 w-4" />
            </button>
            <button 
              onClick={handleFullscreen} 
              className="control-button p-1 hover:bg-gray-700 rounded transition-all duration-200" 
              title="Toggle fullscreen"
              disabled={!isReady}
            >
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoControls; 