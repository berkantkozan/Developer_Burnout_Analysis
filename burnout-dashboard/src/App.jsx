import React, { useState } from 'react';
import { 
  PieChart, Pie, Cell, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const sentimentData = [
  { name: 'Nötr (İşlemsel)', value: 82.9, color: '#94a3b8' }, 
  { name: 'Pozitif', value: 9.8, color: '#34d399' }, 
  { name: 'Negatif (Stres)', value: 7.3, color: '#f87171' } 
];

const productRiskData = [
  { name: 'ARMI', negatifOran: 100, graveyard: false },
  { name: 'STOMP', negatifOran: 100, graveyard: false },
  { name: 'ANNO', negatifOran: 50, graveyard: false },
  { name: 'Android BG Graveyard', negatifOran: 50, graveyard: true },
  { name: 'TSIK', negatifOran: 50, graveyard: false },
  { name: 'Add-on SDK Graveyard', negatifOran: 34.3, graveyard: true },
  { name: 'mozillaignite Graveyard', negatifOran: 28.6, graveyard: true },
  { name: 'MozReview Graveyard', negatifOran: 24.3, graveyard: true },
  { name: 'Context Graph Graveyard', negatifOran: 19.0, graveyard: true },
  { name: 'Firefox Private Network', negatifOran: 18.8, graveyard: false },
];

const lengthData = [
  { name: 'Negatif (Stresli)', karakterSayisi: 122.4, color: '#f87171' },
  { name: 'Pozitif', karakterSayisi: 82.5, color: '#34d399' },
  { name: 'Nötr', karakterSayisi: 71.5, color: '#94a3b8' },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('genel');

  return (
    <div className="p-8 max-w-7xl mx-auto bg-slate-50 min-h-screen font-sans text-slate-800">
      
      <header className="mb-8 border-b border-slate-200 pb-6">
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 mb-2">
          Otonom Ekip Dinamiği ve Burnout Analizi
        </h1>
        <p className="text-lg text-slate-500">
          Doğal Dil İşleme tabanlı sprint stres yükü raporu. Toplam analiz edilen kayıt: <span className="font-semibold">10.000 metin</span>
        </p>
      </header>

      <div style={{ display: 'flex', gap: '50px',justifyContent: 'center', marginBottom: '50px', marginTop: '50px', flexWrap: 'wrap' }}>
        
        <button 
          onClick={() => setActiveTab('genel')}
          style={{ marginRight: activeTab === 'genel' ? '0px' : '0px' }} // Flex gap kullandığımız için margin gerekmez ama kapsayıcıyı zorlar
          className={`px-10 py-6 font-bold rounded-2xl transition-all duration-300 flex items-center gap-4 text-lg ${
            activeTab === 'genel' 
              ? 'bg-indigo-600 text-white shadow-xl transform -translate-y-1' 
              : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Genel Duygu Dağılımı
        </button>

        <button 
          onClick={() => setActiveTab('risk')}
          className={`px-10 py-6 font-bold rounded-2xl transition-all duration-300 flex items-center gap-4 text-lg ${
            activeTab === 'risk' 
              ? 'bg-rose-600 text-white shadow-xl transform -translate-y-1' 
              : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Ürün Bazlı Stres Riski
        </button>

        <button 
          onClick={() => setActiveTab('uzunluk')}
          className={`px-10 py-6 font-bold rounded-2xl transition-all duration-300 flex items-center gap-4 text-lg ${
            activeTab === 'uzunluk' 
              ? 'bg-emerald-600 text-white shadow-xl transform -translate-y-1' 
              : 'bg-white text-slate-500 border border-slate-200 shadow-sm'
          }`}
        >
          Agresyon Analizi
        </button>

      </div>

      <div className="bg-white p-8 rounded-2xl shadow-lg border border-slate-100 flex flex-col items-center justify-center">
        
        {activeTab === 'genel' && (
          <div className="w-full flex flex-col items-center">
            <h2 className="text-2xl font-bold mb-6 text-slate-700">Tüm İletişimlerin Duygu Dağılımı</h2>
            {/* ÇÖZÜM BURADA: height="90%" yerine height={400} yazdık */}
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%" cy="50%"
                  innerRadius={100} outerRadius={150}
                  paddingAngle={4}
                  dataKey="value"
                  label={({name, value}) => `${name}: %${value}`}
                  labelLine={true}
                >
                  {sentimentData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
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
                 <span className="text-sm px-3 py-1 bg-amber-100 text-amber-800 rounded-full font-medium">
                     * "Graveyard" projeler sarı ile vurgulanmıştır.
                 </span>
             </div>
            <ResponsiveContainer width="100%" height={450}>
              <BarChart layout="vertical" data={productRiskData} margin={{ top: 5, right: 30, left: 180, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                <XAxis type="number" domain={[0, 100]} tickFormatter={(val) => `%${val}`} stroke="#64748b" />
                <YAxis dataKey="name" type="category" width={170} tick={{fontSize: 13, fill: '#475569'}} />
                <Tooltip formatter={(value) => [`%${value}`, 'Negatif (Stres) Oranı']} cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '10px' }} />
                <Bar dataKey="negatifOran" radius={[0, 6, 6, 0]} barSize={24}>
                   {productRiskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.graveyard ? '#fbbf24' : '#ef4444'} />
                  ))}
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
                  {lengthData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

      </div>
    </div>
  );
}