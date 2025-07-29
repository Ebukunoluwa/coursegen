import React, { useState, useEffect } from 'react';
import { Play, Pause, SkipBack, SkipForward, RotateCcw, RotateCw, Maximize2 } from 'lucide-react';

const VideoControls = ({ videoId, timestamp, onTimeUpdate }) => {
  const [player, setPlayer] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentVideoId, setCurrentVideoId] = useState(videoId);

  // Debug logging
  console.log('VideoControls props:', { videoId, timestamp, onTimeUpdate });
  console.log('VideoControls state:', { isReady, isPlaying, currentTime, duration, currentVideoId });



  const timestampToSeconds = (timestamp) => {
    if (!timestamp) return 0;
    const parts = timestamp.split(':');
    if (parts.length === 2) {
      const [minutes, seconds] = parts;
      return parseInt(minutes) * 60 + parseInt(seconds);
    } else if (parts.length === 3) {
      const [hours, minutes, seconds] = parts;
      return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(seconds);
    }
    return 0;
  };

  // Handle timestamp changes (when user clicks on chapters)
  useEffect(() => {
    if (player && isReady && timestamp) {
      const seconds = timestampToSeconds(timestamp);
      if (seconds >= 0) {
        try {
          // Add a small delay to ensure player is fully ready
          setTimeout(() => {
            if (player && player.seekTo) {
              player.seekTo(seconds, true);
            }
          }, 100);
        } catch (error) {
          console.error('Error seeking to timestamp:', error);
        }
      }
    }
  }, [timestamp, player, isReady]);

  useEffect(() => {
    if (videoId && videoId !== currentVideoId) {
      setCurrentVideoId(videoId);
      if (player) {
        try {
          // Load the new video
          player.loadVideoById(videoId);
          if (timestamp) {
            const seconds = timestampToSeconds(timestamp);
            if (seconds >= 0) {
              // Add a small delay to ensure player is fully ready
              setTimeout(() => {
                if (player && player.seekTo) {
                  player.seekTo(seconds, true);
                }
              }, 100);
            }
          }
        } catch (error) {
          console.error('Error loading new video:', error);
        }
      }
    }
  }, [videoId, timestamp, player, currentVideoId]);

  useEffect(() => {
    // Load YouTube IFrame API
    if (!window.YT) {
      console.log('Loading YouTube IFrame API...');
      const tag = document.createElement('script');
      tag.src = 'https://www.youtube.com/iframe_api';
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    } else {
      console.log('YouTube API already loaded');
    }

    // Initialize player when API is ready
    window.onYouTubeIframeAPIReady = () => {
      console.log('YouTube API ready, initializing player with videoId:', videoId);
      initializePlayer();
    };

    // Also try to initialize if API is already loaded
    if (window.YT && window.YT.Player) {
      console.log('YouTube API already available, initializing player');
      initializePlayer();
    }

    function initializePlayer() {
      if (videoId) {
        try {
          const startTime = timestamp ? timestampToSeconds(timestamp) : 0;
          console.log('Creating YouTube player with:', { videoId, startTime });
          new window.YT.Player('youtube-player', {
            videoId: videoId,
            playerVars: {
              start: startTime,
              controls: 0, // Hide default controls
              modestbranding: 1,
              rel: 0,
              showinfo: 0,
              fs: 0, // Disable fullscreen button
            },
            height: '315',
            width: '560',
            events: {
              onReady: (event) => {
                console.log('YouTube player ready!', { videoId, startTime });
                // Ensure the player is properly initialized
                if (event.target && event.target.getDuration) {
                  setPlayer(event.target);
                  setIsReady(true);
                  setDuration(event.target.getDuration());
                  setCurrentTime(startTime);
                  console.log('Player initialized successfully');
                  // Add a small delay to ensure player is fully ready before seeking
                  setTimeout(() => {
                    try {
                      if (event.target && event.target.seekTo) {
                        event.target.seekTo(startTime, true);
                        if (event.target.playVideo) {
                          event.target.playVideo();
                        }
                      }
                    } catch (error) {
                      console.error('Error in onReady event:', error);
                    }
                  }, 100);
                } else {
                  console.error('Player not properly initialized');
                }
              },
              onStateChange: (event) => {
                console.log('Player state changed:', event.data);
                if (event.data === window.YT.PlayerState.PLAYING) {
                  setIsPlaying(true);
                } else if (event.data === window.YT.PlayerState.PAUSED) {
                  setIsPlaying(false);
                }
              },
              onError: (event) => {
                console.error('YouTube player error:', event.data);
              }
            },
          });
        } catch (error) {
          console.error('Error initializing YouTube player:', error);
        }
      } else {
        console.error('No videoId provided to VideoControls');
      }
    };

    // Update time every second
    const interval = setInterval(() => {
      if (player && isPlaying && isReady) {
        try {
          if (player.getCurrentTime) {
            const time = player.getCurrentTime();
            setCurrentTime(time);
            if (onTimeUpdate) onTimeUpdate(time);
          }
        } catch (error) {
          console.error('Error updating time:', error);
        }
      }
    }, 1000);

    // Cleanup function
    return () => {
      if (player) {
        try {
          if (player.destroy) {
            player.destroy();
          }
        } catch (error) {
          console.error('Error destroying player:', error);
        }
      }
      clearInterval(interval);
    };
  }, [videoId, player, isPlaying, isReady, onTimeUpdate, timestamp]);

  // Validate videoId - moved after all useEffect hooks
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handlePlayPause = () => {
    if (player && isReady) {
      try {
        if (isPlaying) {
          if (player.pauseVideo) {
            player.pauseVideo();
          }
        } else {
          if (player.playVideo) {
            player.playVideo();
          }
        }
      } catch (error) {
        console.error('Error toggling play/pause:', error);
      }
    }
  };

  const handleRewind = () => {
    if (player && isReady) {
      try {
        const newTime = Math.max(0, currentTime - 10);
        if (player.seekTo) {
          player.seekTo(newTime, true);
          setCurrentTime(newTime);
        }
      } catch (error) {
        console.error('Error rewinding:', error);
      }
    }
  };

  const handleFastForward = () => {
    if (player && isReady) {
      try {
        const newTime = Math.min(duration, currentTime + 10);
        if (player.seekTo) {
          player.seekTo(newTime, true);
          setCurrentTime(newTime);
        }
      } catch (error) {
        console.error('Error fast forwarding:', error);
      }
    }
  };

  const handleSkipBack = () => {
    if (player && isReady) {
      try {
        const newTime = Math.max(0, currentTime - 30);
        if (player.seekTo) {
          player.seekTo(newTime, true);
          setCurrentTime(newTime);
        }
      } catch (error) {
        console.error('Error skipping back:', error);
      }
    }
  };

  const handleSkipForward = () => {
    if (player && isReady) {
      try {
        const newTime = Math.min(duration, currentTime + 30);
        if (player.seekTo) {
          player.seekTo(newTime, true);
          setCurrentTime(newTime);
        }
      } catch (error) {
        console.error('Error skipping forward:', error);
      }
    }
  };

  const handleFullscreen = () => {
    if (player && isReady) {
      try {
        if (isFullscreen) {
          // Exit fullscreen
          if (document.exitFullscreen) {
            document.exitFullscreen();
          } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
          } else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
          } else if (document.msExitFullscreen) {
            document.msExitFullscreen();
          }
          setIsFullscreen(false);
        } else {
          // Enter fullscreen
          const videoContainer = document.getElementById('youtube-player');
          if (videoContainer) {
            if (videoContainer.requestFullscreen) {
              videoContainer.requestFullscreen();
            } else if (videoContainer.webkitRequestFullscreen) {
              videoContainer.webkitRequestFullscreen();
            } else if (videoContainer.mozRequestFullScreen) {
              videoContainer.mozRequestFullScreen();
            } else if (videoContainer.msRequestFullscreen) {
              videoContainer.msRequestFullscreen();
            }
            setIsFullscreen(true);
          }
        }
      } catch (error) {
        console.error('Fullscreen error:', error);
      }
    }
  };

  const handleVideoClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    

    
    if (player && isReady) {
      try {
        // Toggle play/pause
        if (isPlaying) {
          if (player.pauseVideo) {
            player.pauseVideo();
            setIsPlaying(false);
          }
        } else {
          if (player.playVideo) {
            player.playVideo();
            setIsPlaying(true);
          }
        }
      } catch (error) {
        console.error('Error handling video click:', error);
      }
    }
  };

  const handleProgressBarClick = (e) => {
    if (player && isReady && duration > 0) {
      try {
        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const clickPercent = clickX / rect.width;
        const newTime = duration * clickPercent;
        if (player.seekTo) {
          player.seekTo(newTime, true);
          setCurrentTime(newTime);
        }
      } catch (error) {
        console.error('Error handling progress bar click:', error);
      }
    }
  };

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
          className="relative h-2 bg-gray-700 rounded-full mb-3 cursor-pointer hover:h-3 transition-all duration-200" 
          onClick={handleProgressBarClick}
          title="Click to seek to position"
        >
          <div
            className="absolute h-full bg-primary-500 rounded-full"
            style={{ width: `${(currentTime / duration) * 100}%` }}
          ></div>
          {/* Progress bar thumb */}
          <div 
            className="absolute top-1/2 transform -translate-y-1/2 w-3 h-3 bg-primary-500 rounded-full shadow-lg"
            style={{ left: `${(currentTime / duration) * 100}%`, marginLeft: '-6px' }}
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
            <button onClick={handleSkipBack} className="control-button p-1">
              <RotateCcw className="h-4 w-4" />
            </button>
            <button onClick={handleRewind} className="control-button p-1">
              <SkipBack className="h-4 w-4" />
            </button>
            <button onClick={handlePlayPause} className="control-button text-primary-500 p-1">
              {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
            </button>
            <button onClick={handleFastForward} className="control-button p-1">
              <SkipForward className="h-4 w-4" />
            </button>
            <button onClick={handleSkipForward} className="control-button p-1">
              <RotateCw className="h-4 w-4" />
            </button>
            <button onClick={handleFullscreen} className="control-button p-1">
              <Maximize2 className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoControls; 