import React, { useEffect, useState } from 'react';
import api from '../services/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

interface Summary {
  total_threats: number;
  critical_threats: number;
  open_incidents: number;
  pending_alerts: number;
  avg_response_time: string;
}

interface AnalyticsData {
  summary: Summary;
  threat_trends: { date: string; count: number }[];
  top_ips: { source_ip: string; count: number }[];
  severity_distribution: { critical: number; high: number; medium: number; low: number };
  analyst_performance: { name: string; resolved: number }[];
}

export default function Dashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await api.get('/analytics/dashboard/');
        setData(res.data);
      } catch (err) {
        console.error("Failed to load analytics:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        Loading dashboard analytics...
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 text-red-400">
        Failed to load dashboard data.
      </div>
    );
  }

  // Chart Options (Dark Theme)
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#9ca3af' } },
    },
    scales: {
      x: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
      y: { ticks: { color: '#9ca3af' }, grid: { color: '#374151' } },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'right' as const, labels: { color: '#9ca3af' } },
    },
  };

  // Chart Data
  const trendData = {
    labels: data.threat_trends.map(t => t.date.slice(5)), // Show MM-DD
    datasets: [
      {
        label: 'Threats Detected',
        data: data.threat_trends.map(t => t.count),
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const ipData = {
    labels: data.top_ips.map(ip => ip.source_ip),
    datasets: [
      {
        label: 'Attack Count',
        data: data.top_ips.map(ip => ip.count),
        backgroundColor: '#ef4444',
        borderRadius: 4,
      },
    ],
  };

  const severityData = {
    labels: ['Critical', 'High', 'Medium', 'Low'],
    datasets: [
      {
        data: [
          data.severity_distribution.critical,
          data.severity_distribution.high,
          data.severity_distribution.medium,
          data.severity_distribution.low,
        ],
        backgroundColor: ['#ef4444', '#f97316', '#eab308', '#22c55e'],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Security Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Real-time overview of your security posture</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SummaryCard title="Total Threats" value={data.summary.total_threats} icon="🚨" color="border-blue-500" />
        <SummaryCard title="Critical Threats" value={data.summary.critical_threats} icon="🔥" color="border-red-500" />
        <SummaryCard title="Open Incidents" value={data.summary.open_incidents} icon="📋" color="border-yellow-500" />
        <SummaryCard title="Pending Alerts" value={data.summary.pending_alerts} icon="🔔" color="border-purple-500" />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Trends */}
        <div className="lg:col-span-2 bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">📈 Threat Trends (Last 30 Days)</h2>
          <div className="h-64">
            <Line data={trendData} options={chartOptions} />
          </div>
        </div>

        {/* Severity Distribution */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">🎯 Severity Distribution</h2>
          <div className="h-64 flex items-center justify-center">
            <Doughnut data={severityData} options={doughnutOptions} />
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Attacking IPs */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">🌍 Top Attacking IPs</h2>
          <div className="h-64">
            <Bar data={ipData} options={{ ...chartOptions, indexAxis: 'y' as const }} />
          </div>
        </div>

        {/* Analyst Performance */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-white mb-4">👥 Analyst Performance (Resolved)</h2>
          <div className="space-y-4">
            {data.analyst_performance.length === 0 ? (
              <p className="text-gray-500 text-sm">No resolved incidents in the last 30 days.</p>
            ) : (
              data.analyst_performance.map((analyst, idx) => (
                <div key={idx} className="flex items-center justify-between bg-gray-800 p-3 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-900 text-blue-300 rounded-full flex items-center justify-center font-bold text-sm">
                      {analyst.name.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-white text-sm font-medium">{analyst.name}</span>
                  </div>
                  <span className="text-green-400 font-bold">{analyst.resolved} Resolved</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function SummaryCard({ title, value, icon, color }: { title: string; value: number; icon: string; color: string }) {
  return (
    <div className={`bg-gray-900 border-l-4 ${color} border-gray-800 rounded-xl p-5 shadow-lg`}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-400 text-sm font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-2">{value.toLocaleString()}</p>
        </div>
        <span className="text-2xl">{icon}</span>
      </div>
    </div>
  );
}