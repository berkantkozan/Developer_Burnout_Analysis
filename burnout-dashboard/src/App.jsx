import React, { useState, useMemo, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, LineChart, Line, ReferenceLine
} from 'recharts';
import { sentimentData, productRiskData, lengthData, ZAMAN_SERISI } from './data';


export default function App() {
  const [activeTab, setActiveTab] = useState('genel');
  const [viewMetric, setViewMetric] = useState('burnout'); // 'burnout' veya 'commit'
  const [threshold, setThreshold] = useState(3.0);
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [analysis, setAnalysis] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/get-dashboard-data');
        const data = await response.json();
        setChartData(data.zaman_serisi);
      } catch (error) {
        console.error("Veri çekme hatası:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  // Tıklama ile Analiz Başlatan Fonksiyon
  const handleChartClick = async (data) => {
    if (!data || !data.activePayload) return;
    
    const payload = data.activePayload[0].payload;

    // Sadece eşiği geçen (kritik) noktalarda analiz yap
    if (payload.burnoutRisk >= threshold) {
      setIsAnalyzing(true);
      setAnalysis(null); // Eski analizi temizle

      try {
        const response = await fetch('http://127.0.0.1:8000/analyze-weekly-burnout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        messages: payload.criticalMessages // ANAHTAR ISMI 'messages' OLMALI
    })
});
        const result = await response.json();
        setAnalysis(result.analysis);
      } catch (error) {
        setAnalysis("Hata: LLM servisine ulaşılamadı. Lütfen backend'i kontrol edin.");
      } finally {
        setIsAnalyzing(false);
      }
    }
  };

  // özet istatistik hesaplayıcısı
  const stats = useMemo(() => {
    if (chartData.length === 0) return { avgRisk: 0, totalCommits: 0, warningWeeks: 0 };
    
    let totalRisk = 0;
    let totalCommits = 0;
    let warningWeeks = 0;
    
    chartData.forEach(item => {
      totalRisk += item.burnoutRisk;
      totalCommits += item.commitCount;
      if (item.burnoutRisk >= threshold) warningWeeks++;
    });

    return {
      avgRisk: (totalRisk / chartData.length).toFixed(1),
      totalCommits,
      warningWeeks
    };
  }, [chartData, threshold]);

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen font-bold">Veriler Analiz Ediliyor...</div>;
  }
  // Eşiği aşan noktaları kırmızı yapan fonksiyon
  const renderCustomDot = (props) => {
    const { cx, cy, payload } = props;
    const isCritical = payload.burnoutRisk >= threshold;
    return (
      <circle 
        key={`dot-${payload.author_time}`} cx={cx} cy={cy} 
        r={isCritical ? 6 : 4} 
        stroke={isCritical ? "#e11d48" : "#4f46e5"} // Tailwind rose-600 ve indigo-600
        strokeWidth={2} 
        fill={isCritical ? "#ffe4e6" : "#ffffff"} 
      />
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto bg-slate-50 min-h-screen font-sans text-slate-800">
      
      <header className="mb-8 border-b border-slate-200 pb-6">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-2">
          Otonom Ekip Dinamiği ve Burnout Analizi
        </h1>
        <p className="text-lg text-slate-500">
          Doğal Dil İşleme tabanlı stres yükü raporu.
        </p>
      </header>

      <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginBottom: '40px', flexWrap: 'wrap' }}>
        <button 
          onClick={() => setActiveTab('genel')}
          className={`px-8 py-4 font-bold rounded-2xl transition-all duration-300 flex items-center gap-3 text-base ${
            activeTab === 'genel' ? 'bg-indigo-600 text-white shadow-xl transform -translate-y-1' : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Genel Duygu Dağılımı
        </button>

        <button 
          onClick={() => setActiveTab('risk')}
          className={`px-8 py-4 font-bold rounded-2xl transition-all duration-300 flex items-center gap-3 text-base ${
            activeTab === 'risk' ? 'bg-rose-600 text-white shadow-xl transform -translate-y-1' : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Ürün Bazlı Stres Riski
        </button>

        <button 
          onClick={() => setActiveTab('uzunluk')}
          className={`px-8 py-4 font-bold rounded-2xl transition-all duration-300 flex items-center gap-3 text-base ${
            activeTab === 'uzunluk' ? 'bg-emerald-600 text-white shadow-xl transform -translate-y-1' : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Agresyon Analizi
        </button>

        <button 
          onClick={() => setActiveTab('zaman')}
          className={`px-8 py-4 font-bold rounded-2xl transition-all duration-300 flex items-center gap-3 text-base ${
            activeTab === 'zaman' ? 'bg-amber-500 text-white shadow-xl transform -translate-y-1' : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Erken Uyarı Sistemi
        </button>
      </div>

      <div className="bg-white p-8 rounded-2xl shadow-lg border border-slate-100 flex flex-col items-center justify-center">
        
        {activeTab === 'genel' && (
          <div className="w-full flex flex-col items-center">
            <h2 className="text-2xl font-bold mb-6 text-slate-700">Tüm İletişimlerin Duygu Dağılımı</h2>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie data={sentimentData} cx="50%" cy="50%" innerRadius={100} outerRadius={150} paddingAngle={4} dataKey="value" label={({name, value}) => `${name}: %${value}`} labelLine={true}>
                  {sentimentData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Pie>
                <Tooltip formatter={(value) => [`%${value}`, 'Oran']} contentStyle={{ borderRadius: '10px' }} />
                <Legend verticalAlign="bottom" height={40} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'risk' && ( 
          <div className="w-full flex flex-col">
             <div className="flex justify-between items-end mb-6">
                 <h2 className="text-2xl font-bold text-slate-700">En Yüksek Burnout Riski Taşıyan Ürünler</h2>
                 <span className="text-sm px-3 py-1 bg-amber-100 text-amber-800 rounded-full font-medium">* "Graveyard" projeler sarı ile vurgulanmıştır.</span>
             </div>
            <ResponsiveContainer width="100%" height={450}>
              <BarChart layout="vertical" data={productRiskData} margin={{ top: 5, right: 30, left: 180, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" domain={[0, 100]} tickFormatter={(val) => `%${val}`} stroke="#64748b" />
                <YAxis dataKey="name" type="category" width={170} tick={{fontSize: 13, fill: '#475569'}} />
                <Tooltip formatter={(value) => [`%${value}`, 'Negatif (Stres) Oranı']} cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '10px' }} />
                <Bar dataKey="negatifOran" radius={[0, 6, 6, 0]} barSize={24}>
                   {productRiskData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.graveyard ? '#fbbf24' : '#ef4444'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'uzunluk' && (
          <div className="w-full flex flex-col">
            <h2 className="text-2xl font-bold mb-2 text-slate-700">Duygu Durumuna Göre Ortalama Karakter Sayısı</h2>
            <p className="text-slate-500 mb-6">Geliştiricilerin stresli anlarda iletişimlerini ne kadar uzattıklarının göstergesi.</p>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={lengthData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{fontSize: 14, fill: '#475569'}} />
                <YAxis label={{ value: 'Ortalama Karakter Sayısı', angle: -90, position: 'insideLeft', offset: -5, fill: '#64748b' }} stroke="#64748b" />
                <Tooltip formatter={(value) => [`${value} Karakter`, 'Ortalama Uzunluk']} cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '10px' }} />
                <Bar dataKey="karakterSayisi" radius={[8, 8, 0, 0]} barSize={80}>
                  {lengthData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {activeTab === 'zaman' && (
          <div className="w-full flex flex-col">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-50 p-6 rounded-xl border-l-4 border-indigo-500 shadow-sm">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ortalama Risk</div>
                <div className="text-3xl font-extrabold text-slate-800">%{stats.avgRisk}</div>
              </div>
              <div className="bg-slate-50 p-6 rounded-xl border-l-4 border-emerald-500 shadow-sm">
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Toplam Commit</div>
                <div className="text-3xl font-extrabold text-slate-800">{stats.totalCommits.toLocaleString()}</div>
              </div>
              <div className={`bg-slate-50 p-6 rounded-xl border-l-4 shadow-sm ${stats.warningWeeks > 0 ? 'border-rose-500' : 'border-slate-300'}`}>
                <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Kritik Hafta Sayısı</div>
                <div className={`text-3xl font-extrabold ${stats.warningWeeks > 0 ? 'text-rose-600' : 'text-slate-800'}`}>
                  {stats.warningWeeks}
                </div>
              </div>
            </div>
            <div className="flex flex-col md:flex-row justify-between items-center bg-slate-50 p-4 rounded-xl mb-8 border border-slate-200 gap-4">
              <div className="flex bg-slate-200 p-1 rounded-lg">
                <button 
                  className={`px-6 py-2 text-sm font-semibold rounded-md transition-all ${viewMetric === 'burnout' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                  onClick={() => setViewMetric('burnout')}
                >
                  Tükenmişlik Riski (%)
                </button>
                <button 
                  className={`px-6 py-2 text-sm font-semibold rounded-md transition-all ${viewMetric === 'commit' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
                  onClick={() => setViewMetric('commit')}
                >
                  İş Yükü (Commit)
                </button>
              </div>

              <div className="flex items-center gap-4">
                <label className="text-sm font-bold text-slate-600">Uyarı Eşiği:</label>
                <input 
                  type="range" min="1.0" max="100.0" step="0.1" 
                  value={threshold} 
                  onChange={(e) => setThreshold(parseFloat(e.target.value))}
                  className="w-48 accent-rose-500"
                  disabled={viewMetric !== 'burnout'}
                />
                <span className="bg-rose-100 text-rose-700 px-3 py-1 rounded-md text-sm font-bold">
                  %{threshold.toFixed(1)}
                </span>
              </div>
            </div>

            {/* Grafik */}
            <h2 className="text-xl font-bold mb-6 text-slate-700 text-center">
              {viewMetric === 'burnout' ? 'Zaman İçerisinde Takım Stres Yükü' : 'Zaman İçerisinde Kodlama Yoğunluğu'}
            </h2>
            <ResponsiveContainer width="100%" height={400}>
              {viewMetric === 'burnout' ? (
                <LineChart data={chartData} onClick={handleChartClick} style={{ cursor: 'pointer' }} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{fontSize: 13}} />
                  <YAxis stroke="#64748b" domain={[0, 'dataMax + 1']} unit="%" tick={{fontSize: 13}} />
                  <Tooltip contentStyle={{ borderRadius: '10px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                  <Legend />
                  <ReferenceLine y={threshold} label={{ position: 'top', value: 'Kritik Eşik', fill: '#e11d48', fontSize: 12, fontWeight: 'bold' }} stroke="#e11d48" strokeDasharray="3 3" />
                  <Line 
                    type="monotone" dataKey="burnoutRisk" name="Tükenmişlik Skoru" 
                    stroke="#4f46e5" strokeWidth={3}
                    dot={renderCustomDot} activeDot={{ r: 8 }} 
                  />
                </LineChart>
              ) : (
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#64748b" tick={{fontSize: 13}} />
                  <YAxis stroke="#64748b" tick={{fontSize: 13}} />
                  <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '10px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                  <Legend />
                  <Bar dataKey="commitCount" name="Commit Sayısı" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                </BarChart>
              )}
            </ResponsiveContainer>
            {(isAnalyzing || analysis) && (
  <div className={`mt-8 p-6 rounded-2xl border transition-all duration-500 ${
    isAnalyzing ? 'bg-slate-50 border-slate-200 animate-pulse' : 'bg-indigo-50 border-indigo-100 shadow-inner'
  }`}>
    <div className="flex items-center gap-3 mb-4">
      <div className={`w-3 h-3 rounded-full ${isAnalyzing ? 'bg-amber-400' : 'bg-indigo-500'}`}></div>
      <h3 className="text-lg font-bold text-slate-800">
        {isAnalyzing 
          ? 'Yapay Zeka Analiz Ediyor...' 
          : 'YAPAY ZEKA ANALİZ SONUÇLARI'
        }
      </h3>
    </div>
    
    <div className="text-slate-700 leading-relaxed whitespace-pre-wrap">
      {isAnalyzing ? (
        <div className="space-y-2">
          <div className="h-4 bg-slate-200 rounded w-3/4"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
        </div>
      ) : (
        <ReactMarkdown>{analysis}</ReactMarkdown>
      )}
    </div>
  </div>
)}
          </div>
        )}

      </div>
    </div>
  );
}