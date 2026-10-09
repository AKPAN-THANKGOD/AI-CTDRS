// LOCATION: frontend/src/hooks/useThreatWebSocket.ts
import { createContext, createElement, useContext, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import type { Threat } from '../types';

interface SocketState {
  isConnected: boolean;
  latestThreat: Threat | null;
}

const ThreatSocketContext = createContext<SocketState>({ isConnected: false, latestThreat: null });

// ws(s):// host derived from the API URL, so it works on Render as well as locally
function wsBase(): string {
  const api = import.meta.env.DEV
    ? (import.meta.env.VITE_API_URL || 'http://localhost:8000/api')
    : (import.meta.env.VITE_API_URL || 'https://ai-ctdrs.onrender.com/api');
  const u = new URL(api);
  return `${u.protocol === 'https:' ? 'wss:' : 'ws:'}//${u.host}`;
}

function useSocket(): SocketState {
  const [isConnected, setIsConnected] = useState(false);
  const [latestThreat, setLatestThreat] = useState<Threat | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    let ws: WebSocket | null = null;
    let retry: ReturnType<typeof setTimeout> | undefined;
    let clear: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;

    const connect = () => {
      ws = new WebSocket(`${wsBase()}/ws/threats/?token=${encodeURIComponent(token)}`);
      ws.onopen = () => setIsConnected(true);
      ws.onclose = () => {
        setIsConnected(false);
        if (!stopped) retry = setTimeout(connect, 5000); // Render free tier sleeps; reconnect
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'threat_detected') {
            setLatestThreat(data.threat);
            clearTimeout(clear);
            clear = setTimeout(() => setLatestThreat(null), 6000);
          }
        } catch (e) {
          console.error('Bad WebSocket message', e);
        }
      };
    };
    connect();

    return () => {
      stopped = true;
      clearTimeout(retry);
      clearTimeout(clear);
      ws?.close();
    };
  }, []);

  return { isConnected, latestThreat };
}

// ONE socket for the whole app (previously App and Alerts each opened their own)
export function ThreatSocketProvider({ children }: { children: ReactNode }) {
  return createElement(ThreatSocketContext.Provider, { value: useSocket() }, children);
}

export function useThreatWebSocket(): SocketState {
  return useContext(ThreatSocketContext);
}