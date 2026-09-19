import { useEffect, useState, useRef } from 'react';
import type { Threat } from '../types';

export function useThreatWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [latestThreat, setLatestThreat] = useState<Threat | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    // Connect directly to Django Channels (bypassing Vite proxy for WS)
    const wsUrl = `ws://localhost:8000/ws/threats/?token=${token}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("✅ WebSocket connected globally");
      setIsConnected(true);
    };
    
    ws.onclose = () => {
      console.log("🔴 WebSocket disconnected");
      setIsConnected(false);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'threat_detected') {
          console.log("🚨 New threat detected globally:", data.threat.threat_type);
          setLatestThreat(data.threat);
          
          // Clear the notification popup after 6 seconds
          setTimeout(() => setLatestThreat(null), 6000);
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return { isConnected, latestThreat };
}