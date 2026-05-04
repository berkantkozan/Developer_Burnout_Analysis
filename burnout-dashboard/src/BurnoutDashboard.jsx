import React, { useState, useMemo } from 'react';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, ReferenceLine
} from 'recharts';
import './BurnoutDashboard.css';

// Modelimizden gelen veriyi simüle ediyoruz (Bunu CSV'den gelen veriyle değiştireceksiniz)
const MOCK_DATA = [
  { date: '1. Hafta', burnoutRisk: 1.2, commitCount: 250 },
  { date: '2. Hafta', burnoutRisk: 1.5, commitCount: 310 },
  { date: '3. Hafta', burnoutRisk: 2.1, commitCount: 420 },
  { date: '4. Hafta', burnoutRisk: 1.8, commitCount: 380 },
  { date: '5. Hafta', burnoutRisk: 3.5, commitCount: 650 }, // Proje teslimi yaklaşıyor
  { date: '6. Hafta', burnoutRisk: 4.8, commitCount: 780 }, // Zirve - Kriz anı
  { date: '7. Hafta', burnoutRisk: 4.2, commitCount: 600 },
  { date: '8. Hafta', burnoutRisk: 2.5, commitCount: 320 }, // Sürüm çıktı, stres düştü
  { date: '9. Hafta', burnoutRisk: 1.4, commitCount: 210 },
  { date: '10. Hafta', burnoutRisk: 1.1, commitCount: 180 },
];

const BurnoutDashboard = () => {
  const [viewMetric, setViewMetric] = useState('burnout'); // 'burnout' veya 'commit'
  const [threshold, setThreshold] = useState(3.0);

  // İstatistikleri Hesaplama
  const stats = useMemo(() => {
    let totalRisk = 0;
    let totalCommits = 0;
    let warningWeeks = 0;

    MOCK_DATA.forEach(item => {
      totalRisk += item.burnoutRisk;
      totalCommits += item.commitCount;
      if (item.burnoutRisk >= threshold) warningWeeks++;
    });

    return {
      avgRisk: (totalRisk / MOCK_DATA.length).toFixed(1),
      totalCommits: totalCommits,
      warningWeeks: warningWeeks
    };
  }, [threshold]);

  // Özel Nokta Çizici (Eşiği aşanları Kırmızı yapar)
  const renderCustomDot = (props) => {
    const { cx, cy, payload } = props;
    const isCritical = payload.burnoutRisk >= threshold;
    
    return (
      <circle 
        key={`dot-${payload.date}`}
        cx={cx} 
        cy={cy} 
        r={isCritical ? 6 : 4} 
        stroke={isCritical ? "#ef4444" : "#3b82f6"} 
        strokeWidth={2} 
        fill={isCritical ? "#fee2e2" : "#ffffff"} 
      />
    );
  };

  // Tooltip Özelleştirme
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{ backgroundColor: '#fff', padding: '10px', border: '1px solid #ccc', borderRadius: '5px' }}>
          <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>{label}</p>
          <p style={{ margin: 0, color: payload[0].color }}>
            {payload[0].name}: {payload[0].value}{viewMetric === 'burnout' ? '%' : ''}
          </p>
          {viewMetric === 'burnout' && payload[0].value >= threshold && (
            <p style={{ margin: '5px 0 0 0', color: '#ef4444', fontSize: '12px', fontWeight: 'bold' }}>
              ⚠️ Kritik Eşik Aşıldı!
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Geliştirici Tükenmişlik (Burnout) Analizi</h1>
        <p>RoBERTa Modeli NLP Çıkarımları ve Zaman Serisi İzleme Sistemi</p>
      </div>

      {/* ÖZET KARTLARI */}
      <div className="summary-cards">
        <div className="card">
          <div className="card-title">Ortalama Tükenmişlik Riski</div>
          <div className="card-value">%{stats.avgRisk}</div>
        </div>
        <div className="card">
          <div className="card-title">Toplam İncelenen Commit</div>
          <div className="card-value">{stats.totalCommits.toLocaleString()}</div>
        </div>
        <div className={`card ${stats.warningWeeks > 0 ? 'danger' : ''}`}>
          <div className="card-title">Eşiği Aşan Kritik Hafta Sayısı</div>
          <div className="card-value" style={{ color: stats.warningWeeks > 0 ? '#ef4444' : '#0f172a' }}>
            {stats.warningWeeks}
          </div>
        </div>
      </div>

      {/* KONTROL PANELİ */}
      <div className="controls-panel">
        <div className="view-toggles">
          <button 
            className={`toggle-btn ${viewMetric === 'burnout' ? 'active' : ''}`}
            onClick={() => setViewMetric('burnout')}
          >
            Tükenmişlik Riski (%)
          </button>
          <button 
            className={`toggle-btn ${viewMetric === 'commit' ? 'active' : ''}`}
            onClick={() => setViewMetric('commit')}
          >
            İş Yükü (Commit Sayısı)
          </button>
        </div>

        <div className="slider-container">
          <label>Kritik Uyarı Eşiği:</label>
          <input 
            type="range" 
            min="1.0" max="6.0" step="0.1" 
            value={threshold} 
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="threshold-slider"
            disabled={viewMetric !== 'burnout'}
          />
          <span className="threshold-value">%{threshold.toFixed(1)}</span>
        </div>
      </div>

      {/* GRAFİK ALANI */}
      <div className="chart-container">
        <h3 className="chart-title">
          {viewMetric === 'burnout' ? 'Haftalık Tükenmişlik Eğilimi' : 'Haftalık Kodlama İş Yükü Dağılımı'}
        </h3>
        <ResponsiveContainer width="100%" height="90%">
          {viewMetric === 'burnout' ? (
            <LineChart data={MOCK_DATA} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" />
              <YAxis stroke="#64748b" domain={[0, 'dataMax + 1']} unit="%" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              
              {/* Kullanıcının seçtiği Eşik Çizgisi */}
              <ReferenceLine y={threshold} label={{ position: 'top', value: 'Kritik Eşik', fill: '#ef4444' }} stroke="#ef4444" strokeDasharray="3 3" />
              
              <Line 
                type="monotone" 
                dataKey="burnoutRisk" 
                name="Tükenmişlik Skoru" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={renderCustomDot}
                activeDot={{ r: 8 }} 
              />
            </LineChart>
          ) : (
            <BarChart data={MOCK_DATA} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="date" stroke="#64748b" />
              <YAxis stroke="#64748b" />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f1f5f9' }} />
              <Legend />
              <Bar 
                dataKey="commitCount" 
                name="Commit Sayısı" 
                fill="#94a3b8" 
                radius={[4, 4, 0, 0]} 
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default BurnoutDashboard;